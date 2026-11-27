# Architecture

## Roles
- **ChatGPT:** requirements analysis, research, design proposals, schematic/PCB source authoring, firmware authoring, review, and supported GitHub file updates.
- **GitHub:** source of truth, persistent project memory, decision history, experiment archive, and version history.
- **GitHub Actions:** repeatable, deterministic validation and build automation.
- **KiCad:** native schematic and PCB engineering environment.
- **KiCanvas:** optional browser viewing; it does not replace full KiCad editing or electrical verification.

## Recursive improvement target

Improve two coupled systems:
1. **Product system:** requirements, schematics, PCB, firmware, BOM, manufacturing outputs, and test evidence.
2. **Agent scaffold:** repository retrieval, memory organization, procedures, reusable templates, tool orchestration, CI, evaluation suites, and experiment selection.

The hosted foundation model is not modified by GitHub commits. The scaffold is versioned and can be empirically improved. Any future model fine-tuning is a separate project with its own data, compute, licensing, and evaluation requirements.

## Session-start read protocol

For every substantive AI Electronics Lab work session, ChatGPT must read the current GitHub state before proposing or changing project files:
1. Confirm repository identity, default branch, and latest commit.
2. Read `README.md`, this file, `docs/ENGINEERING_RULES.md`, and `docs/RECURSIVE_IMPROVEMENT.md`.
3. Read `memory/README.md` and `memory/PROJECT_STATE.md`.
4. Read the active project's README, design brief, interface plan, BOM, and relevant source files.
5. Inspect recent commits and the latest applicable CI status when the connector exposes them.
6. Retrieve only relevant historical decisions, episodes, and evaluation cases.
7. Summarize verified state, assumptions, unknowns, failed checks, and next safe action.
8. Never assume a previous chat summary is newer than GitHub. GitHub is the project source of truth.

If GitHub cannot be read, explicitly say that repository state was not refreshed and do not claim to have checked it.

## One-button operation

The user should not have to plan tasks or operate a local development environment. Follow [the One-Button Operator Loop](ONE_BUTTON_OPERATOR_LOOP.md): self-select one next task, do supported work now, persist the next task in GitHub, and provide one conversation button to resume. The button is user-triggered and is not a persistent background process.

## Workflow

1. Define requirements and constraints.
2. Select exact parts and verify manufacturer documentation.
3. Create schematic and review symbol pins/net connectivity.
4. Run ERC, then create PCB and run DRC.
5. Build firmware with a pinned, licensed toolchain.
6. Review power, thermal, signal integrity, clearances, and manufacturing constraints.
7. Release Gerbers, drill files, BOM, assembly outputs, and firmware only after review.

## Improvement workflow

1. Establish a baseline from the live repository and CI.
2. Identify a specific limitation supported by evidence.
3. Propose a small, reversible candidate change with an expected measurable benefit.
4. Implement it on a feature branch for changes to core procedures, CI, evaluation, or safety rules.
5. Run existing tests plus new regression tests; distinguish passed, failed, and skipped checks.
6. Inspect the diff for test weakening, scope creep, security issues, and hidden regressions.
7. Merge only after evidence meets the acceptance criteria; preserve rejected candidates and rationale.
8. Record results and update curated project state.

The agent scaffold itself is in scope for this loop. Changes to its own retrieval, memory, planning, tools, evaluators, and CI must be evaluated by tests that are not silently changed to favor the candidate.

## Autonomy and safety boundary

- Prefer direct execution of low-risk, reversible repository work over asking the user for repetitive confirmation.
- Never access the user's local computer or files unless a separate explicit, supported workflow is requested.
- Never expose, request, or commit secrets. Public repository contents are public.
- Keep consequential hardware, electrical safety, manufacturing, spending, account-permission, and data-publication decisions gated.
- Do not claim background execution or always-on autonomy. ChatGPT acts when invoked; GitHub Actions runs only configured deterministic workflows.
- Do not equate CI success with electrical correctness or model self-improvement.

## MCU profiles

Keep platform-specific startup code, linker scripts, SDK/HAL acquisition, compiler versions, and CI commands isolated under `platforms/` or each project's `firmware/`.
