"""Deterministic repetition assembly over the existing Speech transport."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
from pathlib import Path

from .lesson import write_json
from .audio_signal import inspect_audio_signal


def segment_plan(unit: dict) -> tuple[list[str], list[int]]:
    lines = unit['text'].splitlines()
    if unit['name'].startswith('s') and '.v' in unit['name']:
        if len(lines) != 6 or not (lines[0] == lines[1] == lines[4] == lines[5]):
            raise ValueError('Invalid six-part vocabulary sequence')
        return [lines[0], lines[2], lines[3]], [0, 0, 1, 2, 0, 0]
    if unit['name'].endswith('_en') and unit['name'] != 'review_en':
        if len(lines) != 2 or lines[0] != lines[1]:
            raise ValueError('Invalid English sentence pair')
        return [lines[0]], [0, 0]
    return [unit['text']], [0]


def synthesize_plan(plan, output: Path, *, voice, client, instructions):
    from korean_news_media.openai_speech_tts import synthesize_speech_units
    from korean_news_media.tts_common import TtsTextUnit, concatenate_mp3

    def make(unit):
        texts, order = segment_plan(unit)
        speeds = unit.get('segment_speeds', [unit['speed']] * len(texts))
        if len(speeds) != len(texts) or any(type(s) not in (int, float) or not .25 <= s <= 4 for s in speeds):
            raise ValueError('Invalid segment speeds')
        folder = output / 'speech-parts' / unit['name']
        result = synthesize_speech_units(
            [TtsTextUnit(name=f'{unit["name"]}.{i}', text=text, speed=speeds[i]) for i, text in enumerate(texts)],
            folder / 'segment', voice=voice, max_chars=3500, max_units_per_request=1,
            model='gpt-4o-mini-tts', instructions=instructions,
            profile_version='english-single-reading-v1', client=client, resume=True)
        paths = list(result.audio_paths)
        segment_requests = list(result.request_metadata)
        signal_checks = []
        for i, path in enumerate(paths):
            for attempt in range(3):
                check = dict(segment=i, attempt=attempt, **inspect_audio_signal(path))
                signal_checks.append(check)
                write_json(folder / 'signal-qa.json', dict(checks=signal_checks))
                if check['passed']:
                    break
                if attempt == 2:
                    raise ValueError(f'No audible speech in {unit["name"]} segment {i}; two retries failed')
                print(f'Retrying near-silent speech: {unit["name"]} segment {i}', flush=True)
                retry = synthesize_speech_units(
                    [TtsTextUnit(name=f'{unit["name"]}.{i}', text=texts[i], speed=speeds[i])],
                    folder / f'segment_{i}_retry{attempt + 1}', voice=voice, max_chars=3500,
                    max_units_per_request=1, model='gpt-4o-mini-tts', instructions=instructions,
                    profile_version='english-single-reading-v1', client=client, resume=True)
                path = retry.audio_paths[0]
                paths[i] = path
                segment_requests[i] = retry.request_metadata[0]
        sources = [paths[i] for i in order]
        audio = folder / 'assembled.mp3'
        concatenate_mp3(sources, audio)
        input_path = folder / 'assembled.input.txt'
        input_path.write_text(unit['text'], encoding='utf-8')
        meta_path = folder / 'assembled.request.json'
        metadata = dict(audio_path=str(audio), input_path=str(input_path), metadata_path=str(meta_path),
                        unit_names=[unit['name']], provider='openai_speech', voice=voice,
                        speed=unit['speed'], segment_speeds=speeds,
                        source_sha256=hashlib.sha256(unit['text'].encode('utf-8')).hexdigest(),
                        assembly_order=order, assembly_sources=[str(p) for p in sources],
                        segment_requests=segment_requests, signal_checks=signal_checks, status='complete')
        write_json(meta_path, metadata)
        print(f'Completed speech unit: {unit["name"]}', flush=True)
        return metadata

    with ThreadPoolExecutor(max_workers=4) as executor:
        requests = list(executor.map(make, plan))
    return [Path(r['audio_path']) for r in requests], requests
