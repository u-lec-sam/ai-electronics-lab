# 10장 — MCU 시간 기반 주변장치와 실시간 FOC 실행 구조

> **이번 장의 핵심 질문:** 센서와 전류를 언제 측정했는지 어떻게 정확히 알고, 그 데이터로 계산한 제어 명령을 정해진 PWM 경계까지 제시간에 반영할 수 있을까?

## 안전·범위 경계

- 이 장은 MCU 주변장치와 실시간 펌웨어의 이론·설계·검증 방법을 설명한다. 특정 보드의 레지스터 설정이나 핀 연결을 승인하지 않는다.
- AEL-002의 후보 평가 환경으로 TI C2000 F280039C 계열이 기존 조사에 등장하지만, 이번 장만으로 최종 MCU·보드·SDK·주변장치 구성을 확정하지 않는다.
- 실제 AEL-002 MCU 선택/설정, 오실레이터·PLL·분주기, 시스템/주변장치 클록, 핀 mux, QEP/eCAP/ePWM/ADC 라우팅, 인터럽트 우선순위, DMA 채널, PWM/ADC 주파수, 샘플 위치, ISR 예산, WCET와 watchdog 정책은 모두 **TBD**다.
- 실제 데이터시트·기술참조설명서(TRM)·정확한 SDK 버전·보드 리비전·핀아웃을 함께 확인하기 전에는 핀 번호, 레지스터 값, peripheral instance, 인터럽트 번호 또는 성능 수치를 추측하지 않는다.
- 실물 보드 검사, 코드 빌드/다운로드, 신호 측정, 센서 회전, 모터 구동, 시뮬레이션 실행은 이 장의 작성 범위에 포함되지 않는다.
- **NO STACK / NO POWER**를 유지한다.

## 학습 목표와 선수 지식

08장은 진폭 불변 Clarke/Park 변환, PMSM d/q 전류 모델, PI 전류 루프, SVPWM 및 PWM/ADC 동기화의 개념을 정리했다. 09장은 A/B/Z 엔코더, 절대 엔코더, Hall, Resolver의 위치 데이터와 timestamp, 보간, 센서 지연·진단을 정리했다. 10장은 이 둘을 MCU의 시간축·이벤트·메모리·스케줄링으로 연결한다.

학습을 마치면 다음을 할 수 있어야 한다.

1. 오실레이터, PLL, 분주기, 시스템 클록과 주변장치 클록의 관계를 블록 수준으로 설명한다.
2. 타이머 tick, prescaler, counter period, overflow, capture와 compare를 식으로 계산한다.
3. QEP의 A/B quadrature와 index를 카운트·기계각·속도로 변환하고 eCAP timestamp 측정과 구분한다.
4. 비동기 입력의 동기화, 메타안정성, 디지털 필터의 노이즈 제거와 지연 사이의 절충을 설명한다.
5. interrupt latency, jitter, 우선순위, 중첩, critical section과 atomic snapshot의 관계를 분석한다.
6. DMA와 double buffering에서 생산자·소비자·buffer ownership을 명확히 정의한다.
7. PWM time-base 이벤트에서 ADC SOC, acquisition, conversion, ISR, PWM shadow-load까지의 시간 예산을 계산한다.
8. 09장의 센서 timestamp로 ADC aperture 시점의 전기각을 보정하고 08장의 Park 변환에 전달한다.
9. WCET, deadline, overrun, watchdog을 구분하고 결정론적 fault response를 설계한다.
10. 실제 MCU 근거가 없는 구성값을 TBD로 유지하고 검증 증거를 정의한다.

---

## 1. MCU는 명령을 실행하는 장치이자 시간 이벤트 발생기다

### 1.1 CPU 속도만으로 실시간 성능을 판단할 수 없다

CPU clock은 명령을 실행하는 기준 박자다. 그러나 실제 제어 시스템에는 다음 시간이 모두 존재한다.

- 센서 입력이 MCU 핀에 도착하는 시간
- 입력 동기화와 디지털 필터가 신호를 통과시키는 시간
- 타이머가 edge를 capture하고 counter를 갱신하는 시간
- ADC가 입력을 취득하고 변환하는 시간
- DMA가 데이터를 메모리로 옮기는 시간
- interrupt가 CPU에 전달되고 ISR이 시작되는 시간
- FOC 계산이 끝나는 시간
- PWM compare shadow 값이 active 값으로 옮겨지는 시간
- gate driver와 전력 스위치가 실제로 반응하는 시간

CPU가 빠르더라도 ADC가 잘못된 시점에 샘플링하거나, interrupt가 오래 지연되거나, PWM update 경계를 놓치면 제어 지연이 커진다. 따라서 실시간 설계는 **주파수 하나가 아니라 이벤트 사이의 최악 시간**을 관리한다.

### 1.2 개념적인 클록 트리

    외부 크리스털/내부 오실레이터
              |
        입력 분주기
              |
             PLL
              |
        시스템 분주기
              |
          SYSCLK
        /    |     \
     CPU    DMA   버스/주변장치 분배
                    |
            +-------+--------+
            |       |        |
          Timer    ePWM     ADC clock
            |
          eCAP/eQEP 등

이 그림은 일반적인 개념도다. 실제 MCU에서는 PLL 입력 제한, VCO 범위, 분주기, clock domain, peripheral enable, low-power clock, 안전 클록 감시 구조가 제조사마다 다르다. 어떤 주변장치는 SYSCLK를 직접 받지 않고 별도 분주된 클록을 받는다.

클록 트리 검증은 다음 순서로 한다.

1. 정확한 MCU 주문 코드와 silicon revision을 고정한다.
2. 데이터시트의 허용 입력 클록·전압·온도 조건을 확인한다.
3. TRM에서 oscillator, PLL, divider, clock mux와 peripheral clock domain을 확인한다.
4. SDK의 clock initialization 코드와 compile-time 설정을 확인한다.
5. PLL lock, clock failure, clock source fallback, watchdog과 reset 동작을 검토한다.
6. 가능한 경우 독립된 기준 계측으로 실제 clock output 또는 timer 주기를 확인한다.

### 1.3 PLL 주파수 계산의 일반식

일반화한 PLL 모델에서

\[
f_{\mathrm{PLL}}=f_{\mathrm{ref}}\frac{N}{M}
\]

\[
f_{\mathrm{SYS}}=\frac{f_{\mathrm{PLL}}}{D}
=f_{\mathrm{ref}}\frac{N}{M D}
\]

- \(f_{\mathrm{ref}}\): PLL 기준 입력 주파수, Hz
- \(N\): 정수 또는 분수 배율 계수, 무차원
- \(M\): 입력 분주 계수, 무차원
- \(D\): 시스템 출력 분주 계수, 무차원

이는 계산 관계를 설명하는 일반식이다. 실제 칩은 추가 분주기, 배율 제한, VCO 범위, fractional PLL, 별도 CPU/peripheral divider를 가질 수 있다. 위 식을 특정 TI 또는 STM32 레지스터에 그대로 대입하지 않는다.

**가상 예제:** 기준 클록이 10 MHz이고 \(N=24\), \(M=1\), \(D=2\)라고 가정한다.

\[
f_{\mathrm{SYS}}=10\,\mathrm{MHz}\times\frac{24}{1\times2}
=120\,\mathrm{MHz}
\]

단위 검산: MHz × 무차원 = MHz. 이 결과는 계산 연습용이며 AEL-002 설정값이 아니다.

클록 허용오차가 ±50 ppm이면 120 MHz의 절대 오차 한계 예시는

\[
120\times10^6\times50\times10^{-6}=6000\,\mathrm{Hz}
\]

즉 ±6 kHz다. 실제 오차에는 오실레이터 초기 정확도, 온도 드리프트, 노화, PLL 특성, jitter와 계측 오차를 구분해서 넣어야 한다.

---

## 2. 타이머 counter와 prescaler

### 2.1 Timer tick

타이머 입력 클록이 \(f_{\mathrm{timer}}\), prescaler 분주비가 \(P\)라면

\[
f_{\mathrm{tick}}=\frac{f_{\mathrm{timer}}}{P}
\]

\[
T_{\mathrm{tick}}=\frac{1}{f_{\mathrm{tick}}}
=\frac{P}{f_{\mathrm{timer}}}
\]

여기서 \(P\)는 무차원 분주비이며, 실제 레지스터 인코딩은 \(P\) 또는 \(P-1\)일 수 있으므로 칩 문서를 확인한다.

**가상 예제:** 타이머 클록 100 MHz, 분주비 100이라면

\[
f_{\mathrm{tick}}=1\,\mathrm{MHz},\qquad
T_{\mathrm{tick}}=1\,\mu s
\]

10 μs를 재려면 10 tick이 필요하다. 단위 검산: 1 MHz = 10⁶ s⁻¹, 역수는 10⁻⁶ s다.

### 2.2 Up-count period

0부터 period register 값 \(R\)까지 세고, 양 끝점을 포함해 \(R+1\) tick마다 반복하는 일반적인 up-counter 모델은

\[
T_{\mathrm{period}}=(R+1)T_{\mathrm{tick}}
\]

\[
f_{\mathrm{event}}=\frac{f_{\mathrm{tick}}}{R+1}
\]

**가상 예제:** tick = 2 MHz, \(R=1999\).

\[
f_{\mathrm{event}}=\frac{2\times10^6}{2000}=1\,\mathrm{kHz}
\]

주의: 실제 주변장치의 period 이벤트, zero 이벤트, reload, inclusive/exclusive count 규칙은 장치마다 다르다. 식은 counter 동작을 정의한 뒤 적용해야 한다.

### 2.3 Up-down count

이상적인 대칭 up-down counter가 0에서 \(R\)까지 증가한 뒤 0으로 감소하는 경우의 기본 근사는

\[
T_{\mathrm{period}}\approx2R T_{\mathrm{tick}}
\]

\[
f_{\mathrm{event}}\approx\frac{f_{\mathrm{tick}}}{2R}
\]

endpoint 처리에 따라 정확히 \(2R\) 또는 인접 tick 보정이 달라질 수 있으므로 실제 장치의 time-base 설명과 예제를 따른다. PWM에서 center-aligned와 edge-aligned 주파수 식을 혼동하지 않는다.

