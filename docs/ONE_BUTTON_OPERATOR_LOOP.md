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

### AEL Academy: magnetism, electromagnetic induction and motor fundamentals

**Why now:** Chapters 00–04 establish the engineering process, electrical quantities, mathematics, RC/RL transients, AC phasors, balanced three-phase relationships and power. The next dependency is the physical bridge from three-phase current to rotating magnetic fields, induced voltage and motor torque, before deriving PMSM/BLDC models and FOC.

**Scope:**
- Write a Korean lesson on magnetic field, flux, flux density, permeability, Ampere's law intuition, Faraday's law and Lenz's law.
- Derive motional/transformer induced voltage at an introductory level; explain back-EMF, torque production and energy conversion with sign conventions.
- Explain pole pairs, mechanical/electrical angle, electrical frequency vs rotor speed, and why three-phase winding placement plus phase sequence produces a rotating field.
- Introduce DC motor, induction motor, synchronous motor, PMSM and BLDC distinctions without prematurely selecting a motor.
- Add worked calculations, units, exercises/solutions, datasheet interpretation and a safe simulation-only exercise.
- Review chapters 00–04 against the lesson checklist; record assumptions and source links.
- Update Academy index, project memory and operator queue; preserve CI definitions and all hardware safety gates.

**Acceptance criteria:** Faraday/Lenz signs and units are explicit; mechanical/electrical angle conversion uses pole-pair count; motor examples are dimensionally checked; educational values are not presented as AEL-002 ratings; no wiring or energization instructions are implied.

**Blockers:** none for theory/documentation. Actual motor model, pole pairs, winding R/L, back-EMF/torque constants, encoder, supply capability, load/inertia, duty and cooling remain TBD. Hardware remains **NO STACK / NO POWER** pending sample-specific physical inspection and an approved procedure.

### AEL-002: sample-specific no-power inspection and requirements intake (gated)
Resume only when physical inspection and motor/supply/load data can be supplied. Never infer sample jumper states from schematic drawings.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)
Resume after the AEL-002 evaluation-stack interface is established, unless a dependency makes it higher priority.
