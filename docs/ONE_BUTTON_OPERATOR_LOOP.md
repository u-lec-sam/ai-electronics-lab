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

### AEL Academy: power semiconductor and gate-driver architecture (Chapter 14)

**Why now:** Chapters 07–13 cover DC link, inverter operation, FOC, sensing, real-time firmware, communications and integration verification. The next dependency is understanding the switching devices, gate-drive requirements and hardware protection chain before any power-stage BOM or schematic can be responsibly selected.

**Scope:**
- Compare silicon MOSFET, GaN and IGBT operating regions and device-selection parameters without selecting an AEL part.
- Explain gate charge, Miller plateau, dv/dt, di/dt, common-source inductance, gate loop and power loop.
- Derive deadtime, shoot-through and body-diode/reverse-conduction trade-offs.
- Compare bootstrap, isolated and charge-pump gate supplies; UVLO, negative gate bias and Miller clamp where applicable.
- Explain overcurrent, short-circuit/desaturation, comparator, gate-driver fault, hardware latch and independent inhibit paths.
- Build worst-case loss/thermal and fault propagation calculations with clearly hypothetical values.
- Cross-check every critical claim against applicable standards, exact manufacturer datasheets/reference manuals and independent professional sources.
- Keep actual AEL-002 device/BOM, gate driver, DC bus, current, gate resistor, deadtime, protection thresholds and timing TBD.

**Acceptance criteria:** source register complete for critical claims; assumptions and operating conditions explicit; calculations independently checked; fault chain and verification matrix defined; no device ratings or board settings inferred.

**Blockers:** exact motor, DC supply, board revision, candidate semiconductor/driver and cooling remain unverified. Generic education and requirements templates can proceed.

### AEL-002: sample-specific no-power inspection and requirements intake (gated)
Resume only when physical inspection and motor/supply/load data can be supplied. Never infer sample jumper states from schematic drawings.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)
Resume after AEL-002 integration interfaces are established, unless a dependency makes it higher priority.
