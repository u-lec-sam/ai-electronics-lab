# 15장 — 모터 제어 전류 센싱과 아날로그 프런트엔드

> **핵심:** FOC가 사용하는 전류값은 shunt나 센서 하나의 출력이 아니다. 전류 경로, 센서 배치, 아날로그 증폭·필터, ADC sample-and-hold, PWM 시점, 보정·진단, 독립 보호회로가 함께 만든 측정 결과다.

## 학습 목표

1. low-side single/dual/three-shunt, inline phase shunt, DC-link shunt의 관측 가능 구간과 장단점을 비교한다.
2. shunt의 저항·전력·TCR·공차·기생 인덕턴스와 Kelvin sense 배선을 설계 입력으로 해석한다.
3. current-sense amplifier, 차동/계측 증폭기, isolated amplifier, Hall 센서의 공통모드·절연·대역폭·오차 한계를 비교한다.
4. gain, reference/offset, anti-alias filter, noise, ADC acquisition settling/kickback의 예산을 계산한다.
5. PWM switching edge와 amplifier recovery를 고려해 ADC aperture를 배치하고 Chapter 10의 ePWM/ADC/ISR/DMA 타이밍과 연결한다.
6. offset/gain/polarity/phase calibration, plausibility, saturation, invalid sample, comparator fast OCP를 검증한다.
7. 불확도와 fault injection을 요구사항·시험 증거로 바꾼다.

## 1. 전류 측정 체인의 전체 그림

전류는 도선의 단면을 통과하는 전하의 시간 변화율이다. FOC의 \(i_a,i_b,i_c\)는 단순히 ADC 숫자가 아니라, 정해진 방향과 시각에서 측정된 상전류다.

\[
I = \frac{dQ}{dt},\qquad V_{sh}=I R_{sh}
\]

측정 체인:

\[
I_{phase}\rightarrow R_{sh}\rightarrow
\text{analog front end}\rightarrow
\text{anti-alias / ADC driver}\rightarrow
\text{ADC S+H}\rightarrow
\text{calibration}\rightarrow
(i_a,i_b,i_c,valid,timestamp)
\]

별도 보호 경로는 가능한 한 CPU 소프트웨어의 ADC 처리와 독립적으로 설계한다.

\[
R_{sh}\rightarrow \text{fast comparator}\rightarrow
\text{hardware trip / gate disable}
\]

ADC 기반 소프트웨어 OCP는 평균·필터·진단·기록에 유용하지만, 변환·인터럽트·태스크 지연을 기다리는 보호 경로로 오인하면 안 된다.

## 2. 측정 위치와 shunt topology

### 2.1 Low-side shunt

각 인버터 하단 스위치와 DC− 사이에 shunt를 둔다. 공통모드가 낮아 저전압 증폭기와 ADC로 연결하기 쉽다.

- **3-shunt:** 각 하단 leg의 전류를 측정한다. 유효한 PWM 상태와 샘플 시점에 따라 각 상전류를 얻는다. 전류 재구성은 스위칭 상태·전류 방향·blanking·deadtime·최소 샘플 창에 의존한다.
- **2-shunt:** 두 상을 직접 측정하고, 3선식 모터에서 \(i_a+i_b+i_c=0\) 가정이 성립할 때 세 번째를 \(i_c=-(i_a+i_b)\)로 재구성한다. 누설·공통모드·센서 오프셋 때문에 합이 정확히 0이 아닐 수 있다.
- **1-shunt:** DC− 또는 DC-link return의 단일 shunt에서 스위칭 상태별 전류 구간을 읽어 상전류를 재구성한다. 활성벡터 구간이 너무 짧거나 modulation 영역/저속/과변조/zero-vector 비중에 따라 관측 창이 사라질 수 있다. PWM 재배치·샘플링 시프트·전류 재구성 알고리즘이 필요하다.

**장점:** 입력 공통모드가 낮고 비용·손실·배선이 단순할 수 있다.  
**주의:** low-side shunt는 스위칭 중 모든 순간의 상전류를 연속 관측하지 못한다. 측정 가능한 구간은 PWM 상태와 전류 경로로 증명해야 한다. shunt가 GND 경로에 들어가면 analog ground와 power return의 전위차·접지 바운스가 제어 신호에 섞일 수 있다.

### 2.2 Inline phase shunt

각 half-bridge 출력과 모터 사이 상 경로에 shunt를 직렬 삽입한다. 상전류를 직접 읽으므로 low-side처럼 특정 하단 스위치 on-window에만 의존하는 관측 제약을 줄인다.

- 상전류의 연속 경로를 측정하기 쉽고, 고성능 FOC에 유리하다.
- shunt 양단의 공통모드가 PWM으로 크게 움직인다. amplifier는 정적 common-mode 범위뿐 아니라 \(dV_{CM}/dt\), transient immunity, recovery, input absolute maximum을 만족해야 한다.
- shunt·배선이 전력 경로에 직렬로 들어가므로 전력 손실, 발열, 기생 L, 스위칭 노이즈를 평가한다.
- differential input trace는 shunt 양단에서 Kelvin으로 분기하고, 두 입력의 임피던스·필터를 대칭으로 유지한다.

