"""Pinned surface-token frequency ranks, never a Korean-rank proxy."""
from importlib.metadata import version
from wordfreq import top_n_list

VERSION = 'wordfreq-3.1.1-en-top6000-surface-or-lemma-v1'


class EnglishFrequency:
    def __init__(self):
        if version('wordfreq') != '3.1.1':
            raise RuntimeError('Install the pinned wordfreq==3.1.1 dependency')
        self.ranks = {w: i for i, w in enumerate(top_n_list('en', 6000), 1)}

    def lookup(self, surface, lemma):
        values = [self.ranks.get(surface.casefold()), self.ranks.get(lemma.casefold())]
        known = [v for v in values if v is not None]
        return dict(surface_rank=values[0], lemma_rank=values[1],
                    rank=min(known) if known else None,
                    rank_basis='surface-token rank; more common of surface and contextual lemma')
