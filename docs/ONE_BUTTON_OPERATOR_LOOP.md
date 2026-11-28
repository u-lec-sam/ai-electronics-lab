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

### AEL Academy: MCU real-time control infrastructure (Chapter 10)

**Why now:** Chapter 08 defines FOC/PWM/ADC control needs and Chapter 09 defines the sensor timing/data contract. The next dependency is to understand MCU timers, QEP/capture, interrupts, DMA, ADC/PWM triggering, scheduling, latency and worst-case execution time before selecting actual peripheral routes or target-specific code.

**Scope:**
- Write a Korean lesson on MCU clock trees, timer counters/prescalers, capture/compare, QEP/quadrature decoding, input synchronization and digital filtering.
- Explain interrupt architecture, priorities, nesting, latency, jitter, critical sections, atomic snapshots and race conditions.
- Cover DMA data movement, buffer ownership, double buffering and cache/coherency caveats where relevant.
- Derive PWM time-base and ADC trigger relationships, center/edge-aligned sampling windows, conversion/acquisition time, sensor timestamps and control-loop latency.
- Explain deterministic scheduling, ISR/task partitioning, WCET measurement/analysis, deadline misses, watchdog and overrun response.
- Include timing diagrams in text/ASCII, equations, dimensional checks, worked hypothetical calculations, exercises with complete solutions, firmware state flow and verification templates.
- Connect encoder/Hall/Resolver timestamps from Chapter 09 to Park angle prediction and current-loop sampling from Chapter 08.
- Keep actual AEL-002 MCU selection/configuration, clocks, peripheral pin mux, QEP/eCAP/ePWM/ADC routes, interrupt priorities, DMA channels, PWM/ADC rates, ISR budgets and WCET **TBD** until exact board/SDK evidence is verified.
- Review Academy 00–09 and the quality checklist; update index, project memory and next task.
- Preserve existing CI definitions and **NO STACK / NO POWER**.

**Acceptance criteria:** timing equations are dimensionally correct; event-to-sample latency is explicit; ADC aperture and PWM switching noise are not conflated; ISR concurrency and fault response are testable; no MCU pin or peripheral assignment is invented.

**Blockers:** theory, timing budgets and software tests can proceed. Exact board revision, MCU SDK version, pin mux and peripheral allocation remain unverified. Hardware remains **NO STACK / NO POWER**.

### AEL-002: sample-specific no-power inspection and requirements intake (gated)
Resume only when physical inspection and motor/supply/load data can be supplied. Never infer sample jumper states from schematic drawings.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)
Resume after the AEL-002 evaluation-stack interface is established, unless a dependency makes it higher priority.
