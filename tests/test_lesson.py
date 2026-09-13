import copy
import unittest

from english_news.lesson import import_story, make_plan, validate_explanations, written_lesson
from english_news.audio import segment_plan


SOURCE = '''## Headline 1

Families share a home.
가족들은 집을 공유한다.

## Bilingual Lesson (sentence by sentence)

Each household has a home.
### Vocab:
- 가구: household: 함께 사는 사람들

각 가구에는 집이 있다.

## Full Summary

가족들은 집을 공유한다.
각 가구에는 집이 있다.
'''


class LessonTests(unittest.TestCase):
    def setUp(self):
        self.lesson = import_story(SOURCE, '20260913_fixture')
        self.response = {'entries': [{'id': 's1.b1.v1', 'en_explanation': 'A group of people who live together.'}]}
        self.explanations = validate_explanations(self.lesson, self.response)

    def test_exact_vocabulary_and_sentence_sequence(self):
        plan = make_plan(self.lesson, self.explanations)
        self.assertEqual(plan[0]['text'], '가족들은 집을 공유한다.')
        self.assertEqual(plan[1]['text'].splitlines(), ['Families share a home.'] * 2)
        self.assertEqual(plan[2]['text'], '각 가구에는 집이 있다.')
        self.assertEqual(plan[3]['text'].splitlines(), ['household.', 'household.', '가구.',
                         'A group of people who live together.', 'household.', 'household.'])
        self.assertEqual(plan[4]['text'].splitlines(), ['Each household has a home.'] * 2)
        self.assertEqual(plan[-1]['text'], 'Full review.\nFamilies share a home.\nEach household has a home.')
        self.assertEqual([u['speed'] for u in plan], [1.07, .88, 1.07, .88, .88, .88])

    def test_source_definitions_are_preserved(self):
        original = copy.deepcopy(self.lesson)
        written = written_lesson(self.lesson, self.explanations)
        make_plan(self.lesson, self.explanations)
        self.assertEqual(self.lesson, original)
        self.assertEqual(self.lesson['sentences'][0]['vocab'][0]['ko_def'], '함께 사는 사람들')
        self.assertIn('## 영어 전체 복습', written)
        self.assertLess(written.index('각 가구'), written.index('- household'))

    def test_audio_assembly_guarantees_all_repetitions(self):
        for unit in make_plan(self.lesson, self.explanations):
            segments, order = segment_plan(unit)
            self.assertEqual('\n'.join(segments[i] for i in order), unit['text'])
        segments, order = segment_plan(make_plan(self.lesson, self.explanations)[3])
        self.assertEqual(len(segments), 3)
        self.assertEqual(order, [0, 0, 1, 2, 0, 0])

    def test_import_rejects_misalignment(self):
        with self.assertRaises(ValueError):
            import_story(SOURCE.replace('각 가구에는 집이 있다.', '다른 내용.', 1), 'run')

    def test_import_rejects_missing_story(self):
        with self.assertRaises(ValueError):
            import_story(SOURCE, 'run', 2)

    def test_explanations_must_cover_exact_ids(self):
        for entries in ([], self.response['entries'] * 2, [{'id': 'wrong', 'en_explanation': 'A group of people.'}]):
            with self.assertRaises(ValueError):
                validate_explanations(self.lesson, {'entries': entries})

    def test_korean_explanation_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_explanations(self.lesson, {'entries': [{'id': 's1.b1.v1', 'en_explanation': 'A group of 사람들.'}]})


if __name__ == '__main__':
    unittest.main()
