# AEL-002 — SENS007 enable-net and power-jumper documentary audit

- Date: 2026-11-27
- Evidence branch: `agent/ael-002-48v-modular-servo-brief`
- Scope: TI SENS007 Rev A (SLURAY0A), BOOSTXL-3PHGANINV assembly drawing SLURAY2 and PCB drawing SLURAY3; LAUNCHXL-F280039C schematic SPRR444A Rev A; TI product-page design-file listings.
- Status: documentary schematic/board-drawing audit only. No physical sample inspected, no continuity test, no mating, no power applied.

## 1. Direct SENS007 sheet-5 trace: ambiguity resolved

The earlier text-extraction ambiguity is resolved by inspecting the rendered original schematic page 5 (PDF page index 4), not by relying on OCR token order.

| Function | SENS007 Rev A connector / IC | Directly traced net path | Conclusion |
|---|---|---|---|
| Active-low MCU request | BoosterPack signal header J2/J4 pin 11 | J2/J4-11 → `nEn_uC` → U12 SN74LVC1G32 input 1 | **Confirmed: EVM header pin 11** |
| OCP combination | Internal signal | `IComp` → U12 input 2; R79 is shown as a 0-ohm OCP link and R80 10-kΩ pull-down path | OCP is combined in hardware; do not bypass/alter R79 |
| Buffer enable | U12 output `nEnable` → U4 SN74AVC8T245 OE, package pin 22 | **Internal net only; not a separate J2/J4 connector pin** |
| Buffer direction | J2/J4 pin 19 → U4 DIR, package pin 2 | R28 10-kΩ pull-up to 3V3; schematic note DIR='1', A→B | **Confirmed: EVM header pin 19**; default direction is A→B |
| Buffer OE logic | U4 OE, package pin 22 | Schematic note nOE='0' enabled; U12 OR gate output `nEnable` drives it | Active-low output-enable; OCP can force disable |

Thus 11/12/13/18 were not four competing connector assignments. The correct separation is:
- J2/J4-11 = external `nEn_uC` request.
- `nEnable` is the internal U12 output, not a host connector signal.
- U4 pin 22 is the IC's OE pin, not header pin 22.
- U4 pins 11/12/13 are IC ground pins; U4 pin 18 is B4, a buffer data output. Confusing U4 package pins with J2/J4 header pins explains the extracted 12/13/18 candidates.
- J2/J4-19 = DIR input.

### LaunchPad-side correspondence

SPRR444A Rev A sheet 2 identifies BoosterPack Site-1 as J1/J3 (pins 1–30) plus J4/J2 (pins 11–40):
- SENS007 J2/J4-11 mates with LaunchPad Site-1 J4/J2-11. LaunchPad schematic labels the GPIO route at this position as GPIO22/GPIO23; the exact selectable MCU route/configuration must be checked against the actual board population/routing before firmware assignment. Do not silently collapse this to one GPIO.
- SENS007 J2/J4-19 DIR mates with LaunchPad Site-1 J4/J2-19, GPIO5_BP.
- J2/J4-20 GND mates with Site-1 J4/J2-20 GND.
- The already audited PWM pins 40..35 and OT pin 33 remain as previously recorded.

## 2. EVM J5 and board revision / pin-1 evidence

- SENS007 sheet 2 labels J5 as a 2-pin connector and names its signal `3V3_LaunchPad_IN`; its stated purpose is the option to power the LaunchPad from the EVM's 3.3-V rail.
- SENS007 sheet 2 explicitly documents the board's 3.3-V/5-V rail generation. The J5 shunt/link fitted state is a property of the actual sample, not something proven by the schematic.
- TI SLURAY2 assembly drawing shows SENS007 board # and **Rev A**, with separate component-side and bottom-side views. The underside BoosterPack headers are visible in the bottom-side drawing. It does not provide sufficient unambiguous physical pin-1/square-pad marking evidence to certify the actual sample's connector orientation from the PDF alone.
- TI SLURAY3 PCB drawing is published; its existence does not establish that the user's actual EVM is the same revision/assembly variant.
- LAUNCHXL-F280039C SPRR444A is **Rev A**, drawing MCU103, 8 sheets. TI product page lists design archive SPRR445.ZIP and schematic SPRR444A.PDF. The official schematic identifies connector numbering/site but does not establish the physical sample's populated revision or visible pin-1 marker.
- Therefore both schematic revision identifiers are known (SENS007 Rev A and LaunchPad MCU103 Rev A); actual hardware revision/assembly match and pin-1 pad/mark inspection remain **sample-specific and unverified**. Do not mate boards based only on inferred view orientation.

