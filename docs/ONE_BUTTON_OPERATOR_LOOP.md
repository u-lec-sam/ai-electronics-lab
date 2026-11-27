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

### AEL-002: resolve motor/supply/load requirements and compare control MCU evaluation paths

**Why now:** AEL-002's architecture and benchmark brief is captured, but exact power-stage ratings and MCU selection depend on a real motor, encoder, supply and mechanical load.

**Scope:**
- Compare exact TI C2000 F280039C evaluation hardware and STM32G4 evaluation options using official datasheets, SDK support, availability and toolchain constraints.
- Define the minimum motor/encoder and bench-supply information needed to size the first power stage.
- Build a parameter intake and selection matrix; keep ratings provisional until values are known.
- Inspect vendor reference designs for current sensing, gate drive, bus protection and regenerative-energy handling.
- Do not select power MOSFETs, gate driver, shunts, connectors or thermal limits without a defined electrical envelope.

**Acceptance criteria:**
- Exact candidate orderable MCU/evaluation boards and official source revisions are compared.
- Motor, encoder, supply, load, duty-cycle and cooling inputs are explicitly enumerated.
- The first power-stage envelope is derived only from sourced/confirmed values.
- Results and remaining blockers are committed to GitHub and CI-tested.

**Dependencies / blockers:** motor make/model and encoder, supply voltage/current/sink capability, mechanical load/inertia, desired speed/torque/duty, cooling, communications and budget are not yet specified. Continue with platform comparison and a requirements template without inventing these values.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)

Resume STM32G0B1CET6 LQFP48 exact pin/alternate-function verification and provisional power-tree proposal after AEL-002's initial platform/requirements pass, unless a dependency makes it higher priority.
