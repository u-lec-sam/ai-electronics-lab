# 10장 — MCU 클록·타이머·인터럽트·DMA와 실시간 제어

## 학습 목표

FOC는 수학적으로 올바른 계산뿐 아니라 **언제 샘플을 취득하고, 언제 각도를 계산하고, 언제 PWM에 반영했는가**가 중요하다. 이 장은 clock tree, timer/capture/compare, QEP, interrupt, DMA, PWM/ADC timing, scheduling/WCET를 연결한다.

AEL-002의 MCU 주문 코드·silicon revision·clock·pin mux·QEP/eCAP/ePWM/ADC route·interrupt priority·DMA channel·PWM/ADC frequency·ISR budget·WCET는 정확한 보드/SDK 근거를 대조하기 전까지 **TBD**다. 아래 숫자는 모두 교육용 가상값이다.

## 1. 쉬운 설명: MCU에는 여러 개의 시계가 있다

CPU는 명령을 실행하고, 주변장치는 독립된 clock과 counter로 이벤트를 만든다. clock tree는 기준 발진기에서 CPU와 peripheral까지 clock을 나누는 구조다. timer는 시간을 세고, capture는 외부 edge가 온 순간 counter를 저장하며, compare는 counter가 설정값에 도달했을 때 이벤트를 만든다. QEP는 A/B quadrature 신호를 하드웨어로 해석한다. DMA는 CPU 대신 메모리 전송을 수행한다.

비유의 한계: 실제 MCU에는 PLL, 분주기, clock gating, bus wait-state, synchronizer, clock-domain crossing(CDC)이 있다. peripheral clock이 CPU clock과 같다고 가정하지 않는다.

## 2. Clock tree와 시간 단위

주파수 f는 초당 반복 횟수(Hz = s⁻¹), 주기 T는 반복에 걸리는 시간(s)이다.

\[
T=1/f,\qquad f=1/T
\]

100 MHz clock의 주기는 \(10\,ns\)다. 단위 검산: \(1/s^{-1}=s\).

~~~text
외부 발진기 → PLL → SYSCLK → 분기/분주 → CPUCLK / PERCLK / TBCLK / ADCCLK
~~~

확인 순서:
1. 실제 oscillator 부품/주파수, MCU 주문 코드와 silicon revision을 확인한다.
2. datasheet 허용 clock과 reference manual의 PLL/분주 구조를 확인한다.
3. SDK clock init 및 생성 설정을 읽는다.
4. PLL lock/fail-safe/저전력 복귀와 watchdog clock을 확인한다.
5. CPU, timer, PWM, ADC clock을 각각 계산하고 레지스터와 대조한다.

기준 발진기 오차 ±20 ppm은 1초에 약 ±20 μs의 오차를 만들 수 있다. 온도·노화·PLL 오차는 별도다.

서로 다른 clock domain 신호를 직접 샘플링하면 metastability 위험이 있다. 단일 bit에는 2단 synchronizer 등을 사용할 수 있지만 multi-bit bus는 handshake, Gray counter, asynchronous FIFO 등이 필요하다. encoder A/B synchronizer/filter는 노이즈 위험을 낮추는 대신 지연과 jitter를 더한다.

## 3. Timer, counter, prescaler

입력 clock \(f_{in}\), 분주비 D라면

\[
f_{cnt}=f_{in}/D,\quad T_{tick}=D/f_{in}
\]
\[
T_{period}=(N+1)T_{tick},\quad f_{period}=1/T_{period}
\]

0부터 N까지 세므로 tick 수는 N+1이다. 일부 register는 D가 아니라 D−1을 기록한다. 실제 encoding은 MCU reference manual에서 확인한다.

**가상 예:** 80 MHz, D=8, count 0~999.
- \(f_{cnt}=10MHz\), \(T_{tick}=100ns\)
- \(T=1000\times100ns=100\mu s\)
- \(f=10kHz\)

count(무차원) × s/count = s로 단위가 맞다.

n-bit unsigned counter의 wrap 주기는

\[
T_{wrap}=2^n/f_{cnt}
\]

