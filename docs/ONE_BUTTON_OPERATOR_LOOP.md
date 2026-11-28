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

### AEL Academy: encoder, rotor-angle feedback and sensor diagnostics (Chapter 09)

**Why now:** Chapter 08 defines the FOC transform and control loops, but their correctness depends on a trustworthy rotor electrical angle. The next dependency is to understand encoder/Hall/resolver feedback, angle conventions, alignment, interpolation, startup and sensor fault detection before binding any algorithm to MCU pins.

**Scope:**
- Write a Korean lesson on incremental encoder A/B/Z, absolute encoders, Hall sensors and resolver fundamentals; distinguish position, speed and electrical angle.
- Derive mechanical-to-electrical angle conversion, pole-pair mapping, direction, zero offset, wraparound and multi-turn handling.
- Explain encoder edge counting, x1/x2/x4 decoding, speed estimation, timestamping, interpolation and quantization/noise limits.
- Explain Hall sector resolution and commutation/FOC angle limitations; explain resolver signal chain and demodulation at conceptual level.
- Cover startup alignment and index acquisition risks, sensor plausibility, missing edges, illegal transitions, CRC/status/timeout and redundant cross-checks.
- Include dimensional checks, worked examples, exercises with complete solutions, firmware state-flow and verification templates.
- Keep actual AEL-002 sensor type/model, resolution, interface, pin mapping, electrical offset, speed range and timing TBD until sample and source evidence exist.
- Review Academy 00–08 and the quality checklist; update index, project memory and next task.
- Preserve existing CI definitions and **NO STACK / NO POWER**.

**Acceptance criteria:** angle conventions are internally consistent; direction and pole-pair conversion are testable; quantization/timing limits are quantified; startup and fault behavior are explicit; no actual sensor or pin assignment is invented.

**Blockers:** theory and offline calculations can proceed. Actual encoder/sensor sample, board revision, pin map and timing remain unverified. Hardware remains **NO STACK / NO POWER**.

### AEL-002: sample-specific no-power inspection and requirements intake (gated)
Resume only when physical inspection and motor/supply/load data can be supplied. Never infer sample jumper states from schematic drawings.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)
Resume after the AEL-002 evaluation-stack interface is established, unless a dependency makes it higher priority.
