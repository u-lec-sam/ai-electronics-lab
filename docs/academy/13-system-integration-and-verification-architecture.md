# 13장 — 시스템 통합과 검증 아키텍처

> **핵심 질문:** 회로·센서·FOC·실시간 펌웨어·통신이 각각 동작한다는 사실을 넘어, 전체 서보드라이브가 요구된 시간 안에 올바른 데이터를 사용하고 고장 시 정해진 안전 상태로 전이한다는 것을 어떻게 증명할까?

이 장은 특정 MCU나 보드 설정을 확정하지 않는다. Chapters 08–12의 기능을 end-to-end 계약과 시험 증거로 묶는다. 모든 숫자 예제는 가상값이며 AEL-002 정격·주기·안전 임계값이 아니다.

## 1. 학습 목표와 용어

학습 후 다음을 할 수 있어야 한다.
1. 요구사항을 측정 가능한 shall 문장과 acceptance criteria로 바꾼다.
2. 요구사항–아키텍처–인터페이스–시험–결과의 양방향 추적성을 만든다.
3. verification과 validation, analysis·inspection·demonstration·test를 구분한다.
4. ADC sample부터 PWM active update까지 end-to-end timing budget을 계산한다.
5. Chapters 08–12 interface contract를 단위·범위·timestamp·validity·ownership·deadline으로 정의한다.
6. host unit test, integration test, SIL, HIL, physical test의 증거 범위를 구분한다.
7. safety fault detection부터 independent inhibit까지 시간과 권한 경계를 분석한다.
8. 재현 가능한 test record, configuration baseline, release gate를 만든다.
9. 여러 공식·전문 출처를 교차 확인하고 불일치·미확인 상태를 기록한다.

**Verification(검증):** 정해진 요구사항을 제품/산출물이 만족하는가?  
**Validation(타당성 확인):** 실제 사용 목적과 운용 시나리오에 적합한가?

NASA Systems Engineering Handbook는 요구사항별 verification method/matrix, validation matrix, integration plan 및 end-to-end V&V를 분리해 다룬다. IEEE 1012-2024는 시스템·소프트웨어·하드웨어와 인터페이스의 V&V lifecycle process를 다룬다. 이 강의는 두 자료의 개념을 학습용 프로세스로 사용하며 인증이나 표준 준수를 주장하지 않는다.

## 2. 요구사항을 시험 가능한 문장으로 바꾸기

### 2.1 요구사항의 최소 구조

예시:
- TIM-ADC-001: 정의된 최악 실행 부하에서 전류 제어 계산은 해당 PWM shadow-load deadline 전에 완료되어야 한다.
- COM-CMD-002: 수신한 command는 schema, sequence, freshness, range, drive-state 검사를 모두 통과하기 전에는 control mailbox에 게시되어서는 안 된다.
- SAFE-FAULT-003: latched safety fault가 존재하는 동안 원격 통신 요청만으로 fault latch를 clear하거나 PWM enable을 허가해서는 안 된다.

요구사항마다 다음을 기록한다.

| 필드 | 질문 |
|---|---|
| ID | 유일하고 변경에 안정적인가? |
| Source | 고객 요구, 위험 분석, 표준, 설계 결정 중 어디서 왔나? |
| Rationale | 왜 필요한가? |
| Shall statement | 주체·행위·조건·결과가 분명한가? |
| Operating condition | 전압/온도/속도/부하/통신 부하 등 적용 조건은? |
| Metric/unit | 무엇을 어떤 단위로 측정하나? |
| Acceptance criteria | pass/fail 경계가 정의됐나? |
| Verification method | analysis/inspection/demonstration/test 중 무엇인가? |
| Evidence | test ID, report, tool, version, artifact, SHA는? |
| Owner/status | 담당·미확인·승인 상태는? |

"빠르게", "안전하게", "충분히", "정확하게"만 있는 문장은 acceptance criteria가 아니다. 값이 아직 없으면 숫자를 발명하지 않고 TBD requirement로 남기며, 어떤 입력/위험 분석으로 값을 결정할지 적는다.

### 2.2 요구사항 품질 규칙

- 하나의 요구사항은 한 가지 검증 의무를 표현한다.
- 주어·조건·동작·관찰 가능한 결과가 명확하다.
- 단위·부호·좌표계·시간 기준을 정의한다.
- 구현 방법을 불필요하게 강제하지 않는다.
- 모순·중복·순환 참조가 없다.
- 요구사항 자체가 시험 가능한 acceptance criteria를 포함한다.
- 변경 시 상위 요구사항, 하위 설계, 코드, 테스트 영향이 추적된다.

### 2.3 Traceability graph

