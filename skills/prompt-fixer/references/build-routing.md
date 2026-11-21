# Architecture and execution routing

Use before substantial coding, agent design or business-system implementation, and again when a material assumption fails. This is a focused architectural decision, not another mandatory planning phase. Reuse settled decisions and current project guidance.

## Own the technical route

Translate the user's business intent into observable system behavior and a delivery target: who will use it, which real workflow it supports, existing assets, required integration, quality bar and what usable delivery means. Keep explicit ambitions and required scope. A thin prototype, scaffold, workflow export or isolated demo cannot replace a requested operational system.

Check the actual repository, environment, available tools, access and applicable specialist workflows before significant implementation. Distinguish missing information, missing capability, missing authorization and an architectural uncertainty. Inspect current primary docs and maintained source for decision-relevant versions and major component choices. Avoid broad repeated browsing and tool collection.

Assess the few genuinely competitive routes: reuse/extend an existing system, combine maintained components, or build a justified custom part. Include more advanced orchestration when it improves the actual outcome. Retaining today's spreadsheet or choosing the newest framework both require fit; neither wins by default.

Choose and recommend the best appropriate route using:
- coverage of the agreed user journey and quality requirements;
- fit with real data, integrations and operating environment;
- speed to a usable result, including avoidable rework;
- reliability, observability, access controls and recovery relevant to this process;
- total implementation, inference, operating and maintenance cost;
- adoption, ownership and the ability to change or exit later.

The goal is useful performance and delivery per total resource, not minimum token count or maximum architectural complexity. Use stronger available models, tools and environments where their benefit justifies their total cost within existing authority. Do not silently lower quality to save tokens. An advanced option may be the most efficient once repeated use, failure and maintenance are included.

Own reversible technical choices and explain consequential trade-offs briefly. Do not ask the user to choose frameworks they cannot meaningfully assess. For a material user-owned choice, explain its practical consequence and recommend a route. Existing approvals persist; new spending or consequential production changes still need suitable authority.

## Make the recommendation actionable

For a major choice, provide a compact architecture decision in natural language: recommended route and why, important reused assets, one meaningful alternative/trade-off if it exists, riskiest dependency, real completion evidence and next executable action. Show a small diagram only if it clarifies state, dependencies or topology. Then continue authorized implementation; do not stop at an architecture document.

If another available environment or specialist workflow materially improves capability, use it when authorized and accessible. Otherwise identify the exact capability gap, why the better route matters, the required transfer/access and how success will be checked. Continue independent work. Never present a simulated integration as a substitute for the missing access or claim another host is ready without checking.

## Orchestrate resources deliberately

Sequence work around dependencies and the critical user journey. Test the architectural risk early; make the first slice part of the intended system, with an honest prototype/test/live status. Complete the requested scope after that slice. Preserve sound architecture, working assets, actual acceptance checks and necessary production controls; avoid disposable demonstrations when the user requested delivery.

Use deterministic tools for search, transforms, schemas and checks when appropriate. Give each task only relevant sources and current interface contracts. Reuse inspected results and verified examples; avoid rediscovering decisions, copying whole repositories into context or restarting intake. Prefer small reviewable changes and targeted checks to large speculative code generation.

Separate rules, retrieval, AI judgment and dynamic agent planning. Give tool calls clear inputs, outputs, errors and stop conditions. Add durable state, retries, duplicate handling, queueing or approval gates when the actual process requires them. Do not add them as a generic checklist to every task.

Parallel work, subagents, model routing and repeated optimization require a concrete benefit, supported host capabilities and applicable authority. They are optional orchestration mechanisms, not a synonym for an advanced system. Keep bounded task context, output contracts and checks; avoid duplicate research and uncontrolled retries.

Track delivery against the agreed behavior and real evidence. A successful API call is not adoption, and a local test is not deployed production. Explain the few unfamiliar concepts at the decision point so the user can operate and assess the result. Finish when the requested quality and acceptance are met, unless a material unresolved risk remains.
