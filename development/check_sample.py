"""Check speech artifacts and optionally transcribe representative generated units."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from english_news.lesson import write_json
from english_news.audio import segment_plan
from english_news.runtime import client_from_existing_key
from korean_news_media.tts_transcription import transcribe_audio
from mutagen.mp3 import MP3
import imageio_ffmpeg

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('run', type=Path)
p.add_argument('--env-file', type=Path)
p.add_argument('--transcribe', action='store_true')
args = p.parse_args()
run = args.run.resolve()
metadata = json.loads((run / 'run.json').read_text(encoding='utf-8'))
plan = json.loads((run / 'speech-plan.json').read_text(encoding='utf-8'))['units']
requests = [request for story in metadata['stories'] for request in story['audio_requests']]
assert len(requests) == len(plan)
checks = []
for unit, request in zip(plan, requests):
    path = Path(request['audio_path'])
    assert path.resolve().is_relative_to(run)
    input_text = Path(request['input_path']).read_text(encoding='utf-8').strip()
    assert input_text == unit['text'].strip(), unit['name']
    record = json.loads(Path(request['metadata_path']).read_text(encoding='utf-8'))
    assert record['source_sha256'] == hashlib.sha256(input_text.encode('utf-8')).hexdigest()
    assert record['speed'] == unit['speed']
    if 'segment_speeds' in unit:
        assert record['segment_speeds'] == unit['segment_speeds']
    if 'assembly_order' in record:
        _, expected_order = segment_plan(unit)
        assert record['assembly_order'] == expected_order
        assert abs(MP3(path).info.length - sum(MP3(p).info.length for p in record['assembly_sources'])) < 1
    length = MP3(path).info.length
    assert length > 0
    checks.append(dict(name=unit['name'], seconds=length, speed=unit['speed']))
audio = Path(metadata['combined_audio_path'])
duration = MP3(audio).info.length
assert abs(duration - sum(c['seconds'] for c in checks)) < 2
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(audio), '-f', 'null', '-'], check=True)
report = dict(units=checks, audio_seconds=duration, decode='passed')
if args.transcribe:
    client = client_from_existing_key(args.env_file)
    selected = {'headline_en', 's1.b1.v3', 'body1_en', 'review_en'}
    def check(pair):
        unit, request = pair
        transcript = transcribe_audio(Path(request['audio_path']), client=client)
        return dict(name=unit['name'], expected=unit['text'], transcript=transcript)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        report['transcription_samples'] = list(executor.map(check, [(u, r) for u, r in zip(plan, requests) if u['name'] in selected]))
    write_json(run / 'transcription-qa.json', dict(samples=report['transcription_samples'],
               note='Human review required: ASR may normalize names or collapse repetitions.'))
write_json(run / 'audio-qa.json', report)
print(f'Audio QA passed: {len(checks)} speech units; {duration:.3f} seconds; full decode passed.')
