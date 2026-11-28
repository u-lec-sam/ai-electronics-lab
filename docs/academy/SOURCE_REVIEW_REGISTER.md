# Engineering Academy — 출처 교차검증 기록부

## 목적
핵심 기술 주장이 단일 링크나 단일 공급자 설명에 종속되지 않도록 규격·제조사 1차 문서·전문기관·학술 자료를 claim-by-claim으로 대조한다. 같은 원문을 복제한 페이지 여러 개는 독립 출처 여러 개로 세지 않는다.

## 출처 등급
- **N — Normative:** 적용 가능한 IEC/ISO/IEEE/TIA/CiA 규격 원문과 amendment/errata.
- **M — Manufacturer primary:** exact part datasheet, reference manual, errata, official SDK/release notes.
- **P — Professional:** CiA technical report, 제조사 application report, 전문 학회·기관 기술문서.
- **A — Academic:** 대학 교재, peer-reviewed 논문, 공식 강의 자료.
- **S — Secondary:** blog/forum/video. 발견과 보조 설명에만 사용하며 안전/정격/핀맵의 단독 근거로 사용하지 않는다.

## 교차검증 규칙
1. 각 핵심 claim을 하나의 검증 가능한 문장으로 쪼갠다.
2. 규격이 있는 claim은 적용 edition의 normative source를 먼저 확인한다.
3. 부품/MCU claim은 exact order code, package, silicon revision, datasheet, reference manual, errata, SDK release를 함께 확인한다.
4. 표준/제조사 문서와 독립적인 전문 자료 또는 구현 문서를 대조한다. 서로 인용하는 자료인지 확인한다.
5. 수식은 단위·차원·경계조건을 확인하고 독립적으로 다시 계산한다.
6. 상충하는 값은 평균하지 않는다. 문서 edition, operating condition, topology, tolerance 차이를 기록한다.
7. 전문을 열람하지 못한 유료 규격은 공개 scope/abstract 범위까지만 설명하고 clause-level compliance를 주장하지 않는다.
8. generic truth, candidate-part support, exact-target integration, measured result를 구분한다.
9. critical safety/rating/pinout claim은 단일 출처로 확정하지 않는다.
10. 모든 기록에 access date, reviewer, commit SHA를 남긴다.

## Claim review template
| Field | Entry |
|---|---|
| Claim ID / sentence | |
| Domain | |
| Source role (N/M/P/A/S) | |
| Issuer / exact title | |
| Document number / revision / edition / date | |
| Clause / page / table / figure / register / API | |
| URL / access date | |
| Claim supported / conditions | |
| Independent cross-check | |
| Conflict / limitation | |
| Applicability (generic/candidate/exact target/measured) | |
| Confidence (confirmed/conditional/TBD/contradicted) | |
| Reviewer / date / commit SHA | |

## 2026-11-28 — Chapter 13 source review
| Claim group | Primary source | Cross-check | Scope / limitation |
|---|---|---|---|
| Requirements traceability and V&V matrix | NASA Systems Engineering Handbook, Appendix D/E and V&V chapters | IEEE 1012-2024 public scope/abstract | NASA handbook is guidance; IEEE full normative text not accessed |
| System/software/hardware V&V lifecycle | IEEE 1012-2024 | NASA Systems Engineering Handbook | Public catalogue scope confirmed; no compliance claim |
| Safety-related software lifecycle | IEC 61508-3:2010 catalogue | IEC 61508-3:2026 FDIS/pre-release status page | 2026 FDIS is not final published edition; 2010 published edition retained |
| Drive functional safety scope | IEC 61800-5-2:2016+AMD1:2026 | IEC publication catalogue description | Scope only; no AEL certification/STO claim |
| PWM/ADC timing integration | TI SPRACN0F Rev. F | TI SPRAD12A Rev. A and MC SDK guide | C2000 examples; exact AEL target route remains TBD |
| CAN-FD bit timing and system design | CiA 601 series technical documents | ISO 11898-1:2024 scope plus Microchip controller reference manual | CiA technical report/guidance; controller manual implementation-specific |
| RS-485 termination/bias | TI SLLA272D Rev. D | TI SSZT656 and ISO15/ISO35 datasheet | Generic design guidance plus part-family example; no AEL transceiver selected |

