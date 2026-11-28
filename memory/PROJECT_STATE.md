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


## Engineering Academy progress — mathematics and transient circuits (2026-11-28)

- Added `docs/academy/02-mathematics-and-physics-for-engineers.md`: SI units/dimensions, prefixes, algebra, graphs, degree/radian, sinusoidal functions, vectors, derivatives, integrals, exponentials and differential-equation intuition; worked examples, exercises and explanations.
- Added `docs/academy/03-rc-rl-transient-response.md`: capacitor/inductor physics and stored energy, derivations of RC charge/discharge and RL current rise/decay, time constants, calculations, component data-sheet selection factors, motor-winding connection, simulation exercises and answer key.
- Added `docs/academy/LESSON_REVIEW_CHECKLIST.md` with repeatable checks for pedagogy, math/physics, units, derivations, datasheets, project scope, safety, source traceability and CI.
- Updated Academy index and repository root README. Corrected chapter 01 to distinguish conventional current direction from electron drift and use energy change `ΔE` rather than ambiguous `W` in the voltage definition.
- Technical cross-check references: OpenStax University Physics Vol. 2 RC circuits (10.5), RL circuits (14.4), Calculus Vol. 2 first-order linear equations (4.5), and RLC energy/ODE discussion (14.6). The equations were checked against these open textbook derivations. Educational examples are idealized and are not AEL-002 ratings.
- Existing CI/test definitions were not modified. No firmware, schematic, PCB, BOM, physical test, stack, or power-up was performed.
- AEL-002 **NO STACK / NO POWER** remains mandatory. Sample board revisions, pin-1 orientation, EVM J5, LaunchPad JP1/JP2A/JP2B and grounding remain physically unverified; motor/supply/load/regeneration/cooling requirements remain open.
- CI evidence for these academy changes is to be added only after a run completes on the exact final commit.


## Engineering Academy progress — AC circuits and three-phase power (2026-11-28)

- Added docs/academy/04-ac-circuits-and-three-phase-power.md: periodic waveforms, frequency/period/angular frequency/phase, peak/peak-to-peak/average/RMS definitions, derivation of sinusoidal RMS, phasors, complex impedance, R/L/C phase and reactance, series RLC and resonance, balanced three-phase 120-degree sequence, vector derivations of Y/Delta line/phase relations, P/Q/S, power factor, THD, displacement vs true PF, triplen harmonics, worked calculations, four calculation/model exercises and 12 fully worked questions.
- The chapter explicitly separates AEL-002's first externally supplied 24–48 VDC bus feeding a three-phase PWM inverter from a future industrial 200/400 VAC three-phase mains-input architecture. No mains wiring or power-up instructions are included; no ratings are inferred from educational examples.
- Re-read the live Academy 00–03 lessons and LESSON_REVIEW_CHECKLIST.md before writing. The lesson follows the established intuition → formal definition → derivation → worked examples → project boundary → exercises/solutions → completion criteria structure.
- Theory cross-check sources: OpenStax University Physics Vol. 2 §§15.2–15.4; U.S. DOE Electrical Science Handbook DOE-HDBK-1011/3-92, Three-Phase Circuits; MIT OCW 6.622 Lecture 21; NCEES FE Reference Handbook, Balanced Three-Phase Systems. Links are included in the lesson.
- Updated Academy index and this operator queue. Existing CI workflow/test definitions were not changed. Exact-commit CI for the new lesson is pending and must be checked before claiming validation.
- No firmware, schematic, PCB, BOM, component ratings, local device access, physical inspection, board stack, power-up or hardware test occurred. AEL-002 NO STACK / NO POWER remains mandatory; motor/supply/load/regeneration/cooling requirements remain open.


## Post-write verification checkpoint — Academy chapter 04 (2026-11-28)

