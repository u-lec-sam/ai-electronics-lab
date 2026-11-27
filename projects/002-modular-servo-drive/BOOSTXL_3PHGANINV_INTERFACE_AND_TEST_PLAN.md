# AEL-002 — BOOSTXL-3PHGANINV controller interface and guarded validation plan

**Evidence date:** 2026-11-27  
**Power board:** BOOSTXL-3PHGANINV, schematic SENS007 Rev A (2018-01-24), EVM guide SLUUBP1A Rev A (2018-04)  
**SDK evidence:** Motor Control SDK Universal Project and Lab, SPRUJ26A Rev A (2024-04)  
**Status:** documentary interface review only; no boards inspected, no continuity measurements, no firmware build, no energized test, and no approval to apply power.

## 1. Compatibility decision

**LAUNCHXL-F280039C + BOOSTXL-3PHGANINV is an explicitly documented TI MotorControl SDK evaluation pairing.** The April 2024 revision of TI's Universal Project and Lab guide §3.2.12 names LAUNCHXL-F280025C, LAUNCHXL-F280039C, and LAUNCHXL-F2800137 for this inverter, directs connection to LaunchPad sites J1/J3 and J4/J2, and shows the assembly in Figure 3-14. Its Table 3-1 lists the same three controller kits for BOOSTXL-3PHGANINV.

This is stronger and more current evidence than relying only on the generic BoosterPack connector. It corrects the earlier statement that F280039C was necessarily a custom integration.

**Source-list discrepancy retained:** TI's BOOSTXL-3PHGANINV product page separately lists LAUNCHXL-F280049C, LAUNCHXL-F28379D, and LAUNCHXL-F280025C. The 2024 Universal Lab guide's specific inverter row instead lists F280025C, F280039C, and F2800137. Do not merge these lists into one unqualified compatibility claim. For the AEL-002 MotorControl SDK workflow, the 2024 guide is the specific board setup evidence; product-page recommendations remain a separate vendor-published list whose exact SDK project/revision mapping needs confirmation.

## 2. Board-level facts from official TI documents

- EVM user guide SLUUBP1A Rev A: DC input 12–60 V, nominal 48 V; three LMG5200 integrated 80-V/10-A GaN half-bridges; each phase has a 5-mΩ inline shunt and INA240 current-sense amplifier, gain 20 V/V, output midpoint 1.65 V.
- Interface signals: six complementary phase PWM inputs (AH/AL, BH/BL, CH/CL); three phase-current analog feedback signals; three scaled phase-voltage feedback signals; scaled DC-link voltage; active-low PWM enable; active-low PCB over-temperature alert; 3.3-V interface supply.
- PWM is buffered on the EVM. The host's active-low PWM enable controls the common buffer output enable.
- Hardware OCP: TLV3201 comparator-based circuit; user guide states 12-A trip threshold and 1-A hysteresis. This is a board protection threshold, not a motor operating current target or a substitute for firmware/bench limits.
- Thermal monitor: TMP302 near the GaN stage; active-low alert to the host.
- Current-feedback polarity caveat: the EVM guide says I_A/I_B/I_C equivalent output voltages at J1-14/J1-16/J1-18 are inverted versus the DRV8301 BoosterPack. Preserve the EVM-specific polarity in ADC scaling and control configuration.
- Power: EVM generates 5 V from the bus using LM5017, has a 3.3-V LDO and 3.3-V reference. Jumper J6, when fitted, supplies 3.3 V to LaunchPad interface J1-1 with a maximum continuous current of 300 mA. Do not simultaneously power the LaunchPad from USB with J6 fitted; remove J6 for USB-powered debug or use the vendor-specified power jumper arrangement.
- The EVM guide's current limit description and product-page rating differ from the MotorControl SDK table: the product page says 7 A RMS per phase; SPRUJ26A Table 3-1 describes the inverter as 3.5 A. Neither value should be assumed as a safe continuous application rating without confirming test conditions, cooling, PCB revision, and thermal derating. The 12-A hardware OCP threshold is not a continuous rating.