~~~text
Stakeholder / Hazard / Standard
              |
              v
        System Requirement
              |
              v
       Architecture Element
              |
              v
     Interface / Timing Contract
              |
              v
       Design / Implementation
              |
              v
         Verification Case
              |
              v
       Test Result / Evidence
              |
              v
        Release Decision
~~~

양방향으로 추적한다. 시험이 없는 요구사항은 verification gap이다. 요구사항이 없는 시험은 목적과 위험을 다시 확인한다. 모든 shall 요구사항은 적어도 하나의 planned verification case를 가진다. safety-critical requirement는 분석·검사·시험 등 독립된 방법을 조합한다.

## 3. V&V 방법과 증거 수준

### 3.1 네 가지 verification method

| 방법 | 의미 | 예 |
|---|---|---|
| Analysis | 모델·수식·정적 분석으로 입증 | timing budget, thermal model, CAN response-time analysis |
| Inspection | 문서·회로·코드·실물의 정적 확인 | pin map, BOM, source review |
| Demonstration | 계측 정밀도보다 기능의 존재/절차를 확인 | 진단 화면, maintenance workflow |
| Test | 입력을 주고 관찰값을 측정해 기준과 비교 | parser fault injection, ADC timing capture |

시뮬레이션은 모델 실행에 의한 분석/시험의 일부로 분류할 수 있다. 모델 검증(model verification: 방정식/구현이 모델 정의와 일치하는가)과 모델 타당성(model validation: 모델이 현실을 충분히 대표하는가)을 구분한다.

### 3.2 AEL 증거 단계

아래는 프로젝트 내부 분류이며 ISO/IEC의 공식 maturity level이 아니다.

| Level | 이름 | 증거 | 주장 가능한 범위 |
|---|---|---|---|
| E0 | 주장/가설 | 아이디어, 요구사항 초안 | 설계 의도 |
| E1 | 문헌·분석 | 표준/공식 문서, hand calculation | 이론/조건부 예측 |
| E2 | 정적 산출물 | schematic/code/config review, static checks | 산출물의 정적 특성 |
| E3 | Host test | target-independent unit/property/fuzz tests | host 실행 경로의 동작 |
| E4 | SIL/model | 명시된 모델에서 closed-loop/fault test | 모델 범위 내 동작 |
| E5 | Target/HIL | exact target build, I/O/plant HIL, measured timing | 시험한 target/configuration 범위 |
| E6 | Physical verification | 통제된 실제 하드웨어·부하·계측 시험 | 시험한 sample, 조건, revision만 |

한 단계의 성공이 다음 단계를 자동으로 증명하지 않는다. E3 host parser pass는 MCU DMA, CAN transceiver, FOC deadline을 증명하지 않는다. E4 SIL pass는 실제 MOSFET, 절연, 방열을 증명하지 않는다. E6도 시험하지 않은 온도·부하·전압·수명 범위까지 보장하지 않는다.

**현재 AEL-002 상태:** 승인된 실제 hardware test 증거가 없다. NO STACK / NO POWER를 유지한다.

## 4. End-to-end control timing budget

### 4.1 기준 시점 정의

- \(t_m\): rotor sensor measurement timestamp
- \(t_s\): current ADC effective aperture timestamp
- \(t_c\): control computation start
- \(t_f\): control computation finish
- \(t_w\): PWM shadow register write completion
- \(t_u\): new PWM value becomes active at hardware load event

\[
T_{sample\to active}=t_u-t_s
\]
\[
T_{compute}=t_f-t_c,\quad T_{write}=t_w-t_f,\quad T_{wait}=t_u-t_w
\]
\[
T_{sample\to active}=T_{compute}+T_{write}+T_{wait}
\]

ADC conversion latency before CPU reads data is a separate segment from analog aperture to data-ready. Do not count it twice. Sensor measurement age \(t_s-t_m\) is another segment; do not silently equate sensor timestamp and ADC timestamp.

### 4.2 Deadline inequality

\[
T_{ADC\_ready}+T_{dispatch}+T_{FOC}+T_{write}\leq T_{deadline}
\]

A complete budget adds bounded interrupt masking, higher-priority ISR interference, DMA arbitration, cache/bus stalls (if applicable), and measurement uncertainty. Worst-case execution time (WCET) is not average execution time.

For periodic tasks, utilization is a first screen:

\[
U=\sum_i\frac{C_i}{T_i}
\]

\(C_i\) is worst-case execution time and \(T_i\) is period. \(U<1\) alone does not prove deadline feasibility when priorities, blocking, release jitter, non-preemptive sections, interrupt interference and shared buses exist.

### 4.3 Chapters 08–12 integrated timing path

~~~text
Rotor sensor edge/sample
      | timestamp + validity (Ch09)
      v
