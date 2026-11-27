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


## Corrective official connector crosswalk audit (2026-11-27)

- Reviewed TI BOOSTXL-3PHGANINV assembly drawing SLURAY2 (top and bottom views), PCB overlay SLURAY3, SENS007 Rev A schematic SLURAY0A sheets 2/4/5, LAUNCHXL-F280039C Rev A schematic SPRR444A sheet 2, LaunchPad guide SPRUJ31, pinout map SPRUJ30 and MotorControl SDK guide SPRUJ26A §3.2.12/Figure 3-14.
- Found and corrected the earlier false pin conflict: F280039C Site-1 uses J1/J3 pins 1–30 and J4/J2 pins 11–40; J4/J2 pin 40 is GPIO0. The earlier GND comparison was a header-site naming/side-view interpretation error.
- Confirmed the EVM and LaunchPad Site-1 analog pin mapping by same-numbered header pins: EVM J1/J3-23 VDC → LP ADCINA6; 24 VA → ADCINA2/B6/C9; 25 VB → ADCINA3/B9/C7; 26 VC → ADCINA14/B14/C4; 27 IA → ADCINA11/B10/C0; 28 IB → ADCINB12/C2; 29 IC → ADCINA7/C3; 30 VREF → ADCINA1/B7. EVM pins 1/21/22 map 3V3 feed / no connection on +5V / GND.
- Confirmed six PWM channel order: EVM J2/J4 40→PWM_AH, 39→PWM_AL, 38→PWM_BH, 37→PWM_BL, 36→PWM_CH, 35→PWM_CL; these same-numbered LaunchPad Site-1 pins map to GPIO0/1/2/3/10/11.
- Confirmed EVM OT on J2/J4-33 maps to LaunchPad J4/J2-33 GPIO48; TMP302 OUT connects to OT and is pulled up to 3V3.
- Important unresolved: extracted connector details conflict on exact nEn_uC/nEnable/OE pins (11/12/13/18 appear in different source extractions). Keep enable pin unassigned until direct net tracing in native schematic/CAD or qualified unpowered continuity confirmation. DIR also requires separate confirmation.
- EVM J5 optional 3.3-V feed, LaunchPad power-domain jumpers, physical pin-1 marks and actual board revisions remain sample-specific checks. GND/PGND and USB/XDS110 earth measurement setup is not signed off.
- No physical board access, continuity testing, stacking, energization, motor rotation, firmware build, HIL or bench test occurred. No power authorization is granted.


## CI for corrected header crosswalk

- GitHub Actions run #89 (ID 46008094544) on exact crosswalk commit `8f8d3dfe8a3643a4d5e781c36e61241c17fc6b1b`: **success**.
- Scaffold: structure/table validation, recursive-improvement contract tests and C scaffold syntax all passed.
- KiCad job: succeeded; KiCad CLI/ERC/DRC skipped because native KiCad files are absent.
- Tests and workflow definitions were not modified. No board inspection, continuity test, stacking, energization or motor operation is claimed.


## SENS007 enable and LaunchPad power-link audit (2026-11-27)

- Original TI SENS007 Rev A schematic sheet 5 was visually traced. J2/J4-11 = nEn_uC → U12 SN74LVC1G32 input1. IComp enters U12 input2. U12 output nEnable drives U4 SN74AVC8T245 OE pin22. Therefore nEnable is an internal logic net, not a header signal; U4 OE is active-low. U4 package pins11/12/13 are GND and pin18 is B4, explaining the OCR candidate confusion. DIR is J2/J4-19 → U4 DIR pin2, R28 10-kΩ pull-up, DIR='1' A→B.
- LAUNCHXL-F280039C SPRR444A Rev A Site-1 pin11 route is labelled GPIO22/GPIO23; pin19 is GPIO5_BP. Do not select one GPIO22/23 route without checking board routing/SDK configuration.
- EVM SENS007 Rev A optional 3.3-V LaunchPad feed connector is J5 (2-pin), confirmed on schematic sheet2; earlier J6 mention was incorrect for this schematic revision.
- LaunchPad SPRR444A Rev A: JP1 is USB↔XDS110 power/ground isolation; JP2A/JP2B bridge XDS110↔target MCU 5-V/3.3-V domains. JP4/JP6 are 3-pin +3V3_MCU headers; JP5/JP7 are 3-pin +5V0_MCU headers (pins1/2 rail, pin3 GND), not isolation jumpers. Actual link/shunt population is not known.
- SLURAY2 confirms SENS007 board #/Rev A in drawing and shows top/bottom views, but physical pin-1 marks and user's sample revision are not certified. LaunchPad schematic is MCU103 Rev A; actual sample still uninspected.
- Full trace and source links: `projects/002-modular-servo-drive/SENS007_ENABLE_AND_POWER_JUMPER_AUDIT.md`. No local device access, physical inspection, continuity, stack, power, or motor test. No test or CI definition changed. No-power hold remains.


## Superseding status — SENS007 trace and CI #102 (2026-11-27)