## 3. Controller comparison and support classification

| Controller | Vendor evidence for BOOSTXL-3PHGANINV | Controller capability / integration notes | Classification |
|---|---|---|---|
| LAUNCHXL-F280039C | SPRUJ26A §3.2.12 and Table 3-1 explicitly name it; Figure 3-14 shows the pairing | F28003x C28x/CLA real-time control; LaunchPad provides PWM/ADC/GPIO/encoder peripherals; use the exact F28003x LaunchPad guide, schematic and SDK board configuration for pin mux and sampling setup | **Documented TI SDK pairing** |
| LAUNCHXL-F280025C | SPRUJ26A §3.2.12 and Table 3-1 explicitly name it; also on TI product page | Same published connection sites in §3.2.12; compare exact resource/timing needs against F280039C | **Documented TI SDK pairing; also product-page listed** |
| LAUNCHXL-F2800137 | SPRUJ26A §3.2.12 and Table 3-1 explicitly name it; Figure 3-14 | Vendor guide notes board-specific switch/feature constraints in nearby setup material; check the F2800137 section and switch configuration, especially SFRA/serial function sharing | **Documented TI SDK pairing** |
| LAUNCHXL-F280049C | Listed on BOOSTXL-3PHGANINV product page; not named in SPRUJ26A Table 3-1's specific inverter row | Do not infer that the 2024 Universal Lab configuration is identical; obtain exact SDK example, pin map and revision evidence before choosing it for this workflow | **Vendor product-page listed; exact current SDK row not confirmed here** |
| LAUNCHXL-F28379D | Listed on BOOSTXL-3PHGANINV product page; not named in SPRUJ26A Table 3-1's specific inverter row | Older C2000 platform; verify exact software example and board header mapping independently | **Vendor product-page listed; exact current SDK row not confirmed here** |

**Decision:** retain F280039C as the AEL-002 primary controller candidate. For the named TI MotorControl SDK Universal Lab route, it is not a custom controller pairing. A custom adapter or custom software port is only needed if AEL-002 changes the documented board revisions, connector topology, or software configuration, or if a pin-level audit identifies a mismatch.

## 4. Controller-to-inverter interface matrix

The matrix below is the functional contract supported by the EVM guide and schematic. Do not invent MCU GPIO numbers: the EVM guide describes signals and header sites, while exact F280039C GPIO/ADC/ePWM mux assignments must be cross-checked against the matching LaunchPad schematic/pinout and the selected SDK board configuration before connection.

