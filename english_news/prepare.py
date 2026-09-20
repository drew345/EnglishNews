"""Text-only preparation. Paid requests require --allow-model; never makes media."""
import argparse
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import re

from .content import (load_content_run, content_lesson, apply_composition, validate_grounding,
                      COMPOSITION_INSTRUCTIONS, GROUNDING_INSTRUCTIONS)
from .lesson import digest, write_json, written_lesson, make_plan, vocab_entries, import_story
from .selection import analyze, apply_selection, SelectionConfig, SELECTION_INSTRUCTIONS, VERSION

PREPARATION_VERSION = 'english-text-preparation-v1'


def model_response(instructions, payload, model, cache_root, validator, *, client=None, replay=None):
    identity = digest(dict(instructions=instructions, payload=payload, model=model))
    path = Path(cache_root) / f'{identity}.json'
    if replay is not None:
        validator(replay)
        return replay
    if path.exists():
        saved = json.loads(path.read_text(encoding='utf-8'))
        if saved.get('identity') != identity or saved.get('response_sha256') != digest(saved.get('response')):
            raise ValueError('Corrupted model response cache')
        validator(saved['response'])
        return saved['response']
    if client is None:
        raise ValueError('No validated cached response. Use --responses for offline replay or --allow-model for a new run.')
    messages = [{'role': 'system', 'content': instructions},
                {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}]
    for attempt in range(2):
        response = client.chat.completions.create(model=model, response_format={'type': 'json_object'},
            messages=deepcopy(messages))
        try:
            value = json.loads(response.choices[0].message.content)
            validator(value)
        except (ValueError, KeyError, TypeError) as exc:
            raw = response.choices[0].message.content
            write_json(Path(cache_root) / 'invalid' / f'{identity}-{digest(raw)[:12]}.json',
                       dict(identity=identity, raw_response=raw, validation_error=str(exc)))
            if attempt == 1:
                raise
            messages.extend([{'role': 'assistant', 'content': raw or ''},
                             {'role': 'user', 'content': f'Validation failed: {exc}. Return the complete corrected JSON. Use only supplied IDs, do not repeat IDs across items and rejections, and use only the allowed rejection reasons.'}])
            continue
        write_json(path, dict(identity=identity, response=value, response_sha256=digest(value)))
        return value


def clean_lesson(lesson):
    result = deepcopy(lesson)
    for s in result['sentences']:
        s['vocab'] = []
    return result


def prepare_lessons(lessons, output_root, *, config=SelectionConfig(), model='gpt-5.6-luna',
                    contents=None, rewrite=False, candidates_only=False, responses=None, client=None):
    if not lessons or len({l['source_run_id'] for l in lessons}) != 1:
        raise ValueError('Expected one source run')
    if [l['source_story_number'] for l in lessons] != list(range(1, len(lessons) + 1)):
        raise ValueError('Stories must be complete and in selected order')
    source_run = lessons[0]['source_run_id']
    if not re.fullmatch(r'\d{8}_[A-Za-z0-9_-]+', source_run):
        raise ValueError('Invalid source run ID')
    if rewrite and (not contents or candidates_only):
        raise ValueError('Rewrite requires structured facts and semantic evaluation')
    cache = Path(output_root).parent / '.text-cache'
    prepared, reports, counts = [], [], {}
    for index, original in enumerate(lessons):
        lesson = clean_lesson(original)
        replay = (responses or {}).get(str(index + 1), {})
        if rewrite:
            content = contents[index]
            composition = model_response(COMPOSITION_INSTRUCTIONS, content, model, cache,
                lambda r: apply_composition(content, r), client=client, replay=replay.get('composition'))
            lesson = apply_composition(content, composition)
            model_response(GROUNDING_INSTRUCTIONS, dict(content=content, lesson=lesson), model, cache,
                validate_grounding, client=client, replay=replay.get('grounding'))
        analysis = analyze(lesson, config)
        if candidates_only:
            reports.append(analysis)
            prepared.append(lesson)
            continue
        # Excluded spans stay in the local audit, never in the model's choices.
        payload = dict(lesson=lesson, analysis={k: v for k, v in analysis.items() if k != 'rejected'})
        selection = model_response(SELECTION_INSTRUCTIONS, payload, model, cache,
            lambda r: apply_selection(lesson, analysis, r, config, run_counts=dict(counts)),
            client=client, replay=replay.get('selection'))
        lesson, report = apply_selection(lesson, analysis, selection, config, run_counts=counts)
        prepared.append(lesson)
        reports.append(report)
    profile = dict(version=PREPARATION_VERSION, selector=VERSION, config=asdict(config), model=model,
                   rewrite=rewrite, candidates_only=candidates_only)
    payload = dict(source_run_id=source_run, lessons=prepared, reports=reports, profile=profile,
                   status='candidates_only' if candidates_only else 'text_ready_for_review', publication_enabled=False)
    identity = digest(payload)
    output = Path(output_root) / f'{source_run[:8]}_english_text_{identity[:12]}'
    output.mkdir(parents=True, exist_ok=True)
    blocks, plans = [], []
    for lesson, report in zip(prepared, reports):
        number = lesson['source_story_number']
        write_json(output / f'story-{number:02d}-selection.json', report)
        if not candidates_only:
            explanations = {v['id']: dict(en_explanation=v['en_explanation'], review_note='') for v in vocab_entries(lesson)}
            blocks.append(written_lesson(lesson, explanations))
            plans.extend(make_plan(lesson, explanations))
    if not candidates_only:
        (output / 'written.txt').write_text('\n---\n\n'.join(blocks), encoding='utf-8')
        write_json(output / 'speech-plan.json', dict(units=plans))
    write_json(output / 'preparation.json', dict(content_sha256=identity, content=payload))
    return output


