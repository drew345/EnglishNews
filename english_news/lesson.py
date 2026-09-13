from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def import_story(text: str, source_run_id: str, story_number: int = 1) -> dict:
    """Strict importer for the historical written format, not a live producer hook."""
    sections = re.split(r'^## Headline (\d+)\s*$', text, flags=re.M)
    matches = [sections[i + 1] for i in range(1, len(sections), 2) if int(sections[i]) == story_number]
    if len(matches) != 1:
        raise ValueError('Expected exactly one selected headline')
    content = matches[0].split('\n---')[0]
    headline, body = content.split('## Bilingual Lesson (sentence by sentence)', 1)
    body, review = body.split('## Full Summary', 1)
    pair = [line.strip() for line in headline.splitlines() if line.strip()]
    if len(pair) != 2:
        raise ValueError('Expected English/Korean headline pair')
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    sentences = []
    pos = 0
    while pos < len(lines):
        en = lines[pos]
        pos += 1
        vocab = []
        if pos < len(lines) and lines[pos] == '### Vocab:':
            pos += 1
            while pos < len(lines) and lines[pos].startswith('- '):
                fields = lines[pos][2:].split(': ', 2)
                if len(fields) != 3 or not all(fields):
                    raise ValueError('Malformed vocabulary row')
                vocab.append(dict(id=f's{story_number}.b{len(sentences)+1}.v{len(vocab)+1}',
                                  word=fields[0], en_def=fields[1], ko_def=fields[2]))
                pos += 1
        if pos >= len(lines) or lines[pos].startswith(('#', '- ')) or not re.search('[가-힣]', lines[pos]):
            raise ValueError('Expected aligned Korean body sentence')
        sentences.append(dict(en=en, natural_ko=lines[pos], vocab=vocab))
        pos += 1
    expected_review = ' '.join([pair[1]] + [s['natural_ko'] for s in sentences])
    if ' '.join(review.split()) != expected_review:
        raise ValueError('Historical Korean review does not match imported sentences')
    if not sentences:
        raise ValueError('Empty story')
    return dict(schema_version=1, source_run_id=source_run_id, source_story_number=story_number,
                provenance='historical-written-import-v1',
                source_text_sha256=hashlib.sha256(text.encode('utf-8')).hexdigest(),
                headline=dict(en=pair[0], natural_ko=pair[1]), sentences=sentences)


def vocab_entries(lesson: dict) -> list[dict]:
    return [v for s in lesson['sentences'] for v in s['vocab']]


def validate_explanations(lesson: dict, result: dict) -> dict:
    entries = result.get('entries', [])
    if not isinstance(entries, list):
        raise ValueError('Expected explanation entries')
    indexed = {}
    for entry in entries:
        key = entry['id']
        explanation = entry['en_explanation']
        if key in indexed or not isinstance(explanation, str) or not 3 <= len(explanation.split()) <= 30:
            raise ValueError('Duplicate ID or invalid explanation')
        if re.search('[가-힣\r\n]', explanation):
            raise ValueError('Explanations must be single-line English')
        indexed[key] = dict(en_explanation=explanation.strip(), review_note=str(entry.get('review_note', '')))
    if set(indexed) != {v['id'] for v in vocab_entries(lesson)}:
        raise ValueError('Explanation IDs do not match vocabulary')
    return indexed


def sentence(text: str) -> str:
    return text if text[-1:] in '.!?。' else text + '.'


def make_plan(lesson: dict, explanations: dict, *, target_speed=.88, native_speed=1.07) -> list[dict]:
    units = []
    def add(name, text, speed):
        units.append(dict(name=name, text=text, speed=speed))
    h = lesson['headline']
    add('headline_ko', h['natural_ko'], native_speed)
    add('headline_en', '\n'.join([h['en']] * 2), target_speed)
    for i, body in enumerate(lesson['sentences'], 1):
        add(f'body{i}_ko', body['natural_ko'], native_speed)
        for v in body['vocab']:
            gloss = sentence(v['en_def'])
            add(v['id'], '\n'.join([gloss, gloss, sentence(v['word']),
                sentence(explanations[v['id']]['en_explanation']), gloss, gloss]), target_speed)
        add(f'body{i}_en', '\n'.join([body['en']] * 2), target_speed)
    add('review_en', 'Full review.\n' + '\n'.join([h['en']] + [s['en'] for s in lesson['sentences']]), target_speed)
    return units


def written_lesson(lesson: dict, explanations: dict) -> str:
    h = lesson['headline']
    lines = ['## 뉴스 1', '', h['natural_ko'], h['en'], '', '## 문장별 영어 학습', '']
    for body in lesson['sentences']:
        lines.extend([body['natural_ko'], ''])
        if body['vocab']:
            lines.append('### 어휘')
        for v in body['vocab']:
            lines.extend([f"- {v['en_def']} — {v['word']}", explanations[v['id']]['en_explanation']])
        lines.extend(['', body['en'], ''])
    lines.extend(['## 영어 전체 복습', '', h['en'], '', ' '.join(s['en'] for s in lesson['sentences']), ''])
    return '\n'.join(lines)
