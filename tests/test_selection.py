from copy import deepcopy
import unittest

from english_news.frequency import EnglishFrequency
from english_news.lesson import make_plan, vocab_entries, written_lesson
from english_news.selection import analyze, apply_selection, SelectionConfig


def lesson(text, number=1):
    return dict(source_run_id='20260920_test', source_story_number=number,
                headline=dict(en='A local update', natural_ko='지역 소식'),
                sentences=[dict(en=text, natural_ko='지역의 새로운 소식을 전합니다.',
                                vocab=[dict(word='잘못된 단어', en_def='never import this')])])


def item(candidate, **kwargs):
    return dict(id=candidate['id'], ko_gloss='확대하다', en_explanation='To make something larger or more available.',
                sense_key='increase availability', usefulness=4, reason='Useful in everyday news',
                familiar_borrowing=False, borrowing_ko='', borrowing_matches_context=False,
                context_appropriate=True, learning_unit_appropriate=True, adds_learning_value=True,
                is_entity=False, **kwargs) if not kwargs else dict(item(candidate), **kwargs)


class SelectionTests(unittest.TestCase):
    def candidate(self, report, text):
        return next(c for c in report['candidates'] if c['target'] == text)

    def test_real_nlp_entities_lemmas_frequency_and_phrases(self):
        source = lesson('Seoul will expand ferry departures for commuters who take part in local events.')
        report = analyze(source)
        self.assertTrue(any(c['target'] == 'Seoul' and c['reason'] == 'name_geography_or_entity' for c in report['rejected']))
        departure = self.candidate(report, 'departures')
        self.assertEqual(departure['lemma'], 'departure')
        self.assertEqual(departure['rank'], EnglishFrequency().lookup('departures', 'departure')['rank'])
        self.assertTrue(self.candidate(report, 'take part in')['phrase'])
        self.assertFalse(any('never import' in c['target'] for c in report['candidates']))
        for c in report['candidates']:
            self.assertEqual(source['sentences'][0]['en'][c['start']:c['end']], c['target'])

    def test_prepositional_expression_and_hyphenated_word(self):
        config = SelectionConfig(cutoff=0)
        report = analyze(lesson('Health-conscious residents walk in spite of the rain.'), config)
        self.assertFalse(self.candidate(report, 'Health-conscious')['phrase'])
        self.assertFalse(any(c['target'] == 'conscious' for c in report['candidates']))
        self.assertTrue(self.candidate(report, 'in spite of')['phrase'])

    def test_reflexive_expression_is_available_without_trailing_preposition(self):
        report = analyze(lesson('He supports himself with four part-time jobs.'))
        self.assertTrue(self.candidate(report, 'supports himself')['phrase'])

    def test_common_forms_and_normalized_overrides(self):
        source = lesson('Workers expanded local services.')
        config = SelectionConfig(include=(' LOCAL ',), exclude=('Expand',))
        report = analyze(source, config)
        self.candidate(report, 'local')
        self.assertTrue(any(c['target'] == 'expanded' and c['reason'] == 'manual_exclude' for c in report['rejected']))
        with self.assertRaises(ValueError):
            SelectionConfig(include=('Local',), exclude=('local',))
        freq = EnglishFrequency()
        self.assertEqual(freq.lookup('workers', 'worker')['rank'], min(freq.ranks['workers'], freq.ranks['worker']))

    def test_borrowing_same_sense_removed_different_sense_survives(self):
        source = lesson('The ferry is part of the new service.')
        config = SelectionConfig(cutoff=0)
        report = analyze(source, config)
        row = item(self.candidate(report, 'ferry'), familiar_borrowing=True, borrowing_ko='페리', borrowing_matches_context=True)
        selected, audit = apply_selection(source, report, {'items': [row]}, config)
        self.assertEqual(vocab_entries(selected), [])
        self.assertEqual(next(d['decision'] for d in audit['decisions'] if d['target'] == 'ferry'), 'familiar_loanword')
        row['borrowing_matches_context'] = False
        selected, _ = apply_selection(source, report, {'items': [row]}, config)
        self.assertEqual(len(vocab_entries(selected)), 1)

    def test_unknown_id_or_changed_source_fails(self):
        source = lesson('Commuters will expand ferry departures.')
        report = analyze(source)
        row = item(self.candidate(report, 'expand'))
        with self.assertRaises(ValueError):
            apply_selection(source, report, {'items': [dict(row, id='invented')]})
        with self.assertRaises(ValueError):
            apply_selection(source, report, {'items': [row, row]})
        changed = deepcopy(source)
        changed['sentences'][0]['en'] = 'Changed input'
        with self.assertRaises(ValueError):
            apply_selection(changed, report, {'items': [row]})

    def test_redundant_rejection_is_audited_but_cannot_reintroduce_excluded_word(self):
        source = lesson('Officials expand local services.')
        report = analyze(source)
        gated = next(c for c in report['rejected'] if c['target'] == 'local')
        selected, audit = apply_selection(source, report, {'items': [], 'rejections': [dict(id=gated['id'], reason='not_useful')]})
        self.assertEqual(vocab_entries(selected), [])
        self.assertEqual(audit['supplemental_rejections'][0]['id'], gated['id'])
        with self.assertRaises(ValueError):
            apply_selection(source, report, {'items': [item(gated)]})
        with self.assertRaises(ValueError):
            apply_selection(source, report, {'items': [], 'rejections': [dict(id='invented', reason='not_useful')]})

    def test_no_padding_overlap_or_inherited_vocabulary_and_exact_speech(self):
        source = lesson('Commuters take part in community events.')
        config = SelectionConfig(cutoff=0, include=('part',))
        report = analyze(source, config)
        rows = [item(self.candidate(report, text)) for text in ('take part in', 'part')]
        selected, audit = apply_selection(source, report, {'items': rows}, config)
        self.assertEqual(len(vocab_entries(selected)), 1)
        self.assertTrue(audit['below_soft_target'])
        self.assertIn('overlapping_selection', [d['decision'] for d in audit['decisions']])
        self.assertEqual(source['sentences'][0]['vocab'][0]['word'], '잘못된 단어')
        v = vocab_entries(selected)[0]
        explanations = {v['id']: dict(en_explanation=v['en_explanation'])}
        unit = next(u for u in make_plan(selected, explanations) if u['name'] == v['id'])
        self.assertEqual(unit['text'].splitlines(), ['take part in.', 'take part in.', '확대하다.', v['en_explanation'], 'take part in.', 'take part in.'])
        self.assertIn('- take part in: 확대하다:', written_lesson(selected, explanations))

    def test_same_meaning_deduplicates_and_run_limit_is_three(self):
        source = lesson('They expand services and expand opportunities.')
        report = analyze(source)
        rows = [item(c) for c in report['candidates'] if c['target'] == 'expand']
        counts = {}
        for expected in (1, 1, 1, 0):
            selected, _ = apply_selection(source, report, {'items': rows}, run_counts=counts)
            self.assertEqual(len(vocab_entries(selected)), expected)

    def test_target_is_soft_and_reports_overage_without_truncation(self):
        source = lesson('Officials expand ferry departures.')
        config = SelectionConfig(target_min=1, target_max=1)
        report = analyze(source, config)
        rows = [item(self.candidate(report, text)) for text in ('expand', 'departures')]
        selected, audit = apply_selection(source, report, {'items': rows}, config)
        self.assertEqual(len(vocab_entries(selected)), 2)
        self.assertTrue(audit['above_soft_target'])

    def test_cutoff_changes_only_common_single_word_gate(self):
        source = lesson('Officials expand ferry departures.')
        reports = [analyze(source, SelectionConfig(cutoff=c)) for c in (3500, 4000, 4500)]
        self.assertTrue(any(c['target'] == 'expand' for c in reports[0]['candidates']))
        self.assertFalse(any(c['target'] == 'expand' for c in reports[1]['candidates']))
        self.assertEqual([{c['target'] for c in r['candidates'] if c['phrase']} for r in reports],
                         [{c['target'] for c in reports[0]['candidates'] if c['phrase']}] * 3)
