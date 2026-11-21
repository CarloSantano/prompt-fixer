# Work directions: roles, functions, goals and evidence

Use the actual requested job and existing project stage. The examples below are candidate information lenses, not requirements to add to every task. Prefer the real process and practical benefit. Load the appropriate responsibility profile from [roles.md](roles.md) only as needed.

## Core process lens

Reconstruct one real instance: what triggers the work, who acts, which decision is made, which data and systems it touches, what happens next and what useful result reaches whom. Ask the user for what only they know; inspect existing sources for the rest.

Identify the work's current bottleneck before proposing a tool. Distinguish a lack of clarity, demand, process, data, access, implementation and adoption. Choose a useful deliverable for that stage rather than repeating setup or discovery.

## Direction map

| Work direction | Responsibility and function | Goal and useful information lenses | Concrete evidence/output |
| --- | --- | --- | --- |
| OS / CRM / agency operations | Operations process designer; software/automation architect when implementation is needed | Enable the next real business action. Follow lead-to-customer-to-delivery events, owners, statuses, handoffs, source of truth and next actions. Look for dropped work and repeated entry before adding dashboards. | One observed workflow; actual records and state changes; a usable next-action view or working flow. |
| Sales / offers / follow-up | Sales process and offer strategist; delivery judgment for feasibility | Help a specific buyer reach a sensible decision. Inspect buyer/problem/trigger, promised outcome, evidence, qualification, objections, follow-up stage and economics. Choose the current conversion bottleneck. | Real conversation/offer examples, a usable offer or sales action, clear next step; demand remains a hypothesis until tested. |
| Leadgen / prospecting | Customer research and data workflow designer | Find relevant, reachable opportunities and preserve evidence. Inspect ICP fit, purchase signals, source coverage, freshness, identity matching, duplicates and the path to outreach. | Sourced qualified records or a bounded sourcing workflow; permissions and actual channel fit. |
| AI automation / integrations | Automation architect and reliability engineer | Move a real input to a useful authorized output. Inspect trigger/data/decision/action, rules versus AI judgment, tool/API fit, credentials, duplicate processing, exceptions, approvals and maintenance. | A representative input/output path; duplicate/failure behavior where relevant; clear mock/test/live distinction. |
| Agentic AI / agent systems | Agent workflow designer with delivery ownership | Give a bounded task the right context, tools, actions and completion checks. Identify what needs reasoning, what can be deterministic, stopping conditions, tool quality, escalation and observed task success. | A representative task completed with traceable artifacts and bounded actions. Multi-agent work requires a concrete benefit and suitable authority. |
| Product / app / SaaS | Product lead with software architecture judgment | Solve one important user job and reach usable delivery. Inspect user scenario, alternatives, scope, demand, adoption, business model if relevant, feasibility and the critical journey. | A testable product decision, working user journey or meaningful validation. Building does not by itself prove demand. |
| Client service / agency delivery | Service designer and delivery lead | Make an outcome repeatably deliverable. Inspect inputs, scope, client responsibilities, production work, acceptance, handoff, support, cost and margin. | A client-usable deliverable or bounded service package with acceptance and actual access. |
| E-commerce | Commerce operator with automation and unit-economics judgment | Test a viable offer and workable operation. Inspect buyer demand evidence, contribution margin, acquisition assumptions, supplier capability, shipping/returns, support and controllable automation. | Sourced assumptions, a coherent product-to-order flow or authorized pilot; no guaranteed winning product or profit. |
| Website / design / content | Product designer, art director or editor according to the artifact | Make a specific audience understand or act. Inspect information hierarchy, offer/message, actual references, assets, interaction states, accessibility and conversion path. | Current renders or usable content and a checked action path; use the existing website workflow when available. |
| Research / strategy / decisions | Research analyst and decision advisor | Resolve a named choice. Inspect criteria, alternatives, mechanisms, current primary evidence, counterexamples and the uncertainty that would change the recommendation. | A sourced recommendation or comparison; stop once further information is unlikely to change the decision. |
| Learning during real work | Task-appropriate practitioner with mentor responsibility | Help the user make the next decision and complete the task. Explain the unfamiliar concept at the point of use, with one concrete example and consequence. | An understood decision and useful output; deeper theory can remain an optional next topic. |

## Choosing missing dimensions

A useful angle changes what should be searched, built, decided or checked. Prioritize:
1. The hidden step where the real process fails.
2. A missing fact that could reverse the recommendation.
3. An unaddressed dependency or approval needed for actual use.
4. A proven existing component or example that changes the implementation path.
5. An adoption, cost or maintenance issue that could erase the expected benefit.
6. A different framing of the same user goal that better fits the observed problem.

Select a few, explain why and gather evidence. Avoid generic "also consider security, scalability, marketing..." lists without a task-specific consequence. Do not attach all lenses to every question or every turn.

## Focused search direction

Internally specify:
- Decision or behavior to enable.
- Beneficiary and process.
- Current stage and existing assets.
- Important constraints and actual environment.
- Mechanisms or solution families worth comparing.
- Evidence that could confirm or reject the recommendation.

Turn those into targeted source reads or queries. For example, a sales OS needs evidence about actual follow-up ownership and buyer progression before a general catalog of CRM features. A simple follow-up message needs the offer, recipient context and next action; it does not need an OS redesign.

## Example compact fixes

### Rough request: "noriu OS pardavimams, kad AI viską sužiūrėtų"

Possible refinement, with unknowns left open:
"Veik kaip pardavimų procesų analitikas ir automatizacijų architektas. Iš mūsų faktinės užklausos–pasiūlymo–follow-up eigos nustatyk svarbiausią prarandamo darbo vietą ir sukurk sutartą sprendimą, kuriame matomas atsakingas žmogus bei kitas veiksmas. Patikrink vieną realų kelią nuo įvesties iki rezultato."

Potential high-value angles: who owns the next action; what event moves a deal to the next stage; which data already exists. Ask for a concrete recent case if these are not in project sources. Do not assume a full custom CRM is necessary.

### Rough request: "noriu agentinio AI produkto, kurį galėčiau parduoti"

Possible refinement:
"Veik kaip produkto ir paslaugos kūrimo vadovas su AI įgyvendinimo atsakomybe. Padėk pasirinkti konkretų kliento darbą ir parengti parduodamo sprendimo hipotezę, tada patikrink esmines prielaidas ir pristatyk sutartą veikiančią apimtį."

Potential high-value angles: who has the problem now; what evidence justifies autonomy instead of a simpler workflow; what the user must control before the output becomes actionable. Do not invent customer demand, pricing or purchase intent.

### Rough request: "šita užklausų automatizacija stringa"

Possible refinement:
"Veik kaip integracijų diagnostikas. Iš dabartinio įvykio, logų ir duomenų kelio atkurk gedimą, nustatyk lūžtančią ribą, pataisyk ją ir patikrink rezultatą."

Potential high-value angles: repeated-event handling; a failed handoff between systems; a missing permission. Read accessible logs before asking the user to explain them.