- Live branch verification confirms chapter 04 exists, the Academy index links it, the operator loop now queues the magnetism/induction/motor-fundamentals lesson, and this project memory contains the AC/three-phase progress record.
- Chapter 04 blob SHA: f9fae8b77bd5dfdec6fcc7a5a22851a38456042c. The branch currently includes all three metadata/index updates and the new lesson.
- The first push and PR CI runs for the lesson-only commit e79f79ee2c16122d8ba4336b644247b0ed9f92fc succeeded (#155 push, #156 pull_request). Later index/operator/memory commits caused their superseded runs to be cancelled; a fresh run on the final consolidated branch HEAD is required before claiming final CI success.
- CI workflow definition was inspected and is not being changed. No KiCad files or physical validation are introduced by this lesson.


## Exact-commit CI result — Academy chapter 04 (2026-11-28)

- Final consolidated content/index/operator/memory checkpoint commit 772af027361c6d40391c2b1a6a0f318bb8961db8 was validated by GitHub Actions run #162 (ID 46074054416): **success** on the exact SHA.
- Scaffold job passed repository structure/table validation, repository and recursive-improvement contract tests, and C scaffold syntax.
- KiCad job completed successfully; KiCad CLI installation, ERC and DRC were correctly skipped because the repository contains no native KiCad schematic/PCB files. This is not an ERC/DRC or electrical validation result.
- PR #3 remains open and draft; no merge was performed.


## Engineering Academy progress — magnetism, induction and motor fundamentals (2026-11-28)

- Added docs/academy/05-magnetism-induction-and-motor-fundamentals.md with beginner intuition and university-level derivations for H/B/flux/permeability, Ampere's law, Faraday/Lenz laws, motional emf, back-EMF, Lorentz force, coil torque, electrical/mechanical angle and pole pairs, three-phase rotating magnetic field, and brushed DC/induction/synchronous/PMSM/BLDC motor distinctions.
- Includes dimensional checks, five worked calculations, four calculation/model exercises, 15 questions with complete solutions, motor datasheet interpretation checklist, hypothetical-only example, AEL-002 requirements TBD list and explicit NO STACK / NO POWER boundary.
- PMSM dq torque equation states its Park-transform normalization and peak-current convention; warns that RMS/power-invariant conventions change coefficients. Ke/Kt are not numerically converted without matching line/phase, RMS/peak, waveform and speed definitions.
- Re-read live Academy chapters 00–04 and LESSON_REVIEW_CHECKLIST.md before authoring. The Academy index and operator loop were updated; next queued task is motor electrical/mechanical model and load requirements.
- Theory references included: OpenStax University Physics Vol. 2 §§11.1, 11.5, 12.5, 13.1–13.2; MIT OCW Physics II lecture notes; MIT OCW Electric Motors notes; Yale PHYS 201 lecture 11.
- No specific motor was selected; actual model, pole pairs, winding parameters, Ke/Kt conventions, current/torque/speed limits, encoder, load/inertia, motion profile, supply/regeneration sink and cooling remain TBD.
- No firmware, schematic, PCB, BOM, local device access, physical inspection, board stack, power-up or motor test occurred. Existing CI definitions unchanged. AEL-002 **NO STACK / NO POWER** remains.
- Exact final branch SHA and CI result are recorded in the subsequent verification checkpoint below once the final commit run completes.


## Engineering Academy chapter 06 (2026-11-28)

- Added `docs/academy/06-motor-electrical-mechanical-and-thermal-models.md`.
- Reviewed Academy chapters 00–05 and `LESSON_REVIEW_CHECKLIST.md` before authoring.
- Chapter covers DC equivalent motor equations; PMSM amplitude-invariant Park convention, d/q flux/voltage/torque equations; electrical/mechanical speed; carefully qualified Ke/Kt conversions; torque-speed/current/voltage limits; reflected gear and screw inertia; acceleration torque; copper loss, efficiency, continuous/peak ratings, one-node thermal time constant and duty-cycle RMS current.
- Added a manufacturer-datasheet intake template and AEL-002 motor/load/supply/regeneration/cooling requirements worksheet. All real motor and drive ratings remain TBD.
- Mathematical examples are explicitly hypothetical. Source links include TI TIDM-02018 and MathWorks PMSM model references; equations are restated under declared conventions rather than mixed across conventions.
- No firmware, schematic, PCB, simulation execution, motor test, thermal measurement, physical inspection or power-up is claimed.
- **NO STACK / NO POWER** remains. The physical sample revision, pin-1 orientation, jumpers, USB/XDS110 and grounding/test configuration remain unverified.
- Next Academy task: Chapter 07 on DC link, three-phase two-level inverter, phase/line voltage, PWM/SVPWM, dead time, switching/conduction losses, capacitor stress and regenerative energy. Actual component ratings remain TBD.


## Engineering Academy chapter 07 (2026-11-28)

- Added `docs/academy/07-dc-link-and-three-phase-inverter.md` (26,927 characters).
- Re-read the live operator protocol, README, Academy index, quality checklist, Academy chapters 00–06 and current CI workflow before writing.
- Chapter covers DC-link charge/energy/power balance; two-level three-phase VSI pole/phase/line voltage; all eight switching states; SPWM and SVPWM with explicitly distinguished modulation-index conventions; linear voltage limits; SVPWM dwell-time derivation; deadtime and current-dependent voltage error; MOSFET/IGBT conduction, switching and gate-drive losses; capacitor voltage/ripple-current/ESR/thermal stress; regenerative energy and braking paths.
- Includes dimensional analysis, four worked design calculations and twelve fully solved exercises, manufacturer datasheet intake templates for switches/gate drivers/capacitors, and an AEL-002 power-stage requirements worksheet.
- Reference basis includes TI SPRJUF4A, Infineon loss/deadtime application notes, Kolar & Round DC-link capacitor RMS ripple-current analysis, and Cornell Dubilier capacitor application guidance. Manufacturer EVM/module values are not copied as AEL-002 ratings.
- All real AEL-002 DC bus limits, motor current, PWM frequency, semiconductor, gate-driver, capacitor, brake chopper/resistor and cooling ratings remain **TBD**.
- No firmware, schematic, PCB, simulation execution, hardware inspection, motor test, thermal measurement or power-up is claimed.
- **NO STACK / NO POWER** remains. No local device or filesystem access was used.
- Next Academy task: Chapter 08 on Clarke/Park transforms, PMSM d/q current dynamics, FOC current loop, cascaded speed/position loops, sampling and PWM/ADC synchronization.


## Engineering Academy Chapter 08 — FOC theory and verification plan (2026-11-28)

- Added \`docs/academy/08-clarke-park-pmsm-foc.md\` (25,339 characters).
- Reviewed the live Academy index, corrected Chapter 00 filename (\`00-learning-and-safety.md\`), Chapters 01–07, the lesson quality checklist, operator protocol, current project state, PR #3 and existing CI workflow before authoring.
- Chapter 08 declares the amplitude-invariant Clarke/Park convention and inverse transforms; derives electrical/mechanical angle conversion, PMSM d/q voltage dynamics, SPMSM/IPMSM torque; explains current PI, cross-coupling feed-forward, vector voltage saturation, anti-windup, cascaded speed/position loops, PWM/ADC synchronization, current-sensor offset/scale/polarity/reconstruction/calibration, firmware state flow and verification templates.
- Includes dimensional checks, four worked examples, twelve fully solved exercises, a TBD requirements matrix, SIL/software verification checklist and an explicitly gated real-hardware test plan.
- Cross-check convention: amplitude-invariant Clarke/Park means phase-current peak equals the balanced alpha-beta vector magnitude; instantaneous power and torque equations retain the 3/2 factor. The inverse transforms and norm-preservation checks are stated.
- Real motor type/parameters, Rs/Ld/Lq/psi_f, pole pairs, encoder, sensor/ADC details, current limits, PWM/ADC timing, PI gains and WCET remain **TBD**. Example values are educational only.
- No firmware build, SIL/HIL execution, motor simulation, hardware inspection, calibration, board stack or power-up is claimed.
- Existing CI workflow file remains unchanged; its branch blob SHA remains \`7af60d723f8b98c2eeb1767c7251a8978fa3cfb3\`.
- **NO STACK / NO POWER** remains. No local device/filesystem access was used.
- Next Academy task: Chapter 09 on encoder/Hall/resolver feedback, angle sensing, electrical-angle offset/alignment, interpolation, startup and sensor diagnostics, with all actual AEL-002 sensor selections and pin mappings TBD.


## Engineering Academy Chapter 09 — rotor position sensing (2026-11-28)

- Added \`docs/academy/09-rotor-position-sensors-and-feedback.md\` (30,898 characters).
- Re-read live branch/PR #3, current CI checks, operator loop, Academy index, Chapters 00–08, and the lesson quality checklist before authoring.
- Chapter 09 covers incremental A/B/Z quadrature, PPR versus CPR and x1/x2/x4 decoding, index acquisition and its distinction from electrical zero, single-turn/multi-turn absolute encoders, Gray/binary coding, serial frame validation and CRC, three-Hall six-sector sensing/interpolation, Resolver excitation and synchronous SIN/COS demodulation, atan2 and amplitude diagnostics, mechanical/electrical angle and pole pairs, speed M/T methods, timer timestamps/wrap, interpolation/extrapolation, quantization/jitter/delay error budgets, signal integrity, plausibility diagnostics, dual-sensor residuals, FOC data contract, firmware states and test templates.
- Includes derivations, dimensional checks, four worked example groups, twelve fully solved exercises, TBD requirements matrix, software/SIL test scenarios, hardware-gate checklist, and source links.
- Convention cross-check: \`theta_e = wrap(p * theta_m + theta_0)\`; resolver electrical cycles are not presumed equal to motor pole pairs; Hall sectors are 60 electrical degrees only under the stated ideal three-Hall assumption; PPR/CPR definitions are not conflated.
- Actual AEL-002 sensor type/model/revision, PPR/CPR/bit resolution, interface, wiring/pin map, sensor supply, direction, motor pole pairs, electrical offset, speed range, edge/frame rates, timer/ADC timing, error thresholds and redundancy policy remain **TBD**.
- Updated Academy index, project state and operator loop. Next task is Chapter 10 on MCU timers/QEP/capture/interrupts/DMA, PWM/ADC scheduling and real-time execution budgets.
- Existing CI workflow remains unchanged. Branch workflow blob SHA: \`7af60d723f8b98c2eeb1767c7251a8978fa3cfb3\`.
- No local device/filesystem access. No sensor inspection, alignment, calibration, firmware build, SIL/HIL execution, motor test, stack or power-up was performed.
- **NO STACK / NO POWER** remains.


## Engineering Academy Chapter 10 — MCU timing and real-time execution (2026-11-28)

- Added \`docs/academy/10-mcu-timing-interrupts-dma-realtime.md\` (17,989 characters).
- Re-read live PR #3, branch state, CI workflow, operating protocol, Academy 00–09, Academy index and lesson quality checklist before authoring.
- Covers clock tree/CDC, timer/prescaler/counter wrap, capture/compare, QEP quadrature x1/x2/x4, input synchronization/filter delay, interrupt priority/nesting/latency/jitter, critical section/race/atomic snapshot, DMA double buffering/ownership/cache coherency, PWM time-base, ADC SOC/aperture/acquisition/conversion, timestamp-based rotor-angle prediction, FOC scheduling, utilization/response time/WCET, deadline miss/overrun and watchdog.
- Includes ASCII timing/state diagrams, equations and dimensional checks, hypothetical calculations, 12 fully solved exercises, TBD configuration matrix, timing verification matrix, fault-injection test matrix and hardware gate.
- Chapter 08/09 integration: predict electrical rotor angle at ADC aperture from sensor timestamp and speed; preserve Chapter 08 amplitude-invariant Clarke/Park convention and define shadow-load timing separately from CPU computation completion.
- AEL-002 MCU order code/revision, clock tree, pin mux, QEP/eCAP/ePWM/ADC routing, interrupt priorities, DMA channels, PWM/ADC rates, ISR budget and WCET remain **TBD** pending exact board/SDK evidence. No peripheral route or hardware setting was invented.
- Existing CI workflow unchanged; branch workflow SHA remains \`7af60d723f8b98c2eeb1767c7251a8978fa3cfb3\`.
- No firmware build, static timing proof, SIL/HIL, oscilloscope measurement, physical inspection, sensor calibration, motor test, stack or power-up is claimed.
- **NO STACK / NO POWER** remains. No local device/filesystem access was used.
- Next task: Chapter 11 on embedded C architecture, memory model, fixed-point/numeric robustness, HAL/driver boundaries, state machines, fault handling and testable firmware interfaces; keep target-specific code/configuration TBD until exact MCU/SDK evidence is verified.


## Engineering Academy Chapter 10 — MCU real-time timing and scheduling (2026-11-28)

- Added \`docs/academy/10-mcu-real-time-timing-and-scheduling.md\` (47,049 characters).
- Re-read live Academy chapters 00–09, the lesson review checklist, Academy index, operator protocol, project state, PR #3 and current CI workflow before authoring.
- Chapter 10 covers generic clock-tree/PLL relationships, timer prescalers/ticks/period/overflow, input capture/output compare, QEP quadrature and x1/x2/x4, M/T speed estimation, asynchronous input synchronization/metastability/digital qualification, interrupt architecture/priority/nesting/latency/jitter, critical sections/race conditions/atomic snapshots, DMA double-buffer ownership/cache coherency, PWM time-base/ADC SOC/acquisition/conversion/aperture timing, sensor timestamp alignment to the Chapter 08 FOC Park transform, WCET/response-time/utilization/deadline misses, watchdog and overrun handling.
- Includes text timing diagrams, equations and dimensional checks, fully worked hypothetical calculations, 12 exercises with complete solutions, integrated firmware dataflow/pseudocode, TBD matrix, clock/timer/QEP/interrupt/ADC/DMA/FOC/fault verification templates and review questions.
- Cross-chapter timing contract: sensor measurement timestamp \(t_m\), ADC effective aperture \(t_s\), and PWM active-output update \(t_u\) are distinct. Park uses angle predicted to \(t_s\); output-application delay to \(t_u\) is a separate control-delay problem. The lesson explicitly avoids treating conversion-complete or ISR-entry time as the analog sample time.
- Clock/counter equations are generic models with endpoint semantics and prescaler encoding subject to the exact MCU TRM. ADC settling equation is an ideal first-order approximation, not a substitute for device minimum acquisition time or source-impedance validation.
- Actual AEL-002 MCU/board/revision, oscillator/PLL/clock tree, pin mux, QEP/eCAP/ePWM/ADC routes, interrupt priorities/nesting, DMA channel, cache/coherency policy, PWM/ADC rates and aperture, ISR budget/WCET, watchdog and overrun policy remain **TBD** until exact board/SDK evidence is available.
- Official TI references checked for C2000 peripheral overview and F28003x SYSCTL/ePWM/ADC DriverLib API concepts. These documents do not prove the project's actual board routing or installed SDK version.
- Updated Academy index and project state. The live operator protocol already queues Chapter 11 (embedded firmware architecture and robust C foundations), so its active task was preserved rather than overwritten.
- Existing CI workflow definition unchanged. No local device/filesystem access, firmware build/download, simulation, SIL/HIL, board inspection, signal measurement, motor test, stack or power-up was performed.
- **NO STACK / NO POWER** remains mandatory.


## Chapter 10 consolidation note (2026-11-28)

- The Academy index now points to one canonical Chapter 10: \`docs/academy/10-mcu-real-time-timing-and-scheduling.md\`.
- Consolidated additional timing-requirement and software fault-injection matrices plus supplementary references into the canonical lesson; removed the duplicate alternate Chapter 10 file to avoid two competing curricula entries.
- The operator protocol's live next task remains Chapter 11 (embedded firmware architecture and robust C foundations).


## Engineering Academy Chapter 11 — embedded C architecture and robust firmware (2026-11-28)

- Added \`docs/academy/11-embedded-c-architecture-and-robust-firmware.md\` (35,761 characters).
- Re-read live PR #3, branch/CI state, operator protocol, Academy chapters 00–10 (including the canonical Chapter 10), lesson review checklist, Academy index and existing CI workflow before authoring. Correct Chapter 00 path is \`00-learning-and-safety.md\`; canonical Chapter 10 is \`10-mcu-real-time-timing-and-scheduling.md\`.
- Covers integer widths/ranges/signedness, promotions and conversions, signed overflow UB versus unsigned modulo wrap, checked arithmetic/saturation, physical unit/range contracts, fixed-point Q scaling/product widths/rounding, floating-point precision/NaN/∞/FPU timing, C object lifetime and memory layout, stack/heap/static storage, linker sections/startup, pointer/alignment/aliasing, const/volatile/atomic distinctions, C11 memory order and lock-free/ISR caveats.
- Defines application/control/middleware/driver/HAL/platform layering and interface contracts; integrates Chapter 08 Clarke/Park sign/normalization, Chapter 09 rotor feedback timestamp/validity and Chapter 10 ADC aperture/DMA ownership/ISR/PWM update timing.
- Includes state-machine flow, set-dominant software fault latch, event/active/latched/clear/re-arm distinction, fault records, parameter schema/version/length/CRC/range/cross-field validation, CRC versus authenticity, dual-slot power-fail-safe NVM concept, host unit-test seams/fakes, property tests, static-analysis/build hygiene, code-review checklist, worked calculations, 12 fully solved exercises and numeric/interface/parameter/fault verification templates.
- Concurrency caution: volatile is not atomic or a lock; C11 atomics may not be lock-free/ISR-safe on a given compiler/ABI. DMA is not a C language thread and requires separate bus/cache/ownership rules. Example SPSC ring buffer is conditional on target lock-free atomic verification. Multi-field non-atomic seqlock payload is not presented as data-race-safe C.
- Fixed-point Q1.15 example explicitly defines 16-bit signed storage and F=15; Q notation ambiguity is called out. All target-specific scaling and Q formats remain TBD.
- Actual AEL-002 MCU/revision, compiler/ABI/C dialect, SDK, startup/runtime, linker file, memory map, stack/heap, FPU, atomic lock-free behavior, DMA memory/cache, HAL/peripheral drivers, parameter NVM schema and build/static-analysis flags remain **TBD** pending exact board/SDK/toolchain evidence.
- References include SEI CERT C INT32-C/INT02-C/INT30-C/INT31-C, C11 atomic memory-order reference and TI C2000 Code Generation Tools overview. References explain generic language/tool concepts; they do not establish AEL-002 toolchain configuration.
- Updated Academy index, project memory and operator queue. Next task: Chapter 12 on embedded communications and diagnostic services (UART/RS-485, CAN/CAN-FD, framing/serialization, arbitration, timeouts, bus-off/error recovery, command freshness/sequence, parameter transport and safe command semantics); keep exact physical interface, transceiver, baud/bit rate, pin mux, SDK and network topology TBD until evidence is available.
- Existing CI workflow unchanged (branch blob SHA \`7af60d723f8b98c2eeb1767c7251a8978fa3cfb3\`). No local device/filesystem access, target build, static analysis run, SIL/HIL, hardware inspection, measurement, motor test, stack or power-up is claimed.
- **NO STACK / NO POWER** remains mandatory.


## Engineering Academy Chapter 12 — embedded communications and diagnostics (2026-11-28)

- Added `docs/academy/12-embedded-communications-and-diagnostics.md` on branch `agent/ael-002-48v-modular-servo-brief`.
- Re-read the live PR #3, branch/head, operator protocol, Academy index, quality checklist, project state, CI workflow and Academy 00–11 lesson sources before authoring. PR #3 was open/draft/not merged at review time.
- Chapter 12 covers UART asynchronous framing/throughput, RS-485 differential physical layer, half-duplex DE/RE and UART transmission-complete ordering, termination/bias/stub/common-mode considerations; Classical CAN and CAN-FD frame fields, identifiers, non-destructive arbitration, bit timing, BRS, bus-load estimation, error-active/error-passive/bus-off and bounded recovery.
- Defines an educational delimiter/escape framing example and explicit little-endian serialization schema with version, type, flags, sequence, timestamp, payload length, payload and CRC-16/CCITT-FALSE parameters/test vector. Distinguishes link ACK from application received/accepted/applied acknowledgements and CRC from authentication.
- Defines modular sequence wrap/replay rejection, monotonic clock-domain rules, local receive-time freshness, per-message timeout, and stale command rejection.
- Separates command, telemetry, diagnostics, parameter transfer and firmware update services. Integrates Chapter 08 FOC limits/sign conventions, Chapter 09 sensor validity/timestamps, Chapter 10 DMA ownership/ISR/WCET, and Chapter 11 C serialization/parameter schema/fault records.
- Adds drive state and communication recovery state machines, bounded bus-off recovery, fault-injection matrix, protocol/message/timing verification templates, worked UART/RS-485/CAN/CAN-FD/sequence/CRC calculations and 15 fully solved exercises.
- Communication can read/acknowledge fault notifications but cannot clear FAULT_LATCH or directly enable PWM. Supervised clear returns only to DISARMED; link recovery never auto-resumes old torque/speed commands.
- Actual AEL-002 transceiver, connector/pinout, DE/RE mapping, UART baud, CAN controller/transceiver, nominal/data bit rates, CAN ID map, topology, termination/bias, isolation, protocol profile, timeout/stop profile, security model, SDK/driver/compiler remain TBD until exact board/BOM/peer/toolchain evidence is available.
- Generic sources: TI RS-485 Design Guide SLLA272D; TI fail-safe biasing article; CiA CAN-FD basic concept and technical documents; ISO 11898-1. They explain generic protocol behavior, not AEL-002 hardware integration.
- Updated Academy index and operator queue. Next task: Chapter 13 system integration and verification architecture—derive end-to-end timing/latency budgets across Chapters 08–12, define SIL/host fault-injection and interface conformance strategy, trace safety requirements to tests, and retain all target/hardware settings as TBD until evidence exists.
- Existing CI workflow remains unchanged (blob SHA `7af60d723f8b98c2eeb1767c7251a8978fa3cfb3`). No local device/filesystem access, target build, bus measurement, SIL/HIL, physical inspection, hardware test, stack or power-up is claimed.
- **NO STACK / NO POWER** remains mandatory.


## Engineering Academy Chapter 13 — system integration and verification architecture (2026-11-28)

- Added `docs/academy/13-system-integration-and-verification-architecture.md` (approximately 30k characters). Re-read live PR #3, branch/head, CI, operator protocol, index, checklist, project state and canonical Academy 00–12 before authoring.
- Defines measurable shall requirements, acceptance criteria, bidirectional traceability, verification vs validation, analysis/inspection/demonstration/test, model verification vs validation, and internal E0–E6 evidence classes (explicitly not an ISO/IEC maturity scheme).
- Integrates Chapters 08–12 with timestamp distinctions (sensor measurement, ADC aperture, control compute, PWM write, hardware load), end-to-end timing/WCET budget, phase-delay calculation, interface contracts for ADC/FOC/PWM, QEP/Hall/Resolver, DMA, communications, parameter transactions, telemetry and fault manager.
- Defines fault-to-safe-state trace, set-dominant latch, deterministic fault injection, host/unit/fuzz/SIL/HIL/target/physical evidence boundaries, reproducible test record/configuration baseline and G0–G5 release gates.
- Adds worked timing/utilization/phase-error/fault-latency calculations, 18 fully solved exercises, 13 draft integration requirements and 16 fault-injection cases.
- Introduces claim-by-claim source triangulation. Added reusable `docs/academy/SOURCE_REVIEW_REGISTER.md`; updated lesson review checklist to require source role, edition/location, independent cross-check, normative-vs-informative distinction, discrepancy handling and independent calculation checks.
- Sources checked: NASA Systems Engineering Handbook (requirements verification matrix, validation matrix, integration/V&V), IEEE 1012-2024 public scope, IEC 61508-3:2010 catalogue and 2026 FDIS status, IEC 61800-5-2:2016+AMD1:2026 catalogue, TI SPRACN0F Rev. F, TI SPRAD12A Rev. A, TI MotorControl SDK official guide/release page. Full paid standard text was not accessed; no clause-level compliance claim is made. IEC 61508-3:2026 is pre-release/FDIS, not yet a published final edition.
- Corrected a malformed CiA CAN-FD URL in Chapter 12 and expanded its source list with CiA 601 series, Microchip MCP25xxFD controller reference manual, TI ISO15/ISO35 transceiver datasheet and TI RS-485 FAQ. These are complementary sources, not evidence that AEL-002 uses those parts.
- Updated Academy index and source register. Next task: Chapter 14 on power semiconductor and gate-driver architecture—MOSFET/GaN/IGBT operating limits, gate charge/Miller plateau, dv/dt and common-source inductance, deadtime/shoot-through, bootstrap/isolated supplies, UVLO, OCP/short-circuit/desaturation protection and fault propagation. Require multi-source official/professional cross-checking; keep actual BOM, driver, bus voltage/current, gate resistance and timing TBD.
- Actual AEL-002 motor/load, board revision, MCU/compiler/SDK, ADC/PWM timing, sensors, DMA, communication hardware/network, hardware inhibit and physical test remain TBD. G0/G1 documentation only; no G2/G3/G4 or G5 physical test claimed.
- Existing CI workflow unchanged (blob SHA `7af60d723f8b98c2eeb1767c7251a8978fa3cfb3`). No local device/filesystem access, target build, SIL/HIL, timing measurement, safety certification, hardware test, stack or power-up is claimed.
- **NO STACK / NO POWER** remains mandatory.


## Engineering Academy Chapter 14 — power semiconductors and gate-driver architecture (2026-11-28)

- Added `docs/academy/14-power-semiconductors-and-gate-driver-architecture.md` (~25,851 characters). Re-read live PR #3, branch/head, CI, operator protocol, Chapters 07/08/11/12/13, quality checklist, project state and BOOSTXL/SENS007 interface audits before authoring.
- Covers silicon MOSFET, enhancement-mode GaN HEMT and IGBT conduction/switching behavior; device datasheet comparison; gate charge/Qg/Qgd, Miller plateau, source/sink current, gate resistor, gate/power loop, common-source inductance, dv/dt/di/dt and parasitic false turn-on.
- Derives worst-case deadtime budget and shoot-through/reverse-conduction trade-off; compares low-side, level-shift/half-bridge, bootstrap and isolated bias architectures; explains UVLO, Miller clamp, OCP, DESAT, soft turn-off and system fault-latch authority.
- Includes hypothetical Miller current, gate current, deadtime, bootstrap capacitor, conduction/switching/gate-drive loss and stored-energy calculations; 18 fully solved exercises; AEL-002 requirement and verification templates.
- Multi-source official/professional review: Infineon AN_2203_PL18_2204_004502 V1.0 (2022-04-20), Infineon gate-driver requirement/feature guides, TI SLUAAM3 (2022-08) and SLYA091 (2024-12), TI SLLA456, EPC AN003 and eGaN drive paper, Infineon CoolGaN layout and AN-1123 Rev.1.01 (2024-11-20), ST STGAP4S DS13833 Rev.6 (2024-12) and AN5789 Rev.1 (2022-03), onsemi AND9987/D, IEC 61800-5-1:2022 corrected through 2025-12 and IEC 61800-5-2:2016+AMD1:2026 catalogue scopes.
- Scope caveats: Infineon AN_2203 explicitly covers silicon MOSFET, not IGBT/WBG. STGAP4S is a reference driver only, not an AEL selection. Paid IEC normative text was not reviewed clause-by-clause; no compliance/STO claim is made. Manufacturer app notes are informative, device-specific guidance.
- Updated Academy index and source review register with Chapter 14 claim groups, revisions, independent cross-checks and limitations. Next task: Chapter 15 on current sensing and analog front-end for motor control—shunt topology/Kelvin routing, current-sense amplifier/isolated sensing, common-mode/transient recovery, anti-alias filtering, ADC input acquisition/kickback, offset/gain/phase calibration, comparator fast path, uncertainty and fault diagnostics. Keep exact AEL-002 shunt, amplifier, ADC route, gains, bandwidth, current limits and calibration TBD.
- Actual AEL-002 power device/driver, gate bias, deadtime, protection thresholds, power bus/current, thermal path, board revision and physical test remain TBD. No target build, double-pulse test, switching waveform, HIL or hardware measurement performed.
- Existing CI workflow remains unchanged (blob SHA `7af60d723f8b98c2eeb1767c7251a8978fa3cfb3`). No local device/filesystem access. **NO STACK / NO POWER** remains mandatory.
