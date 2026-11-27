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

### AEL Academy: AC circuits, phasors, RMS and three-phase fundamentals

**Why now:** Academy chapters 00–03 now cover development/safety, electrical basics, engineering mathematics, and RC/RL transients. The next dependency is AC waveform analysis, phase, impedance and three-phase power, which are needed before explaining inverter switching and motor phase quantities.

**Scope:**
- Write a Korean lesson on periodic signals, frequency/period/angular frequency, phase, peak/peak-to-peak/RMS, average power, and the limits of sinusoidal RMS shortcuts.
- Derive sinusoidal R/L/C impedance and phase relationships with a clear sign convention and phasor explanation.
- Explain three-phase 120-electrical-degree relationships, line/phase voltage and current for balanced Y/Delta systems, active/reactive/apparent power and power factor; distinguish balanced sinusoidal assumptions from PWM/nonlinear drive input.
- Add worked examples, diagrams or calculation tables, exercises and full solutions; connect to AEL-002's DC-fed three-phase inverter without expanding its first prototype to mains AC input.
- Review chapters 00–03 with the Academy checklist; fix errors and preserve source traceability.
- Update Academy index, project memory and CI evidence. Keep CI definitions and safety hold unchanged.

**Acceptance criteria:** all equations define symbols/units and assumptions; line/phase relationships are derived, not memorized; examples are independently checkable; power-factor claims distinguish displacement factor and true power factor when harmonics exist; no mains wiring instructions or power-up authorization are implied.

**Blockers:** none for theory/documentation. Hardware remains **NO STACK / NO POWER** pending sample-specific revision, pin-1, EVM J5, LaunchPad JP1/JP2A/JP2B and grounding checks; motor/supply/load/regeneration/cooling requirements remain open.

### AEL-002: sample-specific no-power inspection and requirements intake (gated)
Resume only when physical inspection and motor/supply/load data can be supplied. Never infer sample jumper states from schematic drawings.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)
Resume after the AEL-002 evaluation-stack interface is established, unless a dependency makes it higher priority.
