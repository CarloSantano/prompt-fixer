# Prompt Fixer

[![Checks](https://github.com/CarloSantano/prompt-fixer/actions/workflows/ci.yml/badge.svg)](https://github.com/CarloSantano/prompt-fixer/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Rough idea → visible prompt improvement → execute when you ask.**

An instruction layer for your existing AI assistant. For builders who want to
ship useful products, services and automations without learning prompt syntax.
No extra server, API key or model call from this package. Your AI host's access,
tools, permissions and usage costs still apply.

[Lietuviškai: pradžia draugui](docs/QUICKSTART_LT.md) ·
[Download the release](https://github.com/CarloSantano/prompt-fixer/releases/latest) ·
[Evidence and limitations](qa/README.md)

## What you see

1. **Your request** — your actual words; long inputs use a marked excerpt.
2. **Improved prompt** — separately copyable instructions in your language.
3. **What changed** — one short account of concrete changes.

A short status identifies rewriting versus execution. Ask for "only the final
prompt" to skip the comparison. Specific user instructions remain in control.

| Request | Behavior |
| --- | --- |
| Invoke with "build me a client-request app; choose the technology" | Show an improved prompt and stop before building. |
| "Improve and execute now: add a CSV export to this project" | Inspect the available project and perform authorized work. |
| "Does Prompt Fixer need a backend?" | Answer the question directly. |
| Invoke without a task | Ask for the task. |

Ordinary implicit use preserves the original mode. Automatic selection is
host-dependent. This skill is not an interceptor or cross-chat memory service.

## Quick install: Codex or Claude Code

Clone, then install into **one existing project**. Python 3.12+ is needed only
for the optional offline helper; no pip install is required.

```sh
git clone https://github.com/CarloSantano/prompt-fixer.git
cd prompt-fixer
python -B -m prompt_fixer install --host codex --project "/absolute/path/to/your-project" --dry-run
python -B -m prompt_fixer install --host codex --project "/absolute/path/to/your-project"
python -B -m prompt_fixer doctor --host codex --project "/absolute/path/to/your-project"
```

Replace the example path with your real project. On Windows use a quoted path
such as `"C:\Users\you\Projects\my-app"`; `py -3.12` may replace `python` if
that is how Python is installed. For Claude Code replace `--host codex` with
`--host claude` in each command.

| Host | Installed project folder | Invocation after discovery |
| --- | --- | --- |
| Codex | `.agents/skills/prompt-fixer/` | `$prompt-fixer` plus your request |
| Claude Code | `.claude/skills/prompt-fixer/` | `/prompt-fixer` plus your request |

Open or reload your project in the host and confirm `prompt-fixer` is in its
skills list. Try:

```text
$prompt-fixer build me an internal sales tool; choose the technical approach.
```

Use `/prompt-fixer` in Claude Code. Success means a visible comparison appears
without building the underlying app. Say "execute that prompt" to proceed.

The installer refuses unmanaged or user-edited installs and changes no global
settings. `doctor` verifies files and receipt, not discovery by a running host.

**Without Python:** copy the entire `skills/prompt-fixer/` folder, including its
references, into the host's project folder above. Manual copying creates no
installer receipt; manage later updates yourself.

## ChatGPT Work Mode

If your account supports creating custom plugins, download the portable ZIP
from [Releases](https://github.com/CarloSantano/prompt-fixer/releases/latest),
attach it in Work Mode with Plugin Creator available, and ask it to create a
**private personal plugin from the attached archive**. Select your own Prompt
Fixer plugin and mention it with your request.

This depends on your account's features. An ordinary chat does not automatically
install a repository. The author's private plugin grants no access to another
account. This is a portable source distribution, not a marketplace listing.

## Update or remove

Run `git pull --ff-only` in this source checkout, then rerun installation with
`--replace`. An unchanged managed install is backed up in the target project's
`.prompt-fixer/backups/` before replacement.

```sh
python -B -m prompt_fixer install --host codex --project "/absolute/path/to/your-project" --replace
python -B -m prompt_fixer uninstall --host codex --project "/absolute/path/to/your-project"
```

Removal moves unchanged managed files to a recoverable backup. Reconcile user
edits first; the helper refuses to overwrite or remove them. No auto-update or
global configuration is added.

## Offline checks

```sh
python -B -m unittest discover -s tests -v
python -B -m prompt_fixer check --evidence
python -B qa/evalkit.py validate
python -B qa/downstream_checks.py candidate ingest
python -B qa/downstream_checks.py candidate approval
python -B tools/build_release.py
```

These commands make no API/model calls. Run outputs stay outside the source
bundle. CI checks Windows and Linux. Historical response replay is separate from
correspondence to current recorded evidence; neither executes a new AI model.
Instruction or helper-code changes invalidate current evidence.

Evidence includes a small same-model study and targeted fresh-context checks.
It does **not** establish human validation, universal activation, production
integrations, billed-token savings or improved revenue.

To compare actual caller-supplied host/API usage for the whole path:

```sh
python -B -m prompt_fixer measure examples/usage-ledger.json
```

Count fixer, execution and repair steps. The empty template reports unknown
usage; missing counts are never zero. Successful outcomes, matched conditions
and the same execution model are required. Cache/reasoning counts are subsets,
not extra totals. The helper cannot capture telemetry, verify outcomes or detect
omitted steps independently. Never publish private task data in a usage ledger.

## Design

Resolve intent, preserve constraints and selectively load references for roles,
questions, architecture, methods and completion. Distinguish assumptions from
requirements; ask questions that change a meaningful decision. Personal work
needs no business interview. Roles identify useful responsibilities, not
fictional experience. Approvals retain the exact target/recipient and reviewed
content/version. Prompt text alone does not enforce production security.

Skill locations follow the [Codex documentation](https://learn.chatgpt.com/docs/build-skills)
and [Claude Code documentation](https://code.claude.com/docs/en/skills), checked
2026-11-21. Verify actual discovery in your own session.

See [contributing](CONTRIBUTING.md), [changes](CHANGELOG.md),
[provenance](NOTICE.md), [public-distribution notes](docs/PUBLIC_DISTRIBUTION.md)
and the [MIT license](LICENSE).
