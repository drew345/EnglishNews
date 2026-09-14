import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from english_news.workflow import snapshot, timeline
from english_news.workflow import workflow_lock
from english_news.render import render_fingerprint


class WorkflowTests(unittest.TestCase):
    def test_concurrent_build_is_rejected_and_lock_released(self):
        with tempfile.TemporaryDirectory() as tmp, patch('english_news.workflow.ROOT', Path(tmp)):
            with workflow_lock():
                with self.assertRaisesRegex(RuntimeError, 'Another English build'):
                    with workflow_lock():
                        pass
            with workflow_lock():
                pass

    def test_render_identity_changes_with_audio_text_images_or_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run, lab = root / 'run', root / 'lab'
            run.mkdir(); (lab / 'scripts').mkdir(parents=True)
            paths = [run / n for n in ('run.json', 'audio.mp3', 'written.txt', 'story.txt', 'image.png')]
            paths.append(lab / 'scripts/render.py')
            for path in paths:
                path.write_bytes(b'original')
            metadata = dict(combined_audio_path=str(paths[1]), combined_written_path=str(paths[2]),
                            stories=[dict(written_path=str(paths[3]))], video_story_images=[dict(path=str(paths[4]))])
            initial = render_fingerprint(run, metadata, lab)
            for path in paths:
                path.write_bytes(b'changed')
                self.assertNotEqual(initial, render_fingerprint(run, metadata, lab))
                path.write_bytes(b'original')

    def test_timeline_is_contiguous_and_preserves_order(self):
        stories = timeline([dict(duration=12.5, title='one'), dict(duration=20.25, title='two')])
        self.assertEqual([(s['start_sec'], s['end_sec']) for s in stories], [(0, 12.5), (12.5, 32.75)])
        self.assertEqual(stories[1]['title'], 'two')
        with self.assertRaises(ValueError):
            timeline([dict(duration=0)])

    def test_snapshot_rejects_changed_or_incomplete_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, staged, dest = root / '20260914_test', root / 'staged', root / 'snapshot'
            source.mkdir(); staged.mkdir()
            meta = dict(run_id=source.name, status='completed', stories=[{}])
            (source / 'run.json').write_text(json.dumps(meta))
            (staged / 'run.json').write_text(json.dumps(meta))
            (source / '20260914-news-written.txt').write_text('lesson')
            (staged / 'story-01-video-image.png').write_bytes(b'image')
            snapshot(source, staged, dest)
            snapshot(source, staged, dest)
            (source / '20260914-news-written.txt').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'changed'):
                snapshot(source, staged, dest)
            self.assertEqual((dest / 'source/20260914-news-written.txt').read_text(), 'lesson')
            meta['status'] = 'running'
            (source / 'run.json').write_text(json.dumps(meta))
            with self.assertRaisesRegex(ValueError, 'completed'):
                snapshot(source, staged, dest)
