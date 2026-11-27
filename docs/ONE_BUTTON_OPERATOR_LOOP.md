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

### AEL-002: sample-specific no-power inspection and SDK route closure

**Why now:** the original rendered SENS007 Rev A schematic now resolves the parsed 11/12/13/18 ambiguity: EVM J2/J4-11 is nEn_uC; nEnable is the internal U12 output to U4 OE pin22; DIR is J2/J4-19 to U4 DIR pin2. The LaunchPad pin11 GPIO22/GPIO23 route and actual board population still need exact sample/SDK confirmation.

**Scope:**
- Verify actual SENS007 and LAUNCHXL-F280039C board revisions and visible pin-1/square-pad marks; verify EVM J5 and LaunchPad JP1/JP2A/JP2B shunt states.
- Keep JP4–JP7 classified as 3-pin supply access headers, not isolation links. Review GND/PGND/USB_GND/instrument earth configuration.
- Resolve LaunchPad pin11 GPIO22/GPIO23 selectable routing and exact SDK board pinmux; inspect OCP/TMP302 configuration and fault handling.
- Obtain motor, encoder, supply current-limit/sink capability, load/inertia, motion profile and cooling requirements before any bench procedure.

**Acceptance criteria:** sample revision/pin-1 and all power-source links are confirmed; GPIO route and SDK configuration are exact; a reviewed guarded, current-limited procedure exists. Existing tests remain unchanged; CI passes.

**Blockers:** physical board inspection and actual motor/supply/load/cooling data are not available in this chat. **No stack or power** until the sample-specific checks are completed.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)

Resume after AEL-002 evaluation-stack interface is established, unless a dependency makes it higher priority.


### AEL-002: verify F280039C-to-inverter evaluation path and interface contract

**Why now:** TI MotorControl SDK SPRUJ26A §3.2.12 and Figure 3-14 explicitly document BOOSTXL-3PHGANINV with LAUNCHXL-F280039C. The previous pin-40/GND conflict was a header-site naming error; official Rev A schematics now establish the analog and six-PWM Site-1 pin crosswalk. The active-low enable net pin remains ambiguous and is the next hard hold point.

**Scope:**
- Resolve the SENS007 Rev A nEn_uC/nEnable header pin ambiguity (parsed sheet-5 evidence conflicts between J2/J4 pins 11/12/13/18) using native schematic net tracing or exact-revision official CAD; map the active-low request, nEnable/OE and DIR separately. Confirm pin-1/square-pad orientation and actual EVM/LaunchPad revision before any physical mating.
- Resolve TI's product-page versus April 2024 SDK LaunchPad list and the 3.5-A SDK table versus 7-A RMS product-page rating; obtain thermal/test conditions and exact SDK release target files.
- Verify EVM J5 optional 3.3-V feed link, LaunchPad JP1/JP4–JP7 power-domain jumpers, GND/PGND reference configuration and USB/XDS110 earth path from exact board revision documentation. Resolve EVM OCP and TMP302 behavior.
- Only after document/revision review, prepare a written, current-limited staged bench test procedure; no energization until motor/supply/regeneration/load/cooling requirements and qualified guarded test setup are approved.
- Keep motor, encoder, supply sink capability, load/inertia, duty and cooling as TBD until supported by actual datasheets or user input.

**Acceptance criteria:**
- Analog pins, six PWM pins and OT pin are mapped by official board revision; enable/OE ambiguity and physical pin-1/revision checks remain explicit no-power hold points.
- Officially supported board combinations are distinguished from custom/unverified pairings.
- Regeneration, hardware inhibit, current limit, thermal stop criteria and guarding are included in the bring-up procedure.
- Existing tests remain unchanged; CI passes; experiment and project state record the evidence.

**Dependencies / blockers:** motor/encoder model, supply current limit and sink capability, reflected inertia/load, motion profile and cooling are unknown. Do not choose power components or authorize energized tests until enable/OE mapping, physical board revision/pin-1, power-source selection and bench limits are verified.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)

Resume STM32G0B1CET6 LQFP48 exact pin/alternate-function verification and provisional power-tree proposal after the AEL-002 evaluation-stack interface is established, unless a dependency makes it higher priority.
