# AEL-002 — Modular Low-Voltage Servo Drive

**Status:** concept / preliminary requirements (not a released design)  
**Benchmark:** LS Mecapion iX7NH and iX7M  
**Prototype boundary:** one axis, externally supplied 24–48 VDC bus, three-phase PMSM/BLDC, guarded bench evaluation

## 1. Product intent

Develop a general-purpose servo-drive platform rather than a controller tied to one motor. The long-term product is a family of drives sharing a motion-control interface, firmware architecture, diagnostics, and motor/feedback configuration model, with power stages sized independently.

The first prototype is deliberately narrower: one low-voltage axis to prove the control loop, feedback abstraction, protection, commissioning, and reproducible test process. It is **not** an industrial mains-input drive and is not claimed to be compatible with every motor or encoder.

## 2. Benchmark observations

| Reference | Publicly documented characteristics | Design implication |
|---|---|---|
| LS Mecapion iX7NH | EtherCAT network servo family; LS lists AC 100–120 V and 200–240 V variants and a broad 0.1–15 kW family. Encoder options include BiSS, quadrature, Tamagawa, Panasonic, EnDat 2.2, SSI, Nikon and optional sinusoidal. ETG lists 125 µs position, 62.5 µs speed and 31.25 µs current control cycles for the registered series entry. | Benchmark the complete drive experience: motor/encoder setup, deterministic control, fieldbus, diagnostics, commissioning and protection—not just the inverter. |
| LS Mecapion iX7M | LS lists a 200–240 VAC EtherCAT multi-axis family, 0.2–1 kW. | Keep multi-axis expansion as a later product-family direction; do not confuse iX7M multi-axis with iX7NH's network single-axis product family. |

