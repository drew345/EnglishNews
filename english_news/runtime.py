"""English-owned runtime settings, independent of the historical importer."""
import logging
import os
from pathlib import Path

ROOT = Path(os.environ.get('ENGLISH_NEWS_HOME', Path(__file__).resolve().parents[1])).resolve()


def archive_history(method, folder):
    """Optional archive adapter; the implementation lives in the NewsHistory repo."""
    import importlib.util
    root = Path(os.environ.get('NEWS_HISTORY_REPO') or
                Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')).parent / 'Projects' / 'NewsHistory')
    try:
        spec = importlib.util.spec_from_file_location('news_history_archive', root / 'news_history.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = getattr(module, method)(folder) if method != 'archive_run' else module.archive_run(folder, 'EnglishNews')
        module.store('origin', 'EnglishNews', Path(folder).name,
                     dict(origin_device=os.environ.get('COMPUTERNAME', 'unknown')))
        return result
    except Exception as exc:
        logging.getLogger(__name__).warning('NewsHistory export pending: %s', exc)
        return None

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
