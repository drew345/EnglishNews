from copy import deepcopy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from english_news.definitions import (INSTRUCTIONS, VERSION, refresh_definitions,
                                      validate_definition, validate_revision)
from english_news.lesson import vocab_entries
from english_news.prepare import load_prepared, model_response, prepare_lessons
from english_news.selection import analyze, apply_selection, SELECTION_INSTRUCTIONS
from test_selection import lesson, item


class DefinitionTests(unittest.TestCase):
    def test_length_and_circularity_without_substring_ban(self):
        for explanation in ('People you do not know.', 'Unknown.', 'A sport with five events.'):
            self.assertEqual(validate_definition(explanation, 'strangers'), explanation)
        for explanation in ('Courage.', 'The courage.', 'Courage is a concept.',
                            'one two three four five six seven eight nine ten eleven', '', '...'):
            with self.subTest(explanation=explanation), self.assertRaises(ValueError):
                validate_definition(explanation, 'courage')
        with self.assertRaisesRegex(ValueError, 'circular'):
            validate_definition('To compete.', 'competing', 'compete')
        for target, text in [('uncertain', 'Not certain.'), ('rebuild', 'To build again.'),
                             ('shooters', 'Athletes competing in shooting events.'),
                             ('cover its operating costs', 'Earn enough to pay operating expenses.')]:
            self.assertEqual(validate_definition(text, target), text)

    def test_selection_uses_policy_and_rejects_invalid_definition(self):
        self.assertIn(INSTRUCTIONS, SELECTION_INSTRUCTIONS)
        source = lesson('Officials expand ferry departures.')
        analysis = analyze(source)
        candidate = next(c for c in analysis['candidates'] if c['target'] == 'expand')
        for explanation in ('Expand.', 'one two three four five six seven eight nine ten eleven'):
            with self.assertRaises(ValueError):
                apply_selection(source, analysis, {'items': [item(candidate, en_explanation=explanation)]})

    def test_revision_requires_exact_ids_and_cannot_change_gloss(self):
        entries = [dict(id='one', target='strangers', lemma='stranger')]
        valid = dict(entries=[dict(id='one', en_explanation='People you do not know.')])
        self.assertEqual(validate_revision(valid, entries), {'one': 'People you do not know.'})
        for rows in ([], valid['entries'] * 2, [dict(id='unknown', en_explanation='Unknown people.')],
                     [dict(valid['entries'][0], ko_gloss='변경')]):
            with self.assertRaises(ValueError):
                validate_revision(dict(entries=rows), entries)

    def test_length_failure_uses_existing_corrective_retry(self):
        client = Mock()
        def answer(text):
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps({'definition': text})))])
        client.chat.completions.create.side_effect = [
            answer('one two three four five six seven eight nine ten eleven'), answer('People you do not know.')]
        with tempfile.TemporaryDirectory() as directory:
            result = model_response(INSTRUCTIONS, {}, 'test', directory,
                                    lambda r: validate_definition(r['definition'], 'strangers'), client=client)
            self.assertEqual(result['definition'], 'People you do not know.')
            self.assertIn('exceeds 10 words', client.chat.completions.create.call_args.kwargs['messages'][-1]['content'])
            self.assertEqual(client.chat.completions.create.call_count, 2)

    def test_refresh_preserves_selection_source_and_old_review(self):
        source = lesson('Officials expand ferry departures.')
        candidate = next(c for c in analyze(source)['candidates'] if c['target'] == 'expand')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'reviews'
            first = prepare_lessons([source], root, responses={'1': {'selection': {'items': [item(candidate)]}}})
            original = load_prepared(first)
            old_bytes = (first / 'written.txt').read_bytes()
            key = vocab_entries(original['lessons'][0])[0]['id']
            replay = dict(entries=[dict(id=key, en_explanation='To make something larger.')])
            second = refresh_definitions(first, root, replay=replay)
            revised = load_prepared(second)
            expected = deepcopy(original['lessons'])
            vocab_entries(expected[0])[0]['en_explanation'] = replay['entries'][0]['en_explanation']
            self.assertEqual(revised['lessons'], expected)
            self.assertEqual(revised['reports'], original['reports'])
            self.assertEqual(revised['profile']['definitions'], VERSION)
            self.assertEqual((first / 'written.txt').read_bytes(), old_bytes)
            self.assertNotEqual(first, second)
            self.assertEqual(revised['definition_revision']['response'], replay)
            self.assertFalse(revised['publication_enabled'])


if __name__ == '__main__':
    unittest.main()
