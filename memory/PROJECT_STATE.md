# Current Project State

**Snapshot date:** 2026-11-27 (updated after live branch review)  
**Default branch:** `main`  
**Baseline main commit before AEL-002 candidate:** `6ca4716de7ae11e82e23ad2f61271dc9e4d1e899`

## Verified repository state

- Public GitHub repository; connected GitHub integration has read/write permissions.
- MCU families in scope: STM32, TI MSPM0, C2000, MSP430, ESP32, and future profiles.
- AEL-001 remains a preliminary STM32G0B1CET6 LQFP48 sensor/I/O controller brief. No native KiCad schematic/PCB or flashable firmware is claimed.
- AEL-002 has been added on candidate branch `agent/ael-002-48v-modular-servo-brief` as a preliminary modular low-voltage servo-drive concept; not yet merged at this snapshot.
- AEL-002 benchmark distinguishes LS Mecapion iX7NH network servo from iX7M multi-axis servo.
- AEL-002 first prototype scope is one axis, external 24–48 VDC bus, three-phase PMSM/BLDC, guarded bench evaluation. No mains power stage or component ratings are frozen.
- Candidate MCU: TI C2000 F280039C/F28003x; alternative: STM32G4. Neither is frozen.
- AEL-002 candidate PR #3: https://github.com/u-lec-sam/ai-electronics-lab/pull/3 (draft, awaiting review; not merged).
- Candidate CI run #43 on commit `2f2d47ec1678043966815d1687eabdccd8ce8bf0`: success. Run #41 failed due to a contract regression in the operator document; the assertions were preserved and the document corrected. Run #43 then passed.
- Motor, encoder, supply current limit/regen capability, load/inertia, duty cycle, cooling, communications and budget remain unresolved.

## AEL-002 evaluation update

- TI controller path: LAUNCHXL-F280039C; candidate inverter module: BOOSTXL-3PHGANINV (TI describes it as a 48-V three-phase inverter). Exact current, thermal and interface limits remain to be verified from the module user guide.
- ST reference path: P-NUCLEO-IHM03 = NUCLEO-G431RB + X-NUCLEO-IHM16M1; ST data brief specifies 7–45 VDC and up to 1.5 A RMS, so it is not a 48-V board. NUCLEO-G474RE is a separate controller evaluation board, not assumed plug-compatible with that kit.
- Added a comprehensive motor/encoder/supply/load/duty/cooling/interface/safety intake table and power-stage design-review gates. All motor/power ratings remain TBD.
- No components, schematic, PCB, firmware build, simulation or energized tests are claimed.

## CI baseline

- Latest inspected main workflow run: #35, run ID 45949261831, commit `6ca4716de7ae11e82e23ad2f61271dc9e4d1e899`, conclusion success.
- Scaffold job: repository validation, contract tests and C syntax check passed.
- KiCad job: install/ERC/DRC steps skipped because native KiCad files are absent. Overall green CI is not electrical verification.

## Active project queue

1. **AEL-002 — resolve motor/supply/load requirements and compare control MCU evaluation paths.** See `docs/ONE_BUTTON_OPERATOR_LOOP.md`.
2. AEL-001 — verify STM32G0B1CET6 LQFP48 pin map and establish a provisional power tree after AEL-002's first requirements pass.

## Evidence and limitations

- AEL-002 research and acceptance boundaries: `projects/002-modular-servo-drive/README.md`.
- Session experiment record: `docs/experiments/2026-11-27-ael-002-architecture.md`.
- No schematic, PCB, firmware build, simulation, HIL, hardware measurement, product safety assessment or certification is claimed.
- This snapshot is a candidate-branch record until the pull request is reviewed and merged.


## Compatibility clarification (2026-11-27)

- TI's BOOSTXL-3PHGANINV page specifies 12–60 V input and 7 A RMS output per phase. The listed supported LaunchPads are F280049C, F28379D and F280025C; LAUNCHXL-F280039C is not listed.
- F280039C remains an MCU candidate, but its use with this inverter would be a custom integration until pin mapping, voltage levels, PWM/ADC timing, hardware fault path and software support are verified. No plug-and-play compatibility or energized test is claimed.


## Latest AEL-002 candidate validation

