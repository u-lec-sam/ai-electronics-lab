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

### AEL Academy: system integration and verification architecture (Chapter 13)

**Why now:** Chapters 08–12 define FOC, sensor feedback, real-time scheduling, robust C, communications and diagnostic services. The next safe dependency is an end-to-end integration contract that proves timing, data validity, state transitions and fault response are testable without assuming target hardware.

**Scope:**
- Derive end-to-end timing/latency budgets from ADC/PWM sampling through FOC, sensor timestamp, communication ingress/egress and telemetry.
- Define interface contracts and traceability from requirements to host tests, SIL, HIL and eventual hardware tests.
- Define deterministic fault-injection, scheduler overload, communication loss, sensor invalidity, parameter corruption and fault-latch race tests.
- Specify evidence levels and release gates; distinguish host CI, target build, simulation, HIL and physical verification.
- Keep all actual AEL-002 MCU/SDK, bus timing, hardware ratings, wiring and safety settings TBD until evidence is available.
- Update Academy index, project memory and operator queue; preserve existing CI and **NO STACK / NO POWER**.

**Acceptance criteria:** every critical interface has units/range/validity/timestamp/ownership/deadline; safety faults have traceable detection-to-safe-state paths; test cases identify evidence level and pass criteria; no host/CI result is represented as hardware validation.

**Blockers:** generic integration/test architecture can proceed. Actual target/compiler, motor/load, board revision, transceiver/network and physical stop characteristics remain unverified.

### AEL-002: sample-specific no-power inspection and requirements intake (gated)
Resume only when physical inspection and motor/supply/load data can be supplied. Never infer sample jumper states from schematic drawings.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)
Resume after AEL-002 integration interfaces are established, unless a dependency makes it higher priority.