32-bit, 100 MHz라면 약 42.95 s다. 한 번의 wrap 미만 경과시간은 unsigned modular subtraction으로 구할 수 있다. 여러 번 wrap이 가능하면 overflow epoch를 관리한다.

~~~c
uint32_t elapsed = (uint32_t)(now - then);
~~~

Compare match는 interrupt/output toggle/DMA request 등을 만들 수 있다. counter 방향, shadow register, load event, synchronization에 따라 실제 반영 시점이 달라진다.

## 4. Capture, eCAP, QEP와 quadrature

Capture는 외부 edge에서 free-running counter 값을 저장한다.

\[
\Delta t=(c_2-c_1)T_{tick},\quad f_{edge}=1/\Delta t
\]

예: tick 50 ns, timestamp 차이 4000이면 \(\Delta t=200\mu s\), edge frequency 5 kHz다. 상승 에지만 측정했는지 양 에지인지 구분한다. capture FIFO/register overrun도 감시한다.

A/B는 이상적으로 90° 위상차를 가진다.

~~~text
정방향 예: 00 → 01 → 11 → 10 → 00
역방향 예: 00 → 10 → 11 → 01 → 00
A:         ___|‾‾‾‾‾|_____|‾‾
B:         _____|‾‾‾‾‾|_____
~~~

A/B 교환과 polarity에 따라 방향 명칭이 바뀐다. x1은 한 에지, x2는 한 채널 양 에지, x4는 두 채널 양 에지를 세는 방식이다.

\[
N_{count/rev}=PPR\times k,\quad k=1,2,4
\]
\[
\Delta\theta_m=360^\circ/N_{count/rev}
\]

2048 PPR, x4면 8192 count/rev, 기계각 0.043945°/count다. pole pairs p=4이면 전기각 간격은 0.175781°다. PPR이 이미 x4 count/rev를 뜻하는지 반드시 제조사 정의를 확인한다.

QEP는 A/B decoding, direction, position counter, index, unit timer, low-speed capture 기능을 제공할 수 있다. 실제 기능/입력 route는 MCU별로 다르다. GPIO ISR decoding은 높은 edge rate에서 CPU 부하와 누락 위험이 증가한다.

Digital filter는 glitch를 제거하지만 실제 edge도 늦춘다. minimum pulse width, max edge frequency, synchronizer clock, 안정 샘플 수, A/B 지연차, Schmitt input, 배선/차폐를 검토한다.

\[
\Delta\theta_e=\omega_e t_d=2\pi f_e t_d
\]

500 Hz electrical, 2 μs filter delay면 \(0.006283rad=0.36^\circ\) 전기각이다.

## 5. Interrupt priority, nesting, latency, jitter

~~~text
Peripheral event → interrupt controller/pending/mask/priority
 → exception entry/context save → vector → ISR
 → clear source/return → interrupted code resumes
~~~

진입 비용은 CPU architecture, compiler, FPU context, memory wait-state, nesting, RTOS에 따라 다르다. 우선순위 설계 원칙:
- 안전 차단은 CPU ISR보다 독립 hardware protection 우선 검토.
- 전류 제어 ISR은 ADC/PWM deadline에 맞춰 짧고 결정적으로.
- encoder 위치는 가능하면 QEP hardware 처리, ISR은 snapshot/diagnostic 중심.
- 통신·로깅은 제어 ISR과 분리.
- ISR에서 blocking I/O, dynamic allocation, 무제한 loop 금지.

Latency는 이벤트에서 지정 지점까지의 시간, jitter는 반복 latency/주기의 변동이다.

\[
t_{response}=t_{sync}+t_{pending}+t_{entry}+t_{higher}+t_{ISR}
\]

가상 예: PWM period 50 μs, ADC 완료부터 PWM shadow load까지 20 μs. entry 1.2 μs + 상위 ISR 0.8 μs + sensor snapshot 1 μs + FOC 8 μs + PWM write 0.7 μs + margin 3 μs = 14.7 μs. 남은 여유 5.3 μs다. 이 숫자는 AEL-002 측정치가 아니다.

Jitter는 각도 오차가 된다.

\[
\delta\theta_e\approx\omega_e\delta t=2\pi f_e\delta t
\]

500 Hz에서 2 μs jitter는 0.36° electrical다.

