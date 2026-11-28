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

### AEL Academy: current sensing and analog front-end for motor control (Chapter 15)

**Why now:** Chapters 08–14 define FOC, sensors, MCU timing, robust firmware, communications, system verification and gate-drive architecture. Accurate and diagnosable current feedback is the next essential link between the inverter power stage and the FOC current loop.

**Scope:**
- Compare low-side single/dual/three-shunt, inline phase sensing, DC-link sensing and isolated current sensing.
- Explain shunt selection, Kelvin routing, pulse power, TCR, tolerance, parasitic inductance and common-mode constraints.
- Compare current-sense amplifier, differential amplifier, isolated amplifier and Hall-based sensor classes.
- Derive gain/offset/bandwidth/noise/anti-alias filter and ADC acquisition settling budgets.
- Integrate ADC aperture, PWM switching noise, sample-window placement, amplifier recovery and Chapter 10 timing.
- Define offset/gain/polarity calibration, phase matching, uncertainty, saturation/invalid status and comparator hardware OCP path.
- Cross-check claims against standards, exact manufacturer datasheets/reference manuals and independent professional sources.
- Keep exact AEL-002 shunt/amplifier/sensor, ADC route, gain, bandwidth, current limit and calibration values TBD.

**Acceptance criteria:** source register contains claim-level cross-checks; calculations include tolerances and uncertainty; measurement interface has unit/range/validity/timestamp; hardware fast-trip path is distinguished from software ADC diagnostics; no target-specific setting is invented.

**Blockers:** exact inverter schematic, shunt placement, MCU/ADC route, current range and board revision remain unverified.

### AEL-002: sample-specific no-power inspection and requirements intake (gated)
Resume only when physical inspection and motor/supply/load data can be supplied. Never infer sample jumper states from schematic drawings.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)
Resume after AEL-002 integration interfaces are established, unless a dependency makes it higher priority.