### 2.4 Counter overflow와 wrap

N비트 unsigned counter는 \(0\)부터 \(2^N-1\)까지 증가한 뒤 0으로 돌아간다. 한 번의 wrap을 가정하면 unsigned 차분은

\[
\Delta C=(C_{\mathrm{new}}-C_{\mathrm{old}})\bmod 2^N
\]

이다. 여러 번 overflow가 발생할 수 있는 긴 간격에서는 overflow 횟수를 별도로 추적해야 한다. interrupt가 지연되어 overflow flag가 여러 번 누적되더라도 단일 flag만으로 모든 wrap을 복원할 수 없는 장치가 있다.

**가상 예제:** 16비트 timer에서 이전 값 65,530, 새 값 12라면

\[
\Delta C=(12-65530)\bmod65536=18
\]

tick이 0.5 μs이면 경과시간은 \(18\times0.5=9\,\mu s\)다.

---

## 3. Capture와 compare: 시간을 읽고 이벤트를 예약한다

### 3.1 Input capture

Input capture는 외부 입력의 지정 edge가 들어온 순간 timer counter 값을 하드웨어 레지스터에 복사하는 기능이다. CPU가 interrupt를 처리하는 시각을 edge 시각으로 착각하지 않게 해준다.

- capture 시각: 실제 edge와 가능한 한 가까운 하드웨어 timestamp
- ISR 진입 시각: CPU가 나중에 처리하기 시작한 시각
- 두 시각의 차이: interrupt latency이며 capture 값 자체와 구분한다.

두 edge 사이의 counter 차이가 \(\Delta C\), timer tick 주파수가 \(f_{\mathrm{tick}}\)이면

\[
\Delta t=\frac{\Delta C}{f_{\mathrm{tick}}}
\]

\[
f_{\mathrm{signal}}=\frac{1}{\Delta t}
=\frac{f_{\mathrm{tick}}}{\Delta C}
\]

**가상 예제:** timer tick 10 MHz, 두 상승 edge 사이 capture 차이가 25,000 count라면

\[
\Delta t=\frac{25000}{10^7}=2.5\,ms
\]

\[
f=\frac{1}{2.5\,ms}=400\,Hz
\]

단위 검산: count는 무차원, count/(count/s)=s다.

### 3.2 Output compare

Output compare는 counter가 미리 지정한 compare 값에 도달했을 때 출력 toggle/set/clear, interrupt, DMA request 또는 다른 주변장치 이벤트를 발생시키는 기능이다. CPU가 매번 시간을 재서 GPIO를 바꾸는 방식보다 event timing의 지터를 줄일 수 있다.

Compare 예약 시 확인할 항목:

- compare 값이 이미 지난 counter 위치인지
- wrap을 넘는 예약인지
- shadow register와 active register의 반영 시점
- compare flag clear와 재예약 순서
- event가 interrupt인지 DMA인지 output action인지
- 동일 counter에 여러 compare channel이 있을 때 우선순위/충돌

### 3.3 Capture와 compare를 센서별로 적용하기

- A/B 증분 엔코더: QEP 하드웨어 quadrature decoder가 우선 후보이며, 단순 GPIO interrupt로 모든 edge를 처리하면 CPU 부하와 edge 손실 위험이 커질 수 있다.
- Z index: QEP index/latch 기능 또는 별도 capture 입력을 검토한다. Z가 곧 모터 전기각 영점이라는 뜻은 아니다.
- Hall: 세 입력의 유효 전이 순서와 timestamp를 함께 보존한다. GPIO interrupt 또는 capture 경로는 정확한 MCU route로 확인한다.
- Resolver: SIN/COS 샘플링은 ADC와 복조 처리의 동기·위상·필터 지연을 함께 관리한다. 일반적인 디지털 capture 하나로 아날로그 Resolver 각도가 직접 측정되는 것은 아니다.
- 절대형 직렬 엔코더: 통신 프레임 수신 완료 시각과 실제 센서 측정 시각을 구분한다. 프로토콜이 제공하는 sample counter/timestamp가 있으면 우선 사용한다.

---

## 4. QEP와 quadrature decoding

### 4.1 A/B 두 신호의 위상 관계

증분형 엔코더의 A와 B는 보통 서로 약 90 전기 도 위상차가 있는 펄스열이다. 회전 방향에 따라 두 신호의 선행 관계가 바뀐다.

| 상태 | A | B |
|---|---:|---:|
| S0 | 0 | 0 |
| S1 | 1 | 0 |
| S2 | 1 | 1 |
| S3 | 0 | 1 |
| 다시 S0 | 0 | 0 |

한 방향에서는 S0→S1→S2→S3→S0, 반대 방향에서는 역순으로 진행한다. 위 표는 하나의 극성/방향 예시다. 실제 엔코더 출력 극성, A/B 배선, MCU 입력 극성에 따라 순서가 반대로 보일 수 있다.

정상적인 Gray-code 인접 전이에서는 한 번에 한 비트만 변한다. 두 비트가 동시에 바뀌어 보이면 신호 노이즈, 입력 필터 지연, 샘플 누락, 비동기 관측 또는 실제 배선 문제가 원인일 수 있다. 단일 관측만으로 기계 고장으로 단정하지 않는다.

### 4.2 x1/x2/x4 카운트

- x1: 한 채널의 한 edge 종류만 세는 방식
- x2: 한 채널의 양쪽 edge를 세는 방식
- x4: A와 B 두 채널의 상승·하강 edge를 모두 세는 방식

제조사의 PPR/line count 표기와 드라이버 라이브러리의 CPR/counts per revolution 정의가 서로 다를 수 있다. 09장의 원칙대로 원시 line cycles와 최종 decode counts를 별도로 기록한다.

한 회전당 최종 count가 \(N_c\)일 때 기계각은

\[
\theta_m=2\pi\frac{C}{N_c}
\]

한 count의 기계각 간격은

\[
\Delta\theta_m=\frac{2\pi}{N_c}
\]

극쌍수 \(p\)와 전기각 offset \(\theta_0\)를 적용하면

\[
\theta_e=\operatorname{wrap}_{2\pi}(p\theta_m+\theta_0)
\]

이다. 이 관계는 05·08·09장의 규약과 동일하다.

**가상 예제:** line cycles가 1회전당 2,500이고 x4 decoding이면 \(N_c=10,000\) count/rev다.

\[
\Delta\theta_m=\frac{360^\circ}{10000}=0.036^\circ/count
\]

극쌍수 \(p=5\)라면 이상적인 한 count의 전기각 간격은

\[
\Delta\theta_e=5\times0.036^\circ=0.18^\circ/count
\]

실제 각도 정확도는 count 간격과 같지 않다. encoder accuracy, 설치 편심, 축 비틀림, edge jitter, 입력 지연과 전기각 offset 오차를 별도로 더해야 한다.

### 4.3 QEP 주변장치의 역할

QEP 계열 하드웨어는 일반적으로 다음 기능을 제공할 수 있다.

- A/B 위상 판별 및 up/down position counter
- index/Z event 처리와 position latch
- unit timer를 이용한 일정 시간당 count 차분
- capture unit을 이용한 edge 간격 측정
- direction, position, overflow/underflow 상태 플래그

그러나 기능 이름과 지원 범위는 MCU별로 다르다. QEP clock source, input mux, qualification, polarity, index reset/latch 정책, maximum input frequency, capture prescaler, unit timer clock과 interrupt route를 TRM 및 정확한 SDK에서 확인해야 한다.

### 4.4 QEP 속도 계산의 두 방식

**M 방식 — 고정 시간 창에서 count 차분**

시간 창 \(\Delta t\) 동안 count 변화가 \(\Delta C\), 한 회전당 count가 \(N_c\)이면

\[
n_{\mathrm{rps}}=\frac{\Delta C}{N_c\Delta t}
\]

\[
n_{\mathrm{rpm}}=60\frac{\Delta C}{N_c\Delta t}
\]

**T 방식 — 고정 edge 수의 시간 측정**

동일 방향의 edge \(K\)개 사이에 timer count가 \(\Delta T\), timer tick이 \(f_t\)이면

\[
n_{\mathrm{rps}}=\frac{K f_t}{N_c\Delta T}
\]

두 방법은 상호 보완적이다. M 방식은 고속에서 여러 count를 한 창에 모으기 쉽지만 저속에서는 \(\Delta C=0\)이 되는 양자화 문제가 있다. T 방식은 저속에서 edge 간 시간을 더 잘 활용하지만 고속에서는 timer resolution과 capture 처리율이 중요하다. 혼합 방식은 전환 히스테리시스와 추정 연속성을 검증해야 한다.

**가상 M 예제:** \(N_c=10,000\), 20 ms 창에서 \(\Delta C=500\)이면

\[
n_{\mathrm{rps}}=\frac{500}{10000\times0.020}=2.5\,rps
\]

\[
n_{\mathrm{rpm}}=150\,rpm
\]

**가상 T 예제:** timer tick 1 MHz, \(K=4\), edge 간격 총 20,000 count, \(N_c=10,000\)이면

\[
n_{\mathrm{rps}}=\frac{4\times10^6}{10000\times20000}
=0.02\,rps
\]

여기서 4개 edge가 어떤 구간을 뜻하는지 정의해야 한다. 첫 edge와 네 번째 edge 사이에는 edge 간격이 3개일 수 있다. 따라서 구현에서는 K를 실제 측정 구간의 edge interval 개수로 정의하고, endpoint count를 혼동하지 않는다.

---

## 5. 입력 동기화와 디지털 필터

### 5.1 비동기 입력과 metastability

외부 엔코더·Hall 신호는 MCU 내부 clock과 동기화되어 있지 않을 수 있다. 입력 전이가 flip-flop의 setup/hold window 근처에 오면 metastability가 발생할 확률이 0이 되지 않는다.

일반적인 설계는 입력 synchronizer chain을 사용해 metastability가 다음 로직으로 전파될 확률을 매우 낮춘다. 그러나 동기화는 입력 edge를 몇 clock 늦게 관측하게 만들고, A/B 두 채널의 상대 지연이 달라지면 위상 관계에 영향을 줄 수 있다.

