"""Positive phrase eligibility: exact expressions and bounded grammatical slots."""
import json
from pathlib import Path

VERSION = 'controlled-expressions-v2'
REFLEXIVES = {'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'yourselves', 'themselves', 'oneself'}


def reference():
    return json.loads(Path(__file__).with_name('phrase-reference.json').read_text(encoding='utf-8'))


def basic_sense(span, expression, rules):
    """Conservative context checks for user-confirmed familiar phrase senses."""
    rule = rules.get('basic_senses', {}).get(expression['key']) if expression else None
    if not rule:
        return None
    if rule['context'] == 'any':
        return dict(rule)
    if rule['context'] != 'following_quantity':
        raise ValueError('Unknown basic-expression context rule')
    # Numeric maximums only: do not suppress other senses such as "up to you".
    following = list(span.doc[span.end:span.end + 4])
    while following and following[0].text.casefold() in {'about', 'around', 'approximately', 'nearly', 'a', 'an', '$', '£', '€'}:
        following.pop(0)
    if following and following[0].like_num:
        return dict(rule)
    return None


def match(span, forms, rules):
    words = [t.text.casefold() for t in span]
    literal = ' '.join(words)
    if literal in rules['fixed']:
        return dict(key=literal, kind='fixed_expression')
    head = forms[span.start]
    if span[0].pos_ != 'VERB' or head['status'] in {'ambiguous_inflection', 'unresolved_inflection'}:
        return None
    normalized = ' '.join([head['lemma'], *words[1:]])
    if normalized in rules['verb_expressions']:
        return dict(key=normalized, kind='verb_expression')
    if len(span) == 2 and head['lemma'] in rules['reflexive_verbs'] and words[1] in REFLEXIVES and span[1].pos_ == 'PRON':
        return dict(key=head['lemma'] + ' oneself', kind='reflexive_expression')
    costs = rules['cost_collocations']
    tail = forms[span.end - 1]
    if (head['lemma'] in costs['verbs'] and span[-1].pos_ == 'NOUN'
            and tail['status'] not in {'ambiguous_inflection', 'unresolved_inflection'}
            and tail['lemma'] in costs['nouns']):
        middle = words[1:-1]
        if middle and middle[0] in costs['determiners']:
            middle = middle[1:]
        if not middle or (len(middle) == 1 and middle[0] in costs['modifiers']):
            return dict(key=f"{head['lemma']} {tail['lemma']}", kind='bounded_collocation')
    return None