| Interface | EVM-side signal | Direction | Required controller resource | Electrical / behavior contract | Verification status |
|---|---|---|---|---|---|
| PWM phase A | PWM_AH, PWM_AL | MCU → EVM | Two synchronized ePWM outputs | Complementary timing, configured dead-band and safe inactive state; EVM buffers inputs | Signal function verified; F280039C pin mux still to cross-check |
| PWM phase B | PWM_BH, PWM_BL | MCU → EVM | Two synchronized ePWM outputs | Same as phase A; phase alignment/synchronization required | Signal function verified; pin mux still to cross-check |
| PWM phase C | PWM_CH, PWM_CL | MCU → EVM | Two synchronized ePWM outputs | Same as phase A; phase alignment/synchronization required | Signal function verified; pin mux still to cross-check |
| Phase current | I_A, I_B, I_C | EVM → MCU | Three ADC channels with PWM-synchronous sampling | INA240 gain 20 V/V, 1.65-V midpoint, 5-mΩ shunt; current feedback polarity inversion is called out at J1-14/16/18 | Analog chain verified; exact ADC pin map and scaling calibration pending |
| Phase voltage | V_A, V_B, V_C | EVM → MCU | Three ADC channels | Scaled and low-pass-filtered phase voltage; verify scale, offset, filter and ADC input range from schematic | Functional signals verified; calibration and exact pin map pending |
| DC bus voltage | V_DC | EVM → MCU | ADC channel | Scaled DC-link feedback; compare against independently measured bus voltage before control use | Functional signal verified; exact transfer function and pin map pending |
| PWM inhibit | /PWM enable | MCU → EVM | GPIO output, default inactive | Active-low common enable; firmware reset/boot must hold output disabled; external safe-state must not depend on software alone | Polarity/function verified; controller GPIO assignment pending |
| PCB overtemperature | /PCB OT alert | EVM → MCU | GPIO input/interrupt | Active-low alert from TMP302 thermal monitor; latch fault and disable PWM | Polarity/function verified; exact threshold and pin map pending |
| Hardware OCP | Internal EVM comparator/protection path | EVM internal; affects PWM path | EVM protection plus controller fault-state handling | TLV3201 threshold 12 A, 1-A hysteresis per guide; verify actual shutdown path on schematic and fault behavior before power | Threshold stated; dynamic trip path and recovery test pending |
| Logic supply | 3.3 V | EVM ↔ LaunchPad supply domain | LaunchPad 3.3-V rail | J6 connects EVM 3.3 V to J1-1; max 300 mA. Avoid USB back-power conflict | Voltage and current limit verified; jumper/power plan pending |
| Ground/reference | GND, PGND | Common reference domains as designed | Signal and power reference | Do not assume galvanic isolation. Verify EVM schematic ground strategy, LaunchPad ground and measurement instrument earth before connecting probes/USB | Ground relationship requires explicit bench wiring review |
| Encoder | Encoder connector/interface per SDK setup | Motor/encoder → controller | eQEP plus required receiver/input conditioning | SDK documents encoder connection and Table 3-2 signal wiring for its tested motors; encoder voltage, differential receiver and supply depend on selected encoder | Generic support documented; exact motor/encoder not selected |
| Hall sensors | Hall connector/interface per SDK setup | Motor → controller | GPIO/capture resources as configured | SDK documents Hall path and tested wiring; do not assume Hall support means every sensor voltage/pinout is compatible | Generic support documented; exact sensor TBD |
| Communications | USB/XDS110, UART/CAN on LaunchPad | Host ↔ controller | Debug/communications peripherals | Not part of the inverter power connector contract; validate USB ground path and selected CAN transceiver separately | Board-specific review pending |

### Connector and power notes

- SPRUJ26A §3.2.12 directs BOOSTXL-3PHGANINV to LaunchPad sites J1/J3 and J4/J2 for F280025C/F280039C/F2800137.
- The older EVM guide §2.3 describes BoosterPack-standard header mating and the alternate extended headers. Match the actual LaunchPad revision and board orientation; do not rely on header names alone.
- EVM guide §2.2: J6 fitted powers LaunchPad J1-1 at 3.3 V, max 300 mA. For USB debug, remove EVM J5 to avoid dual-source/backfeed conflict.
- Motor power connector: J4, DC+ / DC−. Motor phase output connector: J3, V_A/V_B/V_C, as shown in the EVM guide.
- The schematic lists signal groups but does not by itself authorize a connector-to-MCU pin map for every LaunchPad revision. Resolve exact net-to-header-to-GPIO/ADC/ePWM mapping from the board-revision-matched LaunchPad schematic/pinout and SDK configuration. No hand-wired adapter is approved until that table is complete.

## 5. Staged current-limited validation plan — HOLD POINT

**No board is to be energized under this record.** This is a future procedure outline, not authorization to apply power. The user has not supplied a motor, encoder, bench supply, supply sink capability, load/inertia, cooling, or a test operator/guarding setup. A qualified engineer must review the exact hardware revisions and test setup before any power is connected.

