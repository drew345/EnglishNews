from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from english_news.audio import synthesize_plan, segment_plan
from english_news.lesson import CURRENT_SPEECH_PROFILE, prepared_plan, speech_script, vocab_entries
from english_news.prepare import prepare_lessons, load_prepared, write_prepared
from english_news.selection import analyze
from english_news.speech_review import prepare_speech_review
from test_selection import lesson, item


class SpeechReviewTests(unittest.TestCase):
    def test_english_only_increase_reaches_actual_transport(self):
        source = lesson('Commuters travel to work.')
        source['sentences'][0]['vocab'] = [dict(id='s1.b1.v0', target='Commuters', ko_gloss='통근자들',
                                               en_explanation='People traveling to work.')]
        plan = prepared_plan(source, dict(speech=CURRENT_SPEECH_PROFILE))
        self.assertAlmostEqual(CURRENT_SPEECH_PROFILE['target_speed'] / .88, 1.02)
        expected = []
        for unit in plan:
            texts, _ = segment_plan(unit)
            speeds = unit.get('segment_speeds', [unit['speed']] * len(texts))
            for text, speed in zip(texts, speeds):
                expected.append((text, speed))
                if unit['name'] == 'headline_label':
                    self.assertEqual(text, 'Headline 1.')
                    self.assertEqual(speed, .8976)
                elif text == '통근자들.':
                    self.assertEqual(speed, .88)
                elif any('\uac00' <= c <= '\ud7a3' for c in text):
                    self.assertEqual(speed, 1.07)
                else:
                    self.assertEqual(speed, .8976)
        captured = []
        def transport(units, prefix, **kwargs):
            prefix.parent.mkdir(parents=True, exist_ok=True)
            captured.extend((u.text, u.speed) for u in units)
            return SimpleNamespace(audio_paths=[prefix.parent / f'{i}.mp3' for i in range(len(units))], request_metadata=[{} for _ in units])
        with tempfile.TemporaryDirectory() as directory, \
             patch('korean_news_media.openai_speech_tts.synthesize_speech_units', side_effect=transport), \
             patch('korean_news_media.tts_common.concatenate_mp3'), \
             patch('english_news.audio.inspect_audio_signal', return_value={'passed': True}):
            synthesize_plan(plan, Path(directory), voice='alloy', client=None, instructions='test')
        self.assertCountEqual(captured, expected)

    def test_old_review_preserved_new_script_matches_plan_and_detects_edits(self):
        source = lesson('Officials expand ferry departures.')
        candidate = next(c for c in analyze(source)['candidates'] if c['target'] == 'expand')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = prepare_lessons([source], root, responses={'1': {'selection': {'items': [item(candidate)]}}})
            historical = load_prepared(first)
            del historical['profile']['speech']
            old = write_prepared(historical, root)
            old_plan = prepared_plan(historical['lessons'][0], historical['profile'])
            self.assertEqual(next(u['speed'] for u in old_plan if u['name'] == 'headline_en'), .88)
            original_bytes = (old / 'speech-plan.json').read_bytes()
            revised_path = prepare_speech_review(old, root)
            revised = load_prepared(revised_path)
            self.assertEqual(revised['lessons'], historical['lessons'])
            self.assertEqual((revised_path / 'written.txt').read_text(encoding='utf-8'),
                             (old / 'written.txt').read_text(encoding='utf-8').replace('## 헤드라인 1', '## Headline 1'))
            self.assertEqual((old / 'speech-plan.json').read_bytes(), original_bytes)
            plan = prepared_plan(revised['lessons'][0], revised['profile'])
            script = revised_path / 'speech-script.txt'
            self.assertEqual(script.read_text(encoding='utf-8'), speech_script(plan))
            unit = next(u for u in plan if u['name'] == vocab_entries(revised['lessons'][0])[0]['id'])
            self.assertEqual(unit['text'].splitlines().count('expand.'), 4)
            script.write_text('An unreviewed edit', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'speech script changed'):
                load_prepared(revised_path)
