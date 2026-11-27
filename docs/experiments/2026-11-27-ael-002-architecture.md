# AEL-002 architecture and benchmark study

- Date: 2026-11-27
- Branch: agent/ael-002-48v-modular-servo-brief
- Baseline commit: 6ca4716de7ae11e82e23ad2f61271dc9e4d1e899
- Status: preliminary research and requirements capture; not a hardware design release

## Problem

The repository's active queue contained only AEL-001. The user requested a general-purpose modular servo-drive workstream benchmarked against LS Mecapion iX7, with a safe low-voltage single-axis first prototype.

## Hypothesis

A narrowly bounded 24–48 VDC one-axis prototype, with control/power functional partitioning and explicit feedback/protection abstractions, can establish reusable servo-drive architecture without prematurely committing to mains power, current ratings, encoder universality, or an industrial fieldbus stack.

## Evidence gathered

- LS Mecapion's current public drive listing distinguishes iX7NH from iX7M: iX7NH is a network servo family across AC input variants; iX7M is a 200–240 VAC multi-axis EtherCAT family.
- EtherCAT Technology Group's iX7NH listing documents multiple encoder families and control cycle figures (position 125 µs, speed 62.5 µs, current 31.25 µs).
- TI's C2000 Motor Control SDK documents F28003x sensored FOC, encoder/Hall support, multiple current sensing methods, and a servo-drive-with-CAN example.
- ST documents a parallel STM32 motor-control ecosystem with PMSM/BLDC FOC and low-voltage evaluation support.

## Candidate change

Add AEL-002 as a preliminary project brief, record benchmark sources and safety/requirements boundaries, and reprioritize the single active task to resolve the motor/supply/load requirements and verify a C2000 evaluation path.

## Expected benefit

Create a traceable servo-drive workstream and prevent premature selection of power devices, ratings, encoder protocols or industrial safety claims.

## Tests and outcomes

- Live repository/protocol/state read: completed.
- Latest main CI run #35: success. Scaffold validation, contract tests and C syntax check passed. KiCad install/ERC/DRC steps were skipped because no native KiCad files exist.
- Documentation link/source review: recorded in the AEL-002 brief.
- Candidate CI run #41 failed in the repository-contract test because the operator-loop edit dropped two asserted contract strings/queue markers. The test was not weakened; the operator document was corrected to preserve the local-device boundary and deferred AEL-001 queue entry.
- Candidate CI run #43 on final tested candidate commit `2f2d47ec1678043966815d1687eabdccd8ce8bf0`: success. Scaffold validation, repository-contract tests and C syntax check passed; KiCad install/ERC/DRC remained skipped because no native KiCad files exist.

## Risks and limitations

No motor or encoder has been selected. No current/power/torque/speed/thermal rating is assigned. No native KiCad, firmware, simulation, HIL, bench or safety certification evidence exists. The 48 V nominal bus requires explicit regenerative-energy and overvoltage handling.

## Decision

Needs CI evidence and independent engineering review before integration. The document is a concept/preliminary brief only.

## Next experiment

Resolve the minimum motor/supply/load requirements and compare exact C2000 F280039C versus STM32G4 evaluation hardware before freezing the control MCU or power-stage envelope.


## Follow-up study: controller evaluation boards and design inputs

- Exact comparison: TI LAUNCHXL-F280039C plus separately selected BOOSTXL-3PHGANINV versus ST P-NUCLEO-IHM03 (NUCLEO-G431RB + X-NUCLEO-IHM16M1); NUCLEO-G474RE considered separately as a controller evaluation board.
- TI official board page lists 120-MHz C28x/CLA, 3 ADC modules, 16 PWM channels, two eQEP, CAN/CAN-FD and the 48-V BOOSTXL-3PHGANINV option. The LaunchPad is a controller board, not a motor inverter by itself.
- ST official P-NUCLEO-IHM03 data brief lists 7–45 VDC and up to 1.5 A RMS for X-NUCLEO-IHM16M1, plus encoder/Hall input and 1-/3-shunt options. It is not a 48-V-rated power board and is a low-current learning platform.
- STM32G474RE offers 170-MHz Cortex-M4, HRTIM, fast ADCs, comparators and op-amps; NUCLEO-G474RE is a separate Nucleo-64 board. No direct plug-in compatibility with the P-NUCLEO-IHM03 is assumed.
- Recommendation: F280039C path leads for the intended 24–48 V prototype, conditional on checking the inverter EVM's detailed operating limits, pin mapping and software support. Keep ST as a low-voltage FOC reference, not as an electrically equivalent 48-V board.
- Added a motor/encoder/supply/load/duty/cooling/communications/safety intake table and a staged power-stage review checklist. All ratings remain TBD.

## Validation update

- Live main commit at session start: 6ca4716de7ae11e82e23ad2f61271dc9e4d1e899.
- Existing AEL-002 PR #3 remained open and draft; branch head before this update: 4d1c10fdbcc903288f739965de561be25a5e43b7.
- Latest candidate CI before this update: run #47 (ID 45979733003), success. Scaffold validation, existing contract tests and C syntax passed; KiCad install/ERC/DRC skipped because no native KiCad files exist.
- This update adds documentation only; CI will be rerun on the updated branch. No tests were deleted or weakened.
- No electrical calculations can be finalized without motor, encoder, supply and load data. No hardware, firmware, simulation, HIL or bench test is claimed.

## Next experiment

