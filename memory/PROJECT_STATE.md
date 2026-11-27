# Current Project State

**Snapshot date:** 2026-11-27 (updated after live branch review)nics-lab`  
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