- MCU가 제공하는 전용 QEP 입력 동기화 경로가 있는지 확인한다.
- A/B 채널에 동일한 동기화·qualification 조건이 적용되는지 확인한다.
- input filter와 synchronizer의 최대 지연을 센서 최대 edge rate와 비교한다.
- 비동기 GPIO를 CPU가 임의 시점에 읽는 것만으로 glitch-free quadrature decoding을 보장하지 않는다.

### 5.2 Digital qualification/filter

디지털 필터는 짧은 glitch를 제거할 수 있지만, 너무 길면 실제 edge를 늦추거나 빠뜨린다. 예를 들어 N회 연속 동일 샘플이 확인되어야 입력을 바꾸는 필터라면, 샘플 주기가 \(T_q\)일 때 이상적인 지연 규모는 대략 N·\(T_q\)에 비례한다. 실제 지연은 샘플 위상과 구현 방식에 따라 달라진다.

**가상 예제:** qualification sample period가 0.5 μs이고 4개의 연속 동일 샘플을 요구한다면 필터 지연 규모는 약 2 μs다. 이 값은 단순 모델이며 MCU 실제 설정이나 최악 지연을 뜻하지 않는다.

필터 설계의 입력은 다음과 같다.

- 최소 정상 펄스 폭
- 최대 edge frequency와 가속 중 edge 간격
- A/B 위상차와 duty distortion
- 노이즈 pulse 폭·진폭·발생 빈도
- synchronizer 및 filter의 최대 지연
- 방향 판정과 position count에 미치는 비대칭 지연

필터를 길게 해서 노이즈를 모두 제거하려는 접근은 틀릴 수 있다. 실제 신호도 함께 제거하거나 위상차를 왜곡할 수 있기 때문이다.

---

## 6. Interrupt architecture, priority, latency와 jitter

### 6.1 Interrupt는 이벤트를 처리하는 예약 통로다

주변장치는 event를 발생시키고, interrupt controller는 pending 상태와 enable, priority, mask 규칙에 따라 CPU에 처리를 요청한다. CPU는 현재 명령 경계, critical section, higher-priority ISR, exception entry 규칙 등에 영향을 받는다.

일반적인 경로:

    peripheral event
         |
    peripheral flag
         |
    interrupt routing/controller
         |
    priority / mask / pending
         |
    CPU exception entry
         |
    ISR prologue
         |
    application handler
         |
    flag clear / acknowledge
         |
    ISR return

주변장치 interrupt flag, interrupt controller pending bit, CPU global mask는 서로 다른 상태일 수 있다. 어떤 flag를 어떤 순서로 clear/acknowledge해야 하는지는 MCU 문서와 SDK 예제로 확인한다.

### 6.2 Priority와 nesting

높은 priority interrupt가 낮은 priority ISR을 선점할 수 있는지, 동일 priority가 어떤 순서로 처리되는지, nesting enable이 언제 허용되는지 확인한다.

중첩을 허용하면 긴 ISR이 중요한 이벤트를 막는 시간을 줄일 수 있지만, 다음 문제가 생긴다.

- 공유 변수에 대한 재진입
- ISR stack 사용량 증가
- 우선순위 역전과 starvation
- 낮은 priority 처리의 무한 지연
- interrupt storm
- peripheral flag와 acknowledge 순서 오류

모든 ISR에서 nesting을 켜는 것이 빠른 설계는 아니다. 최소한의 hard real-time ISR을 짧게 유지하고, 긴 계산·통신·로그는 낮은 우선순위 task 또는 background loop로 이동한다.

### 6.3 Interrupt latency와 jitter

Latency는 이벤트 발생부터 해당 처리 단계가 시작되거나 완료될 때까지의 시간이다. 측정 기준을 먼저 정의한다.

- \(L_{\mathrm{entry}}\): peripheral event → ISR 첫 명령
- \(L_{\mathrm{read}}\): event → 입력/결과 데이터 읽기
- \(L_{\mathrm{done}}\): event → 처리 완료
- \(L_{\mathrm{apply}}\): event → PWM active output 반영

Jitter는 같은 조건에서 latency가 변하는 폭이다. 예를 들어 \(L_{\max}-L_{\min}\) 또는 표준편차로 표현할 수 있지만, hard real-time 설계에서는 평균·표준편차만으로 최악 지연을 대체하지 않는다.

개념적인 worst-case latency budget은

\[
L_{\max}=
L_{\mathrm{sync}}+
L_{\mathrm{mask}}+
L_{\mathrm{higher}}+
L_{\mathrm{entry}}+
L_{\mathrm{bus}}+
L_{\mathrm{software}}
\]

이다. 각 항목은 실제 MCU의 문서와 계측으로 산정해야 하며, 서로 겹치는 항목을 단순 합산하면 이중 계산이 될 수 있다.

**가상 예제:** 입력 synchronizer 0.1 μs, interrupt mask 0.8 μs, higher-priority blocking 0.4 μs, exception entry 0.2 μs라면 ISR 첫 명령까지의 예산 예시는 1.5 μs다. 이 수치는 가상이며 실제 C2000 또는 AEL-002 latency가 아니다.

### 6.4 ISR에서 해야 할 일과 하지 말아야 할 일

빠른 제어 ISR에 적합한 작업:

- ADC 결과·DMA buffer의 유효성 검사
- timestamp와 상태 snapshot 확보
- 전류 offset/scale 보정
- Clarke/Park와 전류 PI
- 전압 제한 및 inverse transform
- 다음 PWM shadow 값 기록
- fault 상태 검사 및 제한된 진단 카운터 갱신

일반적으로 ISR 밖으로 보내야 하는 작업:

- blocking 통신과 긴 timeout 대기
- 동적 메모리 할당
- 파일/콘솔 출력과 긴 문자열 formatting
- 긴 필터·최적화·파라미터 저장
- 비결정적인 lock 대기
- 무제한 loop와 대규모 로그

ISR 안의 함수 호출도 실행시간과 stack, library 구현을 포함해 분석해야 한다. 코드 줄 수가 짧다고 WCET가 짧다는 보장은 없다.

---

## 7. Critical section, atomic snapshot과 race condition

### 7.1 Race condition

한 변수를 ISR과 main loop가 동시에 읽고 쓴다고 하자.

- main loop가 position의 하위 16비트를 읽는다.
- ISR이 position 전체를 새 값으로 갱신한다.
- main loop가 상위 16비트를 읽는다.

결과는 실제로 존재하지 않았던 조합일 수 있다. 이를 torn read 또는 inconsistent snapshot이라 부른다.

C 언어에서 volatile은 최적화 제약을 위한 한정자이지, 여러 바이트의 원자성이나 thread/ISR 동기화를 자동 보장하지 않는다. MCU의 atomic instruction과 C compiler memory model을 별도로 확인해야 한다.

### 7.2 Critical section

공유 데이터 갱신 중 짧은 구간에서 관련 interrupt를 mask하거나, 지원되는 atomic primitive를 사용해 일관성을 지킨다. 단, critical section은 interrupt latency를 증가시킨다.

설계 규칙:

1. critical section은 필요한 최소 명령만 포함한다.
2. disable한 interrupt의 최대 차단 시간을 측정/상한화한다.
3. 중첩 가능한 interrupt와 global mask의 차이를 확인한다.
4. ISR 안에서 main loop가 풀어줄 lock을 기다리지 않는다.
5. 64-bit 값을 32-bit MCU에서 공유할 때 torn read 가능성을 검토한다.
6. DMA가 같은 buffer를 쓰는 동안 CPU가 읽지 않도록 ownership으로 관리한다.

### 7.3 Atomic snapshot 기법

**방법 A — 짧은 interrupt mask:** writer가 ISR인 경우 main loop가 snapshot을 복사하는 동안 해당 writer interrupt를 잠시 mask한다. copy가 짧고 mask가 허용되는 경우에만 사용한다.

**방법 B — sequence counter/seqlock 스타일:** writer가 sequence를 홀수로 바꾸고 data를 갱신한 뒤 짝수로 바꾼다. reader는 읽기 전후 sequence가 같고 짝수인지 확인한다.

    do {
        s1 = sequence;
        if (s1 is odd) retry;
        local = shared_data;
        s2 = sequence;
    } while (s1 != s2);

이는 단일 writer와 적절한 memory ordering을 가정한 개념 의사코드다. 컴파일러 재배치, volatile만으로 해결되는지, atomic sequence access, DMA writer 여부를 확인하지 않고 그대로 복사하지 않는다. reader 재시도는 무한 loop가 되지 않게 제한해야 한다.

**방법 C — double buffer와 ownership:** writer가 현재 reader가 사용 중이지 않은 buffer에 완성된 snapshot을 기록하고, 완료 시 index를 원자적으로 publish한다. buffer가 재사용되기 전에 reader가 사용을 끝냈는지 확인한다.

### 7.4 FOC에 필요한 coherent snapshot

08장 Park 변환에는 \(i_a,i_b,i_c\), ADC timestamp, rotor electrical angle, sensor quality, bus voltage와 fault state가 일관된 시간 기준으로 필요하다. 서로 다른 시각에 갱신된 값을 섞으면 실제로는 존재하지 않았던 상태를 계산할 수 있다.

따라서 제어 ISR이 소비하는 데이터 구조는 최소한 다음을 포함하도록 설계한다.

- 측정값
- 측정/취득 기준 timestamp
- sequence 또는 generation counter
- validity/status flags
- overflow/timeout/CRC/overrun 진단
- scale/calibration version 또는 configuration ID

---

## 8. DMA와 double buffering

### 8.1 DMA가 필요한 이유

DMA(Direct Memory Access)는 CPU가 매 sample마다 데이터를 복사하지 않고 주변장치와 메모리 사이 전송을 수행하도록 돕는다. ADC 결과, SPI encoder frame, serial receive buffer, timer capture log 등에 사용할 수 있다.

