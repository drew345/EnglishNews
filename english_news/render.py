"""Render an English prototype locally, without the publication watcher."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from .lesson import write_json
from .prototype import ROOT


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('run', type=Path)
    args = p.parse_args()
    run = args.run.resolve()
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
    write_json(status_path, dict(status='rendering', audience='english', publication_enabled=False))
    sys.path.insert(0, str(lab))
    from scripts.make_teleprompter_video import build_video
    try:
        video = build_video(run, out)
    except (Exception, SystemExit) as exc:
        write_json(status_path, dict(status='failed', error=str(exc), publication_enabled=False))
        raise
    write_json(status_path, dict(status='completed', run_id=run.name, audience='english',
                                video_path=str(video), publication_enabled=False,
                                completed_at=datetime.now(timezone.utc).isoformat()))
    print(video)


if __name__ == '__main__':
    main()
