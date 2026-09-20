"""Dictionary-only morphology; never guess inflections with an LLM/OOV model."""
from functools import lru_cache
from importlib.metadata import version

VERSION = 'lemminflect-0.2.3-dictionary-roundtrip-v1'
INFLECTED_TAGS = {'NNS', 'NNPS', 'VBZ', 'VBD', 'VBN', 'VBG', 'JJR', 'JJS', 'RBR', 'RBS'}


@lru_cache(maxsize=8192)
def resolve(surface, pos, tag):
    from lemminflect import getAllLemmas, getInflection
    if version('lemminflect') != '0.2.3':
        raise RuntimeError('Install lemminflect==0.2.3')
    word = surface.casefold()
    if tag not in INFLECTED_TAGS:
        # Base forms must not be stripped just because they end in s/ed/ing.
        return dict(lemma=word, status='base_or_surface', alternatives=[word])
    candidates = getAllLemmas(word, upos=pos).get(pos, ())
    verified = sorted({base.casefold() for base in candidates
                       if word in {f.casefold() for f in (getInflection(base, tag, inflect_oov=False) or ())}})
    if len(verified) == 1:
        return dict(lemma=verified[0], status='dictionary_verified', alternatives=verified)
    return dict(lemma=word, status='ambiguous_inflection' if verified else 'unresolved_inflection',
                alternatives=verified)


def token_form(token):
    return resolve(token.text, token.pos_, token.tag_)