Sensor estimate / angle prediction
      |
PWM event -> ADC SOC -> analog aperture -> conversion ready
      |                                  |
      +----------------------------------+
                         |
                  ISR/dispatch (Ch10)
                         |
            snapshot + ownership check (Ch10/11)
                         |
             Clarke/Park + PI + limits (Ch08)
                         |
                 PWM shadow write
                         |
                 PWM load event
                         v
                  Active inverter output

Communication RX (Ch12) -> DMA/ring -> parser -> validation
                         -> mailbox snapshot
                         -> control-cycle boundary check
                         (never bypasses FOC/state/safety gate)
Telemetry (Ch12) <- immutable snapshot / DMA ownership
~~~

통신 parser, CRC 계산, diagnostic formatting, NVM write를 current-loop ISR에 넣지 않는다. 통신 task는 제어 task를 block하지 않는다. control task가 command snapshot을 수락하더라도 sensor validity, fault latch, limits, command age를 control boundary에서 재검사한다.

### 4.4 가상 timing 계산 — 단일 FOC cycle

| Segment | 가상 최악 시간 |
|---|---:|
| ADC aperture to conversion ready | 2.0 µs |
| interrupt dispatch + bounded higher-priority interference | 1.5 µs |
| sensor snapshot/angle prediction | 1.0 µs |
| Clarke/Park/current PI/limits/SVPWM | 7.0 µs |
| PWM shadow write + validation | 0.5 µs |
| **합계** | **12.0 µs** |

가정한 deadline이 20 µs라면 slack:

\[
S=20-12=8\ \mu s,\quad S_r=8/20=0.40=40\%
\]

이는 이 가상 workload에서만 성립한다. 12 µs가 실제 F280039C 또는 STM32 실행시간이라는 뜻이 아니다. 실측/정적 WCET, compiler optimization, memory wait states, ISR interference, DMA contention, temperature/clock condition을 반영해야 한다.

### 4.5 가상 phase-delay 계산

전기각 속도 2,000 electrical rad/s, sample-to-active delay 12 µs라고 가정하면:

\[
\Delta\theta_e=\omega_e\Delta t
=2000\times12\times10^{-6}=0.024\ rad
\]
\[
0.024\times180/\pi=1.375^\circ
\]

지연이 전기각 오차로 변환되는 방법을 보이는 예다. 허용 오차와 보상 방식은 motor speed, pole pairs, sensor latency, PWM update timing, control design으로 결정한다.

## 5. Interface contract — 모든 경계에 필요한 정보

| Contract field | 반드시 정의할 내용 |
|---|---|
| Producer / consumer | 데이터 생성자와 소비자 |
| Data meaning | 물리량/상태의 정확한 의미 |
| Type/representation | width, signedness, fixed-point scale, endian |
| Unit/sign/frame | SI unit, positive direction, dq/abc convention |
| Valid range | min/max, saturation, invalid sentinel |
| Validity | valid/stale/degraded/faulted semantics |
| Timestamp | clock domain, capture point, uncertainty, wrap |
| Ownership | CPU/ISR/DMA/driver owner and handoff |
| Rate/deadline | nominal/max rate, age/deadline |
| Atomicity | snapshot consistency and concurrency rule |
| Error behavior | invalid, timeout, overflow, disconnect |
| Safety authority | interface may/may not command |
| Version | schema/API compatibility |
| Verification | requirement ID, test ID, evidence level |

### 5.1 Interface inventory

| Interface | Contract focus | Chapter |
|---|---|---|
| ADC → current control | aperture, scale, offset, polarity, saturation, sample-valid | 08/10 |
| QEP/Hall/Resolver → estimator | mechanical/electrical angle, timestamp, direction, validity, latency | 09/10 |
| FOC → PWM | normalized command, voltage limit, update deadline, inhibit precedence | 08/10 |
| DMA → CPU | ownership, buffer lifetime, completion, cache/alignment, overrun | 10/11 |
| Communication → command mailbox | schema, session, sequence, age, unit, limits, state permission | 11/12 |
| Fault source → safety manager | source, event timestamp, set-dominant latch, clear authority | 11/12 |
| Parameter service → active config | schema, CRC, range, cross-field consistency, atomic commit | 11/12 |
| Telemetry → transport | immutable snapshot, timestamp, validity, backpressure | 10/12 |

### 5.2 Invalid is not zero

센서 오류를 zero current/zero speed/zero angle로 바꾸면 실제 정상값과 구분할 수 없다. 모든 measurement interface는 value와 함께 validity/status를 전달한다. invalid data는 제어에 사용하지 않고 정의된 degraded/fault response를 적용한다.

## 6. Fault-to-safe-state trace

### 6.1 Safety path