DMA가 CPU 부하를 줄여도 데이터 일관성·버스 경쟁·완료 시점·buffer 재사용 문제는 남는다. DMA transfer complete interrupt는 데이터가 완성되었다는 신호이지, 소비자가 이미 읽었다는 뜻이 아니다.

### 8.2 Double-buffer ownership

두 개의 buffer A/B를 사용한다고 하자.

1. DMA가 A에 쓰는 동안 CPU는 B를 읽는다.
2. DMA가 A 쓰기를 끝내면 완료 이벤트를 발생시킨다.
3. 소프트웨어는 A를 READY로 표시한다.
4. CPU가 A를 소비하는 동안 DMA는 B로 전환한다.
5. CPU가 A를 다 읽으면 FREE로 반환한다.
6. DMA가 다음에 A를 재사용하기 전에 A가 FREE인지 확인한다.

상태 예:

| 상태 | 소유자 | 의미 |
|---|---|---|
| FREE | DMA/dispatcher가 획득 가능 | 이전 소비 완료 |
| FILLING | DMA | 쓰기 진행 중, CPU 읽기 금지 |
| READY | dispatcher | DMA 쓰기 완료, CPU가 소비 가능 |
| READING | CPU | 소비 중, DMA 덮어쓰기 금지 |
| ERROR | 안전 처리 로직 | overrun 또는 ownership 위반 |

READY buffer가 CPU가 소비하기 전에 다시 채워져야 하는 상황이면 overrun이다. 오래된 데이터를 조용히 덮어쓰지 말고 sequence gap, missed frame, overrun count를 기록하고 제어 영향에 따라 fault 또는 degraded mode를 선택한다.

### 8.3 Cache와 memory coherency

cache가 있는 MCU에서는 DMA가 RAM에 쓴 값이 CPU cache에 남아 있거나, CPU가 cache에만 쓴 값이 DMA가 보는 RAM에 반영되지 않는 문제가 생길 수 있다. 해결책은 MCU/컴파일러/SDK가 정의한 cache clean/invalidate, non-cacheable memory, memory barrier 및 DMA alignment 규칙을 따르는 것이다.

cache가 없는 MCU라고 해서 ownership과 ordering 문제가 사라지는 것은 아니다. bus arbitration, peripheral FIFO, write buffer, compiler reordering을 확인한다.

### 8.4 DMA 검증 항목

- DMA source/destination 주소와 transfer width
- burst/transfer count와 alignment
- peripheral request trigger와 channel routing
- circular/one-shot mode와 wrap 동작
- half-transfer/full-transfer event 의미
- buffer ownership 및 재사용 시점
- DMA error, bus error, overrun 대응
- cache maintenance/memory barrier 필요 여부
- CPU와 DMA가 같은 메모리 영역에 접근할 때의 경쟁
- stop/restart와 fault 중 in-flight transfer 처리

---

## 9. PWM time-base와 ADC trigger

### 9.1 PWM counter가 제어 주기의 기준이 된다

PWM time-base는 주기적인 counter를 만들고 compare 값에 따라 출력 전이를 발생시킨다. edge-aligned PWM은 일반적으로 한 방향 count를 사용하고, center-aligned PWM은 up-down count로 대칭 파형을 만든다.

이상적인 edge-aligned 모델:

\[
f_{\mathrm{PWM}}=\frac{f_{\mathrm{TBCLK}}}{R+1}
\]

이상적인 center-aligned up-down 모델:

\[
f_{\mathrm{PWM}}\approx\frac{f_{\mathrm{TBCLK}}}{2R}
\]

여기서 \(f_{\mathrm{TBCLK}}\)는 time-base clock이며, SYSCLK와 같다고 가정하지 않는다. prescaler와 clock divider가 있을 수 있다. 정확한 count endpoint 및 shadow load 규칙은 target TRM에서 확인한다.

### 9.2 PWM 이벤트가 ADC SOC를 시작한다

08장에서 정리한 개념 흐름은 다음과 같다.

    ePWM time-base event
           |
         SOC A/B
           |
       ADC sample-and-hold
           |
       acquisition window
           |
       ADC conversion
           |
      result register/DMA
           |
       control ISR
           |
      PWM compare shadow
           |
     next defined load event
           |
      active PWM output

SOC(Start of Conversion)는 변환 요청 이벤트다. SOC event 시각과 실제 입력 sampling aperture가 같은 시각이라고 단정하지 않는다. ADC trigger synchronizer, arbitration, acquisition window, sample-and-hold 동작이 관여할 수 있다.

### 9.3 Acquisition time과 conversion time

ADC acquisition 동안 입력 신호는 sample capacitor에 충분히 settle되어야 한다. 입력 소스 임피던스, 외부 RC filter, ADC switch resistance, sample capacitor, 채널 전환 전압 차이, reference settling이 필요 시간을 결정한다.

단순 1차 settling 모델에서 full-scale step 후 잔류 오차를 0.5 LSB 이하로 낮추려면

\[
e^{-t_{\mathrm{acq}}/\tau}\le\frac{1}{2^{N+1}}
\]

따라서

\[
t_{\mathrm{acq}}\ge(N+1)\ln(2)\tau
\]

이다. 여기서 \(N\)은 ADC bit 수, \(\tau\)는 source/sample network의 유효 시정수다. 이 식은 단순 RC 근사다. 실제 ADC 입력 모델과 제조사 minimum acquisition requirement가 우선한다.

**가상 예제:** 12-bit ADC, 유효 \(\tau=20\,ns\)라면

\[
t_{\mathrm{acq}}\ge13\times0.693\times20\,ns
\approx180.2\,ns
\]

이 값은 이상적 settling 근사일 뿐 실제 ADC 설정을 결정하지 않는다.

ADC conversion time은 acquisition 이후 내부 변환이 완료되어 result가 유효해질 때까지의 시간이다. SAR, pipeline, oversampling 등 구조에 따라 다르며 channel 수, ADC clock, resolution, conversion mode, arbitration에 영향을 받는다.

**주의:** sample aperture와 conversion complete를 분리한다. FOC 전류값은 conversion complete 시점이 아니라 acquisition aperture 근처의 아날로그 입력을 대표한다. Park 각도 timestamp는 해당 aperture와 일치시켜야 한다.

### 9.4 Center-aligned PWM에서 샘플링 창

스위칭 edge 직후에는 전류 센서, 션트, 증폭기, 배선에 transient가 발생할 수 있다. ADC sample은 스위칭 과도와 충분히 떨어진 유효 창에 배치해야 한다.

    PWM carrier (center-aligned, 개념)
    counter: 0  ->  PERIOD  ->  0
    phase:   / rising  \ falling

    PWM:     ____|‾‾‾‾‾‾‾|____
                  ^       ^
               switching edges

    ADC:          [ acquisition ]
                       ^
                  aperture region

실제 3상 인버터에서는 세 상의 duty와 전류 방향, zero vector/active vector 구간, deadtime, 최소 on/off pulse, shunt topology가 유효 샘플 창을 바꾼다. center-aligned라고 언제나 period 중앙이 최적 샘플 지점인 것은 아니다.

특히 1-shunt current reconstruction은 특정 PWM vector dwell 구간에서만 전류 관측이 가능할 수 있다. 2-shunt/3-shunt도 amplifier settling과 switching transient를 검증해야 한다.

### 9.5 가상 PWM/ADC 시간 예산

가상의 \(f_{\mathrm{TBCLK}}=100\,MHz\), center-aligned period \(R=2500\)을 가정하면

\[
f_{\mathrm{PWM}}\approx\frac{100\times10^6}{2\times2500}
=20\,kHz
\]

\[
T_{\mathrm{PWM}}=50\,\mu s
\]

ADC acquisition 0.5 μs, conversion 0.8 μs, ISR WCET 4 μs, PWM shadow 반영 대기 최악 25 μs라고 가정하면 SOC부터 active PWM 반영까지의 최악 지연 예시는

\[
T_{\mathrm{path}}=0.5+0.8+4+25=30.3\,\mu s
\]

이다. 이 가정에서는 50 μs 주기 안에 반영될 수 있지만, 다음 deadline까지 여유가 19.7 μs라는 단순 계산만으로 보장되지는 않는다. 다른 interrupt, DMA arbitration, ADC queue, critical section, 실제 PWM load event, ISR entry/exit를 포함해야 한다.

---

## 10. 09장 센서 timestamp와 08장 Park angle을 하나의 시간축으로 연결하기

### 10.1 가장 중요한 규칙: 각도에는 시각이 붙어야 한다

09장의 sensor data contract는 position/angle, speed, timestamp, validity/status를 함께 다룬다. 08장의 Park 변환은 current sample과 같은 시각 기준의 electrical angle을 필요로 한다.

다음 세 시각을 분리한다.

- \(t_m\): 센서가 실제로 측정한 시각 또는 가장 가까운 하드웨어 timestamp
- \(t_s\): ADC current sample의 effective aperture 시각
- \(t_u\): 계산한 voltage command가 PWM active output에 반영되는 시각

센서 frame을 CPU가 읽은 시각 \(t_r\)은 센서 측정 시각 \(t_m\)과 같지 않을 수 있다. SPI/serial frame 전송 시간과 interrupt latency 때문에 \(t_r>t_m\)일 수 있다.

### 10.2 각도 예측식

센서에서 얻은 electrical angle \(\theta_e(t_m)\), electrical angular velocity \(\omega_e(t_m)\)가 있다면 일정 속도 가정에서 ADC aperture 시각의 각도는

\[
\hat\theta_e(t_s)=
\operatorname{wrap}_{2\pi}
\left[\theta_e(t_m)+\omega_e(t_m)(t_s-t_m)\right]
\]

가속도 추정 \(\alpha_e\)가 신뢰 가능하면

\[
\hat\theta_e(t_s)=
\operatorname{wrap}_{2\pi}
\left[\theta_e(t_m)+\omega_e\Delta t+
\frac12\alpha_e\Delta t^2\right]
\]

여기서 \(\Delta t=t_s-t_m\)다. 각도 wrap은 2π 범위 또는 프로젝트에서 선언한 범위로 일관되게 수행한다.

기계 속도 \(\omega_m\)에서 전기 속도는

\[
\omega_e=p\omega_m
\]