| Gate | Activity (power state) | Required evidence / pass condition | Stop condition |
|---|---|---|---|
| V0 — document/revision audit (unpowered) | Identify EVM and LaunchPad PCB revisions; obtain current datasheets, errata, schematics, SDK version and board configuration | Revision-matched pin map for all PWM/ADC/GPIO/supply/ground signals; connector orientation confirmed; no conflicts | Any unknown net, pin collision, voltage mismatch, undocumented jumper, or inconsistent revision |
| V1 — unpowered inspection (unpowered) | Inspect board condition, solder bridges, connectors, standoffs, shorts; continuity-check DC rails and grounds using a documented procedure | Inspection and resistance readings reviewed; no unintended short; EVM not physically damaged | Any unexpected continuity, damage, contamination, or unclear ground/earth path |
| V2 — controller-only logic validation (power only after V0/V1 sign-off) | Power LaunchPad alone through its documented source; verify reset/boot, XDS110, firmware state and GPIO safe defaults; inverter disconnected | PWM outputs remain inactive during reset, boot, watchdog and fault; /PWM enable remains inactive | Any PWM glitch, unexpected GPIO state, brownout, USB/back-power ambiguity |
| V3 — EVM auxiliary rails (power only after V0–V2 sign-off) | EVM DC input disconnected from motor; use a bench supply with a pre-approved current limit derived from EVM idle behavior and test equipment; start at the lowest vendor-allowed input voltage | Verify 5-V, 3.3-V and reference rails, polarity, ripple and thermal behavior; compare bus voltage with meter; no motor attached | Current limit reached unexpectedly, rail out of tolerance, heating, smell, abnormal noise, or voltage rise |
| V4 — control I/O without gate activity (power only after V0–V3 sign-off) | Keep PWM buffer disabled; observe all six PWM signals, active-low enable, OT alert and ADC values using appropriately rated isolated/differential instruments | PWM frequency, phase order, complementary behavior and ADC offset/scale agree with configuration; no gate drive enabled | Any unexpected gate activity, unsafe common-mode measurement, wrong polarity or ADC saturation |
| V5 — protection verification (power only after written review) | Verify hardware OCP and thermal-alert behavior using vendor-approved non-destructive method; do not deliberately force destructive overcurrent or overtemperature | Fault causes hardware PWM disable, firmware fault latch and safe restart interlock; capture thresholds/timing | Protection path cannot be proven, fault does not latch, or shutdown depends only on firmware |
| V6 — no-load / low-energy power-stage check (only after all prior gates) | Motor disconnected; current-limited supply set by approved test plan; gate enable only under remote/independent disconnect and guarded setup | Phase switching and bus behavior remain within device and instrument limits; current waveform expected | Overcurrent, bus overshoot, unexpected phase output, ringing beyond limits, thermal rise |
| V7 — motor identification and first rotation (only after motor data and regeneration plan) | Mechanically restrained motor, low-energy/current-limited test, conservative speed/torque limits calculated from motor and EVM data | Correct phase order, encoder/Hall direction, current scaling, commutation alignment and independent stop verified | Unexpected rotation, wrong feedback direction, current limit trip, vibration, overspeed, bus rise |
| V8 — controlled servo/load test (only after V7 and independent review) | Increase torque/speed/duty in documented increments with load guarding and thermal monitoring | Measured current, bus, temperature, speed and tracking remain inside approved envelope; regenerative energy handled | Any thermal trend, supply sink limit, bus overvoltage, fault, guarding or emergency-stop failure |

### Mandatory preconditions before any energized gate

1. Board revision and all connector-to-controller pins confirmed from official schematics/pinout.
2. Supply min/max, current limit, isolation/earth, transient response and regenerative sink capability known. If supply cannot sink energy, a separately engineered braking-energy path and bus-overvoltage protection are required before deceleration.
3. Motor model and datasheet available: phase current RMS/peak, resistance/inductance, back-EMF, pole pairs, speed/torque limits, winding temperature and inertia.
4. Encoder/Hall electrical interface and exact pinout/supply confirmed; no direct connection based only on connector fit.
5. Current limit set below the lowest applicable board/motor/wiring limit and derived from an approved test plan; do not substitute the EVM OCP threshold as the operating current limit.
6. Independent emergency disconnect, physical guarding, safe probe/measurement plan, discharge verification and qualified operator present.
7. J6/USB power-source selection explicitly reviewed; no dual-source condition.
8. Regenerative energy and bus overshoot are bounded before any powered deceleration test.

## 6. Open verification items

