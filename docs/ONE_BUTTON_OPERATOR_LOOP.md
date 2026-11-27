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

### AEL Academy: field-oriented control and PMSM current control (Chapter 08)

**Why now:** Chapters 05–07 now establish motor electromagnetic behavior, its electrical/mechanical/thermal model, and the inverter's realizable voltage vectors and limits. The next dependency is to derive how the controller converts measured phase currents into torque-producing d/q current commands and safely realizes them through PWM.

**Scope:**
- Write a Korean lesson on three-phase current vectors, Clarke and Park transforms, inverse transforms, normalization conventions, and electrical angle.
- Derive PMSM d/q current dynamics and torque production under the chapter 06 convention; distinguish surface PMSM and interior PMSM.
- Explain cascaded current/speed/position loops, PI design intuition, decoupling/feed-forward, saturation, anti-windup, sampling and PWM/ADC synchronization.
- Explain current sensing offsets, scaling, phase order, polarity, reconstruction, ADC timing, noise and calibration evidence.
- Connect voltage-vector saturation to SVPWM limits from chapter 07; explain field weakening only as a bounded future topic.
- Include dimensional checks, worked examples, exercises with complete solutions, firmware state-flow and verification templates.
- Keep actual AEL-002 motor parameters, current limits, PWM rate, ADC timing and controller gains TBD until verified source/sample data exist.
- Review chapters 00–07 and the lesson checklist; update index, project memory and operator queue.
- Preserve existing CI definitions and **NO STACK / NO POWER**.

**Acceptance criteria:** transforms are invertible under the stated normalization; electrical/mechanical angle and pole pairs are consistent; torque equations match chapter 06; control-loop signs and saturation are explicit; no hardware rating or unverified firmware setting is invented.

**Blockers:** theory and offline calculations can proceed. Actual motor/encoder/current-sensor parameters, board revision and timing remain unverified. Hardware remains **NO STACK / NO POWER**.


### AEL-002: sample-specific no-power inspection and requirements intake (gated)
Resume only when physical inspection and motor/supply/load data can be supplied. Never infer sample jumper states from schematic drawings.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)
Resume after the AEL-002 evaluation-stack interface is established, unless a dependency makes it higher priority.