~~~text
Hazard / fault source
      |
      +--> Independent hardware path (where designed)
      |        comparator / gate-driver fault / inhibit
      |                    |
      |                    v
      |             PWM/gate inhibit
      |
      +--> MCU detection path
               |
          fault event capture
               |
          set-dominant latch
               |
          control state transition
               |
          command invalidation
               |
          fault record + diagnostic report
               |
          supervised clear only
               |
          DISARMED (never direct RUNNING)
~~~

소프트웨어 진단은 독립 하드웨어 차단을 대체하지 않는다. 하드웨어 inhibit의 존재, polarity, latency, latch behavior, reset behavior는 exact schematic/datasheet/target inspection이 필요하다. 실제 AEL-002 보드에 특정 comparator/Trip Zone path가 있다고 주장하지 않는다.

### 6.2 Fault response contract

각 fault에 대해 source and detection condition, detection latency and sampling uncertainty, hardware inhibit path and worst-case latency, software latch set latency and priority, outputs/command state, fault record capture/overflow, recovery/clear authority, restart preconditions, test/evidence level, residual risk를 기록한다.

### 6.3 Set-dominant fault latch

\[
Fault_{next}=Fault_{set}\lor(Fault_{current}\land\neg Clear_{authorized})
\]

개념적 상태식이다. 실제 구현의 동시성·atomicity·hardware trip clear sequence는 Chapter 11과 exact MCU documentation을 따라야 한다. 원격 통신은 clear authority가 아니다.

### 6.4 가상 fault latency budget

| Segment | 가상 최악값 |
|---|---:|
| Comparator propagation | 0.8 µs |
| Hardware inhibit propagation | 0.4 µs |
| Gate-driver disable propagation | 0.7 µs |
| **Hardware path total** | **1.9 µs** |

별도 MCU software path가 ADC sample wait 10 µs + dispatch 2 µs + latch 1 µs라면 13 µs다. 두 path는 병렬일 수 있지만 실제 안전 성능은 회로·전력소자·게이트 드라이버·모터의 물리적 turn-off와 energy decay까지 포함해 분석해야 한다. 1.9 µs는 교육용 숫자이며 실제 AEL-002 보호시간이 아니다.

## 7. Test architecture — host부터 physical test까지

~~~text
Physical / production-like validation (E6)
             ^
         HIL / target I/O (E5)
             ^
       SIL / plant model (E4)
             ^
  Host integration / fuzz / property (E3)
             ^
  Unit / static checks / review (E2)
             ^
       Analysis / source (E1)
~~~

- **Unit:** pure function, parser, CRC, sequence arithmetic, fixed-point saturation, state transition.
- **Component integration:** driver adapter + fake peripheral, DMA ownership state, mailbox, fault manager.
- **Host fuzz/property:** malformed length, random byte stream, wrap boundaries, integer overflow, queue-full.
- **SIL:** motor/inverter/sensor/plant model을 연결해 control response와 fault scenario 평가.
- **Target test:** exact MCU, compiler, SDK, linker, clock, board revision에서 build와 timing 확인.
- **HIL:** real controller I/O와 real-time plant simulator 연결. HIL model fidelity와 latency도 검증한다.
- **Physical test:** 승인된 fixture, current-limited source, guarding, emergency stop, measurement plan과 authorized operator 아래서만 수행한다.

Host test는 target interrupt latency, ADC aperture/trigger routing, ePWM shadow/Trip Zone, QEP pin mux, DMA/cache, compiler ABI, transceiver propagation/isolation, gate-driver shutdown과 regenerative energy를 증명하지 않는다.

### 7.1 Deterministic fault injection

각 test는 seed, injected event, time, expected state, measured output, pass/fail을 고정한다. Random fuzz는 seed와 corpus를 저장한다. Test harness clock, scheduler, model fidelity와 sensor noise도 versioning한다.

필수 fault families:
- ADC stuck-at, out-of-range, stale timestamp, conversion overrun
- encoder direction reversal, missed edge, index glitch, Hall invalid sector, Resolver amplitude/phase invalid
- DMA overrun, buffer reuse before completion, torn snapshot
- FOC execution overrun, interrupt storm, priority inversion, watchdog expiry
- UART framing/overrun/CRC/length/sequence error
- CAN error-passive/bus-off, queue overflow, stale command, peer loss
- parameter schema mismatch, CRC fail, interrupted NVM write, cross-field mismatch
- fault set/clear race, repeated fault, diagnostic queue overflow
- communication recovery while drive was RUNNING or FAULT_LATCH

## 8. Test record와 재현성

