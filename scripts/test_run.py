import json
from pathlib import Path
import tempfile
import unittest

import run


class RunnerTest(unittest.TestCase):
    def test_suite_names_do_not_depend_on_folder_name(self):
        for folder in [Path('/tmp/armstrong'), Path('/tmp/renamed-project')]:
            self.assertEqual(run.class_name(folder, 'BvaTest'),
                             'ro.tss.armstrong.BoundaryValueAnalysis')
            self.assertEqual(run.class_name(folder, 'RegressionTest'),
                             'ro.tss.armstrong.RegressionTest')

    def test_summary_excludes_timeouts_and_counts_exceptions_as_kills(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            reports = folder / 'rapoarte'
            reports.mkdir()
            for name in ['tests', 'coverage']:
                (reports / (name + '.json')).write_text('{}')
            resource = folder / 'src/test/resources/regression.tsv'
            resource.parent.mkdir(parents=True)
            resource.write_text('100\tNU\n153\tDA\n')
            for suite in run.SUITES:
                for tool in ['pit', 'major']:
                    (reports / tool / suite).mkdir(parents=True)
                (reports / 'pit' / suite / 'mutations.xml').write_text(
                    '<mutations><mutation status="KILLED"/>'
                    '<mutation status="TIMED_OUT"/><mutation status="SURVIVED"/></mutations>')
                (reports / 'major' / suite / 'details.csv').write_text(
                    'MutantNo,Status\n1,FAIL\n2,EXC\n3,TIME\n4,LIVE\n5,UNCOV\n')
            run.summary(folder)
            result = json.loads((reports / 'rezumat.json').read_text())
            self.assertEqual(result['regression_inputs'], 2)
            pit = result['mutation']['PIT']['BvaTest']
            major = result['mutation']['Major']['BvaTest']
            self.assertEqual((pit['killed'], pit['denominator'], pit['percent']), (1, 2, '50.0%'))
            self.assertEqual((major['killed'], major['denominator'], major['percent']), (2, 4, '50.0%'))