- Extract exact F280039C LaunchPad connector pin assignments from the matching SPRR444A schematic/pinout and reconcile each EVM net to a GPIO/ePWM/ADC channel in the selected MotorControl SDK configuration.
- Verify the exact SDK release and project target files for F280039C and BOOSTXL-3PHGANINV; the guide's April 2024 revision is the current evidence used here, not proof that all future SDK versions preserve the same project.
- Resolve the 3.5-A SDK table versus 7-A RMS product-page current statement with detailed EVM thermal/test conditions. Do not claim a continuous 7-A operating point.
- Verify OCP comparator signal propagation, PWM buffer disable polarity, TMP302 trip behavior and fault recovery from schematic plus non-destructive test method.
- Complete motor, encoder, supply, regenerative sink, load/inertia, motion profile, duty and cooling intake before numeric bench current limits or power-stage sizing.
- Confirm grounding, USB/XDS110 earth path, oscilloscope probe method and any isolation requirements.

## 7. Official sources

- TI BOOSTXL-3PHGANINV EVM product page and its product-page supported LaunchPad list: https://www.ti.com/tool/BOOSTXL-3PHGANINV
- TI BOOSTXL-3PhGaNInv Evaluation Module User Guide, SLUUBP1A Rev A (April 2018): https://www.ti.com/lit/ug/sluubp1a/sluubp1a.pdf
- TI BOOSTXL-3PhGaNInv Schematic, SENS007 Rev A: https://www.ti.com/lit/df/sluray0a/sluray0a.pdf
- TI Motor Control SDK Universal Project and Lab, SPRUJ26A Rev A (April 2024), especially Table 3-1 and §3.2.12: https://www.ti.com/lit/ug/spruj26a/spruj26a.pdf
- TI LAUNCHXL-F280039C product page and schematic/user-guide links: https://www.ti.com/tool/LAUNCHXL-F280039C

## 8. Result

F280039C is confirmed as a TI-documented MotorControl SDK evaluation pairing for BOOSTXL-3PHGANINV by SPRUJ26A Rev A, resolving the earlier false-negative inference from the product-page list alone. Exact GPIO/ADC/ePWM pin map, board revision match, power/ground configuration, current/thermal operating point and bench protection behavior remain open. **No power application, motor rotation, or hardware test is authorized or claimed.**

## 9. Corrected physical header crosswalk — SENS007 Rev A ↔ LAUNCHXL-F280039C Rev A

**Correction:** the earlier claim that EVM J2/J4-40 collided with LaunchPad J4-40 GND was wrong. It mixed connector site naming/side orientation. The TI LaunchPad Rev A schematic explicitly identifies BoosterPack Site 1 as J1/J3 (pins 1–30) plus J4/J2 (pins 11–40); its pin 40 is GPIO0, not GND. The EVM SENS007 Rev A schematic labels the corresponding mating header pairs J1/J3 and J2/J4. TI's MotorControl SDK SPRUJ26A §3.2.12 explicitly instructs connecting BOOSTXL-3PHGANINV to LaunchPad J1/J3 and J4/J2 and names LAUNCHXL-F280039C as a supported target. The earlier false conflict is therefore closed at the **documented header-site and numbering level**.

**Orientation / pin-1 interpretation:**
- TI SENS007 Rev A assembly drawing SLURAY2 shows both top-side and bottom-side assembly views. The BoosterPack headers are on the EVM underside; the bottom-side view shows the J1/J3 header pair above the J2/J4 pair in that drawing view. SENS007 top-overlay SLURAY3 identifies the component-side view.
- TI LAUNCHXL-F280039C Rev A schematic SPRR444A sheet 2 labels Site 1 as the top BoosterPack site and identifies J1/J3 and J4/J2 header pairs with their numbered pins.
- TI SDK SPRUJ26A Figure 3-14 and §3.2.12 show the supported stacked configuration and explicitly name the two mating header sites.
- Therefore the correct physical relationship is **EVM J1/J3 ↔ LaunchPad Site-1 J1/J3** and **EVM J2/J4 ↔ LaunchPad Site-1 J4/J2**, not a comparison of EVM connector labels to a LaunchPad header of a different site.
- The published drawings establish connector pair and pin numbering. They do not prove the as-received sample's pin-1 marker, solder quality, or board revision. Before physical mating, visually verify pin-1/square-pad marks on both boards and confirm the exact board silkscreen/revision. Do not infer pin-1 solely from a top-vs-bottom image without flipping the view correctly.

