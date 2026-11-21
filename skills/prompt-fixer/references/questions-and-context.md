# Context and question selection

## Decision test

Before asking, identify the gap, two plausible answers, and the different next action each would cause. If the actions are the same, do not ask yet.

Choose the shortest reliable path:
- Read when the answer is in an accessible current source.
- Ask when the answer belongs to the user's intent, preferences, or authority.
- Research or test when it concerns technical feasibility.
- Show a representative sample when verbal preferences are too vague.
- Make a reversible assumption for a minor implementation choice.

Do not substitute lengthy questionnaires for inspecting the project. Missing tools or credentials are environment gaps; a more elaborate prompt does not create them.

## Natural interaction

When the user says "noriu viską vienoje vietoje" and no project record exists, ask for the latest concrete incident that motivated the request. Do not start with databases or UI frameworks.

When the problem is known, describe actual alternatives and the trade-off. Example: "Užklausa gali būti užregistruota ir atsakymas parengtas tau peržiūrėti, arba atsakymas siunčiamas automatiškai. Kuri eiga numatyta?" Ask only if existing authorization and sources do not resolve it.

When visual quality is unclear, inspect supplied references. If none exist and discovery is part of the task, select a few relevant examples and explain specific properties. Verify images visually rather than from HTML alone.

When "best" is unspecified, determine which objective changes the choice. Prefer the current task's constraints; do not silently inherit a budget or stack from unrelated past work.

## Stop conditions

Proceed when you can define the requested deliverable, important boundaries, meaningful acceptance, and required available inputs sufficiently for the next authorized step.

Do not ask every possible edge case. Prioritize the expensive-to-reverse decision. If several rounds produce no clearer goal, identify the exact unresolved decision and propose a concrete sample or small experiment rather than continuing abstract questions.

If the user explicitly delegates a choice, decide within that delegation. Existing consent persists. Material spending, external action, and production boundaries still apply.

## Task-local brief

Keep this as a compact working artifact, not a mandatory user form:

- Outcome and beneficiary.
- Primary responsibilities.
- Current inspected sources and actual access.
- Requested deliverable and quality bar.
- Acceptance checks.
- Material boundaries, decisions, and reversible assumptions.
- First executable step and remaining blocker, if any.

Populate fields only from evidence or explicit decisions; label estimates. Omit unhelpful fields for small work. Keep the original request available to catch lost requirements. Do not expose private reasoning.

