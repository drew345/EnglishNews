import unittest
from copy import deepcopy
from tempfile import TemporaryDirectory
from pathlib import Path

from english_news.vocabulary import exclusion_reason, filter_vocabulary
from english_news.lesson import make_plan, written_lesson
from english_news.prototype import enrich


class VocabularyTests(unittest.TestCase):
    def test_korean_country_word_catches_generic_gloss_without_matching_substrings(self):
        for word in ('태국', ' 한국. ', '대한민국', '미국', '호주', '터키', '튀르키예', '대만'):
            self.assertEqual(exclusion_reason('a country in Asia', word), 'korean_word_is_country', word)
        for word in ('태국인', '태국 음식', '미국의', '한국어', '동남아시아', '유대'):
            self.assertIsNone(exclusion_reason('a country in Asia', word), word)

    def test_name_is_a_whole_word(self):
        for gloss in ("a politician's name", 'NAME', 'a country name'):
            self.assertEqual(exclusion_reason(gloss), 'english_gloss_contains_name')
        for gloss in ('nickname', 'surname', 'nameless', 'renamed'):
            self.assertIsNone(exclusion_reason(gloss))

    def test_countries_aliases_and_false_positives(self):
        for gloss in ('Thailand', ' south   korea. ', 'USA', 'U.S.', 'United Kingdom',
                      'Côte d’Ivoire', 'Türkiye', 'Democratic Republic of the Congo', 'Tuvalu'):
            self.assertEqual(exclusion_reason(gloss), 'english_gloss_is_country', gloss)
        for gloss in ('us', 'in', 'Thai', 'South Korean', 'visit Thailand',
                      'Southeast Asian country', 'to hire', 'connection'):
            self.assertIsNone(exclusion_reason(gloss), gloss)

    def test_removed_vocab_never_reaches_text_or_speech_and_source_is_unchanged(self):
        lesson = dict(source_story_number=1, headline=dict(en='Headline.', natural_ko='제목.'),
            sentences=[dict(en='A story.', natural_ko='이야기.', vocab=[
                dict(id='s1.b1.v1', word='이재명', en_def="a politician's name", ko_def='이름'),
                dict(id='s1.b1.v2', word='태국', en_def='Southeast Asian country', ko_def='나라')])])
        original = deepcopy(lesson)
        filtered, report = filter_vocabulary(lesson)
        self.assertEqual(lesson, original)
        self.assertEqual(len(report['removed']), 2)
        self.assertEqual(report['removed'][1]['reason'], 'korean_word_is_country')
        self.assertEqual(report['kept_ids'], [])
        plan = make_plan(filtered, {})
        self.assertFalse(any('vocab_label' in unit['name'] for unit in plan))
        self.assertNotIn('어휘', written_lesson(filtered, {}))
        self.assertIn('A story.', written_lesson(filtered, {}))
        with TemporaryDirectory() as tmp:
            # A client with no API methods proves the empty case makes no call.
            self.assertEqual(enrich(filtered, Path(tmp) / 'cache.json', object(), 'unused'), {})