| Field | 기록 규칙 |
|---|---|
| Test ID | unique stable ID |
| Requirement IDs | verified shall requirements |
| Test level | E1…E6 |
| Source revision | commit SHA, document revision |
| Firmware/build | compiler, flags, SDK, linker, binary hash |
| Hardware article | exact board/PCB/BOM/sample revision or N/A |
| Setup | wiring, fixture, instruments, calibration status |
| Environment | voltage/current/temperature/load/clock/network |
| Input/seed | vector, trace, fault injection, random seed |
| Expected | numeric/logic acceptance criteria |
| Actual | raw measurement/log/result |
| Uncertainty | instrument accuracy, timing resolution, model error |
| Verdict | pass/fail/blocked/not run |
| Anomaly | issue ID, severity, containment |
| Reviewer | author and independent reviewer |
| Artifact | log, waveform, report link |

Pass는 acceptance criteria와 evidence가 있을 때만 쓴다. Not run, blocked, inconclusive는 실패와 구분하되 통과로 세지 않는다.

## 9. 가상 통합 계산과 전체 풀이

### A — end-to-end timing

ADC conversion-ready 2 µs, dispatch 1.5 µs, snapshot 1 µs, FOC 7 µs, PWM write 0.5 µs 가정:

\[
T=2+1.5+1+7+0.5=12\ \mu s
\]

deadline=20 µs이면 slack=25? 아니며 \(20-12=8\ \mu s\), slack ratio=8/20=40%다. 이 수치는 가상이며 target WCET 증거가 아니다.

### B — control phase error

\(\omega_e=2000\ rad/s\), \(\Delta t=12\ \mu s\):

\[
\Delta\theta=2000\times12\times10^{-6}=0.024\ rad
\]
\[
0.024\times180/\pi=1.375^\circ
\]

### C — periodic task utilization

- current loop C=12 µs, T=50 µs
- speed loop C=8 µs, T=1,000 µs
- diagnostics C=40 µs, T=10,000 µs

\[
U=12/50+8/1000+40/10000=0.252=25.2\%
\]

이 값만으로 schedulability를 증명하지 못한다. fixed-priority response-time analysis, ISR interference, blocking, jitter, DMA/bus stalls를 추가한다.

### D — fault path budget

가정된 hardware path: 0.8+0.4+0.7=1.9 µs. MCU software path: sample wait 10 + dispatch 2 + latch 1 =13 µs. 경로의 시작 사건과 endpoint가 다르므로 단순 합산하지 않는다. 병렬 경로의 inhibit 시점과 실제 gate/phase current decay를 별도 측정/분석한다.

### E — sensor sample age

sensor measurement timestamp \(t_m=1000\ \mu s\), ADC aperture \(t_s=1020\ \mu s\), PWM active update \(t_u=1032\ \mu s\):
- sensor age at ADC aperture = 20 µs
- sample-to-active delay = 12 µs
- sensor age at PWM update = 32 µs

센서 timestamp와 ADC aperture를 같은 시각으로 취급하면 20 µs의 sensor age를 놓친다.

## 10. 연습문제와 전체 풀이

1. verification과 validation의 차이를 설명하라.
2. "The drive shall be fast"가 불충분한 이유는?
3. 18 µs timing budget이 25 µs deadline에 들어오면 slack과 ratio는?
4. 10 kHz task의 period는 몇 µs인가?
5. 100 MHz clock에서 1 cycle은 몇 ns인가?
6. C=15 µs, T=50 µs task의 utilization은?
7. task utilization 70%이면 모든 deadline이 보장되는가?
8. ADC aperture=50 µs, PWM active update=62 µs일 때 sample-to-active delay는?
9. sensor measurement=40 µs, ADC aperture=50 µs, PWM update=62 µs일 때 PWM update 시 sensor age는?
10. Host parser test pass가 실제 RS-485 transceiver 동작을 증명하지 않는 이유는?
11. fault set과 clear가 같은 cycle이면 무엇이 우선해야 하는가?
12. link recovery 뒤 이전 torque command를 자동 재개하면 안 되는 이유는?
13. traceability에서 test가 없는 shall은 무엇을 의미하는가?
14. E4 SIL 성공이 실제 MOSFET turn-off를 증명하는가?
15. 가상 fault path 0.8+0.4+0.7 µs의 합은?
16. CRC pass만으로 parameter image를 commit해도 되는가?
17. test report에 commit SHA가 필요한 이유는?
18. 안전 요구사항 하나에 독립적인 verification method를 조합하는 이유는?

**전체 풀이**

