"""Offline silence guard; audible signal is not proof of correct pronunciation."""
from array import array
from pathlib import Path
import subprocess
import sys


def pcm_signal(pcm: bytes) -> dict:
    samples = array('h', pcm)
    if sys.byteorder != 'little':
        samples.byteswap()
    # Require 60 ms of samples above -46 dBFS. This deliberately accepts quiet
    # speech, but rejects tiny near-silent responses and isolated clicks.
    active_seconds = sum(abs(s) >= 164 for s in samples) / 16000
    return dict(seconds=len(samples) / 16000,
                peak=max((abs(s) for s in samples), default=0) / 32768,
                active_seconds=active_seconds, passed=active_seconds >= .06)


def inspect_audio_signal(path: Path) -> dict:
    import imageio_ffmpeg
    pcm = subprocess.check_output([
        imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(path),
        '-f', 's16le', '-ac', '1', '-ar', '16000', '-'])
    return dict(path=str(path), **pcm_signal(pcm))
