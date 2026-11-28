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
