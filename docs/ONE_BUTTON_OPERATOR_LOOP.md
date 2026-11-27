# One-Button Operator Loop

**Goal:** the user should not need to plan tasks or manage repository files. The user-facing interaction for routine work is one button: **Run next task**.

## Contract for every assistant turn in this project

1. **Self-plan first.** Read the live repository and current project state. Select the highest-value safe next task using dependencies, blockers, evidence, and project goals.
2. **Do useful work now.** A button click starts a work cycle; it is not a substitute for doing work in the current turn.
3. **Keep one active next task.** Update this file when the priority changes. The task must be concrete, scoped, and include rationale, acceptance criteria, and blockers.
4. **Make the next action clickable.** End substantive progress reports with one prominent ChatGPT action button labeled **Run next task**. It submits a continuation instruction as a new user turn.
5. **No false persistence claims.** The button is a conversation action, not a background daemon. It only runs after the user presses it. Refresh GitHub on every activation.
6. **No repeated setup.** Do not ask the user to paste repo URLs, file contents, shell commands, or test output when connected tools can retrieve them.
7. **One blocker question at most.** Ask only when a physical action, essential missing requirement, or consequential safety/cost/security decision prevents safe progress.
8. **Report briefly.** State changes, verified results, unverified items, and the next task.

## Autonomy boundaries

- User approval is standing preference for routine, reversible repository work, but does not grant new platform permissions.
- Do not access my local device or the user's local computer, filesystem, browser profile, or private accounts beyond explicitly connected tools.
- Do not incur costs, publish sensitive information, expose credentials, change account permissions, or make consequential physical/electrical safety decisions without appropriate authorization and safeguards.
- Never claim background execution. GitHub Actions runs only configured deterministic workflows.

## Active next task

### AEL Academy: expand the foundations course and establish a lesson-quality gate

**Why now:** the user has requested a self-contained Korean course that starts at zero and enables independent end-to-end project execution. The Academy index, teaching specification, 00장 safety/development method, and 01장 electrical foundations have been added. The next highest-value step is to build the mathematical/physical bridge needed for capacitors, inductors, AC, power electronics and motor models.

**Scope:**
- Write the next lesson on mathematical tools for engineering (units/dimensions, scientific notation, algebra, graphs, trigonometry/phasors, vectors, derivatives/integrals and differential-equation intuition) at two levels: intuitive and formal.
- Add RC/RL transient response with derivations, time constants, energy storage, worked examples, simulation exercises and answer keys.
- Add a repeatable per-lesson review checklist: correctness, units, derivation, source quality, project mapping, exercises, safety and explicit unknowns.
- Link the Academy from the repository root and update project memory; keep the curriculum synchronized with actual AEL-002 design gates.
- Run existing CI unchanged and record the exact tested commit/run. Do not claim the whole textbook is complete.

**Acceptance criteria:** lessons are self-contained, use SI units and defined symbols, show intermediate calculations and assumptions, include worked examples/exercises/solutions, and distinguish theory from AEL-002 decisions. Root README links the Academy. Existing tests/CI definitions remain unchanged and CI passes.

**Blockers:** no physical action is needed for the educational work. AEL-002 hardware remains **NO STACK / NO POWER** until the actual sample revisions, pin-1 orientation, EVM J5, LaunchPad JP1/JP2A/JP2B and grounding are verified; motor/supply/load/cooling requirements remain open.

### AEL-002: sample-specific no-power inspection and requirements intake (gated)
Resume only when physical inspection and motor/supply/load data can be supplied. Never infer sample jumper states from schematic drawings.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)
Resume after the AEL-002 evaluation-stack interface is established, unless a dependency makes it higher priority.
