# Recursive Improvement Protocol (RIP)

**Purpose:** build a bounded, evidence-driven recursive-improvement system by improving both engineering outputs and the agent scaffold that produces them. The repository versions memory, procedures, tools, tests, and workflows. It does not modify the hosted ChatGPT model weights.

## Operating loop

READ → BASELINE → DIAGNOSE → PROPOSE → IMPLEMENT → TEST → REVIEW → INTEGRATE → RECORD → META-REVIEW

1. **READ:** refresh GitHub at the start of each substantive lab session. Read canonical operating docs, curated memory, active-project files, relevant decisions/episodes/evals, recent commits, and latest CI evidence.
2. **BASELINE:** state what is known and verified. Separate facts, assumptions, unknowns, failures, and skipped checks.
3. **DIAGNOSE:** identify a concrete limitation or repeated failure. Link it to an issue, test, log, source, or design artifact where possible.
4. **PROPOSE:** define a small, reversible change, expected measurable benefit, acceptance criteria, and possible regressions.
5. **IMPLEMENT:** make the candidate on a feature branch for changes to core procedures, memory policy, tools, CI, evaluators, or safety rules. Keep product changes similarly traceable.
6. **TEST:** run deterministic checks, relevant domain checks, and existing regression tests. Preserve the baseline and use held-out cases when feasible.
7. **REVIEW:** inspect the actual diff and evidence. Check that the change did not weaken tests, hide errors, change labels, exploit evaluator gaps, expose secrets, or reduce safety.
8. **INTEGRATE:** merge only when acceptance criteria are met. If evidence is incomplete or checks fail, do not claim success; preserve the candidate and report the blocker.
9. **RECORD:** append an experiment record: hypothesis, baseline, change, commit, exact tests, outcomes, regressions, decision, and follow-up.
10. **META-REVIEW:** evaluate whether the loop itself was efficient and reliable. Improve retrieval, test coverage, tool choice, or reporting only when a specific failure or measurable opportunity supports it.

## What may improve

- Product requirements, schematics, PCB, firmware, BOM, and manufacturing artifacts
- Agent role definitions, planning and review procedures
- Repository retrieval and memory indexing
- Reusable prompts, templates, checklists, and platform profiles
- Deterministic validation scripts, CI workflows, and tool orchestration
- Test fixtures, regression cases, task benchmarks, and evaluation coverage
- Experiment selection and candidate comparison methods

## Memory model

- **Working:** current conversation and active task state; temporary.
- **Episodic:** append-only session and experiment logs, including failures.
- **Semantic:** curated engineering facts, architecture, and verified decisions.
- **Procedural:** reusable checklists, prompts, scripts, and skills.
- **Evaluation:** regression tests, expected outcomes, coverage, and known evaluator limitations.

Do not indiscriminately dump complete histories into every prompt. Retrieve the smallest relevant evidence set. Attach sources, revisions, and commit references to durable claims.

## One-button interaction contract

For every substantive response in this project:
1. Read the live repository and choose the next safe, high-value task without asking the user to plan it.
2. Execute all useful supported work in the current turn; do not merely describe a plan.
3. Keep exactly one prioritized next task in `docs/ONE_BUTTON_OPERATOR_LOOP.md`, including scope, rationale, acceptance criteria, and blockers.
4. End the response with one ChatGPT action button labeled **Run next task**. It must submit the fixed continuation instruction specified in that document.
5. On button activation, refresh GitHub again before doing anything. Never assume chat memory is current.
6. Do not ask the user to repeat repository URLs, paste files, run shell commands, or inspect CI when connected tools can do it.
7. Ask only one essential blocker question when a physical action, missing requirement, or consequential safety/cost/security decision prevents progress.
8. The button is user-triggered conversation continuation, not background execution or a persistent agent daemon. Never claim work happened between presses.

## Evaluation and anti-gaming rules

- A change is an improvement only against a stated baseline and acceptance criteria.
- Do not delete or weaken a failing test merely to improve a score.
- Do not change evaluation criteria after observing a candidate result without a separate rationale and review.
- Keep regression tests when adding new tests; preserve known failures as cases.
- Report skipped checks as skipped, never passed.
- Use more than one evidence type for important changes: automated tests, static analysis, independent review, datasheet checks, simulation, and prototype measurements as appropriate.
- A green CI badge does not prove electrical correctness, manufacturability, or physical safety.
- Preserve rejected candidates and explain why they were rejected.

## What must not be self-approved

- Removing or weakening a failing test to make a score improve
- Changing safety rules or evaluation criteria solely to pass a candidate
- Marking unverified hardware or firmware as verified
- Overwriting historical experiment results
- Committing credentials, private data, or unlicensed vendor material
- Making consequential electrical, safety, thermal, or manufacturing decisions without appropriate review

## User-effort and access policy

- Minimize repetitive user questions. Perform supported research, repository reads/writes, documentation, code generation, and deterministic tests directly.
- The user does not need to operate a local development environment for the default workflow.
- Do not access the user's local device, filesystem, or accounts outside the explicitly connected tools.
- Ask only for missing requirements, physical measurements/actions, or consequential decisions that cannot be safely inferred or executed.
- User approval does not override platform permissions, tool limitations, legal obligations, or engineering safety.
- Never claim that an action was completed unless the tool or test result confirms it.

## Autonomy levels

- **L0 — Manual:** user directs every change.
- **L1 — Assisted iteration:** ChatGPT reads, diagnoses, proposes, tests, and records supported changes.
- **L2 — Gated evolution:** candidate branches and CI are used; consequential merges are gated by review.
- **L3 — Bounded automation:** pre-approved low-risk changes may be merged automatically under fixed tests and rollback controls.
- **L4 — Open-ended self-modification:** the agent changes its own code and improvement mechanism with broad autonomy.

Current target: L2 for the repository workflow. L3 requires proven rollback, evaluator robustness, least-privilege permissions, and a bounded change allowlist. L4 is not claimed or enabled. This ChatGPT + GitHub workflow is not an always-on autonomous process and does not self-train the foundation model.

## Experiment record template

Store meaningful experiments under `docs/experiments/`:
- Date, branch, baseline commit, and candidate commit
- Problem and evidence
- Baseline and hypothesis
- Proposed change and expected measurable benefit
- Tests and exact results
- Regression/side-effect review
- Decision: accepted, rejected, or needs more evidence
- Next experiment

## Per-session checklist

- [ ] Refresh repository identity, default branch, and latest commit
- [ ] Read canonical operating documents and curated memory
- [ ] Read relevant active-project files and historical evidence
- [ ] Inspect latest applicable CI evidence
- [ ] State facts, assumptions, unknowns, failures, and skipped checks
- [ ] Define measurable acceptance criteria before changing the system
- [ ] Make a small, reversible, traceable change
- [ ] Run old and new tests; inspect the diff
- [ ] Record exact outcomes and update curated state
- [ ] Meta-review the workflow itself for evidence-backed improvements
