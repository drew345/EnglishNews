"""Two conservative, offline filters over existing English vocabulary glosses."""
from copy import deepcopy
import json
from pathlib import Path
import re
import unicodedata

VERSION = 'name-country-v1'


def normalize(text):
    text = unicodedata.normalize('NFKC', text).casefold().replace('’', "'")
    return ' '.join(text.strip().strip('.,!?;:').split())


ALIASES = '''South Korea|North Korea|Korea|Republic of Korea|Democratic People's Republic of Korea|
United States|United States of America|USA|U.S.A.|U.S.|United Kingdom|UK|U.K.|Britain|Great Britain|
Russia|Iran|Syria|Vietnam|Viet Nam|Laos|Bolivia|Venezuela|Tanzania|Moldova|Taiwan|Palestine|
Brunei|Czech Republic|Czechia|Turkey|Türkiye|Ivory Coast|Cape Verde|East Timor|Vatican City|
Democratic Republic of the Congo|DR Congo|Republic of the Congo|The Bahamas|The Gambia|
The Netherlands|Kosovo|Burma|Swaziland|UAE|United Arab Emirates'''
COUNTRIES = frozenset(normalize(name) for name in
    json.loads(Path(__file__).with_name('country_names.json').read_text(encoding='utf-8-sig'))
    + ALIASES.replace('\n', '').split('|'))


def exclusion_reason(gloss):
    if re.search(r'\bname\b', unicodedata.normalize('NFKC', gloss), re.IGNORECASE):
        return 'english_gloss_contains_name'
    if normalize(gloss) in COUNTRIES:
        return 'english_gloss_is_country'
    return None


def filter_vocabulary(lesson):
    """Preserve source, sentences and stable IDs; report every removed entry."""
    filtered = deepcopy(lesson)
    removed = []
    for sentence in filtered['sentences']:
        kept = []
        for entry in sentence['vocab']:
            reason = exclusion_reason(entry['en_def'])
            if reason:
                removed.append(dict(entry, reason=reason))
            else:
                kept.append(entry)
        sentence['vocab'] = kept
    return filtered, dict(version=VERSION, removed=removed,
                          kept_ids=[v['id'] for s in filtered['sentences'] for v in s['vocab']])