### 9.1 Analog, supply and ground crosswalk — J1/J3

| EVM SENS007 J1/J3 pin | EVM net | LaunchPad Site-1 J1/J3 pin | F280039C LaunchPad Rev A net / function | Status |
|---:|---|---:|---|---|
| 1 | 3V3_LaunchPad_IN | 1 | +3V3_MCU | **Pin/site mapping confirmed**; EVM optional 3.3-V feed jumper J5 and LaunchPad power-source selection must be inspected before use |
| 21 | NC (5V_LaunchPad) | 21 | +5V0_MCU | **No connection on EVM side**; do not treat as a 5-V supply path |
| 22 | GND | 22 | GND | **Confirmed signal-ground return** |
| 23 | VDC | 23 | ADCINA6 | **Confirmed analog mapping** |
| 24 | VA | 24 | ADCINA2 / ADCINB6 / ADCINC9 mux-capable input | **Confirmed analog mapping**; select ADC module/channel per SDK |
| 25 | VB | 25 | ADCINA3 / ADCINB9 / ADCINC7 mux-capable input | **Confirmed analog mapping**; select ADC module/channel per SDK |
| 26 | VC | 26 | ADCINA14 / ADCINB14 / ADCINC4 mux-capable input | **Confirmed analog mapping**; select ADC module/channel per SDK |
| 27 | IA | 27 | ADCINA11 / ADCINB10 / ADCINC0 mux-capable input | **Confirmed analog mapping**; account for EVM-specific current-sense polarity |
| 28 | IB | 28 | ADCINB12 / ADCINC2 mux-capable input | **Confirmed analog mapping** |
| 29 | IC | 29 | ADCINA7 / ADCINC3 mux-capable input | **Confirmed analog mapping** |
| 30 | VREF | 30 | ADCINA1 / ADCINB7 mux-capable input | **Connector mapping confirmed**; determine whether SDK uses this feedback/reference pin before enabling ADC channel |

All EVM analog outputs are conditioned signals intended for the 3.3-V LaunchPad ADC domain. The SENS007 schematic shows 20-Ω series resistors and input protection/filtering on these signals. Exact ADC SOC timing, acquisition window, ADC module selection, scaling, offsets and current polarity still require SDK/HAL configuration review and later unpowered/low-energy calibration.

### 9.2 Six PWM crosswalk — J2/J4

The SENS007 interface sheet routes the first six EVM J2/J4 pins (40 down to 35) to U4 A1–A6 in order. U4 B1–B6 are explicitly labeled PWM_AH, PWM_AL, PWM_BH, PWM_BL, PWM_CH and PWM_CL. LaunchPad SPRR444A Site-1 J4/J2 maps those same numbered pins to GPIO0, GPIO1, GPIO2, GPIO3, GPIO10 and GPIO11.

| EVM SENS007 J2/J4 pin | U4 input channel | EVM output net | LaunchPad Site-1 J4/J2 pin | F280039C GPIO | MCU peripheral candidate |
|---:|---|---|---:|---|---|
| 40 | A1 → B1 | PWM_AH | 40 | GPIO0 | ePWM1A |
| 39 | A2 → B2 | PWM_AL | 39 | GPIO1 | ePWM1B |
| 38 | A3 → B3 | PWM_BH | 38 | GPIO2 | ePWM2A |
| 37 | A4 → B4 | PWM_BL | 37 | GPIO3 | ePWM2B |
| 36 | A5 → B5 | PWM_CH | 36 | GPIO10 | ePWM6A |
| 35 | A6 → B6 | PWM_CL | 35 | GPIO11 | ePWM6B |