## 2026-11-28 — Chapter 12 source correction
- Corrected the malformed CAN FD link in Chapter 12 to the CiA CAN-FD basic idea page.
- Added CiA 601 series, Microchip MCP25xxFD controller reference manual, and TI ISO15/ISO35 transceiver datasheet as complementary professional/implementation sources.
- Chapter 12 examples remain generic and educational. Exact AEL-002 transceiver/controller/bit timing/topology are TBD.
- Future review must check the exact ISO 11898-1 edition text and selected controller reference manual/errata before any implementation claim.

## Source URLs checked on 2026-11-28
- NASA handbook appendix: https://www.nasa.gov/reference/system-engineering-handbook-appendix/
- IEEE 1012-2024 catalogue: https://standards.ieee.org/ieee/1012/7324/
- IEC 61508-3:2010: https://webstore.iec.ch/en/publication/5517
- IEC 61508-3:2026 pre-release/FDIS status: https://webstore.iec.ch/en/publication/117298
- IEC 61800-5-2:2016+AMD1:2026: https://webstore.iec.ch/en/publication/117563
- TI SPRACN0F Rev. F: https://www.ti.com/lit/an/spracn0f/spracn0f.pdf
- TI SPRAD12A Rev. A: https://www.ti.com/lit/an/sprad12a/sprad12a.pdf
- TI MotorControl SDK guide: https://software-dl.ti.com/C2000/docs/software_guide/mcsdk.html


## 2026-11-28 — Chapter 14 source review

| Claim group | Primary source | Cross-check | Scope / limitation |
|---|---|---|---|
| Silicon MOSFET gate charge/Miller behavior | Infineon AN_2203_PL18_2204_004502 V1.0 (2022-04-20) | Infineon gate-driver parameter guide; onsemi AND9987/D | Infineon note explicitly covers silicon MOSFETs, not IGBT/WBG |
| GaN gate drive/layout | TI SLUAAM3 (2022-08); EPC AN003 | Infineon CoolGaN layout note; EPC eGaN drive paper | Device-family and topology specific; no AEL device chosen |
| Deadtime/Miller clamp | TI SLYA091 (2024-12) | Infineon gate-driver feature guide; onsemi AND9987/D | Application guidance; exact switch timing must use selected part data |
| DESAT/OCP/soft turn-off | ST STGAP4S DS13833 Rev.6 (2024-12) | onsemi AND9987/D; Infineon driver feature guide | STGAP4S is an example device, not an AEL selection |
| Bootstrap sizing | Infineon AN-1123 Rev.1.01 (2024-11-20) | ST AN5789 Rev.1 (2022-03); Infineon AN-978 | Device/controller specific sizing equations and refresh limits |
| Drive electrical/thermal/energy safety | IEC 61800-5-1:2022 corrected 2025-12 catalogue | IEC 61800-5-2:2016+AMD1:2026 catalogue | Public scope/catalogue checked; no full clause-level review or compliance claim |

Links checked on 2026-11-28:
- Infineon MOSFET gate-drive AN: https://www.infineon.com/assets/row/public/documents/24/42/infineon-gate-drive-for-power-mosfets-in-switchtin-applications-applicationnotes-en.pdf
- Infineon driver requirements: https://www.infineon.com/product-information/gate-driver-requirements-mosfet-igbt-sic-gan
- TI GaN layout SLUAAM3: https://www.ti.com/document-viewer/lit/html/SLUAAM3
- TI Miller clamp SLYA091: https://www.ti.com/document-viewer/lit/html/SLYA091
- ST STGAP4S DS13833: https://www.st.com/resource/en/datasheet/stgap4s.pdf
- Infineon bootstrap AN-1123: https://www.infineon.com/dgdl/Infineon-Bootstrap_Network_Analysis-ApplicationNotes-v01_00-EN.pdf
- ST bootstrap AN5789: https://www.st.com/resource/en/application_note/an5789-considerations-on-bootstrap-circuitry-for-gate-drivers-stmicroelectronics.pdf
- IEC 61800-5-1:2022: https://webstore.iec.ch/en/publication/62103
- IEC 61800-5-2:2016+AMD1:2026: https://webstore.iec.ch/en/publication/117563


## 2026-11-28 — Chapter 15 current sensing and analog front-end source review