- Commit `86495525b45aabce6517db05438f6d1010855efc` — GitHub Actions run #59 (ID 45983937041): success.
- Repository validation, existing contract tests and C scaffold syntax passed. KiCad install/ERC/DRC were skipped because no native KiCad files exist.
- PR #3 remains open/draft. No tests were altered, and no electrical/physical validation is claimed.


## Latest workflow run

- Candidate commit `40f3e1cb59b2cf607312ff180d4cf559760e4d27` — GitHub Actions run #62 (ID 45983994095): success.
- Repository validation, existing contract tests and C scaffold syntax passed. KiCad install/ERC/DRC were skipped because no native KiCad files exist.


## BOOSTXL-3PHGANINV interface review (2026-11-27)

- Official TI source correction: SPRUJ26A Rev A (April 2024) §3.2.12 and Table 3-1 explicitly list LAUNCHXL-F280025C, LAUNCHXL-F280039C and LAUNCHXL-F2800137 for BOOSTXL-3PHGANINV. F280039C is therefore a documented MotorControl SDK pairing, not automatically a custom integration.
- TI product page separately lists F280049C, F28379D and F280025C. Preserve this discrepancy; do not conflate product-page recommendations with the 2024 Universal Lab's specific inverter table.
- EVM guide SLUUBP1A Rev A and schematic SENS007 Rev A reviewed. Functional interface includes six PWM, three phase-current, three phase-voltage, DC-bus voltage, active-low PWM enable, active-low PCB over-temperature alert and 3.3-V supply.
- EVM current sensing: 5-mΩ inline shunts, INA240 gain 20 V/V, 1.65-V midpoint; current output polarity inversion is noted for J1-14/J1-16/J1-18. OCP TLV3201 threshold is stated as 12 A with 1-A hysteresis; not an operating-current rating.
- Power: 12–60 V input, LM5017 5-V rail, 3.3-V LDO/reference. EVM J6 supplies 3.3 V to LaunchPad J1-1, max 300 mA; remove J6 for USB-powered debug to avoid dual-source/backfeed.
- Rating discrepancy: TI product page says 7 A RMS/phase, whereas SPRUJ26A Table 3-1 says 3.5 A for the EVM. Thermal/test conditions must be resolved; neither is assumed as a safe continuous application rating.
- Added `projects/002-modular-servo-drive/BOOSTXL_3PHGANINV_INTERFACE_AND_TEST_PLAN.md` with controller comparison, sourced interface contract, unresolved pin-map fields, and staged test gates.
- No exact F280039C GPIO/ADC/ePWM mapping is claimed yet. No motor/encoder/supply/load/cooling selected; no power applied or hardware test claimed.


## F280039C connector cross-check hold point (2026-11-27)

- SENS007 Rev A sheet 5 calls EVM J2/J4 pin 40 a PWM/GPIO input, while SPRUJ30's LAUNCHXL-F280039C map calls LaunchPad J4-40 GND. The EVM J2/J4 pins 40–35 are described as PWM/GPIO/Timer_Cap inputs; LaunchPad J4 pins 40–35 include GND, GPIO05, GPIO32, GPIO059, XRSn, GPIO08.
- This is an unresolved numbering/orientation/connector-pair correspondence. Do not use same-number-to-same-number assumptions and do not stack or energize boards until an official, revision-matched physical crosswalk resolves it.
- SENS007's analog pins 23–29 carry VDC, VA, VB, VC, IA, IB, IC; SPRUJ30 J3 pins 23–29 are ADC-capable. This is a candidate correspondence only pending physical orientation/revision confirmation.
- The MotorControl SDK's explicit F280039C evaluation pairing remains vendor-documented; the present physical pin audit has not yet proven direct stacking for the exact board revisions.
- Next task is now narrowed to connector crosswalk, pin-1/orientation review and fault/power-source mapping. No power application is approved.


## Final validation for connector-audit update

- Final content commit before CI record: `6e13831c9a6493704fd36728e772b6874579ca1d`.
- GitHub Actions runs #79 (ID 46005035231) and #80 (ID 46005039591) on that exact commit: **success**.
- Both runs: repository structure/table validation passed; repository and recursive-improvement contract tests passed; C scaffold syntax passed; KiCad CLI install/ERC/DRC skipped because no native KiCad schematic/PCB exists.
- Existing test files and CI workflow were not changed. PR #3 remains open/draft; no merge.