### 2.3 DC-link shunt

DC 버스의 한쪽 경로에서 합성 DC 전류를 측정한다. 부품 수가 적지만 순간 DC-link current와 각 상전류는 같지 않다. 특정 스위칭 상태에서만 DC-link 전류가 상전류 조합을 나타내므로 PWM 동기 샘플링과 전류 재구성이 필수다. 평균 버스전류·전력 감시와 순간 상전류 FOC 피드백을 구분한다.

### 2.4 Isolated current sensing

절연형 shunt amplifier/modulator, isolated ADC, Hall sensor 등은 고전위와 제어 MCU 사이의 galvanic isolation을 제공할 수 있다. 단, 부품의 isolation rating 하나만으로 시스템 절연이 완성되지 않는다. working voltage, transient voltage, creepage/clearance, pollution degree, altitude, package, PCB slot, isolation barrier supply, 인증 체계를 함께 검토해야 한다.

### topology 비교

| 위치 | 직접 관측 | 주요 장점 | 핵심 제약 |
|---|---|---|---|
| Low-side 3-shunt | 각 하단 leg 경로 | 낮은 공통모드, 3채널 | PWM 유효 샘플 창, 접지 바운스 |
| Low-side 2-shunt | 두 하단 leg | 채널/비용 감소 | 세 번째 상 재구성, 센서 mismatch |
| Low-side/DC− 1-shunt | DC return | 최소 shunt 수 | active-vector 구간, PWM 재구성 복잡 |
| Inline 3-shunt | 각 상 도선 | 상전류 직접 측정 | 큰 PWM 공통모드·dv/dt, 손실 |
| DC-link shunt | 버스 전류 | 버스 전력/전류 감시 | 상전류와 동일하지 않음, 상태 의존 |
| Isolated sensor | 절연 경계 건너 측정 | 공통모드 분리 | 비용·지연·절연 설계·전원 |

어떤 topology가 “최고”인지 일반화하지 않는다. 제어 대역폭, modulation 범위, 최대 전류, 전력 손실, ADC 채널 수, 절연 경계, 비용, 보드 배치, fault response를 요구사항으로 먼저 정한다.

## 3. Shunt resistor 설계와 Kelvin routing

### 3.1 저항값의 선택

\[
V_{sh,pk}=I_{pk}R_{sh},\qquad
P_{sh,avg}=I_{rms}^{2}R_{sh}
\]

저항을 크게 하면 신호가 커져 ADC 분해능/노이즈에 유리하지만, 전압 강하와 발열이 커진다. 작게 하면 손실은 줄지만 amplifier offset/noise, PCB 열기전력, EMI에 비해 유효 신호가 작아진다.

최소한 다음을 계산한다.

- 최대 정상·과도 전류에서 shunt voltage와 amplifier input range
- 연속 RMS 전류에서 평균 전력과 terminal temperature
- PWM pulse peak/duration/repetition의 pulse-energy 및 overload curve
- shunt tolerance, TCR, self-heating, solder/terminal heat flow
- parasitic inductance와 전류 edge의 \(L\,di/dt\) 전압
- amplifier input common-mode, differential range, absolute maximum, clamp current

정격 전력 숫자만 보고 선정하지 않는다. 제조사 derating curve, terminal temperature 조건, pulse-load curve, PCB copper 조건을 적용한다.

### 3.2 TCR와 온도 오차

저항의 1차 온도 근사는 다음과 같다.

\[
R(T)=R_0[1+\alpha(T-T_0)]
\]

여기서 \(\alpha\)는 TCR(temperature coefficient of resistance, ppm/°C)이다. 저항 합금의 TCR과 단자/전극을 포함한 전체 저항의 TCR은 다를 수 있다. 실제 측정 정확도에는 shunt element만이 아니라 terminal, solder, copper, thermal gradient가 포함된다.

### 3.3 Kelvin / force-sense

전류가 흐르는 두 force terminal과 전압을 측정하는 두 sense terminal을 분리한다. sense trace는 shunt의 실제 저항 요소 양단에서 짧고 대칭적으로 뽑는다.

- 고전류 copper trace의 전압 강하가 sense 값에 포함되지 않도록 한다.
- sense pair를 differential로 라우팅하고, switching node와 gate-drive loop에서 떨어뜨린다.
- 두 입력의 series R, differential C, common-mode C, via 수, 길이, 열환경을 가능한 한 대칭으로 한다.
- Kelvin trace가 전류 경로를 우회하거나 다른 shunt 사이의 순환전류 경로가 되지 않게 한다.
- 입력 RC는 amplifier의 input bias current, source impedance, stability와 함께 검토한다.

2-terminal shunt에서 pad를 어디서 sense하느냐에 따라 copper/terminal 저항이 결과에 포함될 수 있다. 4-terminal 구조는 이를 줄이는 데 도움을 주지만, PCB footprint와 연결이 잘못되면 이점이 사라진다.