이다. rpm을 rad/s로 바꾸는 과정도 반드시 포함한다.

### 10.3 계산 예제 — ADC aperture 기준 각도 보정

가상의 센서 데이터:

- \(p=5\)
- 기계 속도 \(n_m=1200\,rpm\)
- 센서 측정 timestamp \(t_m\)
- ADC aperture가 센서 측정 40 μs 뒤에 발생
- \(t_m\)에서 측정된 기계각을 20°라고 가정

기계 각속도:

\[
\omega_m=1200\frac{2\pi}{60}
=40\pi\approx125.664\,rad/s
\]

전기 각속도:

\[
\omega_e=5\times125.664
=628.32\,rad/s
\]

전기각 변화:

\[
\Delta\theta_e=628.32\times40\times10^{-6}
=0.02513\,rad
\]

\[
0.02513\,rad\times\frac{180^\circ}{\pi}
\approx1.44^\circ
\]

기계각 20°는 전기각으로 \(5\times20=100^\circ\)다. 따라서 ADC aperture에서 사용할 예측 전기각은 offset이 이미 적용되었다는 가정 아래 약 \(101.44^\circ\)다. offset이 아직 적용되지 않았다면 \(\theta_0\)를 별도로 더해야 한다.

단위 검산: rad/s × s = rad. 이 예제의 rpm, pole pair, delay는 교육용 가정이며 AEL-002의 실제 값이 아니다.

### 10.4 Park 변환은 sample timestamp에 맞춘다

08장의 FOC current loop를 시간 순서로 다시 쓰면:

1. PWM event가 ADC SOC를 발생시킨다.
2. ADC acquisition aperture에서 실제 전류가 샘플된다.
3. ADC conversion이 끝나고 result가 유효해진다.
4. DMA 또는 ISR이 current result와 timestamp를 읽는다.
5. 센서 snapshot을 가져오고 \(t_m\)에서 \(t_s\)까지 angle을 예측한다.
6. 보정한 \(i_a,i_b,i_c\)를 Clarke 변환한다.
7. **ADC aperture 시각의 \(\hat\theta_e(t_s)\)** 로 Park 변환한다.
8. PI/decoupling/voltage limit/inverse Park/SVPWM을 수행한다.
9. PWM shadow register에 새 duty를 기록한다.
10. 정해진 PWM load event에서 active compare로 반영한다.

센서 angle을 ISR 실행 시각의 값으로 그대로 Park에 넣으면 sample 시각과 angle 시각이 어긋날 수 있다. 이 오차는 09장의 지연에 의한 전기각 오차와 같다.

### 10.5 PWM 반영 시각까지의 예측은 별도 문제다

Park transform은 측정 전류와 같은 시각의 각도를 써야 한다. 반면 voltage command가 실제로 적용되는 시각 \(t_u\)까지의 회전자 회전은 제어 plant의 계산 지연과 PWM update delay에 영향을 준다.

따라서 다음 두 보정을 혼동하지 않는다.

- 측정 좌표 정합: \(\theta_e(t_s)\)를 이용해 ADC 전류를 dq로 변환
- 출력 적용 예측/지연 보상: 제어 명령이 적용되는 \(t_u\)의 회전자 상태와 전압 벡터 지연을 모델링

모든 구현이 동일한 예측 전략을 쓰는 것은 아니다. 실제 지연 보상은 전류 루프 안정도·모터 모델·PWM update 정책으로 검증해야 한다.

### 10.6 Sensor freshness와 FOC validity

다음 조건을 만족하지 못하면 angle을 무기한 외삽하지 않는다.

- sensor status valid
- timestamp가 단조 증가하거나 wrap을 올바르게 처리
- sample age가 허용 범위 이내
- speed/acceleration 추정값이 유효 범위
- encoder count jump 또는 Hall illegal transition 진단 통과
- absolute encoder CRC/timeout 및 frame sequence 정상
- Resolver amplitude/phase/diagnostic 유효
- electrical angle wrap과 pole-pair conversion 정상
- ADC sample timestamp와 PWM cycle ID가 일치

고장 시에는 angle을 stale 상태로 표시하고, 제어 상태기계가 안전한 출력 상태로 전환하도록 한다. 실제 fault threshold와 timeout은 모두 TBD다.

---

## 11. Deterministic scheduling, WCET와 deadline

### 11.1 주기적 작업과 event-driven 작업

서보드라이브 펌웨어는 보통 다음 종류의 작업을 가진다.

| 작업 | 실행 트리거 | 상대적 중요도 |
|---|---|---|
| 하드웨어 fault 처리 | 비동기 fault event | 가장 높은 안전 우선 |
| current sampling/FOC | PWM/ADC 주기 이벤트 | hard real-time |
| sensor capture/position update | edge 또는 주기 timer | 높은 실시간성 |
| speed/position loop | 분주된 주기 tick | 주기적 제어 |
| 통신 수신/명령 검증 | 통신 event | 중간 |
| 진단·통계·로그 | background | 낮음 |
| 파라미터 저장/유지보수 | 상태 기반 task | 낮음, blocking 금지 |

실제 우선순위는 safety analysis와 deadline에 따라 정한다. 표의 상대 순서는 개념 예시다.

### 11.2 WCET

WCET(Worst-Case Execution Time)는 정의한 실행 경로와 환경에서 작업이 완료되는 최악 실행시간의 상한이다. 평균 실행시간이나 한 번 측정한 최대값과 같지 않다.

WCET에 영향을 주는 요소:

- 분기와 loop 횟수
- fixed/floating point 명령 및 라이브러리 경로
- memory wait state와 flash prefetch
- cache hit/miss가 있는 MCU
- DMA/bus arbitration
- interrupt nesting과 masking
- critical section
- compiler optimization과 LTO
- fault/diagnostic 경로
- input-dependent 알고리즘 반복 횟수

WCET 근거는 정적 분석, 명령/메모리 모델, 타깃 계측, worst-case 입력, 동시 DMA/interrupt 부하를 조합한다. 한 번의 GPIO toggle 측정은 평균 또는 관측값일 뿐, 그 자체로 WCET 증명이 아니다.

### 11.3 Deadline와 response time

주기 \(T\) 안에 작업이 끝나야 한다면 deadline \(D\le T\)를 정의한다. 단순 CPU utilization 근사:

\[
U=\sum_i\frac{C_i}{T_i}
\]

- \(C_i\): task i의 실행시간, s
- \(T_i\): task i의 period, s
- \(U\): 무차원 CPU utilization

단일 CPU에서 \(U<1\)이라고 모든 deadline이 보장되는 것은 아니다. priority, blocking, release jitter, non-preemptive section, interrupt overhead와 deadline이 중요하다.

고정 priority preemptive task의 단순 response-time recurrence 예:

\[
R_i=C_i+B_i+\sum_{j\in hp(i)}
\left\lceil\frac{R_i+J_j}{T_j}\right\rceil C_j
\]

여기서 \(B_i\)는 blocking, \(hp(i)\)는 더 높은 우선순위 작업, \(J_j\)는 release jitter다. 실제 시스템에서는 interrupt/task 모델, self-suspension, DMA, multicore와 제조사 실행 모델에 맞게 확장해야 한다.

### 11.4 가상 utilization 예제

세 작업을 가정한다.

| 작업 | WCET | 주기 |
|---|---:|---:|
| current FOC ISR | 5 μs | 50 μs |
| sensor update | 8 μs | 1 ms |
| communication task | 40 μs | 2 ms |

\[
U=\frac{5}{50}+\frac{8}{1000}+\frac{40}{2000}
=0.1+0.008+0.02=0.128
\]

CPU utilization 근사는 12.8%다. 그러나 이것만으로 50 μs current loop의 deadline이 보장되는 것은 아니다. sensor ISR가 FOC를 선점하는지, 통신 task가 critical section으로 차단하는지, DMA가 버스 지연을 만드는지 분석해야 한다.

### 11.5 Deadline miss와 overrun

- **Deadline miss:** 작업이 정해진 시각까지 완료되지 못함.
- **Overrun:** 다음 release가 오기 전에 이전 실행이 끝나지 않거나, buffer/ADC/PWM update가 다음 주기와 충돌함.
- **Late sample:** 제시간에 측정하지 못하거나 sample age가 허용 범위를 넘음.
- **Stale command:** 이전 제어 주기의 명령이 계속 적용됨.

Overrun을 발견하면 다음을 기록한다.

- cycle ID와 timestamp
- 실행 시작/종료 시간
- 예상/실제 WCET
- interrupt nesting 및 pending 상태
- ADC sequence/ DMA generation
- sensor sample age
- PWM shadow load deadline 통과 여부
- fault reason와 counter

제어 출력이 한 주기 늦어졌다고 무조건 이전 duty를 반복하는 것이 안전한 것은 아니다. 전류·속도·bus 상태와 시스템 안전 요구에 따라 제한된 hold, torque ramp-down 또는 hardware disable을 선택한다. 실제 정책은 safety analysis에서 정한다.

---

## 12. Watchdog와 overrun 대응

### 12.1 Watchdog의 목적

Watchdog은 소프트웨어가 정상적인 진행을 멈추거나 정해진 시간 내에 progress를 증명하지 못할 때 reset 또는 fault response를 유도한다. watchdog feed를 단순히 main loop에서 무조건 수행하면 일부 task가 멈춰도 watchdog이 계속 갱신될 수 있다.

더 나은 구조는 필수 task의 progress token/sequence를 확인하고, 모든 필수 task가 해당 cycle에서 성공했을 때만 watchdog service를 허용하는 것이다.

### 12.2 Window watchdog 개념

일부 MCU는 너무 빨리 또는 너무 늦게 watchdog을 갱신해도 fault를 발생시키는 window mode를 제공한다. 이 기능은 runaway loop와 stuck execution을 탐지하는 데 도움을 줄 수 있지만, clock failure, reset cause, watchdog independence, startup grace period를 포함해 검토해야 한다.