## 6. Critical section, atomic snapshot, race condition

Race condition은 ISR과 main/task가 공유 데이터를 동시에 접근해 실행 순서에 따라 결과가 달라지는 오류다. 32-bit 값이 타깃에서 atomic하지 않으면 읽는 도중 torn value가 생길 수 있다.

volatile은 compiler access 최적화를 제한할 뿐 atomicity, mutual exclusion, memory ordering을 보장하지 않는다. 짧은 interrupt-masked copy, mutex, atomic, sequence lock 중 타깃에서 검증 가능한 방식을 선택한다. critical section 길이는 interrupt latency와 WCET에 포함한다.

Sequence counter 개념: 단일 writer가 sequence를 홀수로 바꾸고 데이터를 갱신한 뒤 짝수로 게시한다. reader는 동일한 짝수 sequence를 앞뒤에서 관측한 경우에만 snapshot을 승인한다. 실제 구현은 C11 atomic 또는 compiler/CPU memory barrier, atomic width/alignment, sequence wrap, 단일 writer 조건을 확인한다. 아래는 개념 코드이며 barrier 함수는 타깃별로 구현해야 한다.

~~~c
typedef struct {
    volatile uint32_t seq;
    volatile int32_t position;
    volatile int32_t velocity;
    volatile uint32_t timestamp;
} sensor_snapshot_t;

void publish(sensor_snapshot_t *s, int32_t p, int32_t v, uint32_t t)
{
    s->seq++;                 /* odd: updating */
    TARGET_MEMORY_BARRIER();
    s->position = p;
    s->velocity = v;
    s->timestamp = t;
    TARGET_MEMORY_BARRIER();
    s->seq++;                 /* even: published */
}
~~~

TARGET_MEMORY_BARRIER는 표준 C 함수가 아니다. 실제 compiler intrinsic/atomic을 사용한다. reader는 sequence를 앞뒤에서 읽어 동일하고 짝수인지 검사한다.

## 7. DMA, double buffering, ownership

DMA는 CPU 대신 peripheral-memory 전송을 수행하지만 데이터 의미와 정합성을 자동 보장하지 않는다. source/destination, width, alignment, burst, trigger, complete/error interrupt, arbitration, circular mode, RAM accessibility, cache coherency를 확인한다.

~~~text
DMA fills A → A READY → CPU PROCESSING A
DMA fills B → B READY → CPU PROCESSING B
~~~

| 상태 | DMA | CPU |
|---|---|---|
| FILLING | write | read 금지 |
| READY | 완료 | read 가능 |
| PROCESSING | 다른 buffer 사용 | 현재 buffer read |
| FREE | 재할당 가능 | 사용 종료 |

sequence/generation, length, timestamp, completion flag, consumer ack를 둔다. CPU가 처리 중인 buffer를 DMA가 덮지 않도록 한다.

Cache가 있는 MCU는 DMA와 CPU cache가 자동 일관되지 않을 수 있다. DMA RX 전 invalidate/non-cacheable 영역, TX 전 clean/write-back, RX 완료 후 CPU read 전 invalidate/barrier가 필요할 수 있다. cache line alignment와 DMA 접근 가능 RAM을 확인한다. MCU별 공식 coherency 규칙이 우선한다.

## 8. PWM time-base와 ADC trigger

Up-count 구현에서 period tick이 TBPRD+1이면

\[
f_{PWM}=f_{TBCLK}/(TBPRD+1)
\]

Up-down의 흔한 관계는

\[
f_{PWM}=f_{TBCLK}/(2TBPRD)
\]

끝점/분주/고해상도 동작은 MCU마다 다르다. TBCLK=100 MHz, up-down, TBPRD=2500이면 20 kHz, 50 μs다(교육용).

Edge-aligned는 한쪽 에지를 주기 기준에 맞추고, center-aligned는 펄스 중심을 대칭 배치한다. Center-aligned가 유리할 수 있지만 모든 duty에서 quiet sampling window를 보장하지 않는다.

~~~text
TBCTR: 0 → CMPA → TBPRD → CMPA → 0
PWM : ____|‾‾‾‾‾‾‾|____________|‾‾
                   ↑ event/SOC