| Claim group | Primary source (role / exact revision / location) | Independent cross-check | Conditions / limitations |
|---|---|---|---|
| Low-side, inline and DC-link sensing location; PWM-window dependence | Analog Devices, “Measurement Techniques for Industrial Motion Control” (technical article; motor-current measurement locations and topology section): https://www.analog.com/en/resources/technical-articles/measurement-techniques-for-industrial-motion-control.html | TI BOOSTXL-3PhGaNInv User Guide SLUUBP1A Rev. A (2018-04), pp. 2–3, Fig. 1–2 | ADI article is professional guidance, not a normative standard. TI guide is one EVM topology; no universal superiority claim. |
| Inline shunt PWM common-mode and amplifier response | TI INA240 datasheet SBOS662C Rev. C (2016-07, revised 2021-12), §§1, 6, 8.3.1; common-mode range and enhanced PWM rejection: https://www.ti.com/lit/ds/symlink/ina240.pdf | TI BOOSTXL-3PhGaNInv User Guide SLUUBP1A Rev. A, pp. 2–3; ADI industrial motion-control article | INA240 claims are device-specific and test-condition dependent. PWM rejection does not mean zero recovery time. EVM guide reports about 2 µs settling in its own implementation; do not generalize. |
| Isolated shunt amplifier | TI AMC1302 datasheet SBAS812D Rev. D (2018-06, revised 2021-06), §§1, 6.9 and device description: https://www.ti.com/lit/ds/symlink/amc1302.pdf | TI “An Engineer’s Guide to Isolated Signal Chain Solutions” (2024-12), current-sensing/isolation sections: https://www.ti.com/lit/eb/slyy234/slyy234.pdf | AMC1302 is an example device: ±50 mV input, fixed gain 41, reinforced isolation and CMTI per stated conditions. Not an AEL selection; system creepage/clearance and certification remain separate. |
| Hall current sensing | TI TMCS1100 datasheet SBOS820C Rev. C (2019-09, revised 2025-06), §§1, 6.9; 1.8 mΩ conductor, 80 kHz bandwidth, offset/sensitivity and basic-isolation ratings: https://www.ti.com/lit/ds/symlink/tmcs1100.pdf | TI isolated signal-chain guide (2024-12), magnetic sensing comparison | Product-specific Hall performance only. 600 V lifetime working voltage and 3 kVrms basic isolation are not interchangeable terms; installation and applicable safety system rules still apply. |
| Shunt TCR, tolerance, inductance and power conditions | Bourns CSS2H-2512 series datasheet, Electrical Characteristics table (resistance/power, TCR, tolerance, inductance): https://www.bourns.com/docs/product-datasheets/css2h-2512.pdf | TI “An Engineer’s Guide to Isolated Signal Chain Solutions” (2024-12), shunt/Kelvin discussion; TI SDAA115 (2025-11), low-ohmic shunt parallel layout: https://www.ti.com/lit/an/sdaa115/sdaa115.pdf | Bourns table distinguishes resistive-alloy TCR from TCR including copper terminals; power rating is stated at terminal temperature 70 °C. Pulse overload table is not a substitute for application pulse derating. PDF front matter did not expose a clear revision code in the parsed source; recorded as exact series document and access date. |
| Kelvin / force-sense layout | TI “An Engineer’s Guide to Isolated Signal Chain Solutions” (2024-12), shunt selection and Kelvin connection discussion, pp. 16–17: https://www.ti.com/lit/eb/slyy234/slyy234.pdf | TI SDAA115 (2025-11), layout practices for parallel low-ohmic shunts; Bourns CSS2H series datasheet | Generic layout guidance. Kelvin topology does not remove shunt element TCR, thermal gradient, or incorrect sense-node placement. |
| ADC S+H settling and source impedance | TI SPRACT6A Rev. A (2020-10, revised 2023-03), §§1–3, ADC input model and design steps; explicitly covers F28003x: https://www.ti.com/lit/an/spract6a/spract6a.pdf | TI SBAA531 (2021-11), §2.1 SAR sample-and-hold model: https://www.ti.com/document-viewer/lit/html/SBAA531 | SPRACT6A is an engineering method and example, not a substitute for exact target ADC model, data-sheet minimum acquisition time, or board measurement. |
| F28003x ADC trigger, acquisition, result timing | TI TMS320F28003x TRM SPRUIW9C (2021-10, revised 2024-03), §§16.3.1–16.3.5, pp. 1856–1858; SOC trigger, S+H, input model, channel selection: https://www.ti.com/lit/ug/spruiw9c/spruiw9c.pdf | TI TMS320F28003x datasheet SPRSP61C Rev. C (2021-10, revised 2023-12), §6.13, Tables 6-18/6-19, p. 133: https://www.ti.com/lit/ds/symlink/tms320f280034.pdf | F280039C is only a candidate platform. Verify exact device, silicon revision, SYSCLK/ADCCLK, SOC arbitration and current datasheet before implementation. |
| C2000 CMPSS comparator and trip path | TI TMS320F28003x TRM SPRUIW9C, Chapter 18 §§18.2–18.6, pp. 2045–2053; comparator, reference DAC, filter, latch and delay: https://www.ti.com/lit/ug/spruiw9c/spruiw9c.pdf | TI F28003x Driverlib CMPSS API guide: https://software-dl.ti.com/C2000/docs/C2000_driverlib_api_guide/f28003x/build/html/modules/cmpss.html | Describes candidate MCU facilities, not a verified AEL signal route or safe trip response. Asynchronous path/filter/latch configuration and gate disable must be measured/reviewed. |
| F28003x ADC/CMPSS silicon advisories | TI TMS320F28003x Silicon Errata SPRZ496E Rev. E (2021-10, revised 2026-08), Table 1-2 p. 2; ADC DMA stale result pp. 12–13; CMPSS latch clear pp. 17–18; CMPSS/ADC/AGPIO interaction pp. 18–19: https://www.ti.com/lit/er/sprz496e/sprz496e.pdf | TI F28003x datasheet SPRSP61C Rev. C and TRM SPRUIW9C Rev. C | Advisories shown for silicon revision 0. Confirm exact silicon revision and applicable workaround. In particular, DMA may read stale ADCRESULT under the documented conjunction of late interrupt, divider/timing, DMA trigger and immediate read; CMPSS latch clear can reassert while filter output remains active; shared ADC/CMPSS/AGPIO use can create a comparator glitch. |
| Drive safety scope | IEC 61800-5-1:2022 Edition 3.0, corrected version 2025-12, official catalogue scope: https://webstore.iec.ch/en/publication/62103 | IEC 61800-5-2:2016+AMD1:2026 CSV Edition 2.1, official catalogue scope: https://webstore.iec.ch/en/publication/117563 | Public catalogue/scope only; full normative text was not accessed clause-by-clause. No compliance, STO or certification claim. |