### 12.3 Overrun 상태 흐름

    BOOT_SAFE
       |
    CLOCK_SELF_CHECK
       |
    PERIPHERAL_SELF_CHECK
       |
    SENSOR_VALIDATE
       |
    READY_DISABLED
       |
    CONTROL_ACTIVE
       |
       +---- 정상 deadline 완료 ----> 다음 cycle
       |
       +---- deadline warning ------> 제한된 degraded policy
       |
       +---- 반복 overrun ----------> CONTROLLED_STOP 또는 FAULT
       |
       +---- hardware fault --------> HARDWARE_DISABLE
       |
    FAULT_LATCHED
       |
    원인 기록 / 출력 안전 확인
       |
    명시적 승인·조건 확인
       |
    READY_DISABLED

하드웨어 fault가 발생하면 CPU가 ISR을 실행할 때까지 기다려 PWM을 끄는 구조만으로는 부족할 수 있다. 독립적인 comparator/trip/gate-disable 경로가 먼저 출력을 안전하게 만들고, CPU는 이후 원인 기록과 supervised re-arm을 담당하도록 계층을 나눈다. 실제 보호 경로는 별도 하드웨어 근거와 시험이 필요하다.

### 12.4 Watchdog service 조건 예시

- current control cycle ID 증가 확인
- ADC conversion/DMA buffer 정상 완료 확인
- sensor data freshness 확인
- scheduler heartbeat 정상 확인
- no unhandled interrupt storm
- no repeated deadline miss
- safety state가 watchdog feed를 허용하는 상태인지 확인

Watchdog timeout은 CPU clock, low-power mode, peripheral clock domain, oscillator failover와 독립성 조건에 따라 달라질 수 있다. actual timeout은 TBD다.

---

## 13. 통합 펌웨어 데이터 흐름

### 13.1 데이터 경로

    A/B/Z encoder ──> QEP counter/capture ──┐
    Hall inputs ────> sync/filter/capture ─┤
    Absolute encoder ─> SPI/serial + DMA ──┤
    Resolver SIN/COS ─> ADC + demodulation ┤
                                           v
                                  sensor snapshot
                               {angle, speed, t_m,
                                quality, sequence}
                                           |
    PWM time-base ──> ADC SOC ──> ADC aperture t_s
                                           |
                                      ADC result
                                           |
                                  coherent snapshot
                                           |
                          angle prediction to t_s
                                           |
                          Clarke/Park at t_s
                                           |
                           PI / limit / inverse Park
                                           |
                                      SVPWM
                                           |
                                 PWM shadow update
                                           |
                               active load event t_u

### 13.2 의사코드 — event-driven 구조

    on_pwm_adc_event_or_completion():
        cycle = get_current_cycle_id()
        adc = read_completed_adc_snapshot()

        if !adc.valid or adc.cycle_id != cycle:
            request_safe_control_state(ADC_DATA_INVALID)
            return

        sensor = read_coherent_sensor_snapshot()

        if !sensor.valid or !timestamp_is_fresh(sensor.timestamp):
            request_safe_control_state(SENSOR_STALE)
            return

        t_sample = adc.aperture_timestamp
        theta_sample = predict_electrical_angle(sensor, t_sample)

        if !angle_prediction_valid(theta_sample):
            request_safe_control_state(ANGLE_INVALID)
            return

        i_abc = calibrate_current(adc)
        i_alpha_beta = clarke(i_abc)
        i_dq = park(i_alpha_beta, theta_sample)

        if !control_state_allows_output():
            write_safe_pwm_shadow()
            return

        v_dq = current_controller(i_dq)
        v_limited = apply_voltage_vector_limit(v_dq)
        v_alpha_beta = inverse_park(v_limited, theta_sample)
        duty = svpwm(v_alpha_beta, adc.bus_voltage)

        if !duty_and_deadline_valid(duty, cycle):
            request_safe_control_state(CONTROL_OVERRUN)
            return

        write_pwm_shadow_atomically(duty, cycle)

    on_sensor_dma_complete(buffer_id):
        if !buffer_ownership_is_dma_complete(buffer_id):
            latch_diagnostic(DMA_OWNERSHIP_ERROR)
            return

        validate_frame_crc_sequence_timestamp(buffer_id)
        publish_sensor_snapshot_atomically(buffer_id)
        return_buffer_when_consumed(buffer_id)

    on_hardware_fault():
        // Hardware trip path must already force the defined safe output.
        latch_fault_reason()
        inhibit_rearm_until_supervised_clear()

이 의사코드는 데이터 계약과 흐름을 설명한다. 특정 MCU의 ISR 이름·레지스터·DMA API를 정의하지 않으며 빌드 가능한 펌웨어가 아니다. 실제 구현에는 memory ordering, ISR nesting, hardware trip latency, PWM shadow load semantics, fault priority와 WCET 검증이 필요하다.

---

## 14. AEL-002 설정·요구사항 TBD 표

| 항목 | 현재 상태 | 확정에 필요한 근거 |
|---|---|---|
| 최종 MCU/주문 코드/silicon revision | **TBD** | 승인된 아키텍처와 정확한 부품 문서 |
| 실제 보드 및 리비전 | **TBD** | 보드 실물 식별과 공식 회로도/PCB |
| oscillator source/frequency | **TBD** | 정확한 보드 회로도·부품 BOM·데이터시트 |
| PLL/clock divider/SYSCLK | **TBD** | MCU TRM, SDK clock init, 허용 범위 |
| timer/peripheral clock tree | **TBD** | TRM clock domain 표와 SDK |
| QEP instance 및 A/B/Z pin mux | **TBD** | exact package pin table, board schematic, SDK pinmux |
| eCAP instance/input route | **TBD** | TRM input XBAR/pin mux 및 보드 회로 |
| Hall GPIO/capture/filter route | **TBD** | 센서·모터 문서, pin mux, timing |
| ePWM instance/time-base route | **TBD** | board pinout, gate-driver interface, TRM |
| ADC instance/channel/trigger route | **TBD** | 회로도·pin mux·ADC input model·SDK |
| ADC acquisition/conversion timing | **TBD** | ADC datasheet/TRM, source impedance, amplifier settling |
| PWM frequency/alignment/deadtime | **TBD** | power-stage, gate driver, motor ripple/thermal/EMI analysis |
| ADC SOC 위치와 유효 sampling window | **TBD** | current-sense topology, PWM timing analysis, measurement |
| interrupt priority/nesting | **TBD** | safety timing analysis와 MCU interrupt controller |
| DMA channel/request/buffer route | **TBD** | TRM DMA request table, SDK, memory map |
| cache/coherency 정책 | **TBD** | CPU/cache architecture와 compiler/SDK |
| 센서 timestamp source/resolution | **TBD** | QEP/eCAP/timer clock, sensor protocol |
| FOC ISR WCET/deadline | **TBD** | target compiler/build, measurement and worst-case analysis |
| sensor task WCET/latency | **TBD** | actual protocol, DMA and ISR timing |
| watchdog source/window/timeout | **TBD** | clock tree, TRM, fault safety requirements |
| overrun response/re-arm policy | **TBD** | system hazard analysis and verification |

### 후보 TI C2000 자료를 읽을 때의 주의

기존 AEL-002 연구에서 F280039C가 후보로 언급되었다고 해서, 이번 장의 일반식이 해당 LaunchPad·BOOSTXL 보드에 이미 구성되었다는 뜻은 아니다. 정확한 package pin, board routing, jumper, SDK version, peripheral instance와 interrupt route를 함께 검증해야 한다.

TI F28003x DriverLib 문서에는 SYSCTL clock configuration, ePWM time-base/event trigger, ADC SOC와 acquisition window, DMA/QEP/eCAP 관련 API가 설명되어 있다. 하지만 API 문서는 실제 보드 핀 연결, 샘플 점퍼 상태, 프로젝트의 SDK 버전 또는 안전한 구동 구성을 증명하지 않는다. 특히 API guide의 최신 웹 문서와 로컬 설치 SDK 버전이 다를 수 있으므로 버전을 고정해야 한다.

---

## 15. 가상 통합 타이밍 예제

다음 값은 계산 연습용이며 실제 AEL-002 설정이 아니다.

- PWM 주파수: 20 kHz → 주기 50 μs
- ADC acquisition: 0.5 μs
- ADC conversion: 0.8 μs
- DMA publish/ISR entry overhead: 0.7 μs
- FOC 계산 WCET 가정: 5.0 μs
- PWM shadow write: 0.5 μs
- 다음 active load까지 대기 최악: 20 μs
- sensor timestamp age at ADC aperture: 30 μs
- 전기 각속도: 500 rad/s

ADC aperture에서 sensor age가 30 μs라면 일정 속도 가정의 angle correction은

\[
\Delta\theta_e=500\times30\times10^{-6}
=0.015\,rad\approx0.859^\circ
\]

SOC부터 PWM active update까지의 가상 경로는

\[
0.5+0.8+0.7+5.0+0.5+20=27.5\,\mu s
\]

다. 50 μs 주기보다 짧지만, ADC SOC phase, sample window, conversion scheduling, interrupt interference, PWM load point와 fault handling이 추가되므로 이 단순 합만으로 deadline을 승인할 수 없다.

이 예제가 보여주는 핵심은 두 가지다.

1. 센서 timestamp age는 Park angle 보정에 들어간다.
2. 계산이 끝난 시각과 PWM output이 실제 반영되는 시각은 다르다.

---

## 16. 검증 템플릿

### 16.1 Clock tree 검증 기록

| 필드 | 기록 |
|---|---|
| MCU part number / silicon revision | TBD |
| Board revision / schematic revision | TBD |
| oscillator source / rated frequency | TBD |
| PLL source / multiplier / divider | TBD |
| SYSCLK / CPU clock / peripheral clock | TBD |
| clock tolerance / temperature range | TBD |
| SDK version / compiler version | TBD |
| clock init source file / commit | TBD |
| PLL lock / clock fail behavior | TBD |
| measured timer period / instrument | TBD |
| expected vs measured error | TBD |
| reviewer / date / evidence link | TBD |

### 16.2 Timer/QEP/eCAP 검증 기록