ADC :          [acquisition][conversion][result valid]
                    ↑ sample aperture
~~~

SOC(Start of Conversion)는 변환 시작 요청이다. trigger, 실제 aperture, acquisition, conversion, result valid, ISR entry는 서로 다른 시점이다.

ADC input의 source resistance \(R_s\), switch resistance \(R_{sw}\), sample capacitor \(C_s\)의 1차 근사:

\[
\tau=(R_s+R_{sw})C_s,\quad \epsilon=e^{-t/\tau}
\]

N-bit ADC에서 full-scale step 후 0.5 LSB 이내 settling 조건:

\[
e^{-t_{acq}/\tau}\le2^{-(N+1)}
\]
\[
t_{acq}\ge(N+1)\ln(2)\tau
\]

12-bit, 등가저항 1 kΩ, Cs=20 pF라면 τ=20 ns, \(t_{acq}\ge180.2ns\). ADC의 실제 input model, source impedance, mux switching, temperature와 datasheet minimum이 우선한다. conversion time은 acquisition과 별도다.

전류 sample window는 switching transient 이후, amplifier settling 이후, ADC acquisition이 끝나고 다음 PWM edge 전에 있어야 한다. deadtime, shunt topology, duty, blanking, reconstruction 조건을 반영한다. 관측할 수 없는 전류를 유효 측정값으로 취급하지 않는다.

## 9. Chapter 08 FOC + Chapter 09 sensor timestamp

sensor 값은 timestamp, sequence, validity와 함께 전달한다. ADC aperture 시각 \(t_i\)와 encoder/Hall/Resolver 관측 시각 \(t_s\)가 다르면 그 시각의 전기각을 예측한다.

\[
\theta_e(t_i)=wrap(\theta_e(t_s)+\omega_e\Delta t+\frac12\alpha_e\Delta t^2)
\]
일정 속도 근사:
\[
\theta_{e,pred}=wrap(\theta_{e,s}+\omega_e\Delta t),\quad\omega_e=p\omega_m
\]

rad/s × s = rad로 단위가 맞는다. Chapter 08의 amplitude-invariant Clarke/Park convention과 같은 방향·offset을 사용한다.

예: sensor timestamp에서 ADC aperture까지 12 μs, electrical frequency 300 Hz.
\[
\omega_e=2\pi(300)=1884.96rad/s
\]
\[
\Delta\theta_e=1884.96(12\mu s)=0.02262rad=1.296^\circ
\]

~~~text
quiet current sample → ADC aperture → conversion/result
 → QEP/encoder snapshot → angle prediction to aperture
 → Clarke → Park → PI/decoupling → inverse Park → SVPWM
 → compare shadow write → next safe load event → PWM output
~~~

CPU 계산 종료와 PWM 핀 반영은 같지 않다. shadow register가 실제 반영되는 load event를 확인한다.

\[
t_d=t_{sensor}+t_{sync}+t_{ADC}+t_{IRQ}+t_{compute}+t_{PWM-update}
\]

timestamp가 이미 센서/전송 지연을 보정했는지, ADC 기준이 SOC인지 aperture인지, PWM 기준이 shadow write인지 output edge인지 정의해 중복 계상을 막는다.

## 10. Scheduling, WCET, deadline miss, watchdog

주기 \(T_i\), 실행시간 \(C_i\)의 단순 utilization:

\[
U=\sum_i C_i/T_i
\]

FOC 8 μs/50 μs, speed task 20 μs/1 ms, diagnostic 50 μs/10 ms라면 \(U=0.16+0.02+0.005=18.5\%\). 무차원 비율이다. U<1은 deadline 만족 증명이 아니다.

고정 priority 모델의 response-time 분석 예:

\[
R_i=C_i+B_i+\sum_{j\in hp(i)}\lceil(R_i+J_j)/T_j\rceil C_j
\]

\(B_i\)는 blocking, \(hp(i)\)는 높은 priority 태스크, \(J_j\)는 release jitter다. 모델 가정이 실제 RTOS/interrupt/multicore 구조에 맞는지 확인한다.

