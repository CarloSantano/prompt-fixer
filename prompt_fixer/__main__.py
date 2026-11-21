"""Run from the source root: python -m prompt_fixer --help."""
import argparse
import json
import sys

from .install import doctor, install, uninstall
from .measure import compare_ledger
from .validation import PackageError, bundle_root, check_package, read_json, verify_current

def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline Prompt Fixer setup and evidence helpers. No model or API calls.")
    sub = parser.add_subparsers(dest="command",required=True)
    check = sub.add_parser("check",help="Check package integrity; optionally require current recorded evidence")
    check.add_argument("--evidence",action="store_true")
    sub.add_parser("verify-current",help="Reject stale source versus recorded forward-check evidence")
    for command in ("install","doctor","uninstall"):
        p = sub.add_parser(command)
        p.add_argument("--host",choices=["codex","claude"],required=True)
        p.add_argument("--project",required=True,help="An existing explicit project directory; no global installation")
        if command=="install":
            p.add_argument("--replace",action="store_true",help="Update an unchanged managed install, retaining a backup")
            p.add_argument("--dry-run",action="store_true")
    measure = sub.add_parser("measure",help="Compare reported whole-pipeline usage; never estimates tokens from words")
    measure.add_argument("ledger")
    args = parser.parse_args(argv)
    try:
        root = bundle_root()
        if args.command=="check":
            result = check_package(root,args.evidence)
        elif args.command=="verify-current":
            result = verify_current(root)
        elif args.command=="install":
            result = install(root,args.project,args.host,args.replace,args.dry_run)
        elif args.command=="doctor":
            result = doctor(args.project,args.host)
        elif args.command=="uninstall":
            result = uninstall(args.project,args.host)
        else:
            result = compare_ledger(read_json(args.ledger))
        print(json.dumps(result,ensure_ascii=True,indent=2))
        return 0
    except (PackageError,OSError,ValueError,KeyError,TypeError) as error:
        print(json.dumps({"error":str(error)},ensure_ascii=True),file=sys.stderr)
        return 1

if __name__=="__main__":
    sys.exit(main())
