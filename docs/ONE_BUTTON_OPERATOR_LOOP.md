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

### AEL-002: verify F280039C-to-inverter evaluation path and interface contract

**Why now:** official TI documentation specifies BOOSTXL-3PHGANINV as a 12–60 V, 7 A RMS/phase inverter, but its supported LaunchPad list does not include LAUNCHXL-F280039C. Direct pairing is therefore unverified and must not be assumed. The ST P-NUCLEO-IHM03 remains a separate low-voltage reference (7–45 VDC, up to 1.5 A RMS).

**Scope:**
- Resolve the SENS007 Rev A versus SPRUJ30 F280039C header numbering/orientation conflict (EVM J2/J4 pin 40 is PWM/GPIO; LaunchPad J4-40 is GND in the pinout map) before declaring direct stacking safe. Produce a revision-matched, pin-1-oriented physical crosswalk for all six PWM, phase-current/voltage ADC, VDC, /PWM enable and /PCB OT alert signals.
- Resolve TI's product-page versus April 2024 SDK LaunchPad list and the 3.5-A SDK table versus 7-A RMS product-page rating; obtain thermal/test conditions and exact SDK release target files.
- Verify the EVM OCP and TMP302 shutdown path, J6/USB power-source selection, grounding and instrument isolation plan from schematic and non-destructive test evidence.
- Only after document/revision review, prepare a written, current-limited staged bench test procedure; no energization until motor/supply/regeneration/load/cooling requirements and qualified guarded test setup are approved.
- Keep motor, encoder, supply sink capability, load/inertia, duty and cooling as TBD until supported by actual datasheets or user input.

**Acceptance criteria:**
- Every connector signal and electrical limit is mapped to an official board document and revision; connector-numbering/orientation conflicts are resolved or remain a hard no-power hold point.
- Officially supported board combinations are distinguished from custom/unverified pairings.
- Regeneration, hardware inhibit, current limit, thermal stop criteria and guarding are included in the bring-up procedure.
- Existing tests remain unchanged; CI passes; experiment and project state record the evidence.

**Dependencies / blockers:** motor/encoder model, supply current limit and sink capability, reflected inertia/load, motion profile and cooling are unknown. Do not choose power components or authorize energized tests until the board interface and bench limits are verified.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)

Resume STM32G0B1CET6 LQFP48 exact pin/alternate-function verification and provisional power-tree proposal after the AEL-002 evaluation-stack interface is established, unless a dependency makes it higher priority.