WCET는 정적 분석과 worst-path 분석, cycle counter/GPIO trace 측정, worst input, nesting, DMA/bus contention, flash wait-state, compiler/build option과 memory placement를 포함해 평가한다. 실측 최댓값은 시험한 조건의 최댓값이지 자동으로 WCET 증명이 아니다. 평균이나 99 percentile로 hard deadline을 승인하지 않는다.

Deadline miss/overrun 시:
1. flag와 timestamp 기록
2. 해당 cycle 데이터 invalid 처리
3. 위험 분석에 정의된 PWM inhibit/limit/fault latch 정책 실행
4. 연속 miss, sensor age, current/speed, hardware inhibit 확인
5. 명시적 fault clear와 supervised re-arm 전 토크 자동 복귀 금지

모든 상황에서 duty=0이 안전하다고 단정하지 않는다. 모터 관성, 회생, gate-driver 상태와 hardware protection을 고려한다.

Watchdog을 main loop가 무조건 clear하면 FOC ISR이 멈춰도 fault를 놓칠 수 있다. 핵심 태스크 완료 sequence/deadline/health를 supervisor가 확인한 뒤 watchdog을 갱신한다. watchdog clock/window, reset state, boot 중 PWM inhibit를 실제 MCU 문서와 회로로 검증한다. Watchdog은 독립 gate disable/comparator를 대체하지 않는다.

~~~text
RESET(outputs disabled)
 → CLOCK_INIT → PERIPHERAL_INIT → SELF_TEST → CALIBRATION
 → READY(PWM inhibited) → explicit ARM → RUN
RUN fault: ADC overrun / DMA ownership / sensor timeout / deadline miss /
           watchdog / clock fault / hardware trip
 → FAULT_LATCHED → DIAGNOSE → explicit acknowledge → controlled re-arm
~~~

## 11. AEL-002 configuration TBD

| 항목 | 상태 | 필요한 근거 |
|---|---|---|
| MCU 주문 코드·revision | TBD | BOM/실물 마킹/datasheet |
| oscillator·PLL·CPU/peripheral clock | TBD | 회로도/TRM/SDK clock init |
| timer clock/prescaler/width | TBD | 정확한 MCU TRM/SDK |
| QEP A/B/Z pin mux/filter | TBD | pin mux table + schematic |
| eCAP channel/input crossbar | TBD | TRM + SDK + 회로 |
| ePWM output/trigger route | TBD | TRM + board schematic + SDK |
| ADC channel/SOC/acquisition | TBD | TRM + analog front-end + SDK |
| ADC aperture/conversion latency | TBD | ADC timing table |
| DMA channel/trigger/memory region | TBD | TRM + linker map + SDK |
| interrupt vector/priority/nesting | TBD | core manual + startup code |
| PWM mode/frequency, ADC sample phase | TBD | motor/current-sense requirements |
| ISR budget/WCET/jitter | TBD | compiler build + analysis + trace |
| watchdog clock/window/reset | TBD | MCU TRM + safety analysis |
| sensor-to-actuation latency | TBD | synchronized timestamp measurement |

이전 문서에서 F280039C가 후보로 언급되었더라도 정확한 board/SDK 조합 확인 전에는 peripheral route를 확정하지 않는다.

## 12. 완전히 푼 계산 예제

**A. 1 ms timer:** 48 MHz input, prescaler 48, count 0~999. \(f_{cnt}=1MHz\), tick=1 μs, 1000 tick=1 ms, frequency=1 kHz.

**B. Encoder speed:** x4 count/rev=8192, 1 ms에 +120 count. \(rev/s=(120/0.001)/8192=14.6484\), rpm=878.9. p=4이면 \(\omega_m=92.04rad/s\), \(\omega_e=368.16rad/s\).

**C. ADC acquisition:** 12-bit, Rtotal=1.5 kΩ, Cs=15 pF. τ=22.5 ns, \(t_{acq}\ge13\ln2\times22.5ns=202.9ns\). ADC 공식 spec이 우선.

**D. Angle delay:** p=5, 3000 rpm, delay 8 μs. \(\omega_m=314.159rad/s\), \(\omega_e=1570.80rad/s\), angle error=0.012566 rad=0.72°.

