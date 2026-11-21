"""Project-scoped skill installation with guarded updates and preserved backups."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import tempfile

from .validation import PackageError, check_skill, read_json, skill_files, within

HOSTS = {"codex":Path(".agents/skills"),"claude":Path(".claude/skills")}
RECEIPT = ".prompt-fixer-install.json"

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def project_paths(project, host):
    if host not in HOSTS:
        raise PackageError("Unknown host")
    project = Path(project).expanduser().resolve()
    if not project.is_dir():
        raise PackageError("Project directory must already exist")
    parent = within(project,project/HOSTS[host])
    target = within(project,parent/"prompt-fixer")
    private = within(project,project/".prompt-fixer")
    for candidate in (project/HOSTS[host],project/HOSTS[host]/"prompt-fixer",project/".prompt-fixer"):
        if candidate.is_symlink() or (hasattr(candidate,"is_junction") and candidate.is_junction()):
            raise PackageError("Refusing a linked installation path")
    return project,parent,target,private

def owned_unchanged(target):
    receipt_path = target/RECEIPT
    if not receipt_path.is_file():
        raise PackageError("Existing skill is not managed by this installer; nothing was overwritten")
    receipt = read_json(receipt_path)
    if receipt.get("tool")!="prompt-fixer" or receipt.get("receipt_version")!=1:
        raise PackageError("Unknown installation receipt")
    expected = receipt.get("files",{})
    actual = {p.relative_to(target).as_posix():digest(p) for p in skill_files(target) if p.relative_to(target).as_posix()!=RECEIPT}
    if actual != expected:
        raise PackageError("Installed files were edited or new files added; preserve/reconcile them before updating or removing")
    return receipt

def backup_path(project, private, host):
    backups = within(project,private/"backups")
    backups.mkdir(parents=True,exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    target = within(project,backups/(host+"-"+stamp))
    if target.exists():
        raise PackageError("Backup destination already exists")
    return target

def install(root, project, host, replace=False, dry_run=False):
    root = Path(root).resolve()
    source = root/"skills/prompt-fixer"
    check_skill(source)
    version = read_json(root/"plugin.json")["version"]
    project,parent,target,private = project_paths(project,host)
    source_files = {p.relative_to(source).as_posix():digest(p) for p in skill_files(source)}
    prior = None
    if target.exists():
        prior = owned_unchanged(target)
        if prior["files"]==source_files and prior.get("version")==version:
            return {"status":"already_installed","host":host,"target":str(target),"version":version}
        if not replace:
            raise PackageError("A managed older/different version exists; inspect it, then use --replace for a backed-up update")
    plan = {"status":"dry_run" if dry_run else "installed","host":host,"target":str(target),"version":version,"files":len(source_files),"scope":"project only; no host permissions or global settings changed","activation":"File layout verified; host discovery must be checked in the target host."}
    if dry_run:
        return plan
    staging_parent = within(project,private/"staging")
    staging_parent.mkdir(parents=True,exist_ok=True)
    parent.mkdir(parents=True,exist_ok=True)
    moved_backup = None
    with tempfile.TemporaryDirectory(prefix="install-",dir=staging_parent) as temporary:
        stage = within(project,Path(temporary)/"prompt-fixer")
        shutil.copytree(source,stage)
        receipt = {"tool":"prompt-fixer","receipt_version":1,"version":version,"host":host,"files":source_files}
        (stage/RECEIPT).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        check_skill(stage)
        # Recheck ownership immediately before moving an existing directory.
        if target.exists():
            owned_unchanged(target)
            moved_backup = backup_path(project,private,host)
            within(project,target); within(project,moved_backup)
            target.replace(moved_backup)
        try:
            within(project,stage); within(project,target)
            stage.replace(target)
        except BaseException:
            if moved_backup is not None and not target.exists():
                within(project,moved_backup); within(project,target)
                moved_backup.replace(target)
            raise
    if moved_backup:
        plan["backup"] = str(moved_backup)
    return plan

def uninstall(project, host):
    project,parent,target,private = project_paths(project,host)
    if not target.exists():
        return {"status":"not_installed","host":host}
    owned_unchanged(target)
    backup = backup_path(project,private,host)
    within(project,target); within(project,backup)
    target.replace(backup)
    return {"status":"removed_from_host_location","host":host,"backup":str(backup),"data_deleted":False}

def doctor(project, host):
    project,parent,target,private = project_paths(project,host)
    if not target.exists():
        return {"status":"not_installed","host":host,"target":str(target)}
    check = check_skill(target)
    receipt = owned_unchanged(target)
    return {"status":"managed_files_match_receipt","host":host,"version":receipt["version"],"target":str(target),"skill":check,"limit":"This checks files, not model behavior or automatic host discovery."}
