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

### AEL Academy: embedded firmware architecture and robust C foundations (Chapter 11)

**Why now:** Chapters 08–10 define the control equations, sensor feedback contract and real-time scheduling. The next safe dependency is to define maintainable, testable firmware layers and robust data/numeric/concurrency contracts before target-specific peripheral code.

**Scope:**
- Teach embedded C integer widths, signedness, overflow, fixed-point/Q formats, floating-point limits, scaling and saturation.
- Explain memory map, stack/heap/static storage, linker sections, startup/reset, const/volatile/atomic and compiler optimization.
- Define HAL/LL/driver/middleware/control/application boundaries and hardware abstraction interfaces.
- Cover state machines, event handling, fault latching, parameter validation/CRC/versioning and safe defaults.
- Include coding patterns, interface contracts, unit-test seams, static-analysis checklist, code-review template and fully solved exercises.
- Connect ADC/encoder timestamps, DMA ownership, ISR/task boundaries and FOC cycle timing from Chapters 08–10.
- Keep AEL-002 target-specific compiler, ABI, memory map, peripheral drivers, build flags and numeric formats TBD until exact MCU/SDK/toolchain evidence is verified.
- Update Academy index, project memory and operator queue; preserve CI and **NO STACK / NO POWER**.

**Acceptance criteria:** C examples avoid undefined behavior; arithmetic has explicit range/overflow analysis; module interfaces are testable without hardware; fault paths and parameter validation are deterministic; no target-specific setting is invented.

**Blockers:** General architecture and portable C can proceed. Exact MCU/SDK/compiler/build system and motor numeric ranges remain unverified. Hardware remains **NO STACK / NO POWER**.

### AEL-002: sample-specific no-power inspection and requirements intake (gated)
Resume only when physical inspection and motor/supply/load data can be supplied. Never infer sample jumper states from schematic drawings.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)
Resume after the AEL-002 evaluation-stack interface is established, unless a dependency makes it higher priority.
