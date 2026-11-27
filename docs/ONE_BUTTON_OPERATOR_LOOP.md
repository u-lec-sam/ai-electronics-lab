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

### AEL Academy: inverter and DC-link power electronics foundations (Chapter 07)

**Why now:** Chapters 00–06 now establish project safety/process, circuit and mathematical foundations, AC/three-phase power, electromagnetism, and a consistent motor electrical/mechanical/thermal model. The next dependency is to connect the motor model to the 3-phase inverter and DC bus before selecting any power devices.

**Scope:**
- Write a Korean lesson on the DC link, two-level three-phase voltage-source inverter, six-switch bridge, phase vs line-line voltage, switching states, PWM and SVPWM fundamentals.
- Derive modulation and voltage-limit relationships with explicit normalization, DC-bus and phase/line conventions.
- Explain dead time, switching/conduction loss, ripple current, DC-link capacitor stress, thermal paths, regeneration and overvoltage containment at a conceptual/calculation level.
- Include unit-checked worked examples, exercises with full solutions, data-sheet interpretation and a power-stage requirements worksheet.
- Keep actual AEL-002 bus ripple, current, switching frequency, semiconductor, capacitor, braking and thermal ratings TBD until motor/load/supply data and a reviewed architecture exist.
- Review chapters 00–06 and the lesson checklist; update the Academy index, project memory and this operator task.
- Preserve existing CI definitions and all safety gates.

**Acceptance criteria:** all equations state modulation and voltage conventions; phase/line-line quantities are not mixed; DC-link energy and regeneration are dimensionally checked; losses and thermal assumptions are explicit; no component ratings are invented.

**Blockers:** theory work can proceed. Actual motor, load, supply source/sink capability, motion profile and cooling remain unknown. Hardware remains **NO STACK / NO POWER**.


### AEL-002: sample-specific no-power inspection and requirements intake (gated)
Resume only when physical inspection and motor/supply/load data can be supplied. Never infer sample jumper states from schematic drawings.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)
Resume after the AEL-002 evaluation-stack interface is established, unless a dependency makes it higher priority.