### Chapter 15 review notes
- Source roles: IEC catalogue = normative publication scope/status only; manufacturer datasheets/TRM/errata = primary device-specific evidence; ADI article and TI application notes/e-book = professional informative guidance.
- Claim groups above are cross-checked by source role rather than counting multiple pages that repeat the same source.
- The TI BOOSTXL-3PhGaNInv EVM guide and schematic are a useful concrete reference only: SLUUBP1A Rev. A pp. 2–4 describes three inline 5 mΩ shunts, INA240 gain 20 V/V, 1.65 V midpoint/3.3 V reference, and TLV3201 OCP at 12 A with 1 A hysteresis. The schematic SLURAY0A Rev. A shows phase-A R55=5 mΩ, C52=1.5 nF and INA240A1PW. These are EVM facts, not AEL-002 design selections.
- EVM guide's approximately 2 µs recovery statement is a stated EVM implementation observation, not a universal INA240 guaranteed settling time.
- Actual AEL-002 shunt, amplifier, Hall/isolated sensor, ADC route, gain, bandwidth, current limits, calibration, threshold and board revision remain TBD.
- Calculation examples in Chapter 15 were independently recomputed for dimensions and arithmetic. No target build, SPICE simulation, bench measurement, HIL, CMTI test or OCP response-time test was performed.
- Review date: 2026-11-28. Commit SHA to be added after final CI verification.


## 2026-11-28 — Chapter 16 PMSM FOC current-loop design and tuning source review