Create a parameterized control/power interface specification and test plan for the chosen evaluation stack, then verify the BOOSTXL-3PHGANINV operating limits and exact connector mapping against its official user guide before any energized setup.


## Correction from detailed inverter-board documentation

TI's BOOSTXL-3PHGANINV official page specifies 12–60 V input and 7 A RMS output per phase, but its supported LaunchPad list does not include LAUNCHXL-F280039C. The board's generic BoosterPack interface alone does not prove validated electrical/software compatibility. F280039C remains a controller candidate, while inverter EVM integration is an open compatibility work item. For initial power-stage tests use a listed LaunchPad or finish a documented pin/voltage/timing/fault-path and SDK port review first. No energized setup is approved.


## Final candidate validation

- Candidate commit containing the board comparison, intake table, power-stage review gates and TI compatibility correction: `86495525b45aabce6517db05438f6d1010855efc`.
- GitHub Actions run #59 (ID 45983937041) on that commit: **success**.
- Scaffold job: repository structure/table validation passed; all existing repository/recursive-improvement contract tests passed; existing C scaffold syntax check passed.
- KiCad job: completed successfully with install/ERC/DRC steps **skipped** because the repository still has no native KiCad schematic or PCB files.
- Changed-file review: only README, operator-loop documentation, experiment record, project-state memory and AEL-002 brief changed; no tests or CI rules were modified.
- PR #3 remains open and draft; no merge or hardware approval was performed.


## Follow-up: BOOSTXL-3PHGANINV user guide, schematic and SDK compatibility audit

- Official documents reviewed: BOOSTXL-3PhGaNInv EVM User Guide SLUUBP1A Rev A (April 2018); SENS007 schematic Rev A; Motor Control SDK Universal Project and Lab SPRUJ26A Rev A (April 2024); TI BOOSTXL-3PHGANINV and LAUNCHXL-F280039C product pages.
- Key correction: SPRUJ26A §3.2.12 and Table 3-1 explicitly name LAUNCHXL-F280039C, F280025C and F2800137 for this inverter. F280039C is an officially documented TI SDK evaluation path. The previous compatibility note based solely on the product page is superseded.
- Product-page supported list differs (F280049C, F28379D, F280025C); kept as a separate evidence set rather than assuming all are interchangeable in the 2024 Universal Lab project.
- Interface captured: six complementary PWM; three inline phase-current ADC; three phase-voltage ADC; DC bus ADC; active-low /PWM enable; active-low /PCB OT alert; 3.3-V LaunchPad rail. EVM guide gives J1-14/J1-16/J1-18 current-feedback polarity caveat.
- Analog/power facts: 5-mΩ shunts, INA240 gain 20 V/V, 1.65-V midpoint; 12–60 V bus, LM5017 5-V rail, LP38691 3.3-V LDO, REF3333; J6 LaunchPad 3.3-V feed max 300 mA; no simultaneous J6 and USB-powered LaunchPad. OCP TLV3201 threshold 12 A / 1-A hysteresis; TMP302 active-low overtemperature alert.
- Rating conflict: product page says 7 A RMS/phase; SDK Table 3-1 says 3.5 A. No continuous-current conclusion made.
- Added source-linked controller/interface matrix and V0–V8 staged validation plan in `projects/002-modular-servo-drive/BOOSTXL_3PHGANINV_INTERFACE_AND_TEST_PLAN.md`.
- Exact F280039C LaunchPad pin mapping, board revision correlation, OCP/thermal dynamic verification, and grounding/measurement strategy remain open. No energization, motor rotation, firmware build, HIL or physical test is claimed.
- Tests/CI definitions were not edited. The current pre-change branch head is checked against Actions run #66; the post-change run is pending.


## Additional pinout audit — connector mapping hold point

- Reviewed TI F280039x LaunchPad User Guide SPRUJ31, F280039C pinout map SPRUJ30 and BOOSTXL-3PHGANINV schematic SENS007 Rev A sheet 5.
- Found a material connector-numbering conflict if read naïvely: SENS007 labels EVM J2/J4 pin 40 as PWM/GPIO, but SPRUJ30 labels LaunchPad J4-40 as GND. Other J4 pins also differ in function (LaunchPad J4-36 is XRSn). The SDK §3.2.12 pairing statement does not by itself explain the physical connector orientation or board revision crosswalk.
- Analog candidate correspondence: EVM pins 23–29 map VDC/VA/VB/VC/IA/IB/IC, while LaunchPad J3 pins 23–29 are ADC-capable. This is not yet a verified physical net-to-net mapping.
- The EVM guide's J1-14/16/18 current-sense note and SENS007 combined header numbering are also retained as separate document-specific labels pending crosswalk.
- Updated the interface/test-plan document and operator queue with a hard no-power hold point until official connector orientation, pin-1 marks and exact board revisions are reconciled.
- No boards stacked, no continuity measurement, no power applied, no motor operation. This is a documentation-only finding.


## Final CI result after connector-audit update

- Final content commit: `6e13831c9a6493704fd36728e772b6874579ca1d`.
- GitHub Actions run #79 (ID 46005035231): success; run #80 (ID 46005039591): success, both on the final content commit.
- Scaffold: repository structure/table validation, existing repository/recursive-improvement contract tests, and C scaffold syntax all passed.
- KiCad job: job succeeded; KiCad CLI install and ERC/DRC were skipped because native KiCad schematic/PCB files are absent.
- Tests and CI definitions were not modified. PR #3 remains open/draft. No electrical or physical validation is claimed.
