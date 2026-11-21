"""Deterministic package checks. No network, model calls or source writes."""
from pathlib import Path
import hashlib
import json
import re

class PackageError(ValueError):
    pass

def bundle_root():
    return Path(__file__).resolve().parent.parent

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def within(parent, path):
    parent, path = Path(parent).resolve(), Path(path).resolve()
    if path == parent or not path.is_relative_to(parent):
        raise PackageError("Path must remain below the intended root: " + str(path))
    return path

def skill_files(root):
    root = Path(root)
    if not root.is_dir() or root.is_symlink():
        raise PackageError("Missing or linked skill directory")
    result = []
    for p in sorted(root.rglob("*")):
        if p.is_symlink() or (hasattr(p,"is_junction") and p.is_junction()):
            raise PackageError("Linked skill paths are not supported: " + str(p))
        within(root,p)
        if p.is_file():
            result.append(p)
    return result

def check_skill(root):
    root = Path(root)
    files = skill_files(root)
    main = root/"SKILL.md"
    if not main.is_file():
        raise PackageError("SKILL.md is missing")
    text = main.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise PackageError("Invalid SKILL.md frontmatter")
    header, body = text[4:].split("\n---\n",1)
    name = re.search(r"^name:\s*([a-z0-9-]+)\s*$",header,re.M)
    description = re.search(r"^description:\s*(.+)$",header,re.M)
    if not name or name.group(1)!="prompt-fixer" or not description:
        raise PackageError("Expected prompt-fixer name and one-line description")
    if len(description.group(1))>1026:
        raise PackageError("Skill description exceeds 1024 characters")
    links = 0
    for p in files:
        content = p.read_text(encoding="utf-8")
        if p.suffix != ".md":
            continue
        for target in re.findall(r"\]\(([^)]+)\)",content):
            if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*://",target) or target.startswith("#"):
                continue
            relative = target.split("#",1)[0]
            resolved = within(root,p.parent/relative)
            if not resolved.is_file():
                raise PackageError("Broken skill link: " + str(p) + " -> " + target)
            links += 1
    return {"name":name.group(1),"files":len(files),"links_checked":links,"body_words":len(body.split())}

def runtime_inventory(root):
    root = Path(root)
    skill = root/"skills/prompt-fixer"
    check_skill(skill)
    files = skill_files(skill)
    for tree in (root/"prompt_fixer",root/"tests"):
        if tree.is_dir():
            files.extend(p for p in sorted(tree.rglob("*.py")) if p.is_file())
    files.extend(p for p in (root/"qa/evalkit.py",root/"qa/downstream_checks.py") if p.is_file())
    inventory = {p.relative_to(root).as_posix():hashlib.sha256(p.read_text(encoding="utf-8").replace("\r\n","\n").encode("utf-8")).hexdigest() for p in files}
    for name in ("plugin.json",".codex-plugin/plugin.json"):
        p=root/name
        if p.is_file():
            canonical=json.dumps(read_json(p),ensure_ascii=False,sort_keys=True,separators=(",",":"))
            inventory[name]=hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return dict(sorted(inventory.items()))

def runtime_fingerprint(root):
    inventory = runtime_inventory(root)
    raw = json.dumps(inventory,sort_keys=True,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def verify_current(root):
    root = Path(root)
    path = root/"qa/release-evidence.json"
    if not path.is_file():
        raise PackageError("No current release evidence. Historical replay is not a current-source test.")
    evidence = read_json(path)
    actual = runtime_inventory(root)
    expected = evidence.get("runtime_files",{})
    changed = sorted(k for k in set(actual)|set(expected) if actual.get(k)!=expected.get(k))
    version = read_json(root/"plugin.json")["version"]
    if changed or evidence.get("version")!=version or evidence.get("runtime_sha256")!=runtime_fingerprint(root):
        raise PackageError("Current runtime differs from evaluated source; run affected forward checks. Changed: " + ", ".join(changed or ["version/fingerprint"]))
    cases = evidence.get("behavior_cases",[])
    if not cases or any(x.get("passed") is not True or not x.get("evidence") for x in cases):
        raise PackageError("Missing or failed recorded behavioral checks")
    for case in cases:
        artifact = within(root,root/case["evidence"])
        if not artifact.is_file() or hashlib.sha256(artifact.read_bytes()).hexdigest()!=case.get("evidence_sha256"):
            raise PackageError("Behavior evidence is missing or changed: " + case["evidence"])
    return {"version":version,"runtime_sha256":evidence["runtime_sha256"],"status":"recorded checks match current source","behavior_cases":len(cases),"limit":"Verifies provenance; does not rerun a model or establish production performance."}

def check_package(root, require_evidence=False):
    root = Path(root)
    manifest = read_json(root/"plugin.json")
    compat = read_json(root/".codex-plugin/plugin.json")
    for key in ("name","version","description","author"):
        if manifest.get(key)!=compat.get(key):
            raise PackageError("Manifest mismatch: " + key)
    if compat.get("interface")!=manifest.get("extensions",{}).get("com.openai",{}).get("interface"):
        raise PackageError("Manifest interface mismatch")
    result = check_skill(root/"skills/prompt-fixer")
    qa_manifest = root/"qa/qa-manifest.json"
    if qa_manifest.is_file():
        for entry in read_json(qa_manifest)["files"]:
            p = within(root/"qa",root/"qa"/entry["path"])
            if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=entry["sha256"]:
                raise PackageError("QA artifact changed: " + entry["path"])
    result.update(version=manifest["version"],runtime_sha256=runtime_fingerprint(root),check_scope="static package integrity")
    if require_evidence:
        result["release_evidence"] = verify_current(root)
    return result