## Corrected F280039C/SENS007 Site-1 header crosswalk (2026-11-27)

- Live refresh confirmed main remains on the AEL-001 queue; AEL-002 changes remain on draft PR #3 branch `agent/ael-002-48v-modular-servo-brief`. Latest pre-change CI runs #82/#83 on `ea7e20974c2230b001c421688fe3443b34b1f983` succeeded. No test/workflow files changed in this task.
- Corrected previous false conflict: LAUNCHXL-F280039C SPRR444A Rev A sheet 2 explicitly defines Site-1 J1/J3 pins 1–30 and J4/J2 pins 11–40. Pin 40 is GPIO0, not GND. The prior GND claim mixed header site naming.
- TI MotorControl SDK SPRUJ26A Rev A §3.2.12 explicitly says connect BOOSTXL-3PHGANINV to LAUNCHXL-F280039C J1/J3 and J4/J2; Figure 3-14 shows the supported stack.
- Confirmed by SENS007 Rev A sheet 5 + SPRR444A Site-1: EVM J1/J3 pins 23–30 (VDC, VA, VB, VC, IA, IB, IC, VREF) map to LaunchPad J1/J3 same-number pins and ADC-capable MCU nets; pins 1, 21, 22 map to +3V3 feed, NC +5V, and GND.
- Confirmed six PWM paths: EVM J2/J4 pins 40,39,38,37,36,35 → LaunchPad Site-1 J4/J2 same-number pins → GPIO0, GPIO1, GPIO2, GPIO3, GPIO10, GPIO11 → EVM PWM_AH, PWM_AL, PWM_BH, PWM_BL, PWM_CH, PWM_CL in order.
- Confirmed OT: EVM J2/J4-33 OT → LaunchPad J4/J2-33 GPIO48. SENS007 TMP302 OUT feeds OT with a 10-kΩ pull-up to 3V3.
- Remaining unresolved: SENS007 sheet-5 connector text extraction conflicts on nEn_uC/nEnable mapping (candidate J2/J4 pins 11/12/13/18). Do not guess. DIR and OE also require separate net confirmation. Pin-1 visual mark on actual samples, EVM J5 optional 3.3-V link, LaunchPad JP1/JP4–JP7 power jumper state and GND/PGND/USB earth setup remain physical revision checks.
- Added corrected matrix and explicit no-power hold point to `BOOSTXL_3PHGANINV_INTERFACE_AND_TEST_PLAN.md`. No hardware inspected, stacked, continuity tested or energized; no motor/firmware test claimed.


## CI validation for corrected header crosswalk

- CI run #89, ID 46008094544, exact crosswalk commit `8f8d3dfe8a3643a4d5e781c36e61241c17fc6b1b`: **success**.
- Scaffold checks passed: repository structure/table validation, repository and recursive-improvement contract tests, and C scaffold syntax.
- KiCad job succeeded; CLI install/ERC/DRC were skipped because the repository still contains no native KiCad schematic or PCB files.
- Existing test files and workflow definitions remain unchanged. PR #3 remains open/draft. No hardware validation or power authorization.


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


## GPIO23 / OCP / TMP302 follow-up (2026-11-27)

- Corrected prior shorthand: SPRR444A Rev A Site-1 J4/J2-11 = GPIO23; J4/J2-12 = GPIO22. SENS007 J2/J4-11 `nEn_uC` therefore physically maps to LaunchPad GPIO23, not a selectable GPIO22/GPIO23 path.
- SPRUJ26A Rev A §3.2.2 calls for JP1, JP2 and J101 in the F280039C Universal Lab setup; §3.2.12 documents BOOSTXL-3PHGANINV. Its GPIO23 command-switch example configures GPIO23 as an input. That optional example is not proof of inverter enable configuration and conflicts with using GPIO23 as the SENS007 `nEn_uC` output if enabled unchanged. Exact SDK app/HAL/SysConfig ownership remains unverified.
- SENS007 OCP: three comparator outputs U13/U14/U15 → U16 OR → IComp; U12 combines IComp with nEn_uC; U12 output drives active-low U4 OE. R79 is the OCP link and must not be removed. Schematic comparator threshold annotation 2.75/2.85V differs in representation from EVM guide 12A/1A protection description; no current rating inferred and no dynamic test.
- TMP302BQDRLRQ1 OUT is open-drain active-low with 10k pull-up, OT routes to GPIO48. Trip point/hysteresis depend on configuration resistor population; R54 GND default/R53 PGND DNP per schematic, but as-built population unknown. No MCU fault-latch/restart implementation verified.
- Updated detailed audit: `projects/002-modular-servo-drive/SENS007_ENABLE_AND_POWER_JUMPER_AUDIT.md`. No physical sample inspected; no power/no stack hold remains.
- Existing tests and CI definitions unchanged. Candidate CI validation for this documentation update is pending.


