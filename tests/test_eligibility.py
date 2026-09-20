import json
from pathlib import Path
import unittest
from unittest.mock import patch

from english_news import selection
from english_news.morphology import resolve
from english_news.selection import SelectionConfig, analyze, apply_selection
from english_news.lesson import vocab_entries
from test_selection import lesson, item


class EligibilityTests(unittest.TestCase):
    def test_dictionary_roundtrip_repairs_regular_and_irregular_forms(self):
        for surface, pos, tag, expected in [('hopes','VERB','VBZ','hope'), ('hoped','VERB','VBD','hope'),
                ('hoping','VERB','VBG','hope'), ('went','VERB','VBD','go'), ('bought','VERB','VBD','buy'),
                ('children','NOUN','NNS','child'), ('saw','VERB','VBD','see')]:
            with self.subTest(surface=surface):
                self.assertEqual(resolve(surface, pos, tag)['lemma'], expected)
        self.assertEqual(resolve('saw', 'VERB', 'VB')['lemma'], 'saw')
        self.assertEqual(resolve('news', 'NOUN', 'NN')['lemma'], 'news')

    def test_unknown_and_ambiguous_inflections_are_not_guessed(self):
        self.assertEqual(resolve('glorped','VERB','VBD')['status'], 'unresolved_inflection')
        self.assertEqual(resolve('leaves','NOUN','NNS')['status'], 'ambiguous_inflection')
        report = analyze(lesson('Autumn leaves covered the paths.'), SelectionConfig(cutoff=0))
        self.assertTrue(any(c['target']=='leaves' and c['reason']=='ambiguous_inflection' for c in report['rejected']))

    def test_hope_forms_are_common_without_per_word_exception(self):
        source = lesson('With more than 1,000 athletes and officials competing, the country hopes to win up to 45 gold medals and finish third behind China and Japan.')
        report = analyze(source)
        row = next(c for c in report['rejected'] if c['target']=='hopes')
        self.assertEqual(row['nlp_lemma'], 'hop')  # The original real-run failure.
        self.assertEqual(row['lemma'], 'hope')
        self.assertEqual(row['rank'], 346)
        self.assertEqual(row['reason'], 'common_word')
        self.assertIsNone(row['rank_override'])

    def test_unregistered_combinations_are_unavailable_even_with_include(self):
        text = 'They see a medal opportunity. The service deserves time. Hidden hardships gave him courage to continue.'
        report = analyze(lesson(text), SelectionConfig(include=('medal opportunity', 'deserves time')))
        selected = {c['target'] for c in report['candidates']}
        for target in ('medal opportunity', 'deserves time', 'Hidden hardships', 'gave him courage to continue'):
            self.assertNotIn(target, selected)
            self.assertTrue(any(c['target']==target and c['reason']=='unrecognized_phrase' for c in report['rejected']))
        self.assertIn('hardships', selected)
        forbidden = next(c for c in report['rejected'] if c['target']=='medal opportunity')
        with self.assertRaises(ValueError):
            apply_selection(lesson(text), report, {'items':[item(forbidden)]}, SelectionConfig(include=('medal opportunity','deserves time')))

    def test_phrase_patterns_handle_inflections_and_boundaries(self):
        text = 'They started over and took part in local events. She supports herself and will cover their operating costs.'
        report = analyze(lesson(text))
        candidates = {c['target']:c for c in report['candidates']}
        for surface, key in [('started over','start over'),('took part in','take part in'),
                             ('supports herself','support oneself'),('cover their operating costs','cover cost')]:
            self.assertIn(surface,candidates)
            self.assertEqual(candidates[surface]['phrase_rule']['key'],key)
        self.assertNotIn('supports herself and',candidates)
        self.assertNotIn('part in local events',candidates)

    def test_cost_slots_do_not_admit_arbitrary_modifiers(self):
        report = analyze(lesson('They cover ridiculous costs and cover the travel expenses.'))
        candidates = {c['target'] for c in report['candidates']}
        self.assertNotIn('cover ridiculous costs',candidates)
        self.assertIn('cover the travel expenses',candidates)

    def test_easy_and_rank_overrides_apply_to_verified_base_forms(self):
        source = lesson('Many commuters faced hardships.')
        report = analyze(source,SelectionConfig(easy=('commuter',),rank_overrides=(('hardship',1500),)))
        rejected={c['target']:c for c in report['rejected'] if not c['phrase']}
        self.assertEqual(rejected['commuters']['reason'],'easy_override')
        self.assertEqual(rejected['hardships']['rank'],1500)
        self.assertEqual(rejected['hardships']['rank_override'],1500)
        self.assertEqual(rejected['hardships']['reason'],'common_word')
        self.assertNotEqual(rejected['hardships']['raw_rank'],1500)
        with self.assertRaises(ValueError):
            SelectionConfig(easy=('hope',),include=('Hope',))

    def test_persistent_overrides_are_checked_without_editing_frequency_data(self):
        source = lesson('Many commuters faced hardships.')
        with patch('english_news.selection.easy_overrides', return_value={'easy':['commuter'],'rank_overrides':{'hardship':1500}}):
            report=analyze(source)
        self.assertFalse(any(c['target'] in {'commuters','hardships'} for c in report['candidates']))

    def test_definition_judgments_can_only_veto_and_never_update_lists(self):
        source=lesson('They started over.')
        report=analyze(source)
        candidate=next(c for c in report['candidates'] if c['target']=='started over')
        path=Path(selection.__file__).with_name('easy-overrides.json')
        before=path.read_bytes()
        for field,reason in [('context_appropriate','wrong_context'),('learning_unit_appropriate','awkward_learning_unit')]:
            response={'items':[item(candidate,**{field:False})]}
            selected,audit=apply_selection(source,report,response)
            self.assertEqual(vocab_entries(selected),[])
            self.assertTrue(any(c['decision']==reason for c in audit['decisions']))
        self.assertEqual(path.read_bytes(),before)
        row=item(candidate)
        del row['context_appropriate']
        with self.assertRaises(ValueError):
            apply_selection(source,report,{'items':[row]})