**E. CPU utilization:** FOC 6 μs/50 μs, speed 25 μs/1 ms, diagnostic 100 μs/10 ms. U=0.12+0.025+0.01=15.5%. response-time proof는 별도.

## 13. 연습문제와 전체 풀이

1. 120 MHz timer를 12로 분주하고 0~499를 세면?
2. 16-bit counter가 2 MHz이면 wrap 시간은?
3. 2500 PPR x4일 때 기계각/count는?
4. 25 ns tick, capture 차이 8000 count의 주기와 주파수는?
5. 10 kHz electrical, 1 μs jitter의 각도 오차는?
6. 14-bit ADC의 0.5 LSB acquisition 조건은 몇 τ인가?
7. FOC 7/40 μs, speed 18 μs/800 μs, diagnostic 60 μs/12 ms의 U는?
8. volatile만으로 race가 해결되지 않는 이유는?
9. DMA buffer ownership을 어떻게 관리하는가?
10. timestamp 차이 15 μs, \(\omega_e=1000rad/s\)일 때 angle 보정은?
11. ISR 평균 5 μs, 최악 실측 11 μs, deadline 10 μs면 통과인가?
12. main loop가 watchdog을 무조건 clear하면 왜 위험한가?

**풀이**
1. 120/12=10 MHz, tick=100 ns, 500 tick=50 μs, 20 kHz.
2. \(2^{16}/(2\times10^6)=32.768ms\).
3. 2500×4=10000 count/rev, 360/10000=0.036°/count.
4. 8000×25 ns=200 μs, 5 kHz.
5. \(2\pi(10000)(1\mu s)=0.062832rad=3.6^\circ\).
6. \((14+1)\ln2=10.397\tau\).
7. 7/40+18/800+60/12000=0.2025=20.25%.
8. volatile은 원자성·memory ordering·상호배제를 보장하지 않는다. torn read/lost update가 가능하다.
9. FILLING/READY/PROCESSING/FREE, sequence, length, timestamp, completion flag, consumer ack를 관리하고 처리 중 buffer를 DMA가 재사용하지 못하게 한다.
10. 1000×15 μs=0.015 rad=0.8594°. timestamp 기준과 회전 방향으로 부호를 정한다.
11. 실패. 최악 실측이 deadline을 넘었고 평균은 hard deadline 증거가 아니다.
12. FOC ISR이 멈춰도 main loop가 feed하면 제어 루프 고장을 놓친다. 핵심 태스크 health를 확인한 supervisor가 갱신해야 한다.

## 14. 검증 템플릿

### Timing requirement

| ID | 경로 | 기준 시각 | 최대 latency/age | 측정 | 결과 |
|---|---|---|---|---|---|
| TIM-01 | PWM event→ADC SOC | time-base event | TBD | timer trace | TBD |
| TIM-02 | SOC→ADC aperture | sample aperture | TBD | ADC spec/trace | TBD |
| TIM-03 | aperture→result valid | aperture | TBD | ADC flag/timer | TBD |
| TIM-04 | sensor edge→capture | physical edge | TBD | signal generator/LA | TBD |
| TIM-05 | capture→snapshot | capture timestamp | TBD | cycle counter | TBD |
| TIM-06 | ADC result→FOC start | result valid | TBD | GPIO/cycle counter | TBD |
| TIM-07 | FOC start→PWM shadow write | ISR entry | TBD | cycle counter | TBD |
| TIM-08 | shadow write→PWM output | load event | TBD | scope/LA | TBD |
| TIM-09 | sensor event→actuation | physical event | TBD | synchronized capture | TBD |

### Software fault injection

| ID | 입력/고장 | 기대 결과 | 판정 |
|---|---|---|---|
| RT-01 | timer wrap | modular elapsed 정상 | TBD |
| RT-02 | 불법 A/B transition | error diagnostic | TBD |
| RT-03 | input glitch/min pulse | filter 규격대로 판정 | TBD |
| RT-04 | capture overflow | overrun/invalid | TBD |
| RT-05 | ADC acquisition 부족 | 오차 검출 | TBD |
| RT-06 | DMA 처리 지연 | ownership violation 검출 | TBD |
| RT-07 | high-priority ISR 폭주 | latency/jitter 확인 | TBD |
| RT-08 | FOC 실행시간 증가 | deadline fault path | TBD |
| RT-09 | watchdog 태스크 정지 | supervisor feed 중단 | TBD |
| RT-10 | PWM load miss | stale update 검출 | TBD |
| RT-11 | stale sensor timestamp | angle prediction 무효화 | TBD |
| RT-12 | CPU reset 중 PWM/enable | external inhibit 유지 | TBD |

