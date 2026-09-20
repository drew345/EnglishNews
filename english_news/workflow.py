"""Build media from explicitly reviewed English text. Local review only."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from contextlib import contextmanager

from .lesson import digest, prepared_plan, speech_script, vocab_entries, write_json, written_lesson
from .runtime import ROOT, INSTRUCTIONS, client_from_existing_key
from .prepare import load_prepared

VERSION = 'english-prepared-media-v2'
CHANNEL = 'UCPvS_o6ypGR8-aA0P2pgtdA'


@contextmanager
def workflow_lock():
    """OS lock releases automatically if a build is interrupted or crashes."""
    import msvcrt
    path = ROOT / '.local/workflow.lock'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as stream:
        stream.seek(0, 2)
        if stream.tell() == 0:
            stream.write(b'0'); stream.flush()
        stream.seek(0)
        try:
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            raise RuntimeError('Another English build is running. Wait for it to finish.') from exc
        try:
            yield
        finally:
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(source: Path, staged: Path, destination: Path):
    """Copy only required inputs, verify their identity, never write to production."""
    metadata = json.loads((source / 'run.json').read_text(encoding='utf-8'))
    run_id = metadata['run_id']
    if metadata.get('status') != 'completed' or source.name != run_id:
        raise ValueError('Expected an explicit completed Korean source run')
    if metadata.get('audience', 'korean') != 'korean':
        raise ValueError('Source must be Korean')
    staged_meta = json.loads((staged / 'run.json').read_text(encoding='utf-8'))
    if staged_meta['run_id'] != run_id:
        raise ValueError('Staged images belong to another run')
    files = [(source / 'run.json', 'source/run.json'),
             (source / f'{run_id[:8]}-news-written.txt', f'source/{run_id[:8]}-news-written.txt')]
    files += [(staged / f'story-{i:02d}-video-image.png', f'staged/story-{i:02d}-video-image.png')
              for i in range(1, len(metadata['stories']) + 1)]
    records = [dict(source=str(p.resolve()), relative=r, sha256=sha(p)) for p, r in files]
    manifest = destination / 'manifest.json'
    if manifest.exists() and json.loads(manifest.read_text(encoding='utf-8')) != records:
        raise ValueError('Source inputs changed since snapshot; inspect instead of overwriting')
    for (src, rel), record in zip(files, records):
        dest = destination / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and sha(dest) != record['sha256']:
            raise ValueError(f'Snapshot checksum mismatch: {rel}')
        if not dest.exists():
            shutil.copyfile(src, dest)
        if sha(dest) != record['sha256'] or sha(src) != record['sha256']:
            raise ValueError('Source changed during copy')
    write_json(manifest, records)
    return metadata


def timeline(stories):
    cursor = 0.0
    result = []
    for story in stories:
        duration = story['duration']
        if duration <= 0:
            raise ValueError('Empty story audio')
        result.append(dict(story, start_sec=cursor, end_sec=cursor + duration))
        cursor += duration
    return result


def run(prepared_path, staged, env_file, render=True):
    prepared = load_prepared(prepared_path)
    source_run = prepared['source_run_id']
    lessons = prepared['lessons']
    if len(lessons) != 3:
        raise ValueError('This workflow expects exactly three stories')
    staged_metadata = json.loads((staged / 'run.json').read_text(encoding='utf-8'))
    if staged_metadata.get('run_id') != source_run:
        raise ValueError('Images belong to another source run')
    image_sources = [staged / f'story-{i:02d}-video-image.png' for i in range(1, len(lessons) + 1)]
    image_hashes = [sha(p) for p in image_sources]
    audience_settings = json.loads(Path(__file__).with_name('audience.json').read_text(encoding='utf-8'))
    profile = dict(version=VERSION, voice='alloy',
                   **prepared['profile'].get('speech', dict(target_speed=.88, native_speed=1.07)),
                   preparation_profile=prepared['profile'], audience_settings=audience_settings)
    identity = digest(dict(prepared=prepared, profile=profile, images=image_hashes))
    output = ROOT / 'output/runs' / f'{source_run[:8]}_english_all_{identity[:10]}'
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / 'vocabulary-filter.json', dict(stories=prepared['reports']))
    write_json(output / 'preparation.json', dict(content=prepared, content_sha256=digest(prepared)))
    state = output / 'workflow-status.json'
    write_json(state, dict(status='building_audio', source_run_id=source_run, publication_enabled=False))
    print(f'English output: {output}', flush=True)
    client = client_from_existing_key(env_file)
    from .audio import synthesize_plan
    from korean_news_media.tts_common import concatenate_mp3
    from mutagen.mp3 import MP3
    stories, plans, images, audios, written_blocks, notes = [], [], [], [], [], []
    try:
        for i, lesson in enumerate(lessons, 1):
            folder = output / 'stories' / f'{i:02d}'
            folder.mkdir(parents=True, exist_ok=True)
            explanations = {v['id']: dict(en_explanation=v['en_explanation'], review_note='') for v in vocab_entries(lesson)}
            write_json(folder / 'explanations.json', dict(result={'entries': [dict(id=k, **v) for k, v in explanations.items()]}))
            plan = prepared_plan(lesson, prepared['profile'])
            write_json(folder / 'lesson-bundle.json', dict(content_sha256=digest(lesson), lesson=lesson))
            write_json(folder / 'speech-plan.json', dict(profile=profile, units=plan))
            block = written_lesson(lesson, explanations, headline_label=prepared['profile'].get('speech', {}).get('headline_label', '헤드라인'))
            written_path = folder / 'written.txt'
            written_path.write_text(block, encoding='utf-8')
            print(f'Story {i}: {len(plan)} speech units, {len(vocab_entries(lesson))} vocabulary entries', flush=True)
            paths, requests = synthesize_plan(plan, folder, voice=profile['voice'], client=client, instructions=INSTRUCTIONS)
            audio = folder / 'story.mp3'
            concatenate_mp3(paths, audio)
            audios.append(audio)
            image = output / f'story-{i:02d}-video-image.png'
            shutil.copyfile(image_sources[i - 1], image)
            if sha(image) != image_hashes[i - 1]:
                raise ValueError('Image changed during media build')
            images.append(dict(story_index=i, path=str(image)))
            stories.append(dict(title_en=lesson['headline']['en'], title_ko=lesson['headline']['natural_ko'],
                                duration=MP3(audio).info.length, audio_requests=requests, written_path=str(written_path)))
            plans.extend(plan)
            written_blocks.append(block)
            if prepared['reports'][i - 1].get('below_soft_target'):
                notes.append(f'- Story {i}: fewer than eight suitable vocabulary items; no padding added.')
            if prepared['reports'][i - 1].get('above_soft_target'):
                notes.append(f'- Story {i}: more than twelve selected items; review whether all are worth teaching.')
        combined = output / f'{source_run[:8]}-english-news.mp3'
        concatenate_mp3(audios, combined)
        written = output / f'{source_run[:8]}-english-news-written.txt'
        written.write_text('\n---\n\n'.join(written_blocks), encoding='utf-8')
        write_json(output / 'speech-plan.json', dict(profile=profile, units=plans))
        (output / 'speech-script.txt').write_text(speech_script(plans), encoding='utf-8')
        (output / 'vocabulary-review.md').write_text('# Vocabulary review before upload\n\n' + '\n'.join(notes) + '\n', encoding='utf-8')
        write_json(output / 'run.json', dict(run_id=output.name, source_run_id=source_run, audience='english',
                   audience_settings=audience_settings,
                   status='completed', profile=profile, combined_audio_path=str(combined), combined_written_path=str(written),
                   stories=timeline(stories), video_story_images=images,
                   youtube_publication=dict(status='awaiting_user_review', channel_id=CHANNEL, enabled=False)))
        subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'development/check_sample.py'), str(output)], check=True)
        if render:
            from .render import render_run
            from .review import prepare_review
            video = render_run(output)
            prepare_review(output, video)
        write_json(state, dict(status='ready_for_review' if render else 'audio_checked', source_run_id=source_run,
                              publication_enabled=False, vocabulary_review_count=len(notes)))
    except BaseException as exc:
        write_json(state, dict(status='failed', error=str(exc), publication_enabled=False,
                              resume='Run the same command again; valid speech segments and explanations are cached.'))
        raise
    print(f'READY FOR REVIEW: {output}', flush=True)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared-run', type=Path, required=True)
    parser.add_argument('--staged-run', type=Path, required=True)
    parser.add_argument('--env-file', type=Path)
    parser.add_argument('--audio-only', action='store_true')
    parser.add_argument('--reviewed-text', action='store_true', help='Confirm this exact text preparation has been reviewed')
    args = parser.parse_args()
    if not args.reviewed_text:
        parser.error('Review the text first, then pass --reviewed-text to generate media')
    with workflow_lock():
        run(args.prepared_run.resolve(), args.staged_run.resolve(), args.env_file, not args.audio_only)


if __name__ == '__main__':
    main()
