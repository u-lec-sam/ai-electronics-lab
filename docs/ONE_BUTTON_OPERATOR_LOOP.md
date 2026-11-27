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

### AEL Academy: motor electrical model, torque-speed envelope and load requirements

**Why now:** Chapters 00–05 now cover the project process and safety gates, electrical quantities, engineering mathematics, RC/RL transients, AC/three-phase power, magnetism, induction, back-EMF, torque, pole pairs/electrical angle, rotating fields and motor families. The next useful theory-to-requirements step is to translate a *specific candidate motor datasheet and load profile* into a traceable motor/electrical/mechanical model before selecting a power stage or tuning FOC.

**Scope:**
- Write a Korean lesson on the DC-equivalent and PMSM dq electrical models, torque-speed curves, mechanical equation (J\,d\omega/dt=T_e-T_L-B\omega-T_f), inertia reflection and acceleration torque.
- Derive copper loss, mechanical power, efficiency, continuous vs peak torque/current, thermal time constants and duty-cycle constraints.
- Explain Ke/Kt unit conventions and conversions only when waveform, phase/line, RMS/peak and mechanical/electrical speed definitions are known.
- Build a motor datasheet intake template and a requirements worksheet for motor, encoder, load inertia, speed/torque profile, supply/regeneration and cooling.
- Use clearly labeled hypothetical examples only; do not invent an AEL-002 motor model or ratings.
- Review chapters 00–05 against the checklist; add calculations, worked solutions, simulation-only exercises, source links, index and memory updates.
- Preserve existing CI definitions and all physical safety gates.

**Acceptance criteria:** dynamic equations are dimensionally checked; sign conventions are explicit; reflected inertia and torque-speed limits are correctly defined; all continuous/peak and thermal assumptions are explicit; missing candidate motor/load data remain TBD.

**Blockers:** none for theory. Actual motor model, pole pairs, winding parameters, Ke/Kt conventions, encoder, supply capability, load/inertia, motion profile, regeneration sink and cooling remain unprovided. Hardware remains **NO STACK / NO POWER**.

### AEL-002: sample-specific no-power inspection and requirements intake (gated)
Resume only when physical inspection and motor/supply/load data can be supplied. Never infer sample jumper states from schematic drawings.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)
Resume after the AEL-002 evaluation-stack interface is established, unless a dependency makes it higher priority.
