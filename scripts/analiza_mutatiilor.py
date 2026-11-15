"""Validate PIT/Major artifacts and reproduce the numeric tables of chapter 8.

Run after: python3 main/tools/run.py mutation --exercise 14_armstrong
No packages are downloaded. Java witness checks use the installed Major runtime.
"""
from __future__ import annotations
from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

EXERCISE = Path(__file__).resolve().parents[1]
MAIN = EXERCISE.parent
OUT = EXERCISE / 'rapoarte/studiu_mutatie'
SUITES = ['EpTest', 'BvaTest', 'CegTest', 'McdcTest']
LABELS = ['EP', 'BVA', 'CEG', 'MC/DC']
ALIASES = ['EquivalncePartitioning', 'BoundaryValueAnalysis',
           'CauseEffectGraphing', 'ModifiedConditionDecisionCoverage']
STATUS = {'FAIL': 'KILLED', 'EXC': 'KILLED_EXCEPTION', 'TIME': 'TIMED_OUT',
          'LIVE': 'SURVIVED', 'UNCOV': 'NO_COVERAGE'}


def percent(num, den):
    return f'{100 * num / den:.1f}'.replace('.', ',') + r'\%'


def table(name, headers, rows, columns=None):
    columns = columns or 'l' + 'c' * (len(headers) - 1)
    lines = [r'\begin{center}', r'\begingroup\small',
             r'\begin{tabular}{@{}' + columns + '@{}}', r'\toprule',
             ' & '.join(headers) + r' \\', r'\midrule']
    lines += [' & '.join(map(str, row)) + r' \\' for row in rows]
    lines += [r'\bottomrule', r'\end{tabular}', r'\endgroup', r'\end{center}', '']
    (OUT / (name + '.tex')).write_text('\n'.join(lines))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    operators = {}
    for line in (EXERCISE / 'rapoarte/major/mutants.log').read_text().splitlines():
        parts = line.split(':')
        operators[parts[0]] = {'operator': parts[1], 'description': line}
    assert len(operators) == 31
    assert 'rest > 0 |==> rest != 0' in operators['11']['description']
    assert 'suma == n |==> suma >= n' in operators['29']['description']
    data = {'scope': 'ro.tss.armstrong.Main.evaluate(int)',
            'equivalent_major_ids': ['11'], 'PIT': {}, 'Major': {}}
    native_rows = {'PIT': [], 'Major': []}
    score_rows, adjusted_rows, major_reason_rows = [], [], []
    identities = None
    for suite, label, alias in zip(SUITES, LABELS, ALIASES):
        root = ET.parse(EXERCISE / 'rapoarte/pit' / suite / 'mutations.xml').getroot()
        pit = []
        for m in root:
            assert m.findtext('mutatedClass') == 'ro.tss.armstrong.Main'
            assert m.findtext('mutatedMethod') == 'evaluate'
            assert m.get('status') in ['KILLED', 'TIMED_OUT', 'SURVIVED', 'NO_COVERAGE']
            pit.append({'status': m.get('status'),
                        'operator': m.findtext('mutator').split('.')[-1],
                        'line': int(m.findtext('lineNumber')),
                        'indexes': [int(x.text) for x in m.findall('indexes/index')],
                        'description': m.findtext('description'),
                        'killing_test': m.findtext('killingTest')})
        keys = {(m['operator'], m['line'], tuple(m['indexes'])) for m in pit}
        if identities is None:
            identities = keys
        else:
            assert identities == keys
        major_raw = list(csv.reader((EXERCISE / 'rapoarte/major' / suite / 'details.csv').open()))[1:]
        major = [{'id': i, **operators[i], 'status': STATUS[s]} for i, s in major_raw]
        assert {m['id'] for m in major} == set(operators)
        assert len(pit) == 15 and len(major) == 31
        reasons = Counter(s for _, s in major_raw)
        major_reason_rows.append([label] + [reasons[k] for k in ['FAIL', 'EXC', 'TIME', 'LIVE', 'UNCOV']])
        native_scores = {}
        for name, rows in [('PIT', pit), ('Major', major)]:
            c = Counter(m['status'] for m in rows)
            g = len(rows)
            k = c['KILLED'] + c['KILLED_EXCEPTION']
            t, live, u = c['TIMED_OUT'], c['SURVIVED'], c['NO_COVERAGE']
            assert g == k + t + live + u
            e = 1 if name == 'Major' else 0
            record = {'generated': g, 'killed_without_timeout': k,
                      'timeouts': t, 'survived': live, 'uncovered': u,
                      'detected': k + t, 'equivalent_count': e,
                      'mutation_score': 100 * (k + t) / g,
                      'score_without_timeout': 100 * k / (g - t),
                      'adjusted_score': 100 * (k + t) / (g - e),
                      'test_strength': 100 * (k + t) / (g - u),
                      'mutants': rows}
            data[name][suite] = record
            native_rows[name].append([label, g, k, t, live, u,
                                      f'{k+t}/{g} = ' + percent(k+t, g)])
            score_rows.append([name, label, f'{k}/{g-t}', percent(k, g-t)])
            native_scores[name] = percent(k+t, g)
            if name == 'Major':
                adjusted_rows.append([label, native_scores['PIT'], native_scores['Major'],
                                      f'{k+t}/{g-e} = ' + percent(k+t, g-e)])
                with (EXERCISE / 'rapoarte/major' / suite / 'summary.csv').open() as handle:
                    summary = next(csv.DictReader(handle))
                assert int(summary['MutantsGenerated']) == g
                assert int(summary['MutantsKilled']) == k+t
                assert int(summary['MutantsLive']) == live
            log = (EXERCISE / 'rapoarte' / name.lower() / suite / 'run.log').read_text()
            assert 'ro.tss.armstrong.' + alias in log or name == 'Major'
            if name == 'PIT':
                native_match = re.search(r'Generated (\d+) mutations Killed (\d+)', log)
                assert native_match and (int(native_match[1]), int(native_match[2])) == (g, k+t)
        assert next(m for m in major if m['id'] == '11')['status'] == 'SURVIVED'
    # BVA detects every Major mutant other than the mathematically equivalent id 11.
    assert [m['id'] for m in data['Major']['BvaTest']['mutants'] if m['status'] == 'SURVIVED'] == ['11']
    assert all(m['status'] in ['KILLED', 'TIMED_OUT'] for m in data['PIT']['BvaTest']['mutants'])
    table('pit_results', ['Suită', '$G$', '$K$', '$T$', '$S$', '$U$', '$MS$'], native_rows['PIT'])
    table('major_results', ['Suită', '$G$', '$K$', '$T$', '$S$', '$U$', '$MS$'], native_rows['Major'])
    table('major_status', ['Suită', 'FAIL', 'EXC', 'TIME', 'LIVE', 'UNCOV'], major_reason_rows)
    table('timeout_free', ['Unealtă', 'Suită', '$K/(G-T)$', 'Scor fără timeout'], score_rows, 'llcc')
    table('comparison', ['Suită', 'PIT brut', 'Major brut', 'Major ajustat ($E=1$)'], adjusted_rows)
    op_labels = {
        'ConditionalsBoundaryMutator': r'Conditionals\allowbreak{}Boundary',
        'NegateConditionalsMutator': r'Negate\allowbreak{}Conditionals',
        'EmptyObjectReturnValsMutator': r'Empty\allowbreak{}ObjectReturnVals',
        'MathMutator': 'Math', 'AOR': 'AOR', 'COR': 'COR', 'ROR': 'ROR', 'STD': 'STD'}
    for name in ['PIT', 'Major']:
        op_rows = []
        universe = sorted({m['operator'] for m in data[name]['BvaTest']['mutants']})
        for op in universe:
            g = sum(m['operator'] == op for m in data[name]['BvaTest']['mutants'])
            row = [op_labels[op], g]
            for suite in SUITES:
                detected = sum(m['operator'] == op and m['status'] in ['KILLED', 'KILLED_EXCEPTION', 'TIMED_OUT']
                               for m in data[name][suite]['mutants'])
                row.append(f'{detected}/{g}')
            op_rows.append(row)
        table(name.lower()+'_operators', ['Operator', '$G$', 'EP', 'BVA', 'CEG', 'MC/DC'], op_rows)
    # Exercise the actual automatically generated Major mutants, without editing test suites.
    jdk = next((MAIN / '.tools/jdk11').glob('*/bin/javac')).parents[1]
    runtime = MAIN / '.tools/major/lib/major-rt.jar'
    binary = EXERCISE / 'target/major-classes'
    witness_binary = EXERCISE / 'target/mutation-study'
    witness_binary.mkdir(parents=True, exist_ok=True)
    cp = os.pathsep.join(map(str, [binary, runtime, witness_binary]))
    java_file = EXERCISE / 'scripts/MutationWitnessCheck.java'
    commands = [[str(jdk/'bin/javac'), '-cp', cp, '-d', str(witness_binary), str(java_file)],
                [str(jdk/'bin/java'), '-cp', cp, 'MutationWitnessCheck']]
    transcript = []
    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        transcript.append('$ ' + ' '.join(cmd) + '\n' + result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError(transcript[-1])
    (OUT / 'martori-java.log').write_text('\n'.join(transcript))
    assert 'EQUIVALENT_11_CHECKS 906' in transcript[-1]
    data['witness_checks'] = transcript[-1].splitlines()[1:]
    data['input_sha256'] = {}
    inputs = [EXERCISE/'src/main/java/ro/tss/armstrong/Main.java', EXERCISE/'rapoarte/major/mutants.log']
    inputs += list((EXERCISE/'src/test/java/ro/tss/armstrong').glob('*.java'))
    inputs += [EXERCISE/'scripts/MutationWitnessCheck.java']
    for suite in SUITES:
        inputs += [EXERCISE/'rapoarte/pit'/suite/'mutations.xml',
                   EXERCISE/'rapoarte/major'/suite/'details.csv']
    for path in inputs:
        data['input_sha256'][str(path.relative_to(EXERCISE))] = hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT / 'analiza.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print('OK: 8 rapoarte validate; scoruri recalculate; 5 martori verificați în JVM; mutantul 11 verificat pe 906 intrări')


if __name__ == '__main__':
    main()