| 항목 | 시험 방법 | 합격 기준 |
|---|---|---|
| timer tick | 독립 기준과 counter period 비교 | 오차가 승인된 clock tolerance 이내 |
| overflow | wrap 전후 synthetic count 시험 | wrap 횟수와 delta가 정확 |
| capture | 기준 pulse generator와 edge timestamp 비교 | 오차/지터가 정한 한계 이내 |
| QEP direction | 양방향 low-speed count test | 방향 부호와 count sequence 일치 |
| QEP x4 | 알려진 회전 수와 count 비교 | PPR/CPR 정의와 count/rev 일치 |
| index/Z | index event와 latch 기록 | index와 electrical zero를 혼동하지 않음 |
| digital filter | glitch 폭 sweep | glitch reject와 정상 pulse 통과 조건 모두 충족 |
| max edge rate | 입력 주파수 sweep | missed edge/overflow 없음 |
| Hall transition | 유효/무효 상태 sequence 주입 | invalid transition 검출·safe response |
| timestamp wrap | counter rollover injection | age/ordering 계산 정확 |

### 16.3 Interrupt/WCET 검증 기록

| 항목 | 기록 |
|---|---|
| interrupt source / priority | TBD |
| preemption/nesting policy | TBD |
| maximum critical-section duration | TBD |
| event-to-ISR-entry min/max | TBD |
| event-to-ISR-complete min/max | TBD |
| FOC ISR WCET method | TBD |
| compiler optimization/build ID | TBD |
| DMA/bus contention load | TBD |
| worst-case higher-priority load | TBD |
| deadline / measured margin | TBD |
| overrun counter and fault action | TBD |
| evidence / reviewer | TBD |

### 16.4 ADC/PWM timing 검증 기록

| 항목 | 기록 |
|---|---|
| PWM instance / clock / alignment | TBD |
| PWM frequency / deadtime | TBD |
| SOC source and counter event | TBD |
| ADC channel / resolution / clock | TBD |
| acquisition window | TBD |
| conversion time / arbitration | TBD |
| effective aperture timestamp definition | TBD |
| current amplifier settling | TBD |
| valid sample window across PWM sectors | TBD |
| ADC result/DMA completion time | TBD |
| shadow-load event / active update time | TBD |
| SOC-to-active-output worst latency | TBD |
| measured sample noise / repeatability | TBD |

### 16.5 DMA ownership 검증 기록

- [ ] DMA가 FILLING buffer에만 쓴다.
- [ ] CPU는 READY/READING 상태 buffer만 읽는다.
- [ ] CPU가 읽는 buffer를 DMA가 덮어쓰지 않는다.
- [ ] buffer generation/sequence가 증가한다.
- [ ] half/full transfer event의 의미가 확인되었다.
- [ ] DMA overrun, bus error, timeout을 주입해 처리했다.
- [ ] cache clean/invalidate 및 memory barrier 필요성을 확인했다.
- [ ] fault/reset 도중 in-flight DMA를 안전하게 정리한다.

### 16.6 FOC sensor-time alignment 검증 기록

- [ ] ADC aperture 시각의 정의가 문서화되었다.
- [ ] encoder/QEP/Hall/Resolver/absolute frame의 timestamp 의미가 구분되었다.
- [ ] sensor timestamp와 ADC timestamp가 동일 clock domain인지 확인했다.
- [ ] 서로 다른 clock domain이면 offset/drift 동기화 방법이 정의되었다.
- [ ] \(t_m\rightarrow t_s\) angle prediction의 부호와 wrap을 검증했다.
- [ ] pole pair와 \(\theta_0\)가 올바르게 적용되었다.
- [ ] stale sensor, CRC error, timeout, timestamp reversal에서 출력 안전 동작을 확인했다.
- [ ] PWM active update 시각 \(t_u\)와 ADC aperture \(t_s\)를 혼동하지 않았다.

### 16.7 Fault/overrun 검증 기록


### 추가 timing requirement matrix

| ID | 경로 | 기준 시각 | 측정/검증 방법 | 결과 |
|---|---|---|---|---|
| TIM-01 | PWM event → ADC SOC | time-base event | timer trace / SOC flag | TBD |
| TIM-02 | SOC → ADC aperture | 실제 sample aperture | ADC TRM + 계측 | TBD |
| TIM-03 | aperture → result valid | aperture | ADC flag + timer | TBD |
| TIM-04 | sensor edge → capture | physical edge | pulse generator / logic analyzer | TBD |
| TIM-05 | capture → coherent snapshot | capture timestamp | cycle counter / sequence | TBD |
| TIM-06 | ADC result → FOC start | result valid | cycle counter | TBD |
| TIM-07 | FOC start → PWM shadow write | ISR entry | cycle counter | TBD |
| TIM-08 | shadow write → active PWM | load event | scope / logic analyzer | TBD |
| TIM-09 | sensor event → actuation | sensor timestamp | synchronized capture | TBD |

### 추가 software fault-injection matrix

| ID | 주입 조건 | 기대 결과 |
|---|---|---|
| RT-01 | timer wrap | modular elapsed time 정상 |
| RT-02 | 불법 A/B transition | diagnostic 증가, 각도 유효성 재평가 |
| RT-03 | 입력 glitch / 최소 pulse | filter 요구조건대로 reject/pass |
| RT-04 | capture overflow | sample invalid 또는 overrun fault |
| RT-05 | ADC acquisition 부족 | sample quality fail 또는 진단 검출 |
| RT-06 | DMA 소비 지연 | ownership violation/overrun 검출 |
| RT-07 | high-priority interrupt 폭주 | latency/jitter 상한 확인, deadline 보호 |
| RT-08 | FOC 실행시간 증가 | deadline miss 검출 및 정의된 안전 전이 |
| RT-09 | 필수 task 정지 | supervisor가 watchdog feed 중단 |
| RT-10 | PWM load miss | stale update 검출 |
| RT-11 | sensor timestamp stale/reversal | angle prediction invalid |
| RT-12 | CPU reset 중 PWM/enable | 독립 inhibit가 안전 상태 유지 |

각 시험 기록에는 MCU/revision, board/schematic revision, SDK/compiler/build/linker map, clock tree, pin mux 근거, PWM/ADC timing, interrupt priority/nesting, DMA route/buffer/cache, 시험 조건, 계측기 bandwidth/sample rate/calibration, min/mean/max/jitter/overrun, raw trace, commit SHA와 재현 절차를 남긴다.

- [ ] 높은 우선순위 interrupt storm을 주입했다.
- [ ] 긴 critical section 또는 의도적 CPU load를 주입했다.
- [ ] DMA buffer 소비 지연과 overrun을 주입했다.
- [ ] ADC conversion 지연/누락을 주입했다.
- [ ] 센서 timestamp stale/wrap/reversal을 주입했다.
- [ ] FOC deadline miss를 주입했다.
- [ ] watchdog feed 조건이 필수 task progress를 확인한다.
- [ ] hardware trip은 CPU ISR과 독립적으로 안전 출력을 만든다.
- [ ] fault reason, cycle ID, timestamp가 보존된다.
- [ ] 재무장은 원인 제거와 명시적 승인 절차를 요구한다.

---

## 17. 연습문제

모든 숫자는 교육용 가정이다. 실제 AEL-002 정격이나 MCU 설정으로 사용하지 않는다.

### 문제 1 — PLL 계산

기준 클록 8 MHz, \(N=30\), \(M=1\), \(D=2\)인 일반 PLL 모델의 SYSCLK를 구하라.

### 문제 2 — Timer tick과 주기

Timer clock 80 MHz, prescaler 80, up-counter period register \(R=999\)일 때 tick 주파수, tick 시간, event 주파수를 구하라.

### 문제 3 — Capture 주기 측정

Timer tick 5 MHz, 두 동일 edge 사이 count 차이가 12,500이다. 입력 주파수를 구하라.

### 문제 4 — Counter wrap

16-bit timer에서 이전 capture 65,520, 새 capture 24다. wrap이 한 번만 있었다고 가정할 때 count delta와 tick 2 MHz에서 시간 간격을 구하라.

### 문제 5 — QEP x4와 각도 분해능

엔코더가 1회전당 1,024 line cycles를 제공한다. x4 decoding count/rev와 기계각/count를 구하라. 극쌍수 4일 때 전기각/count도 구하라.

### 문제 6 — QEP M 방식 속도

count/rev = 8,192, 10 ms 동안 count 증가량 256이다. rpm을 계산하라.

### 문제 7 — Input filter 지연

qualification sample period 0.25 μs, 6개의 동일 샘플을 요구하는 단순 필터를 가정한다. 필터 지연 규모를 구하고, 필터가 너무 길 때 생길 수 있는 문제 두 가지를 설명하라.

### 문제 8 — Interrupt latency budget

가상 latency 요소가 mask 0.6 μs, higher-priority blocking 0.9 μs, exception entry 0.2 μs, peripheral/bus delay 0.3 μs다. ISR 첫 명령까지의 budget을 구하라.

### 문제 9 — Atomic snapshot

32-bit MCU에서 64-bit timer timestamp를 main loop가 읽고 ISR이 갱신한다. torn read가 발생할 수 있는 이유와 두 가지 해결법을 설명하라.

### 문제 10 — ADC settling

12-bit ADC의 단순 RC settling model에서 \(\tau=15\,ns\)다. 0.5 LSB 기준 acquisition time의 근사 하한을 계산하라.

### 문제 11 — Sensor timestamp angle correction

극쌍수 6, 기계 속도 900 rpm, sensor measurement에서 ADC aperture까지 50 μs다. 일정 속도 가정에서 전기각 변화량을 rad와 degree로 구하라.

### 문제 12 — WCET와 utilization

작업 A: WCET 4 μs, period 40 μs. 작업 B: WCET 10 μs, period 1 ms. 작업 C: WCET 30 μs, period 2 ms. 단순 CPU utilization을 구하고, 이것만으로 deadline 보장을 말할 수 없는 이유 세 가지를 적어라.

---

## 18. 연습문제 전체 풀이

### 풀이 1

\[
f_{\mathrm{SYS}}=8\,MHz\times\frac{30}{1\times2}
=120\,MHz
\]

### 풀이 2

\[
f_{\mathrm{tick}}=\frac{80\,MHz}{80}=1\,MHz
\]

