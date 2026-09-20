"""Prepare the current speech settings and exact TTS text without generating audio."""
import argparse
from copy import deepcopy
from pathlib import Path

from .lesson import CURRENT_SPEECH_PROFILE, digest
from .prepare import load_prepared, write_prepared


def prepare_speech_review(prepared_path, output_root):
    original = load_prepared(prepared_path)
    revised = deepcopy(original)
    revised['profile']['speech'] = dict(CURRENT_SPEECH_PROFILE)
    revised['speech_revision'] = dict(parent_content_sha256=digest(original),
                                    text_unchanged=True)
    output = write_prepared(revised, output_root)
    load_prepared(output)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared-run', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, default=Path('output/text-review'))
    args = parser.parse_args()
    output = prepare_speech_review(args.prepared_run, args.output_root)
    print(f'TTS REVIEW: {(output / "speech-script.txt").resolve()}')


if __name__ == '__main__':
    main()