The physical pin-to-pin and EVM channel order is confirmed by the SENS007 schematic and SPRR444A LaunchPad connector schematic. The ePWM peripheral labels above are the device GPIO-mux functions to be checked against the exact F28003x datasheet/SDK target configuration before firmware output is enabled. Complementary dead-band, synchronization, polarity and trip-zone behavior are not validated by this wiring table.

### 9.3 Protection, enable and auxiliary GPIO — direct schematic trace

The rendered original SENS007 Rev A sheet 5 resolves the earlier OCR ambiguity. See the full trace and power-link evidence in [SENS007 enable and power-jumper audit](SENS007_ENABLE_AND_POWER_JUMPER_AUDIT.md).

| EVM SENS007 signal | Exact SENS007 connection | LaunchPad Site-1 counterpart | Status |
|---|---|---|---|
| Active-low MCU enable request | J2/J4 pin 11 → `nEn_uC` → U12 SN74LVC1G32 input 1 | J4/J2 pin 11; SPRR444A shows GPIO22/GPIO23 selectable route | **EVM pin confirmed.** Exact LaunchPad GPIO route requires board routing/SDK configuration check. |
| OCP input | Internal `IComp` → U12 input 2; R79 is the 0-Ω OCP link | Internal to EVM | **Schematic path confirmed.** Do not remove R79 or bypass OCP. |
| Buffer enable | U12 output `nEnable` → U4 SN74AVC8T245 OE, package pin 22 | No separate header pin | **Internal net confirmed.** Active-low; nOE=0 enables U4. Do not treat U4 pin22 as connector pin22. |
| Buffer direction | J2/J4 pin 19 → U4 DIR, package pin 2; R28 10-kΩ pull-up | J4/J2 pin19, GPIO5_BP | **EVM pin confirmed.** Default DIR='1', A→B. |
| PCB overtemperature | J2/J4 pin33 OT from TMP302 OUT | J4/J2 pin33, GPIO48 | **Header mapping confirmed.** Firmware threshold/polarity/fault response still require SDK/TMP302 review. |
| Signal ground | J2/J4 pin20 GND | J4/J2 pin20 GND | **Header mapping confirmed.** Grounding/earth setup remains a separate hold. |

The old candidate pin numbers 11/12/13/18 were caused by confusing connector pin numbers with U4 IC package pins and OCR reading order. In the original drawing U4 package pins 11/12/13 are GND and pin18 is B4; they are not alternative J2/J4 assignments for `nEn_uC` or `nEnable`. The external `nEn_uC` request is pin11; `nEnable` is the internal U12 output; U4 OE is package pin22; DIR is connector pin19. LaunchPad pin11 has a GPIO22/GPIO23 route notation, so do not hard-code one MCU GPIO until its routing and SDK configuration are confirmed.

### 9.4 Ground, 3.3-V and orientation limits

- EVM J1/J3-22 and J2/J4-20 are GND connections and mate with the corresponding LaunchPad Site-1 GND pins. The power connector J4 negative terminal is PGND; the schematic also exposes TP1=GND and TP2=PGND. Do not assume an arbitrary external earth/probe/USB connection is safe merely because the signal headers share GND.
- EVM J1/J3-1 is 3V3_LaunchPad_IN. EVM J5 is a two-pin optional link that can connect the EVM's 3.3-V rail to the LaunchPad. LaunchPad J1/J3-1 is +3V3_MCU. The EVM J1/J3-21 (+5V) is explicitly NC. Verify the EVM J5 link and LaunchPad power-domain jumpers before choosing one source; never parallel independent 3.3-V supplies or assume the EVM jumper is fitted.
- LaunchPad SPRR444A shows separate USB/XDS110/MCU power and ground domains with jumper-controlled isolation. The exact JP1/power jumper state and any USB cable earth path must be included in the bench plan.
- SENS007 has a separate DC input connector J4 (VBUS/PGND) and motor output J3 (VA/VB/VC). These are not the BoosterPack signal header J1/J3 or J2/J4 despite overlapping connector designators in different board contexts. Always qualify connector names with the board name.
- EVM assembly drawing SLURAY2 includes top- and bottom-side views. Its bottom-side view is the relevant view for underside BoosterPack header placement; reverse left/right when relating it to the component-side view. Use TI SDK Figure 3-14 for the stacked orientation reference, and inspect the actual pin-1/square-pad marks before mating.

