# Public distribution and evidence

This repository is the public source distribution of Prompt Fixer 0.7.0.
The original private account plugin remains separately owned and private.
Publishing this repository does not change another account's plugin access.

All 11 skill instruction/support files are byte-identical to the evaluated
0.7.0 source. Executable helpers and tests are unchanged. Public manifest
metadata removes the owner's private email and adds this repository and MIT
license. Distribution documentation, release tooling and CI are separate from
the assistant's runtime instructions.

Two historical evidence records contained owner-machine paths. Their public
copies replace that prefix with `<TEST_WORKSPACE>`; task text, results and the
created artifact content are retained. Original private files were not edited.
[Distribution provenance](../qa/distribution-provenance.json) maps before/public
hashes and records identical instruction-file hashes. Some archived historical
hashes intentionally identify the original pre-redaction records, not the
publicly edited copies. The current public QA manifest binds the distributed
files. Current V01–V03 requests and responses are unchanged.

The current release record binds public metadata to the same evaluated
instruction files. This metadata-only adaptation is not a new model run or
evidence of improved performance. Historical and targeted checks retain their
original limitations.

Build the portable ZIP with `python -B tools/build_release.py`. It contains
source, instructions and evidence; it excludes Git history, caches and local
credentials. Runtime use does not require the QA directory or Python helpers.