## SDK source and fault recovery audit (2026-11-27)

- Exact F280039C Universal Lab app/HAL/SysConfig is absent from inspected public TI motor-control-sdk tree. TI 5.02 release notes list F28003x Universal Lab + F280039C + BOOSTXL-3PHGANINV; advertised SDK 6.00 installer was not inspected (export approval).
- GPIO23 physical route confirmed at Site-1 pin 11; GPIO22 is pin 12. Generic optional command-switch example uses GPIO23 input and conflicts with SENS007 nEn_uC output if both active. Software ownership unresolved without target app source.
- Generic ePWM CBC/OST docs do not establish target TZ source/action/ISR/re-arm.
- SENS007 OCP is combinational comparator/OR/U12/U4 OE inhibit, not proven MCU-visible latch. OCP deassertion may re-enable buffer if host enable stays asserted; R79 must remain fitted. Require explicit supervised re-arm.
- TMP302 active-low OUT has sensor 5°C/10°C hysteresis, not firmware latch. GPIO48 app handling/recovery unverified; require software latch, PWM disable and explicit acknowledgement after cooling.
- Detailed audit §10 in `projects/002-modular-servo-drive/SENS007_ENABLE_AND_POWER_JUMPER_AUDIT.md`. No SDK installer, firmware, tests, CI definitions or hardware activity. NO STACK / NO POWER.

- GitHub Actions run #120, ID 46016354866, exact commit `bd046a78124e8fb6edf2cf4c091ebc9ae4451a5f`: **success**. Repository structure/table validation, recursive-improvement contract tests and C scaffold syntax passed. KiCad job passed; CLI/ERC/DRC skipped because native KiCad schematic/PCB files are absent. Existing tests and CI definitions unchanged.


## Engineering Academy baseline (2026-11-28)

- User requested a complete Korean, self-contained learning path from zero to independent design/development/verification of the electronics project, written so a middle-school student can follow while retaining university/industry technical depth.
- Adopted an integrated textbook + project workflow: each lesson teaches principles, derives equations, explains terms/components/datasheets, gives worked calculations, implementation sequence, exercises/solutions, verification and explicit uncertainty; lesson outputs feed project artifacts.
- Added `docs/academy/README.md` with staged curriculum: engineering process/safety; math/physics/electrical basics; components and analog/digital circuits; electrical machines and motors; power electronics and power systems; control theory and PMSM/BLDC FOC; MCU/embedded firmware; schematic/PCB/mechanical/BOM; verification/commissioning/fault analysis; industrial expansion and standards.
- Added `docs/academy/00-learning-and-safety.md` and `docs/academy/01-electricity-and-circuits.md`. This is an initial foundation, not a complete textbook.
- Curriculum explicitly includes three-phase AC, line/phase voltage, Y/Delta, active/reactive/apparent power, power factor and harmonics. Clarification: first AEL-002 prototype is externally supplied by 24–48 VDC; it uses a three-phase motor/inverter but does not include a mains three-phase AC rectifier input. Teach grid/three-phase supply theory for understanding and later industrial expansion, but do not accidentally expand first-prototype scope.
- Every lesson must separate intuition from formal derivation, define variables/units, show assumptions and intermediate calculations, interpret datasheet conditions, map to AEL-002 decisions, include exercises/solutions and objective completion criteria.
- Safety remains unchanged: actual board revision, pin-1, EVM J5, LaunchPad JP1/JP2A/JP2B and grounding unknown; **NO STACK / NO POWER**. No motor/supply/load/cooling requirements or ratings are frozen.
