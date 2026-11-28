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