### 3.4 기생 인덕턴스

shunt와 연결부의 기생 인덕턴스는 스위칭 edge에서 다음 전압을 만든다.

\[
V_L=L_{par}\frac{di}{dt}
\]

따라서 실제 sense voltage는 \(IR\)만이 아니라 \(IR+L_{par}di/dt\) 성분을 포함할 수 있다. shunt body의 inductance뿐 아니라 terminal, copper loop, via, force/sense loop geometry를 본다.

## 4. 아날로그 센서와 amplifier 종류

### 4.1 Current-sense amplifier (CSA)

정밀 내부 저항 네트워크로 shunt 양단의 작은 차동 전압을 증폭한다. low-side, high-side, inline phase 측정용 제품군이 있다.

확인 항목: input common-mode range, differential input range, absolute maximum, CMRR DC/AC, PWM transient response, output swing, gain error/drift, input offset/drift, bandwidth, slew rate, settling/recovery, reference input behavior, output load/capacitance.

“PWM rejection”이라는 문구는 모든 edge에서 출력이 즉시 정확하다는 뜻이 아니다. 데이터시트의 시험 조건과 step response/recovery waveform을 확인하고, PWM edge 이후 invalid/blanking 구간을 실제로 측정해야 한다.

### 4.2 Difference amplifier / instrumentation amplifier

일반 연산증폭기와 저항 네트워크로 차동 신호를 증폭할 수 있다. 하지만 저항비 mismatch는 CMRR을 악화시키며, 입력 공통모드 범위와 출력 headroom이 전원 레일에 제한된다. instrumentation amplifier는 고입력 임피던스와 정밀도를 제공할 수 있지만, 높은 PWM common-mode와 빠른 dv/dt에 적합한지는 별도 검증해야 한다.

### 4.3 Isolated amplifier / isolated modulator

shunt의 작은 전압을 절연 장벽 너머로 전달한다. 출력은 differential analog 또는 digital bitstream일 수 있다. 정확도·대역폭·지연·CMTI·절연 전압·양측 전원·fail-safe 상태·missing-supply detection을 확인한다. 절연형 디지털 modulator는 decimation filter의 group delay와 oversampling 설정까지 전류 루프의 지연 예산에 포함한다.

### 4.4 Hall-effect current sensor

도체 전류가 만드는 자기장을 Hall element로 측정한다. 전기적 삽입 저항이 낮고 절연형 구조가 가능하며 DC/AC를 측정할 수 있다. 대신 offset, offset drift, sensitivity error, bandwidth, magnetic hysteresis, external field, conductor position, temperature, core saturation을 고려한다. 전류 경로의 내부 conductor 저항과 온도 상승도 확인한다.

Hall 센서가 항상 shunt보다 부정확하다고 단정하지 않는다. 정확도는 특정 부품, 전류 범위, 온도, 대역폭, 설치 조건의 비교 문제다.

## 5. Gain, offset, ADC range와 clipping

단일 출력형 CSA의 일반 모델:

\[
V_{out}=V_{ref}+G(I R_{sh}+V_{os,in})+V_{os,out}
\]

- \(G\): amplifier gain (V/V)
- \(V_{ref}\): zero-current output reference
- \(V_{os,in}\): input-referred offset (V)
- \(V_{os,out}\): output-referred offset (V)

ADC 입력 범위 \([V_{min},V_{max}]\)에 대해 양·음 방향 peak current가 clipping되지 않는지 계산한다. 양방향 전류를 측정할 때 \(V_{ref}\)는 중간점 근처일 수 있지만, reference tolerance/noise/drive capability와 output swing margin을 포함한다.

\[
I=\frac{V_{out}-V_{zero}}{G R_{sh}}
\]

여기서 \(V_{zero}\)는 실제 보정한 zero-current output이며, 단순히 nominal reference voltage와 같다고 가정하지 않는다.

### ADC code 예시

이상적인 N-bit unipolar ADC에서:

\[
LSB=\frac{V_{FS}}{2^N}
\]

전류 한 code의 크기는 \(LSB/(G R_{sh})\)다. 이는 quantization step이지 실제 측정 정확도가 아니다. noise, INL, reference error, amplifier offset, gain error, shunt TCR, layout pickup가 더해진다.

## 6. Anti-alias filter와 노이즈

PWM switching ripple과 edge artifact는 ADC sampling frequency보다 높은 주파수 성분을 포함한다. Nyquist 조건만으로 실제 아날로그 필터가 충분하다고 판단하지 않는다. 측정하려는 current-loop bandwidth, PWM frequency, sampling rate, switching sidebands, amplifier bandwidth, ADC aperture, noise budget을 함께 정한다.

1차 RC low-pass의 차단 주파수:

\[
f_c=\frac{1}{2\pi RC}
\]

주파수 \(f\)에서 크기 응답과 위상:

\[
|H(j2\pi f)|=\frac{1}{\sqrt{1+(f/f_c)^2}},
\qquad \angle H=-\tan^{-1}(f/f_c)
\]

