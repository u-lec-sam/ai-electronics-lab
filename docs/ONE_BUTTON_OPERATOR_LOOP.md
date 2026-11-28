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

### AEL Academy: speed/position outer loops and motion-reference architecture (Chapter 17)

**Why now:** Chapter 16 establishes the current loop as the inner torque-producing actuator. The next dependency is to define speed/position loops, trajectory shaping, current/torque limits, cascade bandwidth separation and command arbitration without assuming unknown motor/load parameters.

**Scope:**
- Derive mechanical speed and position plant models using inertia, friction, torque constant and load disturbance.
- Design outer PI/PID structures with current/torque command output and explicit units.
- Explain cascade bandwidth separation, sample-rate ratios, latency and outer-loop anti-windup.
- Define trajectory generators, acceleration/jerk limits, command ramps, feed-forward and setpoint continuity.
- Integrate torque/current envelope, voltage feasibility, thermal/duty constraints, regeneration and DC-bus limits.
- Define local/remote command arbitration, mode transitions, enable/disable and fault response.
- Include fully solved virtual calculations, host/SIL tests, parameter sweeps and fault-injection templates.
- Keep actual motor inertia, friction, torque constant, load profile, current/torque envelope, encoder limits and loop periods TBD until evidence.

**Acceptance criteria:** traceable loop equations and units; explicit rate/latency and saturation semantics; robust corner analysis; tests for step/ramp/reversal, load disturbance, limit arbitration, stale command, mode transition and fault; source register updated; CI passes on exact final SHA.

**Blockers:** actual motor and load data, torque/current limits, thermal envelope, encoder range, command interface, PWM/current-loop period and approved motion profile remain unverified.

### AEL-002: sample-specific no-power inspection and requirements intake (gated)
Resume only when physical inspection and motor/supply/load data can be supplied. Never infer sample jumper states from schematic drawings.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)
Resume after AEL-002 integration interfaces are established, unless a dependency makes it higher priority.
