# Prompt Fixer QA

This is a public source distribution. Owner-machine paths in two historical
records were redacted; original hashes and the public-file mapping are described
in [public distribution notes](../docs/PUBLIC_DISTRIBUTION.md). The evaluated
skill instructions and current V01-V03 responses are unchanged. Public metadata
changes are not new model-run or performance evidence.

## Current release versus historical evidence

`release-evidence.json` binds the current runtime, helper code, tests and
manifests to recorded fresh-context behavior checks. From the source root:

```sh
python -B -m unittest discover -s tests -v
python -B -m prompt_fixer verify-current
python -B -m prompt_fixer check --evidence
python -B qa/evalkit.py validate
```

`validate` exits nonzero on a missing/stale source record, altered evidence,
package integrity failure or recorded historical regression. It does not call a
model. An instruction edit requires fresh affected behavior checks; recomputing
hashes alone is not a new behavioral test. `validate-history` intentionally
checks only old recorded responses and can never certify a new runtime.

The current mutable-subject test covers a blind spot in the original 15 ingest
checks. A controlled alias mutant passes all 15 old checks but fails the new
check; the real historical implementations pass it. These are test-coverage
findings, not evidence that the real implementations previously mutated data.

Run results default to a fresh OS-temp directory. An explicit `--output-dir`
must be outside the source bundle. Original outputs and raw judgments remain
untouched. The original 0.5 evaluator sources are in `evidence/v0.5/`.

Original R04 batch responses fail deterministic exact matching: ASCII `-`
replaced U+2013. Separate escaped replays match the exact original request and
both pass. The raw judge's original `requirements_pass` is retained but does not
override deterministic literal comparison. Report original and replay results
separately; do not call every original case an exact-output pass.

## Historical 0.4.2 versus 0.5.0 study

Owner/developer resources, not ordinary runtime instructions. No model/API calls
are made by these scripts. They replay deterministic checks and summarize already
captured responses. Ordinary use does not load this directory.

From this directory, with Python 3.12 or compatible:

    python evalkit.py verify-lock
    python evalkit.py summarize
    python downstream_checks.py baseline ingest
    python downstream_checks.py candidate ingest
    python downstream_checks.py baseline approval
    python downstream_checks.py candidate approval

The original prompts and rubric were frozen before candidate generation. Four
fresh contexts produced six separate-request responses each. An independent fresh
context reviewed randomized A/B pairs without source version labels. All agents
used the inherited model; this is not human validation or a representative field
trial. Two literal-edit replays used escaped JSON after a terminal display changed
an en dash to a hyphen in both original batches. Keep those original results.

The two downstream code components were generated independently from the exact
rewritten prompts, then checked against the original contracts. They are QA
fixtures, not production templates or working Gmail integrations. Source files
were inspected before execution. No real messages were sent.

The snapshot JSON preserves source text and hashes without adding duplicate
installable skill folders. Only machine-specific resource pointers in bundled
response metadata were canonicalized; response bodies were not edited. Word and
character measurements are proxies, not billed tokens, credits or hidden reasoning.

For new behavioral runs, give a fresh agent only the selected workflow and user
request, never rubric.json, the A/B key, expected results or earlier answers. Use
ASCII-escaped JSON transport when exact Unicode or identifiers matter. Keep new
production observations private and anonymize before reusing them across users.
