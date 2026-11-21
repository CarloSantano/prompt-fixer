"""Regression gates and mutation sensitivity; all fixtures are local and disposable."""
from pathlib import Path
from copy import deepcopy
import hashlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]

def module_at(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

evalkit=module_at("pf_evalkit",ROOT/"qa/evalkit.py")
checks=module_at("pf_checks",ROOT/"qa/downstream_checks.py")

def hashes(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts}

class RegressionGates(unittest.TestCase):
    def test_frozen_history_gate(self):
        result=evalkit.validate_history()
        self.assertEqual(result["status"],"historical gate passed")
        self.assertFalse(all(result["literal_replay"]["original_exact"].values()))
        self.assertTrue(all(result["literal_replay"]["escaped_replay_exact"].values()))

    def test_oversized_response_raises_instead_of_green_summary(self):
        original=evalkit.responses
        def changed(variant):
            values,resources=original(variant)
            if variant=="candidate":
                values["R11"]=" ".join(["word"]*131)
            return values,resources
        with mock.patch.object(evalkit,"responses",side_effect=changed):
            with self.assertRaisesRegex(ValueError,"R11 exceeds word limit"):
                evalkit.validate_history()

    def test_oversized_response_causes_cli_nonzero(self):
        with tempfile.TemporaryDirectory(prefix="pf-regression-") as tmp:
            copied=Path(tmp)/"qa"
            shutil.copytree(ROOT/"qa",copied,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
            for path in (copied/"outputs").glob("candidate-?.json"):
                data=json.loads(path.read_text(encoding="utf-8"))
                for item in data["responses"]:
                    if item["id"]=="R11":
                        item["response"]=" ".join(["word"]*131)
                        path.write_text(json.dumps(data),encoding="utf-8")
            run=subprocess.run([sys.executable,"-B",str(copied/"evalkit.py"),"validate-history"],capture_output=True,text=True,encoding="utf-8",timeout=20)
            self.assertEqual(run.returncode,1,run.stdout+run.stderr)
            self.assertIn("R11 exceeds word limit",run.stderr)

    def test_replay_input_must_match_original(self):
        original=evalkit.load
        def changed(path):
            value=original(path)
            if Path(path).name=="r04-replay.json":
                value=deepcopy(value)
                value["user"]+=" changed"
            return value
        with mock.patch.object(evalkit,"load",side_effect=changed):
            with self.assertRaisesRegex(ValueError,"differs from frozen original"):
                evalkit.literal_replay()

    def test_failed_replay_cannot_excuse_original_exact_failure(self):
        original=evalkit.load
        def changed(path):
            value=original(path)
            if Path(path).name=="candidate-r04-replay.json":
                value=deepcopy(value)
                value["response"]="wrong"
            return value
        with mock.patch.object(evalkit,"load",side_effect=changed):
            with self.assertRaisesRegex(ValueError,"R04 exact output failed"):
                evalkit.validate_history()

    def test_new_runs_leave_frozen_source_unchanged(self):
        before=hashes(ROOT/"qa")
        with tempfile.TemporaryDirectory(prefix="pf-replay-output-") as tmp:
            commands=[
                [str(ROOT/"qa/evalkit.py"),"summarize","--output-dir",tmp],
                [str(ROOT/"qa/downstream_checks.py"),"candidate","ingest","--output-dir",tmp],
            ]
            for args in commands:
                run=subprocess.run([sys.executable,"-B",*args],capture_output=True,text=True,encoding="utf-8",timeout=20)
                self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            self.assertTrue((Path(tmp)/"results/historical-replay.json").is_file())
            self.assertTrue((Path(tmp)/"code-candidate-ingest.json").is_file())
        self.assertEqual(hashes(ROOT/"qa"),before)

    def test_run_output_inside_bundle_is_rejected(self):
        run=subprocess.run([sys.executable,"-B",str(ROOT/"qa/evalkit.py"),"summarize","--output-dir",str(ROOT/"qa/results")],capture_output=True,text=True,encoding="utf-8",timeout=20)
        self.assertNotEqual(run.returncode,0)
        self.assertIn("outside the source bundle",run.stderr)

class MutableSubjectCoverage(unittest.TestCase):
    def test_real_implementations_pass_mutable_subject_check(self):
        for variant in ("baseline","candidate"):
            module=module_at("ingest_"+variant,ROOT/"qa/downstream"/variant/"ingest/solution.py")
            with self.subTest(variant=variant),mock.patch.object(checks,"MODULE",module):
                result=unittest.TextTestRunner(stream=io.StringIO()).run(checks.IngestContract("test_mutable_new_subject_detached_from_both_outputs"))
                self.assertTrue(result.wasSuccessful())

    def test_new_check_catches_alias_mutant_missed_by_old_checks(self):
        original=module_at("ingest_for_mutation",ROOT/"qa/downstream/candidate/ingest/solution.py")
        def ingest(event,store):
            output,result=original.ingest(event,store)
            if result["created"]:
                output[(event["tenant_id"],event["message_id"])]["subject"]=event.get("subject","")
                result["record"]=deepcopy(output[(event["tenant_id"],event["message_id"])])
            return output,result
        mutant=types.SimpleNamespace(ingest=ingest)
        name="test_mutable_new_subject_detached_from_both_outputs"
        old_names=[x for x in unittest.defaultTestLoader.getTestCaseNames(checks.IngestContract) if x!=name]
        with mock.patch.object(checks,"MODULE",mutant):
            old=unittest.TextTestRunner(stream=io.StringIO()).run(unittest.TestSuite(checks.IngestContract(x) for x in old_names))
            new=unittest.TextTestRunner(stream=io.StringIO()).run(checks.IngestContract(name))
        self.assertEqual(old.testsRun,15)
        self.assertTrue(old.wasSuccessful(),"Mutant must demonstrate the original blind spot")
        self.assertFalse(new.wasSuccessful(),"New check must reject the alias mutant")
        self.assertTrue(new.failures)

if __name__=="__main__":
    unittest.main()
