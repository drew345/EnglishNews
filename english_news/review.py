"""Validate local media and collect a review-only publication manifest."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

from .lesson import write_json


def file_hash(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def prepare_review(run: Path, video: Path):
    import imageio_ffmpeg
    from mutagen.mp3 import MP3
    metadata = json.loads((run / 'run.json').read_text(encoding='utf-8'))
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    video_hash = file_hash(video)
    report_path = run / 'video-qa.json'
    previous = json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {}
    if previous.get('sha256') != video_hash or previous.get('decode') != 'passed':
        probe = subprocess.run([ffmpeg, '-hide_banner', '-i', str(video)], capture_output=True, text=True)
        match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', probe.stderr)
        if not match or 'Video:' not in probe.stderr or 'Audio:' not in probe.stderr:
            raise ValueError('Video must contain playable picture and sound')
        hours, minutes, seconds = map(float, match.groups())
        duration = hours * 3600 + minutes * 60 + seconds
        audio_duration = MP3(metadata['combined_audio_path']).info.length
        if not 9 <= duration - audio_duration <= 13:
            raise ValueError('Unexpected video duration or missing lesson tail')
        subprocess.run([ffmpeg, '-v', 'error', '-i', str(video), '-map', '0:v:0', '-map', '0:a:0', '-f', 'null', '-'], check=True)
        write_json(report_path, dict(sha256=video_hash, decode='passed', video_seconds=duration,
                                    audio_seconds=audio_duration, stories=len(metadata['stories'])))
    date = run.name[:8]
    folder = video.parent
    files = [video, folder / f'{date}-youtube-title.txt', folder / f'{date}-youtube-description.txt',
             folder / f'{date}-youtube-thumbnail.png', folder / f'{date}-youtube-chapters.txt']
    for path in files:
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f'Missing review artifact: {path.name}')
    title = files[1].read_text(encoding='utf-8').strip()
    description = files[2].read_text(encoding='utf-8')
    chapters = files[4].read_text(encoding='utf-8').splitlines()
    if not title or len(title) > 100 or len(description) > 5000 or any(c in description for c in '<>'):
        raise ValueError('YouTube title/description validation failed')
    if len(chapters) < 3 or not chapters[0].startswith('00:00 '):
        raise ValueError('Expected at least three valid chapters from 00:00')
    frames = []
    for i, story in enumerate(metadata['stories'], 1):
        frame = folder / f'story-{i:02d}-middle-frame.png'
        if not frame.exists() or previous.get('sha256') != video_hash:
            timestamp = (story['start_sec'] + story['end_sec']) / 2 + 1
            subprocess.run([ffmpeg, '-v', 'error', '-y', '-ss', str(timestamp), '-i', str(video),
                            '-frames:v', '1', '-update', '1', str(frame)], check=True)
        frames.append(str(frame))
    write_json(run / 'upload-package.json', dict(status='awaiting_user_review', publication_enabled=False,
        channel_id='UCPvS_o6ypGR8-aA0P2pgtdA', channel_handle='@SteadyLanternEnglish',
        files=[dict(path=str(p), sha256=file_hash(p)) for p in files],
        vocabulary_review=str(run / 'vocabulary-review.md'), audio_qa=str(run / 'audio-qa.json'),
        video_qa=str(report_path), middle_frames=frames))
    print(f'Video and upload materials checked: {folder}', flush=True)
