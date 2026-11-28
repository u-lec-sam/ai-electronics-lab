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

### AEL Academy: embedded communications and diagnostic services (Chapter 12)

**Why now:** Chapter 11 establishes portable C, module boundaries, state/fault policy, parameter validation and test seams. The next dependency is to define robust external command/telemetry and service interfaces without allowing communication code to bypass the control and safety state machines.

**Scope:**
- Explain UART framing, RS-485 electrical/network concepts, half-duplex direction control, termination/bias and physical-layer versus protocol boundaries.
- Explain CAN/CAN-FD frames, identifiers/arbitration, bit timing concepts, bus load, error counters, error-passive/bus-off and recovery.
- Define serialization, endian, version/length/CRC, sequence counters, timestamps, timeout and stale-command rejection.
- Separate command, telemetry, diagnostics, parameter transfer and firmware-update responsibilities.
- Define safe command semantics: explicit arm, command limits, freshness, acknowledgement, fault latch and controlled re-arm.
- Include communication state machines, fault-injection cases, bus-load calculations, fully solved exercises and verification templates.
- Connect Chapter 08–11 FOC timing, sensor validity, DMA ownership, parameter schema and fault records.
- Keep actual AEL-002 transceiver, connector, pin mux, baud/bit rate, CAN identifier map, network topology, isolation, SDK and protocol profile TBD until board/BOM/SDK evidence is verified.
- Update Academy index, project memory and operator queue; preserve CI and **NO STACK / NO POWER**.

**Acceptance criteria:** physical layer is not confused with protocol; framing is unambiguous; corrupted/stale/replayed/out-of-range commands are rejected; bus-off and timeout have deterministic state transitions; communications cannot independently clear a latched safety fault; all actual AEL-002 wiring/rates remain TBD without evidence.

**Blockers:** Generic protocol architecture can proceed. Exact board transceiver, isolation, connector/pinout, network peer and product protocol requirements remain unverified. Hardware remains **NO STACK / NO POWER**.

### AEL-002: sample-specific no-power inspection and requirements intake (gated)
Resume only when physical inspection and motor/supply/load data can be supplied. Never infer sample jumper states from schematic drawings.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)
Resume after the AEL-002 evaluation-stack interface is established, unless a dependency makes it higher priority.