def load_prepared(path):
    path = Path(path)
    envelope = json.loads((path / 'preparation.json').read_text(encoding='utf-8'))
    payload = envelope.get('content', {})
    if envelope.get('content_sha256') != digest(payload) or payload.get('status') != 'text_ready_for_review':
        raise ValueError('Expected verified, selected text preparation')
    if payload.get('profile', {}).get('version') != PREPARATION_VERSION:
        raise ValueError('Unsupported preparation version')
    source_run = payload.get('source_run_id', '')
    lessons, reports = payload.get('lessons', []), payload.get('reports', [])
    if (not re.fullmatch(r'\d{8}_[A-Za-z0-9_-]+', source_run) or not lessons
            or len(reports) != len(lessons) or payload.get('publication_enabled') is not False):
        raise ValueError('Invalid prepared run')
    blocks, plans = [], []
    for number, (lesson, report) in enumerate(zip(lessons, reports), 1):
        if (lesson.get('source_run_id') != source_run or lesson.get('source_story_number') != number
                or lesson.get('schema_version') != 2 or lesson.get('vocabulary_profile') != VERSION):
            raise ValueError('Invalid prepared lesson order or version')
        entries = vocab_entries(lesson)
        if len({v['id'] for v in entries}) != len(entries) or report.get('selected_count') != len(entries):
            raise ValueError('Prepared vocabulary does not match its audit')
        for i, body in enumerate(lesson['sentences'], 1):
            for v in body['vocab']:
                if v['sentence_index'] != i or body['en'][v['start']:v['end']] != v['target']:
                    raise ValueError('Prepared vocabulary source changed')
        explanations = {v['id']: dict(en_explanation=v['en_explanation'], review_note='') for v in entries}
        blocks.append(written_lesson(lesson, explanations))
        plans.extend(make_plan(lesson, explanations))
    # Media must use exactly the text and speech plan that were presented for review.
    if (path / 'written.txt').read_text(encoding='utf-8') != '\n---\n\n'.join(blocks):
        raise ValueError('Review text changed; prepare and review a new bundle before media')
    if json.loads((path / 'speech-plan.json').read_text(encoding='utf-8')) != dict(units=plans):
        raise ValueError('Review speech plan changed')
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--content-run', type=Path)
    inputs.add_argument('--legacy-written', type=Path, help='Read sentence pairs only; discard inherited vocabulary')
    parser.add_argument('--source-run-id')
    parser.add_argument('--output-root', type=Path, default=Path('output/text-review'))
    parser.add_argument('--cutoff', type=int, default=3500)
    parser.add_argument('--overrides', type=Path, help='JSON include/exclude/easy arrays and rank_overrides object')
    parser.add_argument('--rewrite', action='store_true')
    parser.add_argument('--candidates-only', action='store_true')
    parser.add_argument('--responses', type=Path, help='Offline reviewed model-response fixtures by story number')
    parser.add_argument('--allow-model', action='store_true')
    parser.add_argument('--model', default='gpt-5.6-luna')
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    contents = load_content_run(args.content_run) if args.content_run else None
    if contents:
        lessons = [content_lesson(c) for c in contents]
    else:
        if not args.source_run_id:
            parser.error('--legacy-written requires --source-run-id')
        text = args.legacy_written.read_text(encoding='utf-8')
        count = len(re.findall(r'^## Headline \d+\s*$', text, re.M))
        lessons = [import_story(text, args.source_run_id, i) for i in range(1, count + 1)]
    overrides = json.loads(args.overrides.read_text(encoding='utf-8')) if args.overrides else {}
    config = SelectionConfig(cutoff=args.cutoff, include=tuple(overrides.get('include', [])),
        exclude=tuple(overrides.get('exclude', [])), easy=tuple(overrides.get('easy', [])),
        rank_overrides=tuple(overrides.get('rank_overrides', {}).items()))
    responses = json.loads(args.responses.read_text(encoding='utf-8')) if args.responses else None
    client = None
    if args.allow_model and not args.candidates_only:
        from .runtime import client_from_existing_key
        client = client_from_existing_key(args.env_file)
    output = prepare_lessons(lessons, args.output_root, config=config, model=args.model, contents=contents,
        rewrite=args.rewrite, candidates_only=args.candidates_only, responses=responses, client=client)
    print(f'TEXT REVIEW: {output.resolve()}')


if __name__ == '__main__':
    main()