## 3. LaunchPad JP1 / JP4–JP7 correction

SPRR444A Rev A distinguishes the parts by function:

- **JP1** is the 4-contact USB-to-XDS110 power/ground isolation boundary. Its documented paths are USB-side +5V0_USB and USB_GND to XDS110-side +5V0_XDS110 and GND when bridged. The installed shunt arrangement determines whether those domains are connected. The schematic alone does not tell the as-received jumper population.
- **JP2A/JP2B**, not JP4–JP7, are the 5-V and 3.3-V XDS110-to-target-MCU isolation links: +5V0_XDS110 ↔ +5V0_MCU and +3V3_XDS110 ↔ +3V3_MCU.
- **JP4, JP5, JP6, JP7** are documented as 3-pin power headers, not the USB/MCU isolation links. Their pin pairs are:
  - JP4: pins 1/2 +3V3_MCU, pin 3 GND.
  - JP5: pins 1/2 +5V0_MCU, pin 3 GND.
  - JP6: pins 1/2 +3V3_MCU, pin 3 GND.
  - JP7: pins 1/2 +5V0_MCU, pin 3 GND.
  These are power-access headers; do not call them a jumper configuration selector.
- Actual JP1 and JP2A/JP2B shunt population, any attached accessories, and the USB cable/host grounding path are unknown. JP4–JP7 connector population/accessory wiring is also not inspected.

## 4. Power-source and grounding hold

- Do not fit EVM J5 while also powering the LaunchPad from USB/another 3.3-V source unless a revision-matched TI power configuration explicitly authorizes that exact combination.
- Do not infer that removing J5 alone resolves LaunchPad USB/XDS110 isolation. JP1 and JP2A/JP2B are distinct boundaries and must be checked separately.
- SENS007 schematic shows TP1=GND and TP2=PGND; R54 is the default TMP302 ground reference to GND and R53 is DNP for PGND. Do not assume signal GND, PGND, USB_GND and instrument earth are interchangeable.
- The EVM guide's J6/J5 naming differs across older notes; the original SENS007 Rev A schematic labels the 2-pin LaunchPad-feed connector **J5**. Use the schematic designator J5 for this SENS007 revision and do not perpetuate the earlier J6 label.
- No physical inspection, power-source measurement, continuity check, stack, or energization occurred.

## 5. No-power decision

**NO POWER / NO STACK HOLD REMAINS.** Although the schematic ambiguity is now resolved at the documentary level, do not mate or energize until a qualified person verifies actual sample revision, physical pin-1/square-pad marks, SENS007 J5 shunt state, LaunchPad JP1 and JP2A/JP2B shunt state, and all external USB/earth/ground connections. Motor, encoder, supply current limit and sink capability, regenerative energy, load inertia, motion profile, and cooling remain unspecified. No current rating or test authorization is inferred.

## 6. Official TI evidence

