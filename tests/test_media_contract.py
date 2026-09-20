import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch, Mock

from english_news.lesson import write_json
from english_news.prepare import prepare_lessons
from english_news.render import render_run
from english_news.selection import analyze
from english_news.workflow import run
from test_selection import lesson, item


class MediaContractTests(unittest.TestCase):
    def test_reviewed_text_flows_to_media_without_korean_vocab_or_enrichment(self):
        lessons = [lesson('Officials expand ferry departures.', n) for n in range(1, 4)]
        responses = {str(n): dict(selection={'items': [item(next(c for c in analyze(l)['candidates'] if c['target'] == 'expand'))]})
                     for n, l in enumerate(lessons, 1)}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prepared = prepare_lessons(lessons, root / 'text', responses=responses)
            staged = root / 'staged'
            write_json(staged / 'run.json', dict(run_id='20260920_test'))
            for n in range(1, 4):
                (staged / f'story-{n:02d}-video-image.png').write_bytes(b'test image')
            def concat(paths, output):
                output.write_bytes(b'test audio')
            with patch('english_news.workflow.ROOT', root), patch('english_news.workflow.client_from_existing_key'), \
                    patch('english_news.audio.synthesize_plan', return_value=([], [])) as synth, \
                    patch('korean_news_media.tts_common.concatenate_mp3', side_effect=concat), \
                    patch('mutagen.mp3.MP3', return_value=SimpleNamespace(info=SimpleNamespace(length=20))), \
                    patch('english_news.workflow.subprocess.run'):
                output = run(prepared, staged, None, render=False)
            self.assertEqual(synth.call_count, 3)
            meta = json.loads((output / 'run.json').read_text(encoding='utf-8'))
            self.assertEqual(meta['audience_settings']['lesson_title'], '뉴스로 배우는 영어')
            self.assertFalse(meta['youtube_publication']['enabled'])
            self.assertEqual(meta['stories'][-1]['end_sec'], 60)
            self.assertNotIn('never import', (output / '20260920-english-news-written.txt').read_text(encoding='utf-8'))
            write_json(staged / 'run.json', dict(run_id='different'))
            with self.assertRaisesRegex(ValueError, 'another source run'), patch('english_news.workflow.client_from_existing_key') as client:
                run(prepared, staged, None, render=False)
            client.assert_not_called()

    def test_renderer_uses_explicit_cli_without_linked_worktree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / 'output/runs/20260920_test'
            lab = root / 'independently-located-renderer'
            (lab / 'scripts').mkdir(parents=True)
            (lab / 'scripts/make_teleprompter_video.py').write_text('# Test interface', encoding='utf-8')
            output.mkdir(parents=True)
            audio, written = output / 'audio.mp3', output / 'written.txt'
            audio.write_bytes(b'audio')
            written.write_text('text', encoding='utf-8')
            write_json(output / 'run.json', dict(audience='english', status='completed', stories=[],
                       combined_audio_path=str(audio), combined_written_path=str(written)))
            def render(command, **kwargs):
                (output / 'video/20260920-english-news-lesson.mp4').write_bytes(b'test video')
                self.assertEqual(command, ['chosen-python', str(lab / 'scripts/make_teleprompter_video.py'), str(output), '--out-dir', str(output / 'video')])
                self.assertEqual(kwargs, dict(check=True, cwd=lab))
            with patch('english_news.render.ROOT', root), patch('english_news.render.subprocess.run', side_effect=render):
                video = render_run(output, lab=lab, python='chosen-python')
            self.assertTrue(video.is_relative_to(output))
            self.assertFalse((lab / '.git').exists())
