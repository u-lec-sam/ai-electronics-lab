# One-Button Operator Loop

**Goal:** the user should not need to plan, remember, copy commands, or manage repository files. The user-facing interaction for routine work is one button: **Run next task**.

## Contract for every assistant turn in this project

1. **Self-plan first.** Read the live repository and current project state. Select the highest-value safe next task using dependencies, blockers, evidence, and project goals. Do not ask the user what to do when a safe next step can be chosen.
2. **Do useful work now.** A button click starts a work cycle; it is not a substitute for doing work in the current turn. Complete all safe, supported work that fits the current turn.
3. **Keep one active next task.** Update this file when the priority changes. The task must be a concrete verb-led action with scope, rationale, acceptance criteria, and dependencies. Avoid presenting a long to-do menu to the user.
4. **Make the next action clickable.** End substantive progress reports with one prominent ChatGPT action button labeled **Run next task**. The button submits this fixed instruction as a new user turn: `Continue AI Electronics Lab autonomously. First read the latest GitHub repository state and operating protocol, inspect current CI and the active next task, then execute the highest-priority safe task. Update GitHub memory and the next-task queue with verified results. Do not access my local device. Ask only if a physical action, missing essential requirement, or consequential safety/cost/security decision is unavoidable.`
5. **No false persistence claims.** The button is a conversation action, not a background daemon. It only runs after the user presses it. ChatGPT must still refresh GitHub on every activation; never rely on chat memory alone.
6. **No repeated setup.** Do not ask the user to paste repo URLs, file contents, shell commands, or test output when connected tools can retrieve them.
7. **One blocker question at most.** If work is blocked by an essential unknown or a real-world action, ask only the single most important question. Otherwise continue with safe independent tasks.
8. **Report briefly.** State what changed, what was verified, what remains unverified, and the next task. Avoid long plans unless requested.

## Autonomy boundaries

- User approval is standing preference for routine, reversible repository work, but does not grant new platform permissions.
- Do not access the user's local computer, filesystem, browser profile, or private accounts beyond explicitly connected tools.
- Do not incur costs, publish sensitive information, expose credentials, change account permissions, or make consequential physical/electrical safety decisions without appropriate explicit authorization and safeguards.
- A button click cannot authorize unsafe actions or bypass policy.
- Never claim work continued between conversations. GitHub Actions may run only the deterministic workflows actually configured.

## Active next task

### AEL-001: verify MCU package pins and establish power-tree proposal

**Why now:** the recursive memory and CI scaffold is in place. The active hardware project remains a preliminary brief; exact LQFP48 pin allocation and power design are prerequisites to trustworthy KiCad capture.

**Scope:**
- Retrieve current official STM32G0B1xE datasheet/reference manual and package pinout evidence.
- Confirm STM32G0B1CET6 exact package and pin availability, power pins, decoupling requirements, reset/boot/debug pins, and candidate alternate functions.
- Draft a source-linked pin-allocation table and a power-tree proposal with explicit assumptions and unresolved requirements.
- Do not create fabrication claims or guess pins/footprints.

**Acceptance criteria:**
- Each assigned MCU signal maps to an exact datasheet pin and supported alternate function.
- Power pins, grounds, decoupling, reset, boot, and SWD are accounted for from official documentation.
- Conflicts and unverified details are clearly marked.
- BOM and interface plan remain consistent.
- Results are committed to GitHub and tested where applicable.

**Dependencies / blockers:** input voltage/current and board load budget are not yet specified. Use conservative explicitly marked provisional assumptions; do not finalize regulator selection or thermal claims without a budget.