측정 기록에는 MCU/revision, board/schematic revision, SDK/compiler/build/linker map, clock tree, pin mux 근거, PWM/ADC timing, ISR priority/nesting, DMA route/buffer/cache, 시험조건, 계측기 bandwidth/sample rate/calibration, min/mean/max/jitter/overrun, raw trace, commit SHA와 재현 절차를 남긴다.

## 15. 용어와 참고 자료

- Capture/Compare: edge timestamp 저장/counter 비교 이벤트
- QEP: quadrature position/direction peripheral
- CDC: clock-domain crossing
- Latency/Jitter: 처리 지연/지연 변동
- Critical section/Race: 공유 상태 동시성 제어/순서 의존 오류
- DMA/Double buffer: 직접 메모리 전송/두 버퍼 교대 처리
- SOC/Acquisition: ADC 변환 요청/입력 취득 시간
- WCET/Overrun: 최악 실행시간/주기 deadline 초과

참고:
1. [TI AM263Px MCU+ SDK — Optimizing Real Time Control Applications](https://software-dl.ti.com/mcu-plus-sdk/esd/AM263PX/09_02_00_56/exports/docs/api_guide_am263px/OPTIMIZING_REAL_TIME_CONTROL_APPLICATIONS.html) — sensing/processing/PWM 경로와 ISR latency. ARM R5F cycle 수를 C2000/STM32에 일반화하지 않는다.
2. [TI TMS320F2803x data sheet](https://www.ti.com/lit/ds/sprs584q/sprs584q.pdf) — ePWM/eCAP/eQEP/ADC 장치별 기능 사례이며 AEL 타깃 근거가 아니다.
3. [TI C2000 ePWM Developer's Guide](https://www.ti.com/lit/an/sprad12a/sprad12a.pdf).
4. [TI C2000Ware MotorControl SDK](https://www.ti.com/tool/C2000WARE-MOTORCONTROL-SDK) — 정확한 SDK version/source/example 대조.
5. [Arm Cortex-M exception entry and return](https://developer.arm.com/documentation/dui0552/a/the-cortex-m3-processor/exception-model/exception-entry-and-return) — Cortex-M 개념 참고.
6. [Microchip dsPIC33 DSC documentation](https://www.microchip.com/en-us/products/microcontrollers-and-microprocessors/16-bit-mcus/dspic33-dsc) — QEI 구현 비교.

## 16. 완료 기준과 안전 경계

- [ ] clock tree, timer tick/period, wraparound 계산
- [ ] capture/compare, quadrature x1/x2/x4 설명
- [ ] input synchronizer/filter의 지연 영향 설명
- [ ] interrupt priority/nesting/latency/jitter 분석
- [ ] volatile과 atomicity/memory ordering 구분
- [ ] DMA ownership/double buffer/cache coherency 설명
- [ ] PWM time-base와 ADC SOC/aperture/acquisition/conversion 구분
- [ ] ADC aperture 시각에 맞춰 Chapter 09 rotor angle을 예측하고 Chapter 08 Park 변환에 연결
- [ ] utilization과 WCET/response-time 구분
- [ ] deadline miss/overrun/watchdog fault path 정의
- [ ] AEL-002 실제 설정 TBD 유지

**현재 판정:** 이 장은 원리·계산·펌웨어 구조·검증 계획이다. AEL-002 MCU/clock/pin mux/peripheral route/interrupt/DMA/PWM/ADC/WCET는 TBD다. 펌웨어 빌드, 정적 timing 분석, SIL/HIL, 계측, 실물 점검 또는 모터 시험을 수행했다고 주장하지 않는다.

**안전 상태: NO STACK / NO POWER.**
