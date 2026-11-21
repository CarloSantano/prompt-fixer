from pathlib import Path
from copy import deepcopy
import hashlib
import json
import os
import tempfile
import unittest
from unittest import mock

from prompt_fixer.install import install, uninstall, doctor, RECEIPT
from prompt_fixer.measure import compare_ledger
from prompt_fixer.validation import PackageError, check_package, runtime_inventory, runtime_fingerprint, verify_current

def write_json(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding="utf-8")

def make_bundle(root, version="0.6.0"):
    skill=root/"skills/prompt-fixer"
    (skill/"references").mkdir(parents=True)
    (skill/"SKILL.md").write_text('---\nname: prompt-fixer\ndescription: "A fixture workflow."\n---\n\n# Workflow\n[Guide](references/guide.md)\n',encoding="utf-8")
    (skill/"references/guide.md").write_text("Preserve the user's intent.\n",encoding="utf-8")
    manifest={"name":"prompt-fixer","version":version,"description":"Fixture","author":{"name":"Fixture Owner"},"extensions":{"com.openai":{"interface":{"displayName":"Prompt Fixer"}}}}
    write_json(root/"plugin.json",manifest)
    write_json(root/".codex-plugin/plugin.json",{**{k:manifest[k] for k in ("name","version","description","author")},"interface":manifest["extensions"]["com.openai"]["interface"]})
    return skill

def evidence(root):
    artifact=root/"qa/proof.json"
    write_json(artifact,{"fixture":True,"response":"a controlled response"})
    proof={"version":json.loads((root/"plugin.json").read_text())["version"],"runtime_files":runtime_inventory(root),"runtime_sha256":runtime_fingerprint(root),"behavior_cases":[{"passed":True,"evidence":"qa/proof.json","evidence_sha256":hashlib.sha256(artifact.read_bytes()).hexdigest()}]}
    write_json(root/"qa/release-evidence.json",proof)

