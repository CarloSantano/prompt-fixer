# Contributing

Keep the core small. A change should reduce a concrete failure, ambiguity or
rework without changing user intent or expanding authority. Do not add a role,
questionnaire, framework, mandatory tool call or new dependency without evidence
that the actual task needs it.

1. Describe the failing request and expected user-visible behavior.
2. Change the smallest relevant instructions or helper code.
3. Run the offline commands in the README. Test changed boundaries, not copies
   of implementation logic. Preserve frozen raw responses and judgments.
4. After freezing the changed runtime, obtain fresh behavior responses in new
   contexts. Give executors the actual skill and user request, not expected
   answers or a rubric. Review their outputs separately.
5. Record source hashes, requests, responses, evaluation and limits in a new
   release evidence artifact. Updating hashes without executing affected checks
   is not validation. Refresh the QA manifest last, then run the full gate.

Historical replay checks older recorded responses. Current-source verification
checks correspondence to recorded release evidence. Neither command executes a
new model. A paid or external benchmark needs a separately authorized budget.
Real token claims must count the entire successful pipeline, including fixer
and repair overhead, against a matched direct-execution baseline.

Project installs are reversible and project-scoped. Preserve user edits and
backups. Do not add global settings, network calls, telemetry or auto-updates to
the installer. Do not publish test prompts containing private data.

The public repository runs the offline checks on Windows and Linux. A green CI
run does not establish host discovery or real AI task success. Release tooling
builds a portable ZIP; test its intended host separately before making broader
compatibility claims. Do not claim portability from a file-layout test alone.
