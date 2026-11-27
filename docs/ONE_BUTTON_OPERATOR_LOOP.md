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

**Why now:** the original rendered SENS007 Rev A schematic resolves the parsed 11/12/13/18 ambiguity: EVM J2/J4-11 is nEn_uC; nEnable is the internal U12 output to U4 OE package pin22; DIR is J2/J4-19 to U4 DIR package pin2. LaunchPad pin11 has a GPIO22/GPIO23 route notation, and sample-specific hardware population remains unknown.

**Scope:**
- Verify actual SENS007 and LAUNCHXL-F280039C board revisions and visible pin-1/square-pad marks; verify EVM J5 and LaunchPad JP1/JP2A/JP2B shunt states.
- Keep JP4–JP7 classified as 3-pin supply-access headers, not isolation links. Review GND/PGND/USB_GND/instrument earth configuration.
- Use SPRR444A to map Site-1 J4/J2-11=GPIO23 and pin12=GPIO22; inspect exact SDK project/HAL/SysConfig ownership (the optional GPIO23 command-switch input example may conflict with nEn_uC output); review OCP/TMP302 hardware and fault handling.
- Obtain motor, encoder, supply current-limit/sink capability, load/inertia, motion profile and cooling requirements before any bench procedure.

**Acceptance criteria:** sample revision/pin-1 and all power-source links are confirmed; GPIO23 SDK ownership is resolved without command-switch conflict; OCP/TMP302 behavior and a reviewed guarded, current-limited procedure are documented. Existing tests remain unchanged; CI passes.

**Blockers:** physical board inspection and actual motor/supply/load/cooling data are not available in this chat. **No stack or power** until the sample-specific checks are completed.

### AEL-001: verify STM32G0B1CET6 pin map and provisional power tree (deferred)

Resume after AEL-002 evaluation-stack interface is established, unless a dependency makes it higher priority.
