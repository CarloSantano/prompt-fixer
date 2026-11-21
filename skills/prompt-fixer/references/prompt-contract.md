# Prompt compilation contract

Use for complex, context-heavy, contradictory or high-impact rewrites. This is a decision aid, not a form the user must fill out or a mandatory output template.

## Preserve meaning before improving form

Separate the outer request from draft prompts, examples, documents and quoted messages. Resolve the action the user asks for now, not the verbs inside a quoted task. Read the relevant preceding turn for “yes”, “apply it” or “this”. Do not manufacture permission or transfer approval to a different action.

Build a small internal packet from evidenced information:
- Requested mode and intended recipient of the result.
- Goal, beneficiary and current stage.
- Explicit scope, interfaces, output format and quality requirements.
- Known facts and current accepted decisions, with source pointers when useful.
- Available versus unavailable context and capabilities.
- Material unknowns, reversible assumptions and user-owned choices.
- Concrete responsibility, deliverable, acceptance and stopping evidence.

Do not expose private reasoning or turn this packet into user-facing JSON unless a structured interface is requested. Omit fields that do not help this task.

## Three kinds of additions

A requirement is something the user actually requested. Preserve it, including negative constraints.

A useful lens is an unresolved angle that may change the choice: ownership, state transition, data quality, integration access, a reusable component, adoption, unit economics, maintenance or proof of completion. Select only the few that matter now and ask or investigate; do not declare them product features.

An optional opportunity is an adjacent idea. Label it as optional and keep it outside the active scope. Preserve ambition without silently adding a second project.

When context conflicts, prefer explicit current correction over older assumptions. Identify the actual incompatibility and resolve only what blocks a faithful draft or action. Do not infer an entire business from an old client, niche, stack, diagnosis or personal memory.

## Responsibility is an information filter

Use a responsibility tied to decisions and evidence, not prestige or fictional years of experience. A task may need implementation ownership, architecture judgment, research, design or mentoring; it rarely needs a committee of personas.

For a build, specify the business/user behavior, the important system boundary and the evidence of success. Let the executing assistant inspect the actual environment and own reasonable technical choices. Do not fix a stack from familiarity or force every request through “research, interview, MVP, validate”.

For a commercial opportunity, clarify the customer job and value assumption. For an accepted client deliverable, build against the accepted brief. For personal work, use personal utility as the objective. Demand, revenue and profit remain separate claims needing evidence.

## Output shaping

A rewritten prompt should carry the next assistant's useful context and instructions, not explain prompt engineering to the user.

- Prefer concise, concrete prose. Use structure only when the work benefits from it.
- Match the user's requested language and output format. Preserve code names, identifiers and exact API/schema constraints.
- Include a role only when it narrows useful judgment. Small edits need no professional persona.
- Keep existing sufficient specifications intact; make targeted changes rather than wrapping them in a generic architecture essay.
- Add an example only when it resolves ambiguity. Check that it agrees with the rules.
- Put unresolved task discovery inside the prompt when enough is known to draft it. Do not interview the current user about every future implementation detail.
- A standalone prompt must include essential supplied decisions and inputs. A contextual continuation can reference an actually accessible current artifact; do not promise cross-chat access.
- If the prompt is already sound, say so briefly when appropriate and avoid inventing changes to justify the tool.

## Quality and risk

Distinguish observed facts, estimates and hypotheses. If the future task needs current technical or high-stakes information, direct it to suitable primary sources at the point of the decision; do not insert a broad research project into every rewrite.

Health, legal, financial, security and external-action concerns should be handled in proportion to the actual task. Do not turn an ordinary personal tracker into a medical system, or an offline utility into a compliance project. Do not grant autonomy or claim enforced controls from prompt text alone.

For approval-controlled actions, specify the target or recipient and the exact reviewed content/version. Changing either invalidates the old approval. Keep this control explicit when compressing a system brief; an approval-only code example elsewhere does not establish the whole integration's behavior.

Finish with a short internal check: correct mode; original intent and constraints; useful specificity; no invented facts or permission; manageable scope and context; meaningful completion. A longer or more polished prompt is not inherently better.