class Installation(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="pf-install-test-")
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.bundle=self.root/"bundle"
        self.skill=make_bundle(self.bundle)
        self.project=self.root/"project"; self.project.mkdir()

    def test_dry_run_does_not_write(self):
        result=install(self.bundle,self.project,"codex",dry_run=True)
        self.assertEqual(result["status"],"dry_run")
        self.assertEqual(list(self.project.iterdir()),[])

    def test_codex_layout_and_doctor(self):
        result=install(self.bundle,self.project,"codex")
        target=self.project/".agents/skills/prompt-fixer"
        self.assertEqual(result["status"],"installed")
        self.assertEqual((target/"SKILL.md").read_bytes(),(self.skill/"SKILL.md").read_bytes())
        self.assertEqual(doctor(self.project,"codex")["status"],"managed_files_match_receipt")

    def test_claude_layout(self):
        install(self.bundle,self.project,"claude")
        self.assertTrue((self.project/".claude/skills/prompt-fixer/SKILL.md").is_file())

    def test_same_install_is_idempotent(self):
        install(self.bundle,self.project,"codex")
        self.assertEqual(install(self.bundle,self.project,"codex")["status"],"already_installed")
        self.assertFalse((self.project/".prompt-fixer/backups").exists())

    def test_unmanaged_install_is_not_overwritten(self):
        target=self.project/".agents/skills/prompt-fixer"
        target.mkdir(parents=True); (target/"user.txt").write_text("keep")
        with self.assertRaises(PackageError): install(self.bundle,self.project,"codex",replace=True)
        self.assertEqual((target/"user.txt").read_text(),"keep")

    def test_user_edit_prevents_update_and_removal(self):
        install(self.bundle,self.project,"codex")
        target=self.project/".agents/skills/prompt-fixer"
        (target/"SKILL.md").write_text("my edit")
        with self.assertRaises(PackageError): install(self.bundle,self.project,"codex",replace=True)
        with self.assertRaises(PackageError): uninstall(self.project,"codex")
        self.assertEqual((target/"SKILL.md").read_text(),"my edit")

    def test_untracked_nested_receipt_name_is_not_ignored(self):
        install(self.bundle,self.project,"codex")
        target=self.project/".agents/skills/prompt-fixer"
        (target/"references"/RECEIPT).write_text("user data")
        with self.assertRaises(PackageError): uninstall(self.project,"codex")

    def test_update_requires_explicit_replace_and_keeps_backup(self):
        install(self.bundle,self.project,"codex")
        old=(self.skill/"SKILL.md").read_bytes()
        (self.skill/"SKILL.md").write_text((self.skill/"SKILL.md").read_text()+"New instruction.\n")
        with self.assertRaises(PackageError): install(self.bundle,self.project,"codex")
        result=install(self.bundle,self.project,"codex",replace=True)
        self.assertEqual((Path(result["backup"])/"SKILL.md").read_bytes(),old)
        self.assertIn("New instruction",(Path(result["target"])/"SKILL.md").read_text())

    def test_uninstall_moves_to_recoverable_backup(self):
        install(self.bundle,self.project,"claude")
        result=uninstall(self.project,"claude")
        self.assertFalse((self.project/".claude/skills/prompt-fixer").exists())
        self.assertTrue((Path(result["backup"])/"SKILL.md").exists())
        self.assertIs(result["data_deleted"],False)

    def test_unknown_or_missing_project_refused(self):
        with self.assertRaises(PackageError): install(self.bundle,self.root/"missing","codex")
        with self.assertRaises(PackageError): install(self.bundle,self.project,"unknown")

    def test_invalid_source_link_refused_before_install(self):
        (self.skill/"SKILL.md").write_text((self.skill/"SKILL.md").read_text()+"[Missing](missing.md)\n")
        with self.assertRaises(PackageError): install(self.bundle,self.project,"codex")
        self.assertEqual(list(self.project.iterdir()),[])

    def test_skill_link_cannot_escape_package(self):
        (self.skill/"SKILL.md").write_text((self.skill/"SKILL.md").read_text()+"[Outside](../../outside.md)\n")
        with self.assertRaises(PackageError): install(self.bundle,self.project,"codex")

    def test_failed_activation_restores_prior_install(self):
        install(self.bundle,self.project,"codex")
        target=self.project/".agents/skills/prompt-fixer"
        before=(target/"SKILL.md").read_bytes()
        (self.skill/"SKILL.md").write_text((self.skill/"SKILL.md").read_text()+"Update\n")
        original=Path.replace
        def fail_stage(path,destination):
            if path.name=="prompt-fixer" and path.parent.name.startswith("install-"):
                raise OSError("Injected activation failure")
            return original(path,destination)
        with mock.patch.object(Path,"replace",fail_stage),self.assertRaises(OSError):
            install(self.bundle,self.project,"codex",replace=True)
        self.assertEqual((target/"SKILL.md").read_bytes(),before)

    def test_external_linked_host_root_refused(self):
        outside=self.root/"outside"; outside.mkdir()
        try:
            os.symlink(outside,self.project/".agents",target_is_directory=True)
        except OSError:
            self.skipTest("Host does not permit directory symlinks")
        with self.assertRaises(PackageError): install(self.bundle,self.project,"codex")
        self.assertEqual(list(outside.iterdir()),[])

class SourceEvidence(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="pf-evidence-test-")
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.skill=make_bundle(self.root)

    def test_package_and_current_evidence(self):
        evidence(self.root)
        self.assertEqual(check_package(self.root,True)["release_evidence"]["behavior_cases"],1)

    def test_missing_evidence_is_not_a_pass(self):
        with self.assertRaises(PackageError): verify_current(self.root)

    def test_changed_main_is_rejected(self):
        evidence(self.root)
        (self.skill/"SKILL.md").write_text((self.skill/"SKILL.md").read_text()+"Changed\n")
        with self.assertRaisesRegex(PackageError,"differs"): verify_current(self.root)

    def test_changed_reference_is_rejected(self):
        evidence(self.root)
        (self.skill/"references/guide.md").write_text("Changed\n")
        with self.assertRaisesRegex(PackageError,"differs"): verify_current(self.root)

    def test_changed_evaluator_code_is_rejected(self):
        (self.root/"qa").mkdir()
        (self.root/"qa/evalkit.py").write_text("# original\n")
        evidence(self.root)
        (self.root/"qa/evalkit.py").write_text("# weakened check\n")
        with self.assertRaisesRegex(PackageError,"differs"): verify_current(self.root)

    def test_changed_proof_is_rejected(self):
        evidence(self.root)
        (self.root/"qa/proof.json").write_text("{}")
        with self.assertRaisesRegex(PackageError,"evidence"): verify_current(self.root)

    def test_manifest_mismatch_is_rejected(self):
        path=self.root/".codex-plugin/plugin.json"
        value=json.loads(path.read_text()); value["version"]="other"; write_json(path,value)
        with self.assertRaisesRegex(PackageError,"Manifest"): check_package(self.root)

    def test_evidence_cannot_reference_outside_root(self):
        evidence(self.root)
        path=self.root/"qa/release-evidence.json"
        value=json.loads(path.read_text()); value["behavior_cases"][0]["evidence"]="../outside.json"; write_json(path,value)
        with self.assertRaises(PackageError): verify_current(self.root)