\[
T_{\mathrm{tick}}=1\,\mu s
\]

\[
f_{\mathrm{event}}=\frac{1\,MHz}{999+1}=1\,kHz
\]

### 풀이 3

\[
\Delta t=\frac{12500}{5\times10^6}=2.5\,ms
\]

\[
f=\frac1{2.5\,ms}=400\,Hz
\]

### 풀이 4

\[
\Delta C=(24-65520)\bmod65536=40
\]

\[
\Delta t=\frac{40}{2\times10^6}=20\,\mu s
\]

### 풀이 5

\[
N_c=1024\times4=4096\,count/rev
\]

\[
\Delta\theta_m=\frac{360^\circ}{4096}
\approx0.08789^\circ/count
\]

\[
\Delta\theta_e=4\times0.08789^\circ
\approx0.35156^\circ/count
\]

### 풀이 6

\[
n_{\mathrm{rps}}=\frac{256}{8192\times0.010}
=3.125\,rps
\]

\[
n_{\mathrm{rpm}}=3.125\times60=187.5\,rpm
\]

### 풀이 7

\[
t_{\mathrm{filter}}\approx6\times0.25\,\mu s
=1.5\,\mu s
\]

너무 긴 필터는 (1) 정상적인 짧은 pulse를 제거하거나 edge를 놓칠 수 있고, (2) A/B 채널 위상 관계를 왜곡해 방향/카운트 오류를 만들 수 있다. 정확한 지연은 필터 구현과 입력 위상에 따라 달라진다.

### 풀이 8

\[
L=0.6+0.9+0.2+0.3=2.0\,\mu s
\]

이는 명시한 항목만 포함한 가상 예산이다. 다른 mask, bus wait, ISR prologue가 있다면 추가해야 한다.

### 풀이 9

64-bit timestamp가 두 번의 32-bit memory access로 읽히는 동안 ISR이 값을 갱신하면 상위/하위 word가 서로 다른 세대의 값이 될 수 있다. 해결법 예시는 (1) 매우 짧은 critical section에서 writer interrupt를 mask하고 복사, (2) sequence counter를 읽기 전후 확인하는 snapshot, (3) double buffer와 generation/ownership 사용이다. compiler memory ordering과 MCU atomic semantics를 확인해야 한다.

### 풀이 10

\[
t_{\mathrm{acq}}\ge(N+1)\ln(2)\tau
\]

\[
=13\times0.693\times15\,ns
\approx135.1\,ns
\]

이는 이상적인 RC 근사다. 실제 ADC minimum acquisition time과 입력 source impedance 조건이 우선한다.

### 풀이 11

\[
\omega_m=900\times\frac{2\pi}{60}
=30\pi\approx94.248\,rad/s
\]

\[
\omega_e=6\times94.248
\approx565.487\,rad/s
\]

\[
\Delta\theta_e=565.487\times50\times10^{-6}
\approx0.028274\,rad
\]

\[
0.028274\times\frac{180^\circ}{\pi}
\approx1.62^\circ
\]

### 풀이 12

\[
U=\frac4{40}+\frac{10}{1000}+\frac{30}{2000}
=0.1+0.01+0.015=0.125
\]

즉 12.5%다. 하지만 이것만으로 deadline 보장을 말할 수 없다. 예를 들면 (1) 우선순위 높은 ISR의 간섭과 blocking, (2) critical section과 release jitter, (3) DMA/bus contention 및 worst-case path, (4) deadline이 period보다 짧은 경우, (5) interrupt nesting/overrun 등이 별도 분석 대상이다.

---

## 19. 설계 리뷰 질문

실제 구현 리뷰에서 다음 질문에 답하지 못하면 peripheral configuration을 확정하지 않는다.

1. CPU clock과 peripheral clock은 각각 무엇이며 어떤 분주기를 거치는가?
2. 타이머 tick의 실제 주파수와 오차는 무엇인가?
3. capture timestamp는 edge 발생 시각을 얼마나 잘 대표하는가?
4. QEP 입력의 최대 edge rate와 filter delay가 센서 최대 속도에서 충분한가?
5. ADC aperture는 PWM switching transient와 얼마나 떨어져 있는가?
6. ADC source impedance와 acquisition window가 settle 조건을 만족하는가?
7. ADC conversion 완료와 DMA publish, ISR 진입의 최악 지연은 얼마인가?
8. Park transform에 쓰는 angle timestamp가 ADC aperture와 일치하는가?
9. PWM shadow 값은 어느 counter event에서 active 값으로 반영되는가?
10. 모든 shared data의 ownership과 atomicity가 정의되어 있는가?
11. FOC ISR WCET와 worst-case response time이 deadline보다 충분히 짧은가?
12. deadline miss, DMA overrun, stale sensor와 watchdog failure가 안전한 상태로 이어지는가?
13. hardware trip 경로가 CPU software scheduling과 독립적인가?
14. 각 설정은 exact MCU part, board revision, SDK version, source commit으로 재현 가능한가?

---

## 20. 참고 자료와 적용 범위

### 제조사 1차 자료

1. Texas Instruments, [C2000 Real-Time Control Peripheral Reference Guide, SPRU566 Rev. V](https://www.ti.com/lit/ug/spru566v/spru566v.pdf) — C2000 계열 주변장치 개요. 문서의 peripheral availability table과 실제 주문 코드 일치 여부를 확인해야 한다.
2. Texas Instruments, [F28003x DriverLib API Guide — SYSCTL](https://software-dl.ti.com/C2000/docs/C2000_driverlib_api_guide/f28003x/build/html/modules/sysctl.html) — clock configuration API 개념.
3. Texas Instruments, [F28003x DriverLib API Guide — ePWM](https://software-dl.ti.com/C2000/docs/C2000_driverlib_api_guide/f28003x/build/html/modules/epwm.html) — time-base, compare, event trigger 및 ADC SOC 관련 API.
4. Texas Instruments, [F28003x DriverLib API Guide — ADC](https://software-dl.ti.com/C2000/docs/C2000_driverlib_api_guide/f28003x/build/html/modules/adc.html) — SOC trigger, channel, sample window와 ADC API.
5. Texas Instruments, [TMS320F28003x product documentation](https://www.ti.com/product/TMS320F280039C) — 정확한 device datasheet, TRM, silicon errata와 관련 문서의 최신 개정 확인 진입점.

6. Texas Instruments, [C2000 ePWM Developer's Guide](https://www.ti.com/lit/an/sprad12a/sprad12a.pdf) — ePWM time-base와 ADC trigger 구조 보충 자료.
7. Texas Instruments, [Optimizing Real Time Control Applications (AM263Px MCU+ SDK)](https://software-dl.ti.com/mcu-plus-sdk/esd/AM263PX/09_02_00_56/exports/docs/api_guide_am263px/OPTIMIZING_REAL_TIME_CONTROL_APPLICATIONS.html) — sensing/processing/PWM 경로와 실시간 성능 분석 관점. AM263Px의 ARM R5F cycle 수나 peripheral semantics를 C2000/STM32에 일반화하지 않는다.
8. Arm, [Cortex-M exception entry and return](https://developer.arm.com/documentation/dui0552/a/the-cortex-m3-processor/exception-model/exception-entry-and-return) — Cortex-M exception model 참고이며 C28x 또는 다른 core의 latency 수치 근거가 아니다.

### 적용 주의

- Peripheral reference guide는 제품군 공통 설명이며 모든 peripheral이 모든 part에 존재한다는 보장이 아니다.
- DriverLib API guide는 API 설명이지 실제 보드의 pin mux, connector wiring, jumper setting 또는 특정 프로젝트의 SDK version 증거가 아니다.
- F280039C의 exact package pinout, LaunchPad revision, booster board revision, SDK version, clock init source와 peripheral routing을 한 세트로 확인해야 한다.
- 다른 MCU 계열의 timer, ADC, DMA, interrupt semantics를 C2000에 그대로 적용하지 않는다.
- 본 장의 모든 계산 숫자는 교육용 가상 예제다.

---

## 21. 장 완료 기준

- [ ] clock tree에서 SYSCLK와 peripheral clock의 차이를 설명하고 PLL 계산을 수행한다.
- [ ] timer prescaler, tick, period, overflow와 capture 차분을 계산한다.
- [ ] capture와 compare의 역할을 구분한다.
- [ ] QEP quadrature 방향, x1/x2/x4와 counts/rev를 계산한다.
- [ ] input synchronizer와 digital filter의 noise-delay tradeoff를 설명한다.
- [ ] interrupt priority, nesting, latency, jitter와 WCET를 구분한다.
- [ ] critical section과 atomic snapshot으로 torn read/race condition을 방지하는 방법을 설명한다.
- [ ] DMA double buffer의 ownership과 overrun을 설명한다.
- [ ] PWM event→ADC SOC→aperture→conversion→ISR→PWM active load 시간축을 그린다.
- [ ] sensor timestamp에서 ADC aperture 시각으로 전기각을 예측해 Park 변환에 적용한다.
- [ ] utilization과 deadline guarantee가 다르다는 점을 설명한다.
- [ ] watchdog과 hardware trip의 역할을 구분한다.
- [ ] 실제 AEL-002의 MCU/clock/pin mux/peripheral route/priority/DMA/PWM/ADC/WCET를 근거 없이 확정하지 않는다.
- [ ] **NO STACK / NO POWER** 경계를 유지한다.

**현재 판정:** 이 장은 이론·계산·펌웨어 아키텍처·검증 계획이다. 실제 AEL-002의 MCU configuration, pin mux, peripheral routing, clock, interrupt priority, DMA channel, PWM/ADC frequency, ISR budget, WCET와 watchdog setting은 모두 **TBD**다. 타깃 firmware build, SIL/HIL, 계측, hardware inspection, motor test 또는 power-up을 수행했다고 주장하지 않는다.

**다음 장 연결:** 11장에서는 이 시간 기반 구조 위에 C 언어의 임베디드 구현 규칙, fixed-point/floating-point, memory map, linker/startup, peripheral driver abstraction, unit test와 hardware abstraction을 연결한다.