1. Verification은 명세된 요구사항 만족 여부, validation은 실제 운용 목적/사용자 요구에 대한 적합성이다.
2. 측정량, 조건, deadline, acceptance boundary가 없다. 특정 worst-case load에서 computation 완료 deadline을 명시해야 한다.
3. slack=25−18=7 µs. ratio=7/25=28%.
4. 1/10,000 s=100 µs.
5. 1/100 MHz=10 ns.
6. U=15/50=30%.
7. 아니다. priority, blocking, jitter, ISR, release pattern, WCET가 필요하다.
8. 62−50=12 µs.
9. 62−40=22 µs.
10. host에는 실제 transceiver, cable, common-mode, termination, DE timing, propagation delay가 없다.
11. set-dominant. fault clear가 fault event를 덮어쓰면 안 된다.
12. old command가 stale/replay일 수 있고, 기계 상태·sensor validity·interlocks가 복구됐다는 증거가 없다. DISARMED에서 새 arm을 요구한다.
13. verification gap이다. planned case를 만들거나 requirement를 정정해야 한다.
14. 아니다. model은 실제 power semiconductor, gate driver, layout parasitics, thermal/energy behavior를 포함하지 않을 수 있다.
15. 1.9 µs.
16. 아니다. schema/version/length/range/cross-field/compatibility/transaction integrity와 NVM read-back/commit이 필요하다.
17. 결과를 생성한 정확한 source/configuration을 재현하고 결과와 code baseline을 연결하기 위해서다.
18. 단일 분석/시험의 모델 가정이나 blind spot을 보완하고 independent failure mode를 드러내기 위해서다.

## 11. AEL-002 통합 요구사항·시험 매트릭스 초안

아래 ID는 검증 체계 예시이며 승인된 project requirement baseline이 아니다.

| Req ID | Requirement intent | Planned verification | Evidence now |
|---|---|---|---|
| TIM-001 | ADC-to-PWM update meets configured deadline | WCET analysis + target trace | TBD |
| TIM-002 | missed control deadline triggers defined response | host state test + target fault injection | TBD |
| SNS-001 | invalid sensor sample never enters FOC as valid | unit/property + SIL | TBD |
| SNS-002 | angle and current timestamps preserve clock-domain semantics | analysis + interface test | TBD |
| DMA-001 | CPU reads only completed/owned DMA snapshot | host ownership model + target stress | TBD |
| COM-001 | stale/replay command rejected | parser/property/fuzz | TBD |
| COM-002 | communication recovery does not auto-resume motion | state-machine test + HIL | TBD |
| PAR-001 | invalid parameter transaction never partially updates active config | host power-fail model + NVM target test | TBD |
| SAFE-001 | fault set dominates concurrent clear request | model/unit + target race test | TBD |
| SAFE-002 | communication cannot clear latched safety fault or directly enable PWM | API review + negative test + target I/O test | TBD |
| SAFE-003 | hardware inhibit path remains independent of application task | schematic analysis + target fault test | TBD |
| DIAG-001 | fault record captures source/time/state and overflow behavior | unit + stress test | TBD |
| SYS-001 | telemetry load cannot violate current-loop deadline | response-time analysis + max-load test | TBD |

모든 numeric threshold, actual clock, PWM frequency, current/voltage limit, timeout, sensor accuracy, fault response time, bus rate와 load profile은 target evidence 및 risk analysis 전까지 TBD다.

## 12. Fault-injection matrix

| ID | Injection | Expected invariant | Planned evidence |
|---|---|---|---|
| INT-01 | ADC data stale | invalid data not consumed as fresh | host/SIL/target |
| INT-02 | sensor timestamp discontinuity | angle estimate invalid/degraded | host/SIL |
| INT-03 | QEP/Hall/Resolver implausible jump | diagnostic and defined state response | host/SIL/target |
| INT-04 | FOC execution overrun | no unbounded late PWM update | model/target |
| INT-05 | interrupt storm | deadline monitor detects violation | target |
| INT-06 | DMA buffer reused early | consumer rejects ownership violation | host/target |
| INT-07 | communication burst | current-loop deadline preserved | host/target |
| INT-08 | stale/replay command | mailbox unchanged | host/fuzz |
| INT-09 | CAN bus-off | TX stopped, fault recorded, drive disarmed | host/HIL/target |
| INT-10 | parameter NVM write interrupted | old or fully validated new slot only | host/target |
| INT-11 | fault set+clear same cycle | fault remains latched | host/target |
| INT-12 | remote clear request during fault | request rejected, no PWM enable | host/HIL |
| INT-13 | watchdog reset | reset begins output-inhibited | analysis/target |
| INT-14 | telemetry queue overflow | bounded loss, no control blocking | host/target |
| INT-15 | model parameter mismatch | validation discrepancy recorded | SIL/physical correlation |
| INT-16 | target compiler/SDK update | regression suite and timing re-baseline | build/target |

## 13. Source triangulation — 강의의 근거를 어떻게 확인할까

