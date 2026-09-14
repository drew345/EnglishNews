"""Render an English prototype locally, without the publication watcher."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from .lesson import write_json
from .prototype import ROOT
from .review import file_hash
from .lesson import digest


def render_fingerprint(run, metadata, lab):
    inputs = [run / 'run.json', Path(metadata['combined_audio_path']), Path(metadata['combined_written_path'])]
    inputs.extend(Path(s['written_path']) for s in metadata['stories'] if s.get('written_path'))
    inputs.extend(Path(s['path']) for s in metadata.get('video_story_images', []))
    if any(not p.resolve().is_relative_to(run.resolve()) for p in inputs):
        raise ValueError('Render input escapes English run directory')
    inputs.extend(sorted((lab / 'scripts').glob('*.py')))
    return digest([(str(p), file_hash(p)) for p in inputs])


def render_run(run):
    run = run.resolve()
    if not run.is_relative_to((ROOT / 'output/runs').resolve()):
        raise ValueError('Render only runs inside this EnglishNews development worktree')
    metadata = json.loads((run / 'run.json').read_text(encoding='utf-8'))
    if metadata.get('audience') != 'english' or metadata.get('status') != 'completed':
        raise ValueError('Expected a completed English audio run')
    for key in ('combined_audio_path', 'combined_written_path'):
        if not Path(metadata[key]).resolve().is_relative_to(run):
            raise ValueError(f'Artifact escapes the English run: {key}')
    lab = ROOT.parent / 'KoreanLessonVideoLab'
    if not (lab / '.git').is_file():
        raise ValueError('Expected a linked Video Lab worktree')
    out = lab / 'outputs' / run.name
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
    sys.path.insert(0, str(lab))
    from scripts.make_teleprompter_video import build_video
    print('Rendering video; this can take several minutes.', flush=True)
    try:
        video = build_video(run, out)
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