낮은 \(f_c\)는 aliasing/noise를 줄일 수 있지만 current-loop phase margin을 줄이고 응답을 늦춘다. 필터는 PWM carrier를 제거하는 만능 도구가 아니다. 동기 샘플링과 edge blanking이 먼저고, anti-alias filtering은 남은 고주파 성분을 제한하는 역할이다.

저항의 열잡음 전압밀도는 이상적인 저항 모델에서:

\[
e_n=\sqrt{4kTR}\quad[V/\sqrt{Hz}]
\]

실효 잡음은 대역폭과 필터의 noise bandwidth에 따라 달라진다. amplifier input voltage/current noise, reference noise, ADC noise, ground coupling도 함께 합산한다.

## 7. ADC acquisition settling과 kickback

SAR ADC는 acquisition 구간에 내부 sample-and-hold capacitor를 입력에 연결해 충전한 뒤, 스위치를 열어 변환한다. 입력 source가 너무 높은 임피던스이거나 amplifier가 충분히 빠르게 회복하지 못하면 S/H capacitor가 목표 전압까지 정착하지 못한다.

단순 1차 RC 모델에서 full-scale step을 0.5 LSB 이내로 정착시키려면:

\[
e^{-t_{acq}/\tau}\leq\frac{1}{2^{N+1}},
\qquad
t_{acq}\geq (N+1)\ln 2\,\tau
\]

여기서 \(\tau=R_{eq}C_{eq}\). 실제 ADC input model에는 sampling switch resistance, internal capacitor, pin capacitance, external R/C, amplifier output impedance/bandwidth, channel switching history가 포함된다. 1차 식은 시작점이며, 최종 값은 정확한 MCU datasheet/TRM와 SPICE/bench evidence로 확인한다.

**Kickback:** S/H switch가 닫힐 때 내부 capacitor가 입력 노드와 charge를 주고받아 순간적인 전압 교란을 만든다. 외부 capacitor는 charge reservoir 역할을 할 수 있지만, amplifier stability와 RC settling을 악화시킬 수 있다. source R을 무조건 크게 하거나 C를 무조건 크게 하지 않는다.

**채널 순서:** ADC가 이전 채널 전압을 기억하는 구조라면 큰 입력 step 뒤의 채널은 더 긴 settling을 요구할 수 있다. current phase 채널의 순서, SOC arbitration, acquisition window, simultaneous vs sequential sampling을 실제 MCU 문서와 함께 설계한다.

## 8. PWM 동기 샘플링과 Chapter 10 타이밍

샘플링 시점은 “PWM 주기 중 아무 때나”가 아니다.

1. ePWM time-base와 switching edge를 정의한다.
2. 전류가 유효하게 관측되는 구간을 topology별로 계산한다.
3. switching edge 직후의 ringing, common-mode transient, amplifier recovery, blanking을 피한다.
4. 샘플 aperture 전체가 안정된 창 안에 들어오는지 확인한다. aperture의 끝에서 S/H capacitor가 입력을 capture한다.
5. ADC acquisition window와 conversion latency, result latch, interrupt/DMA, FOC 계산, PWM shadow-load deadline을 연결한다.
6. 샘플 timestamp는 trigger 시각 또는 실제 aperture/capture 시각으로 일관되게 정의한다. Chapter 09의 sensor timestamp와 혼동하지 않는다.

개념 타임라인:

\`\`\`text
PWM edge       |---- switching transient ----| stable current window
CSA output     ~~~~~ ringing/recovery ~~~~~~~|---- settled ----
ADC S+H        [ wait ]                       [ acquisition ]
ADC capture                                      ^
ADC result                                        | conversion -> latch
FOC update                                                        -> PWM shadow load
\`\`\`

샘플 시점이 안정 창 밖이면 숫자가 정상 범위에 있어도 valid=false로 처리한다. 유효 창이 없는 PWM 상태에서는 재구성, modulation 제한, sample relocation 또는 fault policy를 명시한다. 이전 샘플을 무표시로 재사용하지 않는다.

## 9. Calibration, phase matching과 uncertainty

### 9.1 Offset calibration

모터 전류가 0임을 독립적으로 보장하는 승인된 무전류 조건에서 각 채널의 offset을 여러 샘플 평균/통계로 추정한다. PWM switching noise와 ADC offset, amplifier offset, reference drift를 구분한다. 전류가 흐르는 상태에서 평균값을 offset으로 학습하면 실제 DC current를 지워버릴 수 있다.

### 9.2 Gain calibration

정확도가 추적 가능한 외부 기준 전류/계측기와 안전한 시험 fixture를 이용해 2점 이상에서 slope/intercept를 추정한다. 단일점 보정은 offset과 gain을 분리하지 못한다. 실제 current range 전체에 대해 선형성·온도·방향을 확인한다.

### 9.3 Polarity와 phase order

각 상 전류의 양의 방향, shunt IN+/IN−, amplifier output slope, ADC channel, motor U/V/W, Clarke transform phase order를 하나의 interface contract로 고정한다. 부호 반전 하나는 FOC의 torque 방향/전류 feedback을 잘못 만들 수 있다. 실제 motor power test 전에는 저에너지/무전원 continuity/fixture 기반으로 방향을 확인한다.

### 9.4 Phase matching

세 채널의 gain·offset·filter delay·sample timestamp를 맞춘다. 위상별 amplifier/RC tolerance 차이는 \(i_a+i_b+i_c\) 잔차와 dq current ripple로 나타날 수 있다. 채널별 calibration constant와 validity를 보관하고, filter delay가 다르면 디지털 보상 또는 설계 변경을 검토한다.

### 9.5 Uncertainty budget

독립 오차의 통계적 결합은 조건이 맞을 때 RSS(root-sum-square)로 근사할 수 있다.

\[
u_c=\sqrt{u_1^2+u_2^2+\cdots+u_n^2}
\]

최악값 보장은 부호/상관관계가 불명확할 때 절대값 합계를 사용한다. 공차를 RSS로 처리할 때는 독립·분포 가정이 실제로 성립하는지 설명한다. 제조사 maximum error를 임의로 1σ 표준편차로 바꾸지 않는다.

## 10. Comparator fast OCP와 진단 계층

**Fast path:** shunt/센서 → comparator → hardware trip fabric (예: MCU CMPSS/X-BAR/ePWM Trip Zone 또는 외부 comparator → gate-driver disable). 경로가 asynchronous인지, digital filter/blanking이 있는지, latch가 set-dominant인지, trip polarity, reset 조건, propagation delay, output safe state를 확인한다.

**Slow/diagnostic path:** ADC current sample → plausibility/thermal/overload model → software fault latch → telemetry/log. ADC OCP는 fast path의 대체물이 아니다.

기본 정책:
- hardware trip은 PWM/gate output을 안전 상태로 강제한다.
- trip source와 timestamp를 기록하고, 자동으로 출력이 다시 켜지지 않게 한다.
- 명시적 fault acknowledgement와 supervised re-arm sequence가 필요하다.
- comparator threshold에는 shunt tolerance, gain/offset, reference tolerance, propagation delay, filter delay, current overshoot를 포함한다.
- comparator input에 RC filter를 추가하면 glitch immunity가 좋아질 수 있지만 trip delay가 늘어난다. 실제 worst-case response time을 측정/계산한다.
- ADC saturation, amplifier clipping, missing sensor, stuck-at, phase sum residual, impossible slew, stale timestamp는 별도의 invalid/fault code로 처리한다.

### F28003x 후보 플랫폼 주의

AEL-002에서 F280039C는 후보일 뿐 target 확정이 아니다. TI F28003x TRM Rev. C의 ADC SOC/ACQPS와 CMPSS, X-BAR, ePWM Trip Zone 구조는 후보 플랫폼의 설계 참고다. Rev. E silicon errata에는 ADC DMA stale result, fractional ADCCLK divider 성능 저하, CMPSS latch clear, ADC sampling과 AGPIO comparator glitch 관련 advisory가 포함된다. 실제 silicon revision, advisory applicability, workaround, SDK/driverlib version을 exact device 기준으로 확인하기 전에는 설정값이나 안전 성능을 확정하지 않는다.

## 11. 가상 설계 계산 — 전부 교육용 예시

아래 수치는 가상 계산이며 AEL-002의 shunt·gain·current limit·ADC 설정이 아니다.

### 예제 A — shunt 전압과 발열

가정: \(R_{sh}=2.0\,m\Omega\), \(I_{pk}=20\,A\), \(I_{rms}=12\,A\).

\[
V_{sh,pk}=20\times0.002=0.040\,V=40\,mV
\]
\[
P_{avg}=12^2\times0.002=0.288\,W
\]

20 A가 흐르는 순간의 저항 전력은 \(20^2\times0.002=0.8\,W\). 20 A pulse가 2 ms 지속되면 단순 저항 모델의 pulse energy는 \(0.8\times0.002=1.6\,mJ\). 실제 pulse 반복·열 임피던스·terminal 온도·derating을 확인해야 한다.

### 예제 B — amplifier gain과 ADC headroom

가정: \(R_{sh}=2\,m\Omega\), \(G=20\,V/V\), \(V_{ref}=1.65\,V\), 전류 범위 ±20 A.

입력 shunt drop은 ±40 mV. 증폭된 변화는 ±0.8 V이므로 출력은 이상적으로 0.85–2.45 V. 0–3.3 V ADC 범위 안에 있지만, amplifier output swing, transient overshoot, reference tolerance, ADC full-scale margin은 별도 확인한다.

### 예제 C — ADC current LSB

12-bit, 3.3-V full scale의 이상적인 code step:

\[
LSB=3.3/4096=0.8057\,mV
\]
\[
I_{LSB}=0.8057\,mV/(20\times2\,m\Omega)
=20.14\,mA
\]

이는 quantization step이다. 실제 RMS noise/accuracy는 이 값보다 클 수 있다.

### 예제 D — shunt TCR와 tolerance

가정: shunt 초기 tolerance ±1%, total TCR ±75 ppm/°C, 온도 변화 80°C.

\[
\Delta R/R=75\times10^{-6}\times80=0.006=0.6\%
\]

shunt 저항 오차의 단순 worst-case 합은 ±1.6%다. 독립·확률 모델을 가정한 RSS는 \(\sqrt{1.0^2+0.6^2}=1.166\%\). 실제 보증은 제조사 정의와 온도/terminal 조건에 맞춰 worst-case를 우선 사용한다.

### 예제 E — ADC acquisition settling

가정: 단순화한 \(R_{eq}=1.0\,k\Omega\), \(C_{eq}=12.5\,pF\), 12-bit ADC, full-scale step, 0.5 LSB 오차 목표.

\[
\tau=RC=12.5\,ns
\]
\[
t_{acq}\geq(12+1)\ln2\times12.5\,ns
=112.6\,ns
\]

이 값은 단순 1차 모델의 교육용 결과다. 실제 F28003x ADC 입력 모델과 datasheet minimum S+H time, amplifier output impedance, external RC, channel switching을 사용해야 한다.

### 예제 F — anti-alias RC

가정: \(R=1.0\,k\Omega\), 목표 \(f_c=100\,kHz\).

\[
C=\frac{1}{2\pi R f_c}=1.592\,nF
\]

표준값 1.6 nF를 사용하면 실제 cutoff는 약 99.5 kHz. 이 필터의 저주파 group delay는 약 \(1/(2\pi f_c)=1.59\,\mu s\) 규모이므로 current-loop phase budget과 함께 판단한다.

### 예제 G — comparator threshold

가정: \(R_{sh}=2\,m\Omega\), comparator 입력 기준 \(V_{th}=30\,mV\), gain=1의 shunt 직접 감지.

\[
I_{trip}=V_{th}/R_{sh}=0.030/0.002=15\,A
\]

shunt tolerance와 TCR, comparator offset, reference tolerance, filtering, propagation delay를 포함하면 실제 trip current는 달라진다. 예제 threshold는 AEL 설정이 아니다.

### 예제 H — uncertainty

가정한 독립 표준불확도 성분: shunt 0.6%, gain 0.2%, ADC/reference 0.15%, calibration 0.3%.

\[
u_c=\sqrt{0.6^2+0.2^2+0.15^2+0.3^2}=0.715\%
\]

이 RSS는 각 값이 같은 신뢰수준의 표준불확도이고 서로 독립이라는 가정에서만 의미가 있다. maximum tolerance를 그대로 RSS로 넣은 결과를 보증 정확도로 표현하지 않는다.

## 12. 완전 풀이 연습문제

### 문제 1 — shunt 저항 선정 후보 비교
20 A peak에서 최대 shunt drop을 50 mV로 제한하려 한다. 가능한 최대 저항은?

**풀이:** \(R_{max}=V/I=0.050/20=2.5\,m\Omega\). 이는 voltage drop 제약만 만족하는 상한이다. 열·pulse·noise·offset·TCR을 검토해야 최종값을 고를 수 있다.

### 문제 2 — 연속 전력
문제 1의 2.5 mΩ 후보에 10 A RMS가 흐른다. 평균 shunt power는?

**풀이:** \(P=I^2R=10^2\times0.0025=0.25\,W\). 이론상 저항 소모 전력이다. 부품 power rating은 주변 온도·terminal temperature·PCB 열 조건에 따라 derating한다.

### 문제 3 — 증폭기 출력
\(R=2.5\,m\Omega\), \(G=20\), \(V_{ref}=1.65\,V\), \(I=-12\,A\)일 때 이상 출력은?

**풀이:** shunt 전압은 \(-12\times0.0025=-30\,mV\). 증폭 변화량은 \(-0.6\,V\). 출력은 \(1.65-0.6=1.05\,V\).

### 문제 4 — ADC 전류 code
3.3 V, 12-bit ADC, gain 20, shunt 2.5 mΩ의 ideal current LSB는?

**풀이:** \(LSB=3.3/4096=0.8057\,mV\). 감도 \(G R=20\times0.0025=0.05\,V/A\). \(I_{LSB}=0.0008057/0.05=0.01611\,A=16.1\,mA\).

### 문제 5 — Kelvin 오차
2 mΩ shunt에서 force path copper 0.2 mΩ가 측정에 잘못 포함되면 상대 오차는?

**풀이:** 측정 저항은 2.2 mΩ. 오차는 \(0.2/2.0=10\%\). 4-wire Kelvin sense는 force path의 추가 저항이 voltage measurement에 포함되는 것을 줄인다.

### 문제 6 — RC 필터
R=820 Ω, C=2.2 nF인 1차 RC의 cutoff는?

**풀이:** \(f_c=1/(2\pi\times820\times2.2nF)=88.2\,kHz\) (근사). 실제 부품 공차와 amplifier/ADC 입력 임피던스를 포함해 다시 계산한다.

### 문제 7 — settling window
12-bit, 0.5 LSB 기준, \(R_{eq}=600\,\Omega\), \(C_{eq}=20\,pF\)의 1차 정착 최소 시간은?

**풀이:** \(\tau=600\times20pF=12ns\). \(t\geq13\ln2\times12ns=108.2ns\). 실제 acquisition window는 MCU minimum과 analog driver dynamics 중 더 엄격한 조건을 만족해야 한다.

### 문제 8 — 2-shunt 재구성
측정값 \(i_a=4.2A\), \(i_b=-1.7A\)이고 3선식 가정이 성립한다면 \(i_c\)는?

**풀이:** \(i_c=-(4.2-1.7)=-2.5A\). 센서 오차가 있다면 세 상 합 잔차가 0이 아니므로 진단 허용오차와 calibration이 필요하다.

### 문제 9 — TCR drift
50 ppm/°C shunt가 100°C 상승했다. 저항 변화율은?

**풀이:** \(50\times10^{-6}\times100=0.005=0.5\%\). 저항이 증가하면 고정 gain 보정에서 측정 current scale error가 반대 방향으로 나타난다(전압/전류 변환식의 분모가 커짐).

### 문제 10 — comparator response budget
가상 OCP chain: comparator 150 ns, logic route 30 ns, driver disable 250 ns. 총 경로 지연은?

**풀이:** 합계 \(150+30+250=430ns\). 여기에 shunt/amp propagation, input filter, gate discharge, device turn-off, current overshoot 및 계측 불확도를 포함해야 한다. 이 계산만으로 안전 차단 성능을 주장할 수 없다.

## 13. Fault injection 및 검증 템플릿

실물 인버터에 전력을 인가하지 않고도 host test, 회로 시뮬레이션, ADC 데이터 replay, comparator 논리 모델로 많은 결함을 검증할 수 있다. 실제 trip time, CMTI, EMI, thermal, short-circuit는 승인된 fixture와 계측·안전 계획 없이는 검증했다고 주장하지 않는다.

| ID | Fault injection | 기대 반응 | 증거/측정 |
|---|---|---|---|
| CS-01 | ADC input open / sensor disconnected | invalid sensor, PWM inhibit policy | ADC code, status, fault log |
| CS-02 | shunt sense polarity reversed | startup plausibility fail / polarity mismatch | signed current sweep fixture |
| CS-03 | offset step / temperature drift | offset monitor threshold, calibration invalid | zero-current record |
| CS-04 | gain mismatch one phase | phase-sum residual / calibration mismatch | three-channel sweep |
| CS-05 | ADC rail saturation | invalid sample, no stale substitution | raw code and saturation flag |
| CS-06 | amplifier output stuck high/low | range and slew plausibility fault | replayed waveform |
| CS-07 | PWM edge transient injected | sample blanking/recovery policy | scope/ADC timestamp correlation |
| CS-08 | sample outside valid low-side window | invalid/reconstruction fail | PWM state and sample marker |
| CS-09 | ADC SOC collision / delayed result | deadline/sequence detection | SOC flags, result sequence |
| CS-10 | phase channel swapped | phase-order diagnostic | fixture channel mapping |
| CS-11 | comparator threshold crossed | hardware trip dominates CPU | comparator and trip timestamps |
| CS-12 | comparator chatter near threshold | hysteresis/latch policy | threshold ramp replay |
| CS-13 | comparator latch clear attempt while fault active | trip remains asserted | state transition log |
| CS-14 | stale DMA/ADC result | sequence/timestamp mismatch invalidates data | DMA/ADC trace |
| CS-15 | current sum inconsistent | sensor/phase diagnostic | \(i_a+i_b+i_c\) residual |
| CS-16 | isolated sensor supply missing | fail-safe invalid state | supply fault and output state |

### 요구사항/시험 기록 양식

| Field | Required entry |
|---|---|
| Requirement ID | unique ID, measurable acceptance criterion |
| Topology / exact part | manufacturer, exact order code, board revision |
| Current range | continuous RMS, peak, pulse duration/repetition |
| Shunt | resistance, tolerance, TCR, power/overload curve, inductance |
| Amplifier/sensor | CM range, CMTI/transient response, gain, offset, bandwidth, delay |
| Analog filter | R/C, cutoff, tolerance, noise bandwidth, phase delay |
| ADC | MCU/revision, channel/pin, resolution, reference, acquisition model/window |
| PWM timing | carrier, edge, valid sample window, blanking, trigger source |
| Calibration | zero, gain, polarity, phase order, temperature and calibration provenance |
| OCP | threshold range, hysteresis, filter, propagation path, latch/reset/rearm |
| Uncertainty | error contributors, correlation assumptions, worst-case and RSS |
| Test evidence | method, fixture, instruments, calibration, raw data, pass/fail |
| Applicability | generic theory / candidate part / exact target / measured hardware |

## 14. AEL-002 적용과 미확인 사항

프로젝트 문서에는 TI BOOSTXL-3PHGANINV EVM의 **특정 구현 예시**가 기록되어 있다. TI SLUUBP1A Rev. A (2018-04)는 세 개의 inline phase shunt, 각 5 mΩ, INA240 gain 20 V/V, 1.65 V midpoint, 3.3 V reference, TLV3201 hardware OCP 12 A/1 A hysteresis 예시를 설명한다. 이 값은 해당 EVM 회로의 문서값이며 AEL-002의 확정 설계나 실제 샘플 측정값이 아니다. TI guide의 inline shunt output recovery 설명은 약 2 µs라는 해당 EVM 설명 조건에 묶여 있으며 다른 amplifier/PCB에 일반화하지 않는다.

AEL-002 project README는 첫 bring-up의 선호 아키텍처로 three-phase shunt sensing을 기술하지만, 실제 AEL-002 회로도/BOM/board revision이 승인되지 않았으므로 다음 항목은 여전히 **TBD**다.

- 실제 shunt 위치·저항·공차·TCR·pulse rating·Kelvin footprint
- amplifier/isolated sensor/Hall part number, gain, reference, bandwidth, CMTI/recovery
- MCU와 silicon revision, ADC pin/channel route, reference, acquisition window, SOC arbitration
- analog filter, noise/phase delay, PWM frequency, valid sample window
- current continuous/peak/pulse limits와 hardware OCP threshold/hysteresis
- calibration procedure/constants, phase polarity/order, uncertainty acceptance
- comparator-to-trip-to-gate-disable propagation time와 latched reset/re-arm behavior

### 다음 장과의 연결

- Chapter 08: phase current → Clarke/Park → \(i_d/i_q\) current controller.
- Chapter 09: timestamp/validity와 rotor angle prediction의 시간 정합.
- Chapter 10: ePWM trigger, ADC aperture/result latch, ISR/DMA ownership, WCET.
- Chapter 11: typed current sample, unit/range/status, saturating arithmetic, fault latch.
- Chapter 13: requirement traceability, fault injection, evidence grade.
- Chapter 14: gate-driver disable path와 hardware safe state.

## 15. 완료 기준

- shunt topology별 관측 조건과 blind window를 설명할 수 있다.
- shunt voltage/power/TCR/tolerance/pulse 조건을 계산할 수 있다.
- amplifier common-mode, CMTI, bandwidth, offset, recovery를 데이터시트 조건으로 비교할 수 있다.
- ADC S+H settling과 anti-alias filter를 계산하고 정확한 MCU 자료로 확인할 수 있다.
- PWM edge 이후 유효 sample window와 timestamp를 정의할 수 있다.
- offset/gain/polarity/phase calibration 및 uncertainty budget을 작성할 수 있다.
- fast hardware OCP와 ADC/software diagnostic을 분리하고 fault latch/re-arm을 설명할 수 있다.
- AEL-002 미확인 hardware settings를 TBD로 유지한다.

**안전 상태:** 실제 보드·샘플 revision, jumper/pin/ground, current path, hardware inhibit, approved current-limited procedure가 검증되기 전까지 **NO STACK / NO POWER**. 이 강의와 GitHub CI는 실물 전기·열·EMI·fault response 시험을 대신하지 않는다.

## 참고 자료

아래 출처의 문서 번호·개정·확인 위치·범위 제한은 SOURCE_REVIEW_REGISTER.md에 claim group별로 기록한다.

- TI, BOOSTXL-3PhGaNInv Evaluation Module User Guide, SLUUBP1A Rev. A (2018-04), pp. 2–4.
- TI, BOOSTXL-3PhGaNInv Schematic, SLURAY0A Rev. A; phase current sense circuit.
- TI, INA240 datasheet, SBOS662C Rev. C (2021-12), §§6, 8.
- TI, AMC1302 datasheet, SBAS812D Rev. D (2021-06), §§6–8.
- TI, TMCS1100 datasheet, SBOS820C Rev. C (2025-06), §§6–8.
- TI, TMS320F28003x TRM, SPRUIW9C (2024-03), §§16.3–16.8 and CMPSS/X-BAR/ePWM chapters.
- TI, TMS320F28003x datasheet, SPRSP61C Rev. C (2023-12), §6.13, Tables 6-18/6-19.
- TI, TMS320F28003x Silicon Errata, SPRZ496E Rev. E (2026-08), Table 1-2 and ADC/CMPSS advisories.
- TI, SPRACT6A Rev. A (2023-03), ADC Input Circuit Evaluation for C2000 MCUs.
- TI, SBOA165, Low-Side Sensing / current-sense amplifier comparison.
- TI, SBAA531 (2021-11), SAR ADC sample-and-hold and input settling.
- TI, SLYY234 (2024-12), An Engineer's Guide to Isolated Signal Chain Solutions.
- TI, SDAA115 (2025-11), Optimal Layout Practices for Low-Ohmic Current Sense Resistors in Parallel.
- Bourns, CSS2H-2512 datasheet, TCR/tolerance/inductance/power tables.
- Analog Devices, Measurement Techniques for Industrial Motion Control; current measurement location and PWM-synchronized DC-link reconstruction.
- IEC 61800-5-1:2022, corrected version 2025-12; IEC 61800-5-2:2016+AMD1:2026. Public scope/catalogue only; no full normative clause compliance review.
