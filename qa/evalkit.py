"""Replay historical evidence separately from current-source verification. No AI calls."""
from pathlib import Path
import argparse, hashlib, json, random, statistics, sys, tempfile

ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = None

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def save(path, value):
    if OUTPUT_ROOT is None:
        raise RuntimeError("Choose an output directory outside the source tree")
    relative = Path(path).relative_to(ROOT)
    target = OUTPUT_ROOT/relative
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return target

def word_count(text):
    return len(text.split())

def sources():
    return load(ROOT/"evals/requests-a.json")["requests"]+load(ROOT/"evals/requests-b.json")["requests"]

def responses(variant):
    result, resources = {}, set()
    for suffix in ("a","b"):
        path = ROOT/"outputs"/f"{variant}-{suffix}.json"
        doc = load(path)
        for entry in doc["responses"]:
            key,text = entry["id"],entry["response"]
            if key in result or not isinstance(text,str) or not text.strip():
                raise ValueError("Duplicate or empty response: "+key)
            result[key]=text
        resources.update(doc.get("opened_resources",[]))
    if set(result)!={x["id"] for x in sources()}:
        raise ValueError("Incomplete response coverage: "+variant)
    return result,sorted(resources)

def package_metrics(snapshot, resource_paths):
    archived=load(ROOT/"evals/context-snapshots.json")[snapshot]
    text=archived["files"]["skills/prompt-fixer/SKILL.md"]
    header,body=text[4:].split("\n---\n",1)
    counted=[]
    for value in resource_paths:
        marker="skills/prompt-fixer/"
        value=str(value).replace("\\","/")
        if marker not in value:
            raise ValueError("Invalid recorded resource pointer")
        relative=marker+value.split(marker,1)[1]
        source=archived["files"][relative]
        counted.append({"path":relative,"characters":len(source),"words":word_count(source)})
    return {"core_body_words":word_count(body),"core_body_characters":len(body),"metadata_characters":len(header),"core_sha256":archived["main_sha256"],"opened_unique_resources":counted,"opened_unique_characters":sum(x["characters"] for x in counted),"measurement_limit":"Historical batch-level text proxies, not model, reasoning, cache, billing or latency telemetry."}

def literal_replay():
    original=next(x for x in sources() if x["id"]=="R04")
    if load(ROOT/"evals/r04-replay.json")!=original:
        raise ValueError("Literal replay input differs from frozen original")
    expected=load(ROOT/"evals/rubric.json")["cases"]["R04"]["exact"]
    original_pass, replay_pass = {}, {}
    for variant in ("baseline","candidate"):
        values,_=responses(variant)
        original_pass[variant]=values["R04"]==expected
        recorded=load(ROOT/"outputs"/f"{variant}-r04-replay.json")
        replay_pass[variant]=recorded.get("id")=="R04" and recorded["response"]==expected
    return {"original_exact":original_pass,"escaped_replay_exact":replay_pass,"input_matches_original":True,"status":"transport-invalid originals; separate exact replay passed" if not all(original_pass.values()) and all(replay_pass.values()) else "inspect results","original_ai_judgment":"Retained as raw historical review; deterministic exact matching takes precedence."}

def verify_lock():
    for name,digest in load(ROOT/"evals/dataset-lock.json")["sha256"].items():
        if hashlib.sha256((ROOT/"evals"/name).read_bytes()).hexdigest()!=digest:
            raise ValueError("Frozen dataset changed: "+name)
    original=ROOT/"evidence/v0.5/downstream_checks.py"
    expected=load(ROOT/"results/checks-lock.json")["downstream_checks_sha256"]
    if not original.is_file() or hashlib.sha256(original.read_bytes()).hexdigest()!=expected:
        raise ValueError("Historical evaluator does not match its recorded lock")
    return {"status":"historical inputs and original evaluator locked","scope":"Does not evaluate the current runtime."}

def summarize(write=True):
    rubric=load(ROOT/"evals/rubric.json")["cases"]
    result={"scope":"Historical 0.4.2 versus 0.5.0 replay; no new model execution","cases":len(rubric),"paired_runs":{},"deterministic_checks":{},"cases_with_responses":{},"literal_replay":literal_replay(),"limits":["One response per case/variant; four fresh batch contexts, not one per case.","Author-known small set, same inherited model and separate-context model review; no independent human validation.","Words/characters are proxies, not billed tokens or income."]}
    for variant,snapshot in (("baseline","baseline-0.4.2"),("candidate","candidate-0.5.0")):
        output,opened=responses(variant)
        metrics=package_metrics(snapshot,opened)
        lengths=[word_count(x) for x in output.values()]
        metrics.update(response_words_total=sum(lengths),response_words_median=statistics.median(lengths),response_characters_total=sum(map(len,output.values())))
        result["paired_runs"][variant]=metrics
        result["deterministic_checks"][variant]={"complete_nonempty_case_coverage":True,"R04_original_exact":output["R04"]==rubric["R04"]["exact"],"R11_under_130_words":word_count(output["R11"])<=rubric["R11"]["max_words"]}
        for key,text in output.items():
            result["cases_with_responses"].setdefault(key,{})[variant]={"response":text,"words":word_count(text),"characters":len(text)}
    if write:
        result["output"]=str(save(ROOT/"results/historical-replay.json",result))
    return result