- SENS007 Rev A original schematic SLURAY0A, sheet 2 (EVM J5) and sheet 5 (J2/J4, U4, U12, PWM Enable): https://www.ti.com/lit/df/sluray0a/sluray0a.pdf
- SENS007 assembly drawing SLURAY2 (component-side and bottom-side views, board # SENS007 Rev A): https://www.ti.com/lit/df/sluray2/sluray2.pdf
- SENS007 PCB drawing SLURAY3: https://www.ti.com/lit/df/sluray3/sluray3.pdf
- LAUNCHXL-F280039C schematic SPRR444A Rev A, especially sheet 2 and sheet 6: https://www.ti.com/lit/df/sprr444a/sprr444a.pdf
- TI LAUNCHXL-F280039C product page and SPRR445 design archive listing: https://www.ti.com/tool/LAUNCHXL-F280039C
- TI BOOSTXL-3PHGANINV product page and published EVM design files: https://www.ti.com/tool/BOOSTXL-3PHGANINV

## 7. Verification boundary

This is a documentary schematic tracing result, not confirmation of the user's physical board. No electrical tests, firmware changes, native CAD edits, tests, or CI definitions were modified.


## 8. Follow-up audit — GPIO23 mapping, SDK software boundary, OCP and thermal behavior (2026-11-27)

### 8.1 Corrected LaunchPad header interpretation

A direct reading of TI SPRR444A Rev A sheet 2 (Site-1 J4/J2 header) and the MCU signal-to-connector table on sheet 6 resolves the prior ambiguous shorthand:

| Physical Site-1 header | MCU signal | SPRR444A connector mapping | SENS007 function when stacked |
|---|---|---|---|
| J4/J2-11 | GPIO23 | GPIO23 → J2_11 | `nEn_uC` request |
| J4/J2-12 | GPIO22 | GPIO22 → J2_12 | Not the SENS007 `nEn_uC` net |
| J4/J2-19 | GPIO5_BP | GPIO5 → J2_19 | U4 DIR |

Thus **SENS007 J2/J4-11 mates to LaunchPad Site-1 J4/J2-11 = GPIO23**, not a GPIO22/GPIO23 selectable route. GPIO22 is on the adjacent physical pin 12. Earlier notes describing a GPIO22/GPIO23 selection at pin 11 are superseded and incorrect.

### 8.2 SDK pin-mux evidence and unresolved firmware conflict

TI MotorControl SDK guide SPRUJ26A Rev A §3.2.12 documents the F280039C + BOOSTXL-3PHGANINV evaluation pairing and stack sites. The same guide's §3.2.2 identifies C2000Ware board files under `boards/LaunchPads/LAUNCHXL_F280039C` and says to install LaunchPad jumpers JP1, JP2 and J101 for power/debug; it does **not** publish the actual BOOSTXL `nEn_uC` GPIO output configuration or its exact generated SysConfig/HAL files in the guide.

The guide's command-switch example separately shows `MTR1_CMD_SWITCH_GPIO 23` with `GPIO_setPinConfig(GPIO_23_GPIO23)`, input direction, pull-up and 3-sample qualification. This is an example for an optional command switch, not proof that the inverter enable is configured that way. Because the physical SENS007 enable request is also on GPIO23, enabling that command-switch example unchanged would create a same-pin direction/function conflict (input vs required output). **Do not enable/reuse that optional command-switch GPIO until the exact installed MotorControl SDK project, build symbols, HAL source and SysConfig output are inspected.**

The official public MotorControl SDK documentation establishes board pairing and a generic GPIO23 example, but the exact project-specific pin-mux and runtime ownership of GPIO23 for this EVM pairing remains **unverified**. No firmware source was available in the repository and no SDK installer/project was locally accessed. GPIO22 is not an alternate for SENS007 pin 11 based on the published LaunchPad schematic.

### 8.3 Hardware OCP chain

SENS007 Rev A sheet 4 documents three current comparator channels:
- IA/IB/IC each enter a filtered comparator input path (20-ohm input resistor, 2.2-nF filter capacitor, 10-kΩ series resistor, 332-kΩ positive-feedback resistor).
- U13/U14/U15 comparator outputs ICompA/B/C feed U16, an SN74LVC1G332 four-input OR gate, whose output is `IComp`.
- The comparator reference is `CompRef`, derived from VREF through R78=54.9-kΩ and R77=274-kΩ, with C71=2.2-nF.
- Schematic annotation gives comparator thresholds 2.75-V and 2.85-V (100-mV hysteresis window). The EVM guide separately states a nominal 12-A trip threshold and 1-A hysteresis. These are source-described protection values, not a continuous motor-current rating; the guide value should not be extrapolated to arbitrary board revision, thermal conditions or motor operating limits.
- On sheet 5, U12 ORs `nEn_uC` and `IComp` to produce `nEnable`; U12 output drives U4 active-low OE. In normal logic, host request low and no OCP output low permit buffer enable; either host disable high or OCP high forces U12 output high and disables the PWM buffer. R79 is the 0-ohm OCP path; TI's schematic note says removing R79 disables OCP. **Do not remove/bypass R79.**

This is a documentary logic trace only. Comparator polarity, analog trip calibration against real phase current, propagation timing, fault persistence/recovery and actual hardware shutdown under switching conditions have not been measured. The EVM guide's 12-A/1-A figure and schematic's voltage thresholds are retained as different levels of evidence.

### 8.4 TMP302 thermal alert

SENS007 Rev A sheet 2 identifies U6 as TMP302BQDRLRQ1; OUT pin 3 drives net OT with R48=10-kΩ pull-up to 3V3. The LaunchPad Site-1 J4/J2-33 route is GPIO48. TMP302 datasheet SBOS488E specifies open-drain, active-low OUT and selectable trip points/hysteresis. The schematic's TRIPSET0/TRIPSET1 resistor network and HYSTSET configuration must be checked against the released BOM/as-built resistor population before claiming the actual board trip temperature/hysteresis. The schematic also states R54 (GND) is default and R53 (PGND) is DNP for the TMP302 ground reference; sample population remains unverified.

Firmware should treat OT low as a latched thermal fault and inhibit PWM; clearing must require the alert to deassert plus an explicit safe reset policy. This is a proposed control requirement, not behavior proven in the supplied TI firmware. TMP302 itself returns high only after the configured hysteresis window is crossed on cooling; the MCU latch/restart policy is not established by the sensor datasheet.

### 8.5 Power isolation cross-check update

The SPRUJ26A F280039C setup section says JP1, JP2 and J101 are to be installed for the TI Universal Lab power/debug setup. SPRR444A Rev A details the split JP2A/JP2B power paths between XDS110 and target MCU; JP1 separates USB-side and XDS110-side power/ground. These published setup instructions do not establish the as-received shunt population and are not a substitute for a sample-specific no-power inspection. Keep the existing separate EVM J5 feed warning, and do not infer USB, XDS110, MCU GND, PGND or instrument earth isolation from a jumper label alone.

## 9. Sources for this follow-up

- SPRR444A Rev A, Site-1 header table and MCU-to-connector signal map: https://www.ti.com/lit/df/sprr444a/sprr444a.pdf
- MotorControl SDK Universal Project and Lab SPRUJ26A Rev A, §3.2.2, §3.2.12 and GPIO23 command-switch example: https://www.ti.com/lit/ug/spruj26a/spruj26a.pdf
- C2000Ware core SDK official repository (F28003x driverlib and board metadata): https://github.com/TexasInstruments/c2000ware-core-sdk
- SENS007 Rev A sheets 2/4/5: https://www.ti.com/lit/df/sluray0a/sluray0a.pdf
- BOOSTXL-3PHGANINV User Guide SLUUBP1A Rev A: https://www.ti.com/lit/ug/sluubp1a/sluubp1a.pdf
- TMP302 datasheet SBOS488E Rev E: https://www.ti.com/lit/ds/symlink/tmp302.pdf
- TLV3201 datasheet SBOS561C Rev C: https://www.ti.com/lit/ds/symlink/tlv3201.pdf

**Updated decision:** physical SENS007 enable mapping is confirmed as LaunchPad GPIO23 at Site-1 pin 11; exact SDK application pin ownership/configuration is not confirmed. OCP logic and TMP302 active-low electrical behavior are documented, but dynamic protection/recovery is not validated. No stack or power.
