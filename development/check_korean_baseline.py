"""Rebuild deterministic Korean presentation artifacts against the frozen baseline."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent / 'KoreanLessonVideoLab'
sys.path.insert(0, str(LAB))
from scripts.make_teleprompter_video import render_ass_file, render_story_backgrounds, write_youtube_metadata
from scripts.make_youtube_thumbnail import generate_youtube_thumbnail

baseline = ROOT / '.local/baselines/20260913_122823_97cda690'
fixture = ROOT / '.local/regression/20260913_122823_97cda690'
fixture.mkdir(parents=True, exist_ok=True)
metadata = json.loads((baseline / 'staged/run.json').read_text(encoding='utf-8'))
for key in ('combined_audio_path', 'combined_written_path'):
    metadata[key] = str(baseline / 'staged' / Path(metadata[key]).name)
for entry in metadata['video_story_images']:
    entry['path'] = str(baseline / 'staged' / f'story-{entry["story_index"]:02d}-video-image.png')
(fixture / 'run.json').write_text(json.dumps(metadata, ensure_ascii=False), encoding='utf-8')
out = fixture / 'rendered'
written = Path(metadata['combined_written_path'])
paths = [render_ass_file(fixture, out), *render_story_backgrounds(fixture, out),
         generate_youtube_thumbnail(metadata['run_id'], out),
         *write_youtube_metadata(metadata, written, out)]
checks = []
for path in paths:
    if path is None:
        continue
    expected = baseline / 'video' / path.name
    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    expected_hash = hashlib.sha256(expected.read_bytes()).hexdigest()
    checks.append(dict(file=path.name, identical=actual_hash == expected_hash, sha256=actual_hash))
report = dict(checks=checks, all_identical=all(check['identical'] for check in checks))
(fixture / 'comparison.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
if not report['all_identical']:
    raise SystemExit(1)