### 13.1 출처 계층

| Source class | 역할 | 예 |
|---|---|---|
| Normative standard | 요구사항·용어·적합성 기준 | IEC/ISO/IEEE/TIA/CiA normative specification |
| Manufacturer primary source | exact silicon/part limits and implementation | datasheet, reference manual, errata, official SDK |
| Professional technical source | engineering interpretation/system design | CiA technical report, manufacturer application report |
| Academic source | derivation/model/independent explanation | university textbook, peer-reviewed paper |
| Secondary web source | discovery/supplementary explanation only | blog/forum/video |

서로 다른 웹사이트 3개가 같은 원문을 복사한 것은 독립적인 교차검증 3개가 아니다. 발행기관, 원문, 버전, 인용 관계를 확인한다.

### 13.2 Claim-by-claim evidence matrix

| Claim type | Minimum review path |
|---|---|
| Normative protocol behavior | exact applicable standard edition + independent official technical explanation/controller manual |
| Device-specific register/pin/timing | exact device datasheet + reference manual + errata + matching SDK release/example |
| Control theory/equations | canonical textbook/peer-reviewed source + independent derivation/unit check |
| Circuit/thermal rating | exact component datasheet operating conditions + manufacturer application note + worst-case calculation |
| Functional safety | applicable safety standard + hazard/risk analysis + architecture evidence + independent review |
| Software language behavior | language standard/official compiler manual + CERT/recognized coding guidance + target compiler verification |
| Numerical example | documented assumptions + dimensional analysis + independent recomputation |

안전·정격·핀맵·절연·보호 시간에 영향을 주는 주장은 출처가 하나뿐이면 확정하지 않는다. normative requirement는 원문 표준을 우선한다. 보조 자료가 원문과 충돌하면 원문과 적용 edition을 기준으로 차이를 기록한다.

### 13.3 Source record template

각 핵심 주장에 Claim ID and exact sentence, source role (normative/manufacturer/professional/academic), issuer/title/document number/revision/edition/date, clause/page/table/figure/register/API symbol, URL/access date, supported conditions, independent cross-check/disagreement, AEL applicability (generic/candidate/exact target/measured), confidence (confirmed/conditional/TBD/contradicted), reviewer/date/commit SHA를 남긴다.

### 13.4 Chapter 13에서 확인한 공식·전문 자료

1. NASA, *Systems Engineering Handbook* — requirements verification matrix, validation matrix, integration plan, end-to-end integration, test article과 V&V method.
2. IEEE 1012-2024 — system/software/hardware와 interface의 V&V lifecycle process를 정의하는 active standard. 공개 scope/abstract만 확인했으며 유료 전문의 세부 조항 준수 주장은 하지 않는다.
3. IEC 61508-3:2010 — safety-related software lifecycle 요구사항의 현행 공개 catalogue entry. IEC 61508-3:2026은 2026-10-02 pre-release/FDIS로 표시되고 최종 publication forecast가 2027-01-22이므로 아직 published edition으로 인용하지 않는다.
4. IEC 61800-5-2:2016+AMD1:2026 — adjustable-speed power drive system의 safety-related PDS functional safety 범위. AEL-002가 해당 표준을 준수하거나 STO를 구현했다는 뜻은 아니다.
5. TI, *The Essential Guide for Developing With C2000 Real-Time Microcontrollers* (SPRACN0F Rev. F) — PWM/ADC synchronization, sample aperture, interrupt latency, update timing. C2000 사례를 다른 MCU에 일반화하지 않는다.
6. TI, *C2000 ePWM Developer’s Guide* (SPRAD12A Rev. A) — ePWM event, ADC SOC, Trip Zone architecture. 정확한 device routing은 device datasheet/TRM/errata로 확인해야 한다.
7. TI MotorControl SDK official guide/release page — SDK 지원 솔루션과 release version을 확인하는 출발점. 현재 TI page의 SDK 6.00.00.00이 보여도 AEL-002가 그 버전을 사용한다는 근거가 아니다.

### 13.5 출처 간 충돌 처리

- 규격의 적용 edition과 제품/지역 요구사항을 먼저 확인한다.
- 제조사 문서가 표준보다 더 좁은 부품 제한을 두면 exact part limitation을 따른다.
- 개정 간 수치가 달라지면 obsolete revision과 현재 적용판을 표시한다.
- 논문/블로그 수치가 datasheet operating condition과 다르면 조건 차이를 기록한다.
- 원문 표준 전문을 확인할 수 없다면 공개 scope/abstract 범위까지만 말하고 clause-level compliance를 주장하지 않는다.
- 출처가 다른 조건을 가정하면 하나의 숫자로 평균하지 않는다.

## 14. Release gate와 configuration baseline

