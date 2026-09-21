from array import array
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from english_news.audio import synthesize_plan
from english_news.audio_signal import pcm_signal


class AudioSignalTests(unittest.TestCase):
    def test_empty_near_silence_and_click_fail_but_quiet_speech_passes(self):
        for values in ([], [0] * 8000, [43, -43] * 4000, [32000] + [0] * 7999):
            self.assertFalse(pcm_signal(array('h', values).tobytes())['passed'])
        self.assertTrue(pcm_signal(array('h', [200, -200] * 1600).tobytes())['passed'])

    def test_only_bad_korean_clip_is_retried_and_used_in_assembly(self):
        self.run_retry_case([True, False, True, True], succeeds=True)

    def test_persistent_silence_blocks_assembly_after_two_retries(self):
        self.run_retry_case([True, False, False, False], succeeds=False)

    def run_retry_case(self, checks, succeeds):
        unit = dict(name='s1.b2.v1', text='hands-on.\nhands-on.\n직접 체험하는.\nLearning by doing.\nhands-on.\nhands-on.',
                    speed=.8976, segment_speeds=[.8976, .88, .8976])
        calls = []
        def transport(units, prefix, **kwargs):
            prefix.parent.mkdir(parents=True, exist_ok=True)
            calls.append([(u.text, u.speed) for u in units])
            return SimpleNamespace(audio_paths=[prefix.with_name(prefix.name + f'-{i}.mp3') for i in range(len(units))],
                                   request_metadata=[{'input': u.text} for u in units])
        with tempfile.TemporaryDirectory() as directory, \
             patch('korean_news_media.openai_speech_tts.synthesize_speech_units', side_effect=transport), \
             patch('korean_news_media.tts_common.concatenate_mp3') as concat, \
             patch('english_news.audio.inspect_audio_signal', side_effect=[{'passed': x} for x in checks]):
            if succeeds:
                _, records = synthesize_plan([unit], Path(directory), voice='alloy', client=None, instructions='test')
                sources = records[0]['assembly_sources']
                self.assertIn('retry1', sources[2])
                self.assertEqual(sources[0], sources[1])
                self.assertEqual(sources[0], sources[4])
                self.assertEqual(sources[0], sources[5])
                self.assertNotIn('retry', sources[3])
                self.assertEqual(len(calls), 2)
            else:
                with self.assertRaisesRegex(ValueError, 'two retries failed'):
                    synthesize_plan([unit], Path(directory), voice='alloy', client=None, instructions='test')
                concat.assert_not_called()
                self.assertEqual(len(calls), 3)
            for call in calls[1:]:
                self.assertEqual(call, [('직접 체험하는.', .88)])
            report = json.loads((Path(directory) / 'speech-parts/s1.b2.v1/signal-qa.json').read_text())
            self.assertEqual(len(report['checks']), len(checks))
