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

### AEL Academy: implementable FOC current-loop design and tuning (Chapter 16)

**Why now:** Chapters 08 and 15 define the FOC transforms and current measurement chain. The next dependency is to turn calibrated, timestamped phase-current samples into a stable, bounded current controller whose voltage command respects the inverter and timing limits.

**Scope:**
- Derive continuous and discrete PMSM d/q current-loop PI controllers and state the plant assumptions.
- Compare forward Euler, backward Euler and Tustin discretization; document coefficient quantization and numeric limits.
- Explain cross-coupling decoupling/feed-forward, back-EMF compensation, and when parameter mismatch makes them harmful.
- Derive voltage-vector and modulation saturation, d/q priority, anti-windup and integrator reset/hold behavior.
- Include sample-to-actuation delay, PWM update point, ADC/ISR latency, current-sensor filter delay and phase margin.
- Work through current-loop bandwidth and stability examples with uncertainty in Rs, Ld/Lq, flux linkage and DC bus.
- Define host/SIL test vectors, parameter sweeps, fault cases and acceptance templates; do not claim target or motor validation.
- Keep actual motor parameters, current limits, PWM/ADC timings and MCU/SDK settings TBD until evidence.

**Acceptance criteria:** fully solved dimensional calculations; explicit discrete-time equations and saturation semantics; tests for sign, step response, noise, delay, parameter mismatch and invalid current samples; claim-level source register updates; CI passes on exact final SHA.

**Blockers:** exact motor datasheet/identified Rs, Ld/Lq, flux linkage, current envelope, PWM frequency, ADC aperture and target control-update schedule remain unverified.

### AEL-002: sample-specific no-power inspection and requirements intake (gated)
Resume only when physical inspection and motor/supply/load data can be supplied. Never infer sample jumper states from schematic drawings.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)
Resume after AEL-002 integration interfaces are established, unless a dependency makes it higher priority.
