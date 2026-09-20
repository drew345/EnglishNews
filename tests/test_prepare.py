from copy import deepcopy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from english_news.content import load_content_run, content_lesson, apply_composition, validate_grounding
from english_news.lesson import digest, write_json, vocab_entries
from english_news.prepare import prepare_lessons, load_prepared, model_response
from english_news.selection import analyze, SelectionConfig
from test_selection import lesson, item


def content(number=1, count=1):
    return dict(schema='news-content-v1', source_run_id='20260920_test', story_number=number,
                story_count=count, source=dict(title='Local news', text='Selected source facts'),
                facts=[dict(id='f1', en='Services expand', natural_ko='서비스가 확대된다'),
                       dict(id='f2', en='Officials expand ferry departures for commuters.', natural_ko='당국은 통근자를 위해 페리 운항 횟수를 늘린다.')])


class PreparationTests(unittest.TestCase):
    def test_producer_consumer_contract_without_sibling_imports(self):
        from korean_news_media.content_export import story_content, publish_story
        source = SimpleNamespace(title='Title', link='', published='', summary='English source', article_text='')
        pairs = SimpleNamespace(sentences=[SimpleNamespace(**{k: f[k] for k in ('en', 'natural_ko')}) for f in content()['facts']])
        with tempfile.TemporaryDirectory() as directory:
            record = story_content('20260920_test', 1, 1, source, 'summary', pairs)
            path = publish_story(directory, record)
            loaded = load_content_run(path.parent)
            self.assertEqual(loaded, [record])
            self.assertEqual(content_lesson(loaded[0])['sentences'][0]['vocab'], [])

    def test_partial_mixed_and_corrupted_handoffs_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            one, two = content(1, 2), content(2, 2)
            write_json(root / 'story-01.content.json', dict(content=one, content_sha256=digest(one)))
            with self.assertRaisesRegex(ValueError, 'incomplete'):
                load_content_run(root)
            write_json(root / 'story-02.content.json', dict(content=two, content_sha256=digest(two)))
            self.assertEqual(len(load_content_run(root)), 2)
            two['source_run_id'] = '20260920_other'
            write_json(root / 'story-02.content.json', dict(content=two, content_sha256=digest(two)))
            with self.assertRaisesRegex(ValueError, 'Mixed'):
                load_content_run(root)
            write_json(root / 'story-02.content.json', dict(content=two, content_sha256='wrong'))
            with self.assertRaisesRegex(ValueError, 'corrupted'):
                load_content_run(root)

    def test_three_story_replay_is_stable_and_discards_old_vocabulary(self):
        lessons = [lesson('Officials expand ferry departures for commuters.', i) for i in range(1, 4)]
        responses = {}
        for source in lessons:
            candidate = next(c for c in analyze(source)['candidates'] if c['target'] == 'expand')
            responses[str(source['source_story_number'])] = dict(selection={'items': [item(candidate)]})
        with tempfile.TemporaryDirectory() as directory:
            first = prepare_lessons(lessons, Path(directory) / 'review', responses=responses)
            second = prepare_lessons(lessons, Path(directory) / 'review', responses=responses)
            self.assertEqual(first, second)
            prepared = load_prepared(first)
            self.assertEqual([len(vocab_entries(l)) for l in prepared['lessons']], [1, 1, 1])
            self.assertNotIn('never import', (first / 'written.txt').read_text(encoding='utf-8'))
            (first / 'written.txt').write_text('An untracked edit', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Review text changed'):
                load_prepared(first)

    def test_candidates_only_never_calls_model_and_cannot_make_media(self):
        client = Mock()
        with tempfile.TemporaryDirectory() as directory:
            output = prepare_lessons([lesson('Officials expand ferry departures.')], directory, candidates_only=True, client=client)
            client.chat.completions.create.assert_not_called()
            self.assertFalse((output / 'written.txt').exists())
            with self.assertRaises(ValueError):
                load_prepared(output)

    def test_optional_rewrite_requires_complete_facts_and_grounding(self):
        record = content()
        composition = dict(headline=dict(en='Ferry services expand', natural_ko='페리 운항이 확대된다', fact_ids=['f1']),
                           sentences=[dict(en='Officials expand ferry departures for commuters.', natural_ko='당국은 통근자를 위해 페리 운항 횟수를 늘린다.', fact_ids=['f2'])])
        revised = apply_composition(record, composition)
        row = item(next(c for c in analyze(revised)['candidates'] if c['target'] == 'expand'))
        responses = {'1': dict(composition=composition, grounding=dict(approved=True, issues=[]), selection={'items': [row]})}
        with tempfile.TemporaryDirectory() as directory:
            output = prepare_lessons([content_lesson(record)], directory, contents=[record], rewrite=True, responses=responses)
            self.assertEqual(load_prepared(output)['lessons'][0]['provenance'], 'english-composition-v1')
            responses['1']['grounding'] = dict(approved=False, issues=['Unsupported claim'])
            with self.assertRaisesRegex(ValueError, 'fact/translation'):
                prepare_lessons([content_lesson(record)], directory, contents=[record], rewrite=True, responses=responses)
        missing = deepcopy(composition)
        missing['sentences'][0]['fact_ids'] = ['f1']
        with self.assertRaisesRegex(ValueError, 'omitted'):
            apply_composition(record, missing)

    def test_model_cache_validates_retries_and_invalidates_context(self):
        client = Mock()
        def answer(value):
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(value)))])
        client.chat.completions.create.side_effect = [answer({'approved': False, 'issues': ['bad']}), answer({'approved': True, 'issues': []})]
        with tempfile.TemporaryDirectory() as directory:
            value = model_response('Review', {'text': 'one'}, 'model', directory, validate_grounding, client=client)
            self.assertEqual(client.chat.completions.create.call_count, 2)
            self.assertEqual(value, model_response('Review', {'text': 'one'}, 'model', directory, validate_grounding))
            with self.assertRaisesRegex(ValueError, 'No validated'):
                model_response('Review', {'text': 'changed'}, 'model', directory, validate_grounding)
            with self.assertRaisesRegex(ValueError, 'No validated'):
                model_response('New rules', {'text': 'one'}, 'model', directory, validate_grounding)
            cached = next(Path(directory).glob('*.json'))
            data = json.loads(cached.read_text(encoding='utf-8'))
            data['response']['approved'] = False
            write_json(cached, data)
            with self.assertRaisesRegex(ValueError, 'Corrupted'):
                model_response('Review', {'text': 'one'}, 'model', directory, validate_grounding)