## 10. Corrected result and remaining blockers

**Resolved from official documents:** F280039C is a documented TI MotorControl SDK pairing; the false pin-40/GND conflict is closed; EVM-to-LaunchPad Site-1 J1/J3 analog pins 1, 21–30 and J2/J4 PWM pins 40–35 map by matching header pin numbers; six PWM GPIO routes and OT pin 33 are identified.

**Still unresolved:** exact nEn_uC/nEnable connector pin due conflicting schematic text extraction; as-received physical pin-1 marks/revisions; EVM J5 and LaunchPad power jumper state; GND/PGND/USB/earth measurement strategy; SDK project-specific ADC/PWM mux, SOC timing, fault handling; EVM current/thermal derating and supply regeneration.

**No-power hold remains in force.** The documentary crosswalk does not authorize stacking or energizing the hardware. First resolve the enable net and inspect actual board revisions/pin-1 marks while unpowered. No board was physically inspected, continuity-tested, stacked, powered, or driven during this work.

## 11. Official sources

- TI BOOSTXL-3PhGaNInv User Guide SLUUBP1A Rev A (April 2018): https://www.ti.com/lit/ug/sluubp1a/sluubp1a.pdf
- TI BOOSTXL-3PhGaNInv Schematic SENS007 Rev A (2018-01-24), especially sheets 2, 4 and 5: https://www.ti.com/lit/df/sluray0a/sluray0a.pdf
- TI BOOSTXL-3PhGaNInv Assembly Drawing SLURAY2 (top- and bottom-side views): https://www.ti.com/lit/df/sluray2/sluray2.pdf
- TI BOOSTXL-3PhGaNInv PCB top overlay SLURAY3: https://www.ti.com/lit/df/sluray3/sluray3.pdf
- TI LAUNCHXL-F280039C Schematic SPRR444A Rev A, especially sheet 2 (Site-1 header pinouts): https://www.ti.com/lit/df/sprr444a/sprr444a.pdf
- TI LAUNCHXL-F280039C User Guide SPRUJ31: https://www.ti.com/lit/ug/spruj31/spruj31.pdf
- TI F280039C Pinout Map SPRUJ30: https://www.ti.com/lit/ml/spruj30/spruj30.pdf
- TI Motor Control SDK Universal Project and Lab SPRUJ26A Rev A (April 2024), §3.2.12 and Figure 3-14: https://www.ti.com/lit/ug/spruj26a/spruj26a.pdf
- TI LAUNCHXL-F280039C product page: https://www.ti.com/tool/LAUNCHXL-F280039C

## 12. Final conclusion

The prior J4-40/GND conflict was an interpretation error, not a documented incompatibility. Official drawings support a direct Site-1 header-number crosswalk for the analog and six PWM signal groups, and the SDK guide explicitly documents this board pairing. The OT signal also maps to the same-numbered GPIO header position. The active-low enable/control net remains ambiguous in the parsed schematic evidence and is deliberately left unresolved. **Do not stack or apply power until this enable-pin ambiguity, sample pin-1 orientation, board revision and power/ground jumper states are verified.**


## Enable/power-link audit update

See [SENS007_ENABLE_AND_POWER_JUMPER_AUDIT.md](SENS007_ENABLE_AND_POWER_JUMPER_AUDIT.md) for the rendered-sheet-5 net trace, correction of the J5 designator, LaunchPad JP1/JP2A/JP2B vs JP4–JP7 distinctions, and the remaining sample-specific no-power hold. The SENS007 nEn_uC and DIR header pins are resolved at the schematic level; actual board revisions, pin-1 marks and jumper population remain unverified.
