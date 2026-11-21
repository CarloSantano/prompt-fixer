"""Build a checked portable archive outside this source directory. No API calls."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from prompt_fixer.validation import check_package

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",help="ZIP outside the repository; defaults to its parent directory")
    args=parser.parse_args()
    result=check_package(ROOT,require_evidence=True)
    output=Path(args.output).expanduser().resolve() if args.output else ROOT.parent/("prompt-fixer-v"+result["version"]+".zip")
    if output==ROOT or output.is_relative_to(ROOT):
        parser.error("Write the release ZIP outside the source directory")
    allowed_dirs={"skills","prompt_fixer","tests","qa","docs","tools","examples",".codex-plugin",".github"}
    allowed_files={"plugin.json","README.md","LICENSE","CONTRIBUTING.md","CHANGELOG.md","NOTICE.md",".gitignore",".gitattributes"}
    selected=[]
    for p in sorted(ROOT.rglob("*")):
        rel=p.relative_to(ROOT)
        if rel.parts[0] not in allowed_dirs and rel.as_posix() not in allowed_files:
            continue
        if any(x in {"__pycache__",".git",".venv","node_modules"} for x in rel.parts) or p.suffix==".pyc":
            continue
        if p.is_symlink() or (hasattr(p,"is_junction") and p.is_junction()):
            raise ValueError("Linked paths are not release content")
        if p.is_file():selected.append(p)
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED) as archive:
        for p in selected:
            info=zipfile.ZipInfo(p.relative_to(ROOT).as_posix(),date_time=(2026,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            archive.writestr(info,p.read_bytes())
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist())=={p.relative_to(ROOT).as_posix() for p in selected}
    digest=hashlib.sha256(output.read_bytes()).hexdigest()
    checksum=output.with_suffix(output.suffix+".sha256")
    checksum.write_text(digest+"  "+output.name+"\n",encoding="ascii",newline="\n")
    print(json.dumps({"version":result["version"],"files":len(selected),"archive":str(output),"sha256":digest,"checksum":str(checksum)}))

if __name__=="__main__":
    main()