def validate_history():
    verify_lock()
    result=summarize(write=False)
    failures=[]
    rubric=load(ROOT/"evals/rubric.json")["cases"]
    for variant in ("baseline","candidate"):
        output,_=responses(variant)
        for key,criteria in rubric.items():
            if "max_words" in criteria and word_count(output[key])>criteria["max_words"]:
                failures.append(variant+" "+key+" exceeds word limit")
            if "exact" in criteria and output[key]!=criteria["exact"]:
                if key!="R04" or not result["literal_replay"]["escaped_replay_exact"][variant]:
                    failures.append(variant+" "+key+" exact output failed")
    for review in load(ROOT/"review/judgment.json")["reviews"]:
        if review["id"]=="R04":
            continue
        for label in ("A","B"):
            if review[label].get("mode_pass") is not True or review[label].get("requirements_pass") is not True:
                failures.append(review["id"]+" "+label+" recorded semantic failure")
    if failures:
        raise ValueError("Historical regression gate failed: "+"; ".join(failures))
    return {"status":"historical gate passed","scope":"Frozen response checks only, not current model behavior","literal_replay":result["literal_replay"]}

def validate_current():
    sys.path.insert(0,str(ROOT.parent))
    from prompt_fixer.validation import check_package
    current=check_package(ROOT.parent,require_evidence=True)
    return {"current_source":current,"historical":validate_history(),"limit":"Current evidence is provenance-checked; no model is rerun by this command."}

def prepare_review():
    baseline,_=responses("baseline"); candidate,_=responses("candidate")
    rubric=load(ROOT/"evals/rubric.json")["cases"]
    rng=random.Random(20261121); review=[]; mapping={}
    for request in sources():
        key=request["id"]; order=["baseline","candidate"]; rng.shuffle(order)
        mapping[key]={"A":order[0],"B":order[1]}
        output={"baseline":baseline[key],"candidate":candidate[key]}
        review.append({"id":key,"context":request["context"],"user":request["user"],"criteria":rubric[key],"A":output[order[0]],"B":output[order[1]]})
    pairs=save(ROOT/"review/pairs.json",{"requests":review})
    key=save(ROOT/"results/review-key.json",mapping)
    return {"pairs":str(pairs),"private_mapping":str(key),"status":"prepared; no judge or model called"}

def export_prompts():
    written=[]
    for variant in ("baseline","candidate"):
        output,_=responses(variant)
        for key,name in (("R06","ingest"),("R12","approval")):
            target=OUTPUT_ROOT/"downstream"/variant/name/"request.txt"
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(output[key]+"\n",encoding="utf-8")
            written.append(str(target))
    return {"exported":written,"source_modified":False}

def main(argv=None):
    global OUTPUT_ROOT
    sys.dont_write_bytecode=True
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("action",choices=["verify-lock","summarize","prepare-review","export-prompts","validate-history","validate"])
    p.add_argument("--output-dir",help="New run output directory outside this source bundle; default is a fresh OS-temp directory")
    args=p.parse_args(argv)
    bundle=ROOT.parent.resolve()
    OUTPUT_ROOT=Path(args.output_dir).resolve() if args.output_dir else Path(tempfile.mkdtemp(prefix="prompt-fixer-qa-"))
    if OUTPUT_ROOT==bundle or OUTPUT_ROOT.is_relative_to(bundle):
        p.error("Run output must be outside the source bundle")
    OUTPUT_ROOT.mkdir(parents=True,exist_ok=True)
    try:
        result={"verify-lock":verify_lock,"summarize":summarize,"prepare-review":prepare_review,"export-prompts":export_prompts,"validate-history":validate_history,"validate":validate_current}[args.action]()
        print(json.dumps(result,ensure_ascii=True,indent=2))
        return 0
    except (OSError,ValueError,KeyError,TypeError) as error:
        print(json.dumps({"error":str(error)},ensure_ascii=True),file=sys.stderr)
        return 1

if __name__=="__main__":
    sys.exit(main())