| Claim group | Primary source (role / exact revision / location) | Independent cross-check | Conditions / limitations |
|---|---|---|---|
| PMSM rotor d/q voltage/flux equations and decoupling signs | imperix TN111, *Field oriented control of permanent magnet synchronous machine (PMSM)*, posted 2021-03-23; online equations (1)–(5), “General principles”, “Plant model”, “Field oriented control implementation”: https://imperix.com/doc/implementation/field-oriented-control-of-pmsm | imperix TN106, *Vector current control*, updated 2023-01-19, equations (1)–(5), d/q coupling and decoupling implementation: https://imperix.com/doc/implementation/vector-current-control | TN111's displayed model begins with isotropic PMSM framing, while this lesson retains salient (L_d,L_q) terms from the general d/q flux equations. Both are informative technical notes, not normative requirements. Sign convention must match Chapter 08. |
| Decoupled RL plant and magnitude-optimum initial PI gains | imperix TN111, equations (4)–(7), “Plant model” and “Field oriented control implementation”; TN106 equations (4)–(5) / “Tuning and performance evaluation” | MathWorks Simscape Electrical R2026b, *PMSM Current Controller*, equations in “Equations” section: https://www.mathworks.com/help/simscape-electrical/ref/pmsmcurrentcontroller.html | Magnitude-optimum / pole-zero cancellation relies on a first-order plant approximation and explicit delay model. The lesson's (K_p=L/(2T_d)), (K_i=R/(2T_d)) is a parallel-PI form; gain values are not interchangeable with a PI represented as (K_p(1+K_i/s)). Real loop margins need full discrete plant and measured delay. |
| Forward Euler, Backward Euler and Tustin PI discretization | imperix TN105, *Discrete PI controller implementation*, posted 2023-05-04, updated 2025-06-15; equations (1)–(6), “Digital implementation”: https://imperix.com/doc/implementation/pi-controller | MathWorks R2026b PMSM Current Controller, backward-Euler equation and stated discretization rationale | Imperix TN105 summarizes all three methods and derives forward Euler; MathWorks describes one block's backward-Euler implementation. Stability depends on plant, sample time, delay, controller realization and saturation; no discretization is universally best. |
| PI magnitude-optimum derivation and anti-windup | imperix TN105, equations (7)–(12), “PI controller tuning strategies” and “Integrator wind-up and anti-windup methods” | MathWorks R2026b, “Voltage Saturation” and “Integral Anti-Windup”, lines/equations in online reference | Imperix approximates exponential delay by first-order (1/(1+sT_d)) in its MO derivation. Lesson separately gives a pure-delay phase calculation and labels it idealized. MathWorks implementation includes voltage vector saturation, axis priority and back-calculation. Exact signal and anti-windup state conventions must be matched. |
| d/q cross-coupling compensation and implementation signs | imperix TN106, equations (1)–(5) and C/C++ implementation example, where d-axis includes (-omega L i_q) and q-axis includes (+omega L i_d): https://imperix.com/doc/implementation/vector-current-control | imperix TN111 equations (1)–(5); MathWorks R2026b PMSM Current Controller feed-forward inputs | TN106 is grid-tied RL inverter example, so its coupling structure is analogous but not a PMSM PM back-EMF model. TN111 supplies the PM flux term. This lesson re-derives the signs from PMSM equations rather than copying code. |
| Voltage vector limit and d/q axis priority | MathWorks Simscape Electrical R2026b, *PMSM Current Controller*, “Voltage Saturation”, equations/definitions for (V_{ph,max}), vector magnitude and axis-priority limiter: https://www.mathworks.com/help/simscape-electrical/ref/pmsmcurrentcontroller.html | imperix TN111, current controller implementation, DC-bus-dependent saturation; imperix RFOC note's “Dynamic saturation” section gives (V_{dc}/sqrt3) circle in its own convention | (V_{dc}/sqrt3) is ideal linear SVPWM phase-neutral peak limit under the stated amplitude-invariant convention. Actual AEL modulation, scaling, deadtime, minimum pulse, device drop and reserve are unverified. RFOC example is an induction-machine control note; only the inverter voltage geometry is reused. |
| End-to-end sample-to-actuation delay and PWM update | imperix PN142, *Discrete control delay identification*, posted 2021-03-29, updated 2026-05-01; “Definitions of the various delays”, “Control delay”, “Modulator delay”, single-/double-rate examples: https://imperix.com/doc/help/discrete-control-delay | Lan, Yang & Shang, Energies 2025, 18(16), 4306, §3.1, Eq. (6), and §3.2, Eqs. (7)–(12): https://www.mdpi.com/1996-1073/18/16/4306 | PN142 is controller-architecture-specific but provides reusable delay decomposition. MDPI article uses a different PI gain parameterization and a ZOH half-period approximation; its experimental motor/controller values are not AEL settings. Avoid double-counting overlapped timing stages. |
| Parameter identification uncertainty and frequency-response verification | Lan, Yang & Shang, “Design of a High-Performance Current Controller for PMSM via Multi-Frequency Sweep Adjustment”, Energies 2025, 18(16), 4306, DOI 10.3390/en18164306; §§1, 2.3, 3.1–3.2, Eqs. (4), (6)–(12) | imperix TN111/TN105 delay-aware tuning and parameter assumptions | Peer-reviewed open-access paper reports its own experimental system and proposed sweep method. It supports checking Rs/Ld/Lq and delay mismatch, not a universal identification procedure or AEL-002 parameter values. |
| C2000 implementation scope and fast current loop | TI, *C2000 Motor Control Software Guide*, online v1.5; “Sensored FOC solutions” and Table 3: https://software-dl.ti.com/C2000/docs/software_guide/mcsdk.html | TI C2000Ware MotorControl SDK product/release page, SDK 6.00.00.00 released 2026-03-31: https://www.ti.com/tool/C2000WARE-MOTORCONTROL-SDK | SDK guide documents examples including low-side/in-line sensing, sigma-delta and FCL. It does not verify a specific AEL-002 F280039C board route, SDK installation, build or runtime. |
| Drive electrical/thermal/energy safety scope | IEC 61800-5-1:2022 Edition 3.0, corrected version 2025-12, official catalogue scope: https://webstore.iec.ch/en/publication/62103 | AEL-002 Chapter 00/13 safety and V&V process; applicable device datasheets and system hazard analysis | Public catalogue describes scope only. It does not define current-loop PI tuning equations and this lesson makes no clause-level compliance claim. |
| Drive functional safety scope | IEC 61800-5-2:2016+AMD1:2026 CSV Edition 2.1, published 2026-10-30, official catalogue scope: https://webstore.iec.ch/en/publication/117563 | Chapter 13 evidence boundary and Chapter 14 independent inhibit architecture | Public catalogue scope only; no full normative clause review, STO implementation, SIL/PL claim or certification. |

