"""Compare candidate gates offline; this does not select or regenerate a lesson."""
import argparse
from pathlib import Path
import re

from .lesson import import_story, write_json
from .selection import analyze, SelectionConfig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--legacy-written', type=Path, required=True)
    parser.add_argument('--source-run-id', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    text = args.legacy_written.read_text(encoding='utf-8')
    numbers = [int(n) for n in re.findall(r'^## Headline (\d+)\s*$', text, re.M)]
    if numbers != list(range(1, len(numbers) + 1)) or not numbers:
        raise ValueError('Expected sequential source stories')
    reports = []
    lines = ['# Offline English candidate comparison', '',
             f'Source: {args.source_run_id}. Historical diagnostic only; no new lesson or media.', '',
             'These are candidate pools before contextual usefulness and loanword decisions, not final vocabulary selections.', '',
             '| Story | Cutoff | Eligible word occurrences | Phrase windows for semantic review |',
             '|---|---:|---:|---:|']
    for n in numbers:
        lesson = import_story(text, args.source_run_id, n)
        for cutoff in (3500, 4000, 4500):
            analysis = analyze(lesson, SelectionConfig(cutoff=cutoff))
            reports.append(dict(story=n, **analysis))
            words = [c for c in analysis['candidates'] if not c['phrase']]
            phrases = [c for c in analysis['candidates'] if c['phrase']]
            lines.append(f'| {n} | {cutoff} | {len(words)} | {len(phrases)} |')
    for report in reports:
        cutoff = report['config']['cutoff']
        words = list(dict.fromkeys(c['target'] for c in report['candidates'] if not c['phrase']))
        lines.extend(['', f"## Story {report['story']}, cutoff {cutoff}", '', ', '.join(words) or '(none)'])
    lines.extend(['', 'A higher cutoff treats more single words as familiar. Expressions remain eligible independently of component ranks.',
                  'Names/entities and grammar are gated first; the next contextual pass removes familiar same-meaning loanwords, arbitrary phrases and low-value terms.', ''])
    args.output.mkdir(parents=True, exist_ok=True)
    write_json(args.output / 'candidate-comparison.json', dict(source_run_id=args.source_run_id, reports=reports))
    (args.output / 'candidate-comparison.md').write_text('\n'.join(lines), encoding='utf-8')
    print(args.output.resolve() / 'candidate-comparison.md')


if __name__ == '__main__':
    main()