### G0 — Requirements baseline
- system boundary, operating modes, hazards, assumptions, unresolved requirements identified
- all shall requirements have verification approach and acceptance criteria
- interface/timing contracts have owner and version

### G1 — Architecture/design review
- power/control/sensor/communication/fault boundaries reviewed
- independent inhibit assumptions and residual risks documented
- component and target selections supported by exact primary documents
- unresolved values remain TBD

### G2 — Host/static evidence
- unit/property/fuzz tests deterministic and reproducible
- static analysis/compiler warnings policy recorded
- parser, arithmetic, state machine, parameter transaction tests pass
- CI run and commit SHA recorded

### G3 — SIL evidence
- plant/controller/sensor/network model versions pinned
- nominal, boundary and fault scenarios pass
- model fidelity/limitations documented
- no model result represented as physical result

### G4 — Target/HIL evidence
- exact MCU, silicon revision, compiler, SDK, linker, board/BOM revision pinned
- target build and peripheral routing verified from official sources
- I/O timing, DMA ownership, watchdog and fault paths tested
- HIL latency, model error and test coverage recorded

### G5 — Physical test authorization
- approved test plan, risk assessment, fixture, current-limited supply, independent inhibit, guarding and emergency procedure reviewed
- exact hardware sample, connectors, jumpers, pin1, grounding and measurement setup physically verified by authorized personnel
- motor/load/supply ratings and regenerative energy path established
- explicit approval before any stack/power operation

**Current gate:** G0/G1 documentation architecture only. G2/G3/G4 evidence is not inferred from this chapter. G5 is blocked. **NO STACK / NO POWER.**

A reproducible test baseline includes source commit SHA, compiler/version/flags/ABI/linker, SDK/revision/generated config, MCU order code/silicon revision, PCB/assembly/BOM revision, protocol/schema/parameter version, model/test harness revision/seed, calibration/instrument certificates, procedure revision/operator/reviewer, artifact hashes. Baseline 없는 결과는 이후 결과와 신뢰성 있게 비교하기 어렵다.

## 15. AEL-002 현재 미확인 사항

| Domain | Still TBD until evidence |
|---|---|
| Motor/plant | exact motor, pole pairs, R/L/flux, inertia, load, speed/torque profile |
| Power stage | exact BOM, current/voltage/thermal limits, DC-link capacitance, regen sink |
| MCU | exact order code, silicon revision, clock, peripheral route, compiler/ABI |
| FOC timing | PWM/ADC rate, aperture, WCET, ISR interference, shadow-load deadline |
| Sensors | exact encoder/Hall/Resolver, scale, direction, timestamp latency, validity thresholds |
| DMA | channel, ownership, bus contention, cache/coherency, memory placement |
| Communications | transceiver, connector, pin mux, bit rate, topology, ID map, isolation |
| Safety | hazard analysis, hardware inhibit topology, measured propagation, safe stop behavior |
| Validation | SIL model, HIL plant, test fixture, instruments, physical authorization |

후보 MCU 또는 SDK에 특정 기능이 있다는 사실만으로 AEL-002 보드에 해당 회로·핀·배선·펌웨어가 존재한다고 판단하지 않는다.

## 16. 완료 기준

- [ ] verification과 validation을 구분한다.
- [ ] 모든 shall 요구사항이 unique ID, source, acceptance criteria, verification method를 가진다.
- [ ] 양방향 traceability가 있다.
- [ ] timing budget에 measurement aperture, compute, write, load event가 분리돼 있다.
- [ ] WCET와 평균 execution time을 구분한다.
- [ ] interface마다 unit/range/validity/timestamp/ownership/deadline이 정의돼 있다.
- [ ] invalid sensor data가 정상 zero로 위장되지 않는다.
- [ ] fault set이 clear보다 우선한다.
- [ ] host/SIL/HIL/physical evidence 범위가 분리돼 있다.
- [ ] fault injection이 deterministic/reproducible하다.
- [ ] test result에 SHA/configuration/measurement uncertainty가 포함된다.
- [ ] 핵심 주장이 공식·전문 자료로 교차 확인된다.
- [ ] 출처의 edition/revision와 적용 범위가 기록된다.
- [ ] 실제 AEL-002 미확인 항목은 TBD로 유지한다.
- [ ] G5 승인 전 NO STACK / NO POWER를 지킨다.

**현재 판정:** Chapter 13은 통합 요구사항, timing/interface contract, fault trace, V&V evidence hierarchy, source triangulation, release gate를 정의한다. 실제 AEL-002 target build, SIL/HIL, hardware timing measurement, safety certification 또는 physical verification을 수행했다는 증거가 아니다.

**안전 상태: NO STACK / NO POWER.**
