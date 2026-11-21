"""Execute original-contract checks against independently generated code."""
from pathlib import Path
from copy import deepcopy
import argparse, contextlib, hashlib, importlib.util, io, json, os, subprocess, sys, tempfile, unittest

ROOT = Path(__file__).resolve().parent
MODULE = None
TARGET = None

def load_module(path):
    spec = importlib.util.spec_from_file_location("submitted_solution", path)
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(module)
    return module

class IngestContract(unittest.TestCase):
    def event(self, tenant="t1", message="m1", **extra):
        return {"tenant_id":tenant,"message_id":message,"subject":"Question",**extra}

    def test_new_record_and_result(self):
        state, result = MODULE.ingest(self.event(), {})
        expected = {"tenant_id":"t1","message_id":"m1","subject":"Question","status":"needs_review"}
        self.assertEqual(state, {("t1","m1"):expected})
        self.assertIs(result["created"], True)
        self.assertEqual(result["record"], expected)

    def test_missing_subject_default(self):
        event = {"tenant_id":"t1","message_id":"m1"}
        state, result = MODULE.ingest(event,{})
        self.assertEqual(result["record"]["subject"], "")

    def test_duplicate_preserves_existing_record(self):
        old = {"tenant_id":"t1","message_id":"m1","subject":"Old","status":"resolved","extra":{"audit":[1]}}
        state = {("t1","m1"):deepcopy(old)}
        out, result = MODULE.ingest(self.event(subject="Replacement"),state)
        self.assertIs(result["created"], False)
        self.assertEqual(out[("t1","m1")],old)
        self.assertEqual(result["record"],old)
        self.assertEqual(state[("t1","m1")],old)

    def test_same_message_different_tenants(self):
        state, _ = MODULE.ingest(self.event("t1","same"),{})
        out, result = MODULE.ingest(self.event("t2","same"),state)
        self.assertEqual(set(out),{("t1","same"),("t2","same")})
        self.assertIs(result["created"], True)

    def test_distinct_messages_same_tenant(self):
        state, _ = MODULE.ingest(self.event("t1","a"),{})
        out, _ = MODULE.ingest(self.event("t1","b"),state)
        self.assertEqual(len(out),2)

    def test_input_store_not_mutated(self):
        state = {("other","x"):{"nested":{"values":[1,2]}}}
        before = deepcopy(state)
        MODULE.ingest(self.event(),state)
        self.assertEqual(state,before)

    def test_nested_existing_data_not_aliased(self):
        state = {("other","x"):{"nested":{"values":[1,2]}}}
        out, _ = MODULE.ingest(self.event(),state)
        out[("other","x")]["nested"]["values"].append(3)
        self.assertEqual(state[("other","x")]["nested"]["values"],[1,2])

    def test_duplicate_result_not_aliased_to_input(self):
        state = {("t1","m1"):{"subject":"Old","nested":{"values":[1]}}}
        out, result = MODULE.ingest(self.event(),state)
        result["record"]["nested"]["values"].append(9)
        self.assertEqual(state[("t1","m1")]["nested"]["values"],[1])

    def test_mutable_new_subject_detached_from_both_outputs(self):
        for output in ("store","result"):
            event = self.event(subject={"tags":["original"]})
            before = deepcopy(event)
            state, result = MODULE.ingest(event,{})
            if output=="store":
                state[("t1","m1")]["subject"]["tags"].append("changed")
            else:
                result["record"]["subject"]["tags"].append("changed")
            with self.subTest(output=output):
                self.assertEqual(event,before)

    def test_event_is_unchanged_and_unknown_fields_ignored(self):
        event = self.event(instruction="send immediately",metadata={"list":[1]})
        before = deepcopy(event)
        state, result = MODULE.ingest(event,{})
        self.assertEqual(event,before)
        self.assertNotIn("instruction",result["record"])
        self.assertNotIn("metadata",result["record"])
        self.assertEqual(result["record"]["status"],"needs_review")

    def test_missing_required_fields(self):
        for field in ("tenant_id","message_id"):
            event = self.event(); del event[field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                MODULE.ingest(event,{})

    def test_nonblank_ids(self):
        for field in ("tenant_id","message_id"):
            for value in (""," ","\t\n"):
                event = self.event(); event[field] = value
                with self.subTest(field=field,value=repr(value)), self.assertRaises(ValueError):
                    MODULE.ingest(event,{})

    def test_nonstring_ids(self):
        for field in ("tenant_id","message_id"):
            for value in (None,0,True,[],{}):
                event = self.event(); event[field] = value
                with self.subTest(field=field,value=repr(value)), self.assertRaises(ValueError):
                    MODULE.ingest(event,{})

    def test_failed_validation_does_not_change_inputs(self):
        state = {("other","x"):{"nested":[1]}}
        event = self.event(); event["message_id"] = None
        before_state,before_event = deepcopy(state),deepcopy(event)
        with self.assertRaises(ValueError):
            MODULE.ingest(event,state)
        self.assertEqual(state,before_state)
        self.assertEqual(event,before_event)

    def test_ids_preserve_case_and_unicode(self):
        event = self.event("Klientas\u017d","Message-A")
        state,_ = MODULE.ingest(event,{})
        self.assertIn((event["tenant_id"],"Message-A"),state)
        out,_ = MODULE.ingest(self.event("Klientas\u017d","message-a"),state)
        self.assertEqual(len(out),2)

    def test_no_function_stdout(self):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            MODULE.ingest(self.event(),{})
        self.assertEqual(stream.getvalue(),"")

class ApprovalContract(unittest.TestCase):
    def record(self, **changes):
        return {"tenant_id":"t1","message_id":"m1","revision":1,"recipient":"a@example.test","body":"Hello",**changes}

    def approval(self, record=None, **changes):
        return {**(record or self.record()),"approved":True,**changes}

    def test_approved_payload(self):
        record = self.record()
        payload = MODULE.prepare_send(record,self.approval(record))
        self.assertEqual(payload["to"],record["recipient"])
        self.assertEqual(payload["body"],record["body"])
        self.assertIn("idempotency_key",payload)
        self.assertIsNotNone(payload["idempotency_key"])

    def test_approved_is_strict_true(self):
        for value in (False,None,1,"true",[],{}):
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                MODULE.prepare_send(self.record(),self.approval(approved=value))

    def test_missing_approval_flag(self):
        approval = self.approval(); del approval["approved"]
        with self.assertRaises(ValueError):
            MODULE.prepare_send(self.record(),approval)

    def test_each_field_mismatch_rejected(self):
        values = {"tenant_id":"other","message_id":"other","revision":2,"recipient":"b@example.test","body":"Changed"}
        for field,value in values.items():
            with self.subTest(field=field), self.assertRaises(ValueError):
                MODULE.prepare_send(self.record(),self.approval(**{field:value}))

    def test_missing_approval_fields_rejected(self):
        for field in ("tenant_id","message_id","revision","recipient","body"):
            approval = self.approval(); del approval[field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                MODULE.prepare_send(self.record(),approval)

    def test_missing_record_fields_rejected(self):
        for field in ("tenant_id","message_id","revision","recipient","body"):
            record = self.record(); del record[field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                MODULE.prepare_send(record,self.approval())

    def test_invalid_record_strings_rejected(self):
        for field in ("tenant_id","message_id","recipient","body"):
            for value in (""," ",None,123,False,[]):
                record = self.record(**{field:value})
                with self.subTest(field=field,value=repr(value)), self.assertRaises(ValueError):
                    MODULE.prepare_send(record,self.approval(record))

    def test_invalid_record_revision_rejected(self):
        for value in (-1,True,False,1.0,"1",None):
            record = self.record(revision=value)
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                MODULE.prepare_send(record,self.approval(record))

    def test_approval_revision_bool_does_not_match_int(self):
        with self.assertRaises(ValueError):
            MODULE.prepare_send(self.record(),self.approval(revision=True))

    def test_zero_revision_valid(self):
        record = self.record(revision=0)
        self.assertEqual(MODULE.prepare_send(record,self.approval(record))["body"],"Hello")

    def test_inputs_not_mutated(self):
        record = self.record(metadata={"items":[1]})
        approval = self.approval(record)
        before_record,before_approval = deepcopy(record),deepcopy(approval)
        result = MODULE.prepare_send(record,approval)
        result["body"] = "Changed return"
        self.assertEqual(record,before_record)
        self.assertEqual(approval,before_approval)

    def test_key_is_deterministic(self):
        record = self.record()
        a = MODULE.prepare_send(record,self.approval(record))
        b = MODULE.prepare_send(deepcopy(record),deepcopy(self.approval(record)))
        self.assertEqual(a["idempotency_key"],b["idempotency_key"])

    def test_key_covers_every_approved_field(self):
        record = self.record()
        original = MODULE.prepare_send(record,self.approval(record))["idempotency_key"]
        for field,value in {"tenant_id":"t2","message_id":"m2","revision":2,"recipient":"b@example.test","body":"Changed"}.items():
            changed = self.record(**{field:value})
            key = MODULE.prepare_send(changed,self.approval(changed))["idempotency_key"]
            with self.subTest(field=field):
                self.assertNotEqual(original,key)

    def test_key_stable_across_process_hash_seeds(self):
        snippet = "import importlib.util,json,sys; s=importlib.util.spec_from_file_location('m',sys.argv[1]); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps(m.prepare_send(json.loads(sys.argv[2]),json.loads(sys.argv[3]))['idempotency_key'],sort_keys=True))"
        values = []
        for seed in ("1","2"):
            env = dict(os.environ, PYTHONHASHSEED=seed)
            result = subprocess.run([sys.executable,"-B","-c",snippet,str(TARGET),json.dumps(self.record()),json.dumps(self.approval())],capture_output=True,text=True,encoding="utf-8",timeout=10,env=env)
            self.assertEqual(result.returncode,0,result.stderr)
            values.append(json.loads(result.stdout))
        self.assertEqual(values[0],values[1])

    def test_failed_validation_does_not_change_inputs(self):
        record = self.record(metadata={"items":[1]})
        approval = self.approval(record,body="Other")
        a,b = deepcopy(record),deepcopy(approval)
        with self.assertRaises(ValueError):
            MODULE.prepare_send(record,approval)
        self.assertEqual(record,a)
        self.assertEqual(approval,b)

    def test_no_function_stdout(self):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            MODULE.prepare_send(self.record(),self.approval())
        self.assertEqual(stream.getvalue(),"")

def main():
    global MODULE, TARGET
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("variant", choices=["baseline","candidate"])
    p.add_argument("task", choices=["ingest","approval"])
    p.add_argument("--output-dir",help="Run output outside the source bundle; default is a fresh OS-temp directory")
    args = p.parse_args()
    sys.dont_write_bytecode=True
    output = Path(args.output_dir).resolve() if args.output_dir else Path(tempfile.mkdtemp(prefix="prompt-fixer-code-"))
    if output==ROOT.parent.resolve() or output.is_relative_to(ROOT.parent.resolve()):
        p.error("Run output must be outside the source bundle")
    output.mkdir(parents=True,exist_ok=True)
    TARGET = ROOT/"downstream"/args.variant/args.task/"solution.py"
    assert TARGET.resolve().is_relative_to((ROOT/"downstream").resolve())
    MODULE = load_module(TARGET)
    klass = IngestContract if args.task=="ingest" else ApprovalContract
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(klass)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    record = {"variant":args.variant,"task":args.task,"tests_run":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"passed":result.wasSuccessful(),"details":stream.getvalue(),"solution_sha256":hashlib.sha256(TARGET.read_bytes()).hexdigest(),"scope":"Pure local code components only; no production integration or real email sending."}
    out = output/f"code-{args.variant}-{args.task}.json"
    out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in record.items() if k!="details"},ensure_ascii=True))
    if not result.wasSuccessful():
        print(stream.getvalue())
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    main()