class UsageLedger(unittest.TestCase):
    def ledger(self):
        return {"schema_version":1,"task_id":"task-a","condition_id":"same-original-brief-and-execution-setup","direct":{"execution_model":"same-model","passed":True,"outcome_evidence":"checks/direct.json","steps":[{"stage":"execute","input_tokens":300,"output_tokens":200}]},"fixed":{"execution_model":"same-model","passed":True,"outcome_evidence":"checks/fixed.json","steps":[{"stage":"fix","input_tokens":20,"output_tokens":30},{"stage":"execute","input_tokens":100,"output_tokens":80},{"stage":"repair","input_tokens":10,"output_tokens":15}]}}

    def test_entire_fixer_and_repair_path_counted(self):
        result=compare_ledger(self.ledger())
        self.assertEqual(result["fixed"]["total_tokens"],255)
        self.assertEqual(result["fixed_minus_direct_tokens"],-245)
        self.assertEqual(result["reported_saving_percent"],49.0)

    def test_incomplete_usage_is_unknown_not_zero(self):
        data=self.ledger(); data["fixed"]["steps"][0]["input_tokens"]=None
        result=compare_ledger(data)
        self.assertFalse(result["comparison_eligible"])
        self.assertIsNone(result["fixed"]["total_tokens"])
        self.assertIsNone(result["reported_saving_percent"])

    def test_bool_and_negative_counts_rejected(self):
        for value in (True,-1,"10",1.0):
            data=self.ledger(); data["direct"]["steps"][0]["input_tokens"]=value
            with self.subTest(value=value),self.assertRaises(PackageError): compare_ledger(data)

    def test_synthetic_fixture_cannot_be_reported_as_measured_saving(self):
        data=self.ledger(); data["synthetic"]=True
        result=compare_ledger(data)
        self.assertFalse(result["comparison_eligible"])
        self.assertIsNone(result["reported_saving_percent"])

    def test_failed_cheaper_arm_is_not_a_win(self):
        data=self.ledger(); data["fixed"]["passed"]=False
        self.assertFalse(compare_ledger(data)["comparison_eligible"])

    def test_execution_model_must_match(self):
        data=self.ledger(); data["fixed"]["execution_model"]="different-model"
        self.assertFalse(compare_ledger(data)["comparison_eligible"])

    def test_cached_and_reasoning_subsets_are_not_counted_twice(self):
        data=self.ledger(); step=data["direct"]["steps"][0]
        step.update(cached_input_tokens=200,reasoning_tokens=100)
        self.assertEqual(compare_ledger(data)["direct"]["total_tokens"],500)

    def test_invalid_subset_counts_rejected(self):
        for field in ("cached_input_tokens","reasoning_tokens"):
            data=self.ledger(); data["direct"]["steps"][0][field]=999
            with self.subTest(field=field),self.assertRaises(PackageError): compare_ledger(data)

    def test_fixed_arm_must_include_fixer_or_combined_step(self):
        data=self.ledger(); data["fixed"]["steps"]=data["fixed"]["steps"][1:]
        self.assertFalse(compare_ledger(data)["comparison_eligible"])

    def test_zero_baseline_does_not_divide_by_zero(self):
        data=self.ledger(); data["direct"]["steps"][0].update(input_tokens=0,output_tokens=0)
        self.assertIsNone(compare_ledger(data)["reported_saving_percent"])

    def test_schema_bool_is_rejected(self):
        data=self.ledger(); data["schema_version"]=True
        with self.assertRaises(PackageError): compare_ledger(data)

if __name__=="__main__":
    unittest.main()
