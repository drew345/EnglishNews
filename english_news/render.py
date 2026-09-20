"""Render an English prototype locally, without the publication watcher."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

from .lesson import write_json
from .runtime import ROOT
from .review import file_hash
from .lesson import digest


def render_fingerprint(run, metadata, lab):
    inputs = [run / 'run.json', Path(metadata['combined_audio_path']), Path(metadata['combined_written_path'])]
    inputs.extend(Path(s['written_path']) for s in metadata['stories'] if s.get('written_path'))
    inputs.extend(Path(s['path']) for s in metadata.get('video_story_images', []))
    if any(not p.resolve().is_relative_to(run.resolve()) for p in inputs):
        raise ValueError('Render input escapes English run directory')
    inputs.extend(sorted((lab / 'scripts').glob('*.py')))
    inputs.extend(sorted(p for p in (lab / 'assets').rglob('*') if p.is_file()))
    return digest([(str(p), file_hash(p)) for p in inputs])


def render_run(run, lab=None, python=None):
    run = run.resolve()
    if not run.is_relative_to((ROOT / 'output/runs').resolve()):
        raise ValueError('Render only runs inside this EnglishNews output directory')
    metadata = json.loads((run / 'run.json').read_text(encoding='utf-8'))
    if metadata.get('audience') != 'english' or metadata.get('status') != 'completed':
        raise ValueError('Expected a completed English audio run')
    for key in ('combined_audio_path', 'combined_written_path'):
        if not Path(metadata[key]).resolve().is_relative_to(run):
            raise ValueError(f'Artifact escapes the English run: {key}')
    configured_lab = lab or os.environ.get('ENGLISH_NEWS_VIDEO_LAB')
    if not configured_lab:
        raise ValueError('Set ENGLISH_NEWS_VIDEO_LAB to the maintained renderer checkout')
    lab = Path(configured_lab).resolve()
    entry = lab / 'scripts/make_teleprompter_video.py'
    if not entry.is_file():
        raise ValueError('Video Lab renderer entry point is missing')
    python = str(python or os.environ.get('ENGLISH_NEWS_VIDEO_PYTHON') or sys.executable)
    out = run / 'video'
    out.mkdir(parents=True, exist_ok=True)
    status_path = out / 'render-status.json'
    fingerprint = render_fingerprint(run, metadata, lab)
    if status_path.exists():
        previous = json.loads(status_path.read_text(encoding='utf-8'))
        existing = Path(previous.get('video_path', out / 'missing'))
        sidecars = [out / f'{run.name[:8]}-youtube-{suffix}' for suffix in ('title.txt', 'description.txt', 'thumbnail.png')]
        if len(metadata['stories']) >= 3:
            sidecars.append(out / f'{run.name[:8]}-youtube-chapters.txt')
        if (previous.get('status') == 'completed' and previous.get('fingerprint') == fingerprint
                and existing.is_relative_to(out) and existing.is_file()
                and previous.get('video_sha256') == file_hash(existing)
                and all(p.is_file() and p.stat().st_size > 0 for p in sidecars)):
            print(f'Reusing completed render: {previous["video_path"]}', flush=True)
            return Path(previous['video_path'])
    write_json(status_path, dict(status='rendering', audience='english', publication_enabled=False))
    print('Rendering video; this can take several minutes.', flush=True)
    try:
        subprocess.run([python, str(entry), str(run), '--out-dir', str(out)], check=True, cwd=lab)
        video = out / f"{run.name[:8]}-english-news-lesson.mp4"
        if not video.is_file():
            raise ValueError('Renderer did not produce the expected English video')
    except (Exception, SystemExit) as exc:
        write_json(status_path, dict(status='failed', error=str(exc), publication_enabled=False))
        raise
    write_json(status_path, dict(status='completed', run_id=run.name, audience='english',
                                video_path=str(video), publication_enabled=False,
                                fingerprint=fingerprint,
                                video_sha256=file_hash(video),
                                completed_at=datetime.now(timezone.utc).isoformat()))
    print(video)
    return video


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('run', type=Path)
    render_run(p.parse_args().run)


if __name__ == '__main__':
    main()