- This section supersedes earlier snapshot statements in this file that described EVM enable as unresolved, called the SENS007 optional 3.3-V feed connector J6, or classified LaunchPad JP4–JP7 as isolation jumpers.
- Direct original SENS007 Rev A sheet-5 visual trace: EVM J2/J4-11 = nEn_uC → U12 input1; IComp → U12 input2; U12 output nEnable → U4 OE package pin22; U4 OE is active-low. DIR = EVM J2/J4-19 → U4 DIR package pin2; R28 pull-up establishes DIR='1' A→B. nEnable is not a connector signal. The apparent pin12/13/18 readings confused U4 package pins with connector numbering.
- EVM optional LaunchPad 3.3-V feed connector is J5 on SENS007 Rev A sheet2. LaunchPad SPRR444A Rev A: JP1 is USB/XDS110 power-ground boundary; JP2A/JP2B bridge XDS110↔target MCU 5-V/3.3-V; JP4/JP6 are 3.3-V power-access headers, JP5/JP7 are 5-V power-access headers.
- Actual board revisions, visible pin-1 marks and all jumper/shunt populations are not verified; no boards inspected, mated, continuity-tested or energized. **No power / no stack hold remains.**
- Full audit: `projects/002-modular-servo-drive/SENS007_ENABLE_AND_POWER_JUMPER_AUDIT.md`; corrected interface matrix: `projects/002-modular-servo-drive/BOOSTXL_3PHGANINV_INTERFACE_AND_TEST_PLAN.md`.
- Latest operator queue: sample-specific no-power inspection and LaunchPad GPIO22/GPIO23 route/SDK closure; motor, supply, regeneration, load and cooling requirements remain blockers.
- GitHub Actions run #102, ID 46014089845, exact commit `334af4c2d906666b4e78bfd341ba799062ebf27a`: **success**. Scaffold repository structure/table validation, contract tests and C syntax passed. KiCad job succeeded; CLI/ERC/DRC skipped because native KiCad files are absent. Tests and CI definitions unchanged.


## Follow-up: exact LaunchPad GPIO23 mapping, SDK conflict, OCP and thermal alert (2026-11-27)

- Live refresh: main remains `6ca4716de7ae11e82e23ad2f61271dc9e4d1e899`; PR #3 is open/draft on `agent/ael-002-48v-modular-servo-brief`, pre-update head `cd509226a249956354907dbbc9aa02c79d0a3141`. Latest CI #106 succeeded on that head; #105 also succeeded. Existing tests/workflows are to remain unchanged.
- Official SPRR444A Rev A resolves header mapping: Site-1 J4/J2-11 = GPIO23 and pin12 = GPIO22. SENS007 nEn_uC at J2/J4-11 maps to GPIO23. Prior phrase "GPIO22/GPIO23 selectable route at pin11" is superseded.
- SPRUJ26A Rev A §3.2.2 documents board file path and JP1/JP2/J101 setup. Its GPIO23 command-switch sample uses GPIO23 as an input. It is not the inverter nEn output configuration; enabling that optional command-switch setup unchanged conflicts with the required GPIO23 output ownership. Exact SDK project-specific HAL/SysConfig config remains unverified.
- SENS007 OCP hardware trace: IA/IB/IC → three comparator channels → U16 OR → IComp → U12 OR with nEn_uC → U4 active-low OE. R79 must remain populated; schematic explicitly notes removing it disables OCP. Comparator annotation 2.75/2.85V and guide's 12A/1A description are retained as separate source statements. No dynamic test or current rating claim.
- TMP302BQDRLRQ1 open-drain active-low OUT, 10k pull-up, OT to GPIO48. Datasheet permits 5C/10C hysteresis; actual configured trip/hysteresis and GND/PGND selection depend on BOM/population. No firmware latch/recovery behavior verified.
- No local access, physical inspection, firmware build, power, stack, motor test. No test or CI definition changed. No-power hold remains.
- Full audit: `projects/002-modular-servo-drive/SENS007_ENABLE_AND_POWER_JUMPER_AUDIT.md`.


## SDK/HAL availability and PWM/fault recovery audit (2026-11-27)

- TI MotorControl SDK 5.02 release notes list F28003x Universal Lab with LAUNCHXL-F280039C + BOOSTXL-3PHGANINV. TI advertises 6.00.00.00 (Mar 31 2026), but installer requires export approval and was not inspected.
- Inspected full recursive tree of TI public `motor-control-sdk`: no F28003x Universal Lab app/HAL/SysConfig project; current universal example found is AM263x. C2000Ware core is generic device/driverlib, not the missing application source. Exact GPIO23 pinmux, command-switch ownership, ePWM TZ configuration and recovery ISR remain unverified.
- GPIO23 command-switch input example conflicts with SENS007 GPIO23 nEn_uC output if both enabled. Reserve GPIO23 for nEn_uC; relocate/disable command-switch input in future source-reviewed firmware.
- SPRAD12A CBC/OST is generic peripheral behavior, not evidence of target app settings.
- SENS007 OCP comparator OR/U12/U4 OE is combinational inhibit, not documented MCU-visible latch; deassertion may restore PWM buffer if host enable stays asserted. R79 must remain. Require host disable and deliberate supervised re-arm.
- TMP302 OUT active-low open-drain with 5°C/10°C sensor hysteresis is not firmware latch. GPIO48 handler, PWM disable and restart logic unverified; proposed policy is software latch, PWM safe state and explicit acknowledgement/re-arm after cooling.
- No local files/device, SDK installer, firmware, tests or CI definitions changed; no hardware interaction. NO STACK / NO POWER remains. Details in audit §10.
