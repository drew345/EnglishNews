"""English-owned runtime settings, independent of the historical importer."""
import logging
import os
from pathlib import Path

ROOT = Path(os.environ.get('ENGLISH_NEWS_HOME', Path(__file__).resolve().parents[1])).resolve()
INSTRUCTIONS = ('Read this bilingual English-learning script exactly as written. Korean is the learner native language; '
                'English is the target language. Pronounce each language naturally. Preserve every repetition, '
                'including all four English vocabulary readings and both English sentence readings. '
                'Do not translate, summarize, omit, add introductions, or read punctuation aloud. '
                'Pause briefly between lines. Keep a clear, calm teaching voice.')


def client_from_existing_key(env_file: Path | None):
    from openai import OpenAI
    key = os.environ.get('OPENAI_API_KEY')
    if not key and env_file:
        from dotenv import dotenv_values
        logging.getLogger('dotenv.main').setLevel(logging.ERROR)
        key = dotenv_values(env_file, encoding='utf-8-sig').get('OPENAI_API_KEY')
    if not key:
        raise ValueError('OPENAI_API_KEY is missing; specify an existing --env-file or process environment')
    return OpenAI(api_key=key, timeout=300)
