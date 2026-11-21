"""Offline Prompt Fixer regression evidence. No model/API calls or token claims."""
from pathlib import Path
import argparse, hashlib, json, random, re, statistics

ROOT = Path(__file__).resolve().parent

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

def word_count(text):
    return len(text.split())

def sources():
    return load(ROOT/"evals/requests-a.json")["requests"] + load(ROOT/"evals/requests-b.json")["requests"]

def responses(variant):
    result = {}
    resources = set()
    for suffix in ("a", "b"):
        path = ROOT/"outputs"/f"{variant}-{suffix}.json"
        doc = load(path)
        assert isinstance(doc["responses"], list), path
        for entry in doc["responses"]:
            key, text = entry["id"], entry["response"]
            assert key not in result, (variant, key, "duplicate")
            assert isinstance(text, str) and text.strip(), (variant, key, "empty")
            result[key] = text
        resources.update(doc.get("opened_resources", []))
    assert set(result) == {x["id"] for x in sources()}, (variant, "coverage")
    return result, sorted(resources)

def package_metrics(folder, resource_paths):
    folder = Path(folder)
    main = folder/"skills/prompt-fixer/SKILL.md"
    archived = None
    if not main.is_file():
        archived = load(ROOT/"evals/context-snapshots.json")[folder.name]
    text = archived["files"]["skills/prompt-fixer/SKILL.md"] if archived else main.read_text(encoding="utf-8")
    header, body = text[4:].split("\n---\n", 1)
    counted = []
    for value in resource_paths:
        if archived:
            marker = "skills/prompt-fixer/"
            normalized = str(value).replace("\\", "/")
            assert marker in normalized, value
            relative = marker + normalized.split(marker,1)[1]
            source = archived["files"][relative]
        else:
            p = Path(value)
            assert p.resolve().is_relative_to(folder.resolve()), value
            assert p.is_file(), value
            relative = p.relative_to(folder).as_posix()
            source = p.read_text(encoding="utf-8")
        counted.append({"path":relative, "characters":len(source), "words":word_count(source)})
    return {
        "core_body_words":word_count(body),
        "core_body_characters":len(body),
        "metadata_characters":len(header),
        "core_sha256":archived["main_sha256"] if archived else hashlib.sha256(main.read_bytes()).hexdigest(),
        "opened_unique_resources":counted,
        "opened_unique_characters":sum(x["characters"] for x in counted),
        "measurement_limit":"Source/response character and whitespace-word counts only. No inference, cache, hidden-reasoning, billed-token, credit or latency telemetry. Unique loaded source counts are batch-level, not a per-task trace."
    }

def summarize():
    rubric = load(ROOT/"evals/rubric.json")["cases"]
    result = {"cases":len(rubric), "paired_runs":{}, "deterministic_checks":{}, "limits":["One response per case/variant in four fresh batch contexts; cases within a batch share a context window.", "Author-designed cases, not an independently blinded holdout or representative production sample.", "Length is a resource proxy, not correctness or actual token usage."]}
    rows = {}
    for variant, folder in (("baseline", "baseline-0.4.2"), ("candidate", "candidate-0.5.0")):
        output, opened = responses(variant)
        metrics = package_metrics(ROOT/folder, opened)
        lengths = [word_count(x) for x in output.values()]
        metrics.update(response_words_total=sum(lengths), response_words_median=statistics.median(lengths), response_characters_total=sum(map(len, output.values())))
        result["paired_runs"][variant] = metrics
        exact = output["R04"] == rubric["R04"]["exact"]
        short = word_count(output["R11"]) <= rubric["R11"]["max_words"]
        result["deterministic_checks"][variant] = {"complete_nonempty_case_coverage":True, "R04_exact_requested_edit":exact, "R11_under_130_words":short}
        for key, text in output.items():
            rows.setdefault(key, {})[variant] = {"response":text, "words":word_count(text), "characters":len(text)}
    result["cases_with_responses"] = rows
    save(ROOT/"results/measurements.json", result)
    print(json.dumps({k:v for k,v in result.items() if k!="cases_with_responses"}, ensure_ascii=True, indent=2))

def prepare_review():
    baseline, _ = responses("baseline")
    candidate, _ = responses("candidate")
    rubric = load(ROOT/"evals/rubric.json")["cases"]
    rng = random.Random(20261121)
    review, mapping = [], {}
    for request in sources():
        key = request["id"]
        order = ["baseline", "candidate"]
        rng.shuffle(order)
        mapping[key] = {"A":order[0], "B":order[1]}
        outputs = {"baseline":baseline[key], "candidate":candidate[key]}
        review.append({"id":key, "context":request["context"], "user":request["user"], "criteria":rubric[key], "A":outputs[order[0]], "B":outputs[order[1]]})
    save(ROOT/"review/pairs.json", {"requests":review})
    save(ROOT/"results/review-key.json", mapping)
    print("Prepared randomized A/B pairs; version mapping retained separately.")

def export_prompts():
    for variant in ("baseline", "candidate"):
        output, _ = responses(variant)
        for key, name in (("R06","ingest"),("R12","approval")):
            target = ROOT/"downstream"/variant/name
            target.mkdir(parents=True, exist_ok=True)
            (target/"request.txt").write_text(output[key]+"\n", encoding="utf-8")
    print("Exported raw generated prompts without editing them.")

def verify_lock():
    lock = load(ROOT/"evals/dataset-lock.json")
    for name, digest in lock["sha256"].items():
        actual = hashlib.sha256((ROOT/"evals"/name).read_bytes()).hexdigest()
        assert actual == digest, (name, "dataset changed")
    print("Original inputs, rubric and code contracts match their pre-candidate hashes.")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=["verify-lock","summarize","prepare-review","export-prompts"])
    action = p.parse_args().action
    {"verify-lock":verify_lock,"summarize":summarize,"prepare-review":prepare_review,"export-prompts":export_prompts}[action]()

if __name__ == "__main__":
    main()