Sources:
- [LS Mecapion drive lineup](https://www.lsmecapion.com/bbs/board.php?bo_table=pd_drive)
- [LS Mecapion manuals and current manual listings](https://lsmecapion.com/bbs/board.php?bo_table=manual&sca=Servo)
- [EtherCAT Technology Group — iX7NH Series](https://www.ethercat.org/en/products/EF21463130D54BA8BC68CC8DC7935633.htm)
- [LS ELECTRIC iX7NH product page and downloads](https://nahpdev-web.ls-electric.com/product/1715/ix7nh-servo-drives)

These are benchmark facts, not a claim that AEL-002 already matches the commercial product's performance, safety certification, or motor compatibility.

## 3. First-prototype requirements

### 3.1 Scope and constraints

- One motor axis; three-phase PMSM/IPMSM or BLDC with documented electrical parameters.
- External, isolated, current-limited DC bench supply; nominal operating range 24–48 VDC.
- Design envelope must explicitly account for bus transients and regenerative energy. A 48 V nominal bus is not a 48 V maximum bus.
- No AC mains input, onboard mains rectifier, or 200/400 VAC stage in this prototype.
- No current, power, torque, speed, or thermal rating is assigned until a specific motor, supply, cooling arrangement, and test envelope are selected.
- Initial operation on a guarded bench with independent emergency power disconnect; no unattended motion.

### 3.2 Motion and feedback

- Control foundation: field-oriented current control (FOC) for a three-phase synchronous motor.
- Command modes staged by maturity: torque/current first; velocity second; position third.
- Initial feedback target: differential incremental encoder A/B/Z. Hall sensors may be used for coarse commutation/startup where appropriate.
- Feedback abstraction must separate electrical interface, protocol decoder, calibration, commutation alignment, and motor parameter set.
- Absolute encoder support is an extension point, not a universal compatibility promise. BiSS-C, EnDat, SSI, Tamagawa and other protocols require specific electrical interfaces, timing, licensing/implementation and per-motor validation.
- Sensorless operation is a future option; it is not a substitute for verified position feedback in the first closed-loop position-control milestone.

### 3.3 Electrical and protection requirements

- Three-phase MOSFET inverter with a gate driver suitable for the chosen DC bus and switching device ratings.
- Three-shunt phase-current sensing is the preferred first measurement topology for observability and bring-up; ADC sampling must be synchronized to PWM and validated over the usable modulation range.
- Measure DC-bus voltage and at least power-stage temperature; add motor temperature input where the selected motor provides it.
- Hardware gate-disable path independent of firmware; cycle-by-cycle overcurrent/fault response where supported by the selected gate driver/comparator.
- Firmware protections: bus over/undervoltage, overcurrent, overtemperature, overspeed, encoder fault, following error, watchdog and power-stage fault.
- Define fault latching, reset conditions, safe output state, fault history and event timestamps.
- Regeneration can raise the DC bus. Provide a validated energy path (external braking resistor/chopper or a supply explicitly capable of sinking energy) and independent bus-overvoltage shutdown before enabling deceleration tests.
- Add input fuse/current limiting, reverse-polarity strategy, bus discharge verification, connector keying, creepage/clearance appropriate to the actual voltage category, and thermal sensing.
- A prototype hardware inhibit is not certified STO. Do not claim functional-safety compliance.

### 3.4 Control, configuration and communications

- Deterministic PWM/ADC/FOC scheduling with measured worst-case execution time and explicit fault latency.
- Separate fast current loop from slower speed/position loops and supervisory communications.
- Commissioning data model: motor nameplate/electrical parameters, encoder type/resolution/direction, pole pairs, phase order, current limits, bus limits, loop gains, inertia/load notes and firmware/hardware revisions.
- Nonvolatile parameter storage with versioning, CRC, defaults, rollback and export/import.
- First bring-up interface: isolated USB/UART service interface or equivalent safe bench interface; CAN physical interface may be reserved on the control board.
- CANopen/CiA 402 is a candidate first industrial motion profile after basic control is stable. EtherCAT/CoE/CiA 402 is a later network module/workstream; do not promise a working EtherCAT stack in the first board.
- Provide telemetry, alarm trace, command/feedback monitor, parameter backup and firmware update with interrupted-update recovery strategy.

## 4. Proposed architecture

### 4.1 Functional partition

1. **Control board:** real-time MCU, clock/reset, isolated service interface, CAN interface footprint, nonvolatile memory, encoder input front ends, digital/analog I/O, hardware fault aggregation and a defined inter-board connector.
2. **Power stage:** DC input protection and bus capacitance, three-phase MOSFET bridge, gate driver, current shunts/amplifiers, bus-voltage measurement, temperature sensing, braking-energy interface and motor connector.
3. **Feedback interface:** replaceable/option-capable receiver front ends for differential incremental encoder first; future isolated serial absolute-encoder options only after protocol-specific validation.
4. **Firmware layers:** hardware abstraction → PWM/ADC and fault drivers → motor/encoder abstraction → FOC/current loop → speed/position loops → command/state machine → parameter/diagnostics/communications.
5. **Tooling and validation:** host-side unit tests and motor-control math tests, static analysis, firmware build with pinned toolchain, HIL/simulation where available, then guarded bench test records.

The control/power split is a product-family direction, not permission to use an unverified generic connector. Define connector pinout, isolation domains, fault polarity, common-mode limits, sequencing, creepage and EMC before schematic capture.

### 4.2 Candidate control MCU

**Primary evaluation candidate: TI C2000 F280039C / F28003x family.** TI's current Motor Control SDK documents Universal Motor Control Lab support for sensored and sensorless FOC, incremental encoder and Hall feedback, multiple current-sense topologies, and a sensored FOC servo-drive-with-CAN example for F28003x. This directly reduces uncertainty for a servo-oriented first prototype.

**Alternative: STM32G4 (e.g. STM32G474 family).** ST's motor-control ecosystem provides X-CUBE-MCSDK for PMSM/BLDC FOC, motor profiling and monitoring; ST also documents low-voltage three-phase FOC evaluation with an STM32G431RB board. This remains a viable second platform if ecosystem, availability or cost favors it.

The MCU is not frozen. Before selection, compare exact orderable device/package, PWM and ADC timing, encoder peripherals, CAN/Ethernet needs, memory, toolchain/license, development-board availability and lifecycle.

Sources:
- [TI C2000 Motor Control SDK guide](https://software-dl.ti.com/C2000/docs/software_guide/mcsdk.html)
- [TI C2000Ware MotorControl SDK release notes](https://software-dl.ti.com/C2000/c2000_apps_public_sw/c2000ware_sdk/motorcontrolsdk/5_04_00_00/release_notes.html)
- [ST STM32 Motor Control ecosystem](https://www.st.com/content/st_com/en/ecosystems/stm32-motor-control-ecosystem.html)
- [ST UM2538 low-voltage three-phase FOC evaluation manual](https://www.st.com/resource/en/user_manual/um2538-stm32-motorcontrol-pack-using-the-foc-algorithm-for-threephase-lowvoltage-and-lowcurrent-motor-evaluation-stmicroelectronics.pdf)

## 5. Development gates

1. **G0 — requirements freeze:** select a real motor/encoder, supply current limit, mechanical load, cooling, allowed bus range and intended test environment.
2. **G1 — control platform proof:** run vendor-supported FOC example on evaluation hardware; verify encoder direction/alignment, current measurement, fault shutdown and logging without custom power hardware.
3. **G2 — power-stage design:** calculate MOSFET/gate-driver ratings, shunt/amplifier range, bus capacitance, switching losses, thermal path, transient/regen clamp and PCB layout; independently review.
4. **G3 — schematic/PCB:** capture native KiCad files, run ERC/DRC, review isolation/clearance/current loops/thermal/mechanical constraints and BOM lifecycle.
5. **G4 — guarded bring-up:** first power with current-limited supply and no motor; verify rails, gate disable and fault response; then low-energy motor tests with mechanical restraint and independent disconnect.
6. **G5 — servo behavior:** characterize current, speed and position loops, feedback-loss behavior, fault recovery, thermal limits, repeatability and communication timing.
7. **G6 — productization:** only after evidence, add network modules, broader encoder interfaces, multi-axis variants, EMC/environmental tests and applicable safety/compliance assessment.

## 6. Explicitly unresolved

- Motor make/model, phase resistance/inductance, pole pairs, rated/peak current, rated speed, torque constant, back-EMF constant, thermal sensor and encoder electrical/protocol details.
- Supply voltage tolerance, current limit, ability to sink regenerative energy, cable length and grounding.
- Mechanical load/inertia, desired speed/torque/position accuracy, duty cycle and cooling.
- Required communications and target host/controller.
- Enclosure, connector, environmental, EMC and certification requirements.
- Budget and availability constraints.

These unknowns intentionally block component ratings and final power-stage design. Do not invent them.

## 7. Acceptance criteria for this preliminary brief

- iX7NH and iX7M are distinguished correctly and benchmark claims have primary/source links.
- First prototype remains one-axis, external 24–48 VDC, low-voltage only, with no mains stage.
- FOC, feedback abstraction, control modes, diagnostics, communications and protection are represented.
- MCU choice remains an evidence-based candidate, not a frozen part.
- Missing motor/supply/load requirements are explicit.
- No schematic, PCB, firmware build, safety certification or hardware validation is claimed.