### Chapter 16 review notes
- Source roles are deliberately separated: IEC = normative publication scope; TI/MathWorks = vendor primary software documentation; imperix = professional technical/application notes; Energies article = peer-reviewed research. Repeated pages from one source are not counted as independent corroboration.
- The lesson's PMSM equations use the Chapter 08 d/q sign convention and preserve (L_d
e L_q). Decoupling terms were algebraically substituted back into the plant equations to verify signs.
- Parallel PI convention is (C(s)=K_p+K_i/s). The MDPI article writes its controller as (K_p(1+K_i/s)); its (K_i) is a ratio/time parameter and cannot be numerically copied into the lesson's parallel-PI (K_i).
- Imperix TN105 uses a first-order approximation for delay in its MO derivation; PN142 details actual sample/compute/PWM timing by update mode. The lesson's 61.35° idealized estimate assumes a pure-delay approximation and exact pole-zero cancellation; it is not a measured or guaranteed phase margin.
- MathWorks R2026b documents backward Euler, d/q feed-forward, vector saturation, axis priority and back-calculation; these are reference block semantics, not an AEL-002 implementation decision.
- Ideal SVPWM circle (V_{dc}/\sqrt3) is stated for amplitude-invariant d/q phase-neutral peak convention. The actual modulation, bus sensing, reserve and hardware voltage loss are not established.
- The 2025 Energies paper uses an experimental PMSM system and its own parameter-identification/sweep approach; only the general need to characterize parameter and delay mismatch is transferred.
- IEC public catalogues were inspected for scope/status only; no paid normative full text or clause-level compliance audit was performed.
- Independent arithmetic checks on the lesson examples: (K_{p,d}=5.3333), (K_{p,q}=6.6667), (K_i=2333.33), (f_c=1061.03\,Hz), idealized delay-only PM (61.35°), Tustin d-axis (b_0=5.3917,b_1=-5.2750), vector limit (24.942\,V), scaled vector ((16.686,18.540)\,V), back-calculation residual increments ((-0.0329,-0.0365)\,V), flux error residual (2.10\,V).
- No target build, control-loop simulation, Bode measurement, motor identification, SIL/HIL, hardware timing capture or physical motor test was performed.
- Actual AEL-002 motor, (R_s,L_d,L_q,\psi_f), current limits, DC bus range, modulation, (T_s,T_d), ADC/PWM route, PI gains, bandwidth, phase margin target and MCU/SDK remain TBD.
- Review date: 2026-11-28. Final commit SHA and CI run IDs to be appended after final verification.
