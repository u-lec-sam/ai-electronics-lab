# 16장 — PMSM FOC 전류 루프의 이산 설계와 튜닝

> **핵심 질문:** 측정된 \(i_d,i_q\)를 목표값으로 추종시키는 PI 전류 제어기를 어떻게 유도하고, 인버터의 전압 한계·계산 지연·모델 오차 안에서도 포화와 불안정에 빠지지 않게 만들까?

## 안전·범위·선수 지식

- 선수 지식: 06장 PMSM 전기 모델, 07장 2레벨 인버터/SVPWM, 08장 Clarke/Park와 FOC, 10장 PWM/ADC/ISR timing, 11장 robust C/fault latch, 13장 V&V evidence, 14장 gate-driver inhibit, 15장 current sensing/validity.
- 모든 숫자는 **가상 계산 예제**다. 실제 모터 데이터시트·식별값·DC bus 범위·전류 한계·PWM/ADC 타이밍·MCU/SDK 설정이 아니다.
- AEL-002의 \(R_s,L_d,L_q,\psi_f\), pole pairs, current envelope, bus voltage, switching frequency, controller period, ADC aperture, computation time, PWM update mode, voltage margin, current-loop bandwidth, PI gains는 전부 **TBD**다.
- 수학적 유도와 host/SIL 검증 계획을 제공한다. target firmware build, simulation execution, HIL, motor test, physical measurement 또는 safety certification을 수행했다고 주장하지 않는다.
- **NO STACK / NO POWER.**

## 학습 목표

1. PMSM d/q 전압식을 기준으로 두 축의 결합 plant와 decoupling 항을 유도한다.
2. \(G_d(s)=1/(L_ds+R_s)\), \(G_q(s)=1/(L_qs+R_s)\)에 대한 연속 PI와 delay-aware 초기 튜닝값을 계산한다.
3. Forward Euler, Backward Euler, Tustin의 차분식을 직접 유도하고 차이를 설명한다.
4. feed-forward/decoupling의 부호를 검산하고 parameter mismatch의 영향을 정량화한다.
5. SVPWM의 d/q voltage-vector limit, DC bus variation, axis priority 및 vector scaling을 구현 가능한 규칙으로 바꾼다.
6. back-calculation/conditional-integration anti-windup, reset, invalid-sample freeze를 설계한다.
7. sensor/filter/ADC/compute/PWM update delay를 합산하고 phase margin 및 bandwidth 한계를 계산한다.
8. \(R_s,L_d,L_q,\psi_f,V_{dc}\) 불확도에 대한 corner sweep과 host/SIL 검증을 정의한다.

---

## 1. 좌표계·부호·PMSM 모델 계약

이 장은 08장의 진폭 불변 Clarke/Park 규약을 따른다. \(d\)축은 PM 자속 방향, \(q\)축은 전기각 기준 \(+90^\circ\) 방향이다. 양의 상전류 방향은 인버터에서 모터로 흐르는 방향이다. 다른 Park 부호·정규화 SDK를 쓰면 feed-forward와 torque 부호를 다시 유도해야 한다.

| 기호 | 정의 | 단위 |
|---|---|---|
| \(i_d,i_q\) | rotor-frame stator current | A |
| \(v_d,v_q\) | rotor-frame stator voltage | V |
| \(R_s\) | stator phase resistance, model convention | \(\Omega\) |
| \(L_d,L_q\) | d/q incremental inductance | H |
| \(\psi_f\) | PM flux linkage | Wb = V·s |
| \(\omega_e\) | electrical angular speed | rad/s |
| \(p\) | pole-pair count | dimensionless |
| \(T_s\) | current-controller sample period | s |
| \(T_d\) | equivalent sample-to-actuation delay | s |

PMSM flux linkages:

\[
\psi_d=L_di_d+\psi_f,\qquad \psi_q=L_qi_q
\]

Stator voltage equations:

\[
v_d=R_si_d+L_d\frac{di_d}{dt}-\omega_eL_qi_q
\]

\[
v_q=R_si_q+L_q\frac{di_q}{dt}+\omega_e(L_di_d+\psi_f)
\]

따라서 상태 방정식은

\[
\frac{di_d}{dt}=\frac{v_d-R_si_d+\omega_eL_qi_q}{L_d}
\]

\[
\frac{di_q}{dt}=\frac{v_q-R_si_q-\omega_eL_di_d-\omega_e\psi_f}{L_q}
\]

중요한 점:
- \(d\)축 전류 변화에는 \(+\omega_eL_qi_q\) 항이 들어간다.
- \(q\)축 전류 변화에는 \(-\omega_eL_di_d-\omega_e\psi_f\) 항이 들어간다.
- \(\omega_e=p\omega_m\)이다. 기계각속도를 전기각속도로 잘못 넣으면 극쌍수 배수의 오차가 발생한다.
- 이 모델은 포화·교차포화·철손·고주파 skin effect·deadtime·PWM 비선형성·온도 변화·센서 지연을 생략한 제어 설계용 기본 모델이다.

전류 루프를 튜닝할 때 \(\omega_e\)가 제어 한 주기 동안 거의 일정하다고 보는 operating-point approximation을 쓴다. 고속/급가속에서 이 가정이 무너지면 feed-forward와 plant의 time-varying coupling을 별도로 검증한다.

## 2. Decoupling과 feed-forward 유도

원하는 d/q 전류 동역학을 독립 RL plant로 만들기 위해 PI 출력 \(u_d,u_q\)를 다음과 같이 정의한다.

\[
v_d^*=u_d-\omega_eL_qi_q
\]

\[
v_q^*=u_q+\omega_eL_di_d+\omega_e\psi_f
\]

이를 PMSM 전압식에 대입하면

\[
L_d\frac{di_d}{dt}=u_d-R_si_d
\]

\[
L_q\frac{di_q}{dt}=u_q-R_si_q
\]

따라서 이상적인 decoupled plant는

\[
G_d(s)=\frac{I_d(s)}{U_d(s)}=\frac{1}{L_ds+R_s}
\]

\[
G_q(s)=\frac{I_q(s)}{U_q(s)}=\frac{1}{L_qs+R_s}
\]

가 된다. PI controller가 보상해야 하는 것은 각각의 RL plant이며, 교차항과 PM 역기전력은 feed-forward로 먼저 상쇄한다.

**부호 sanity check:** \(i_q>0,\omega_e>0\)일 때 d축 plant에 나타나는 coupling은 \(+\omega_eL_qi_q\)이므로 이를 상쇄하려면 \(v_d^*\)에 \(-\omega_eL_qi_q\)를 더해야 한다. \(i_d=0,\omega_e>0,\psi_f>0\)이면 q축 역기전력은 \(+\omega_e\psi_f\)이므로 이를 선보상하려면 \(v_q^*\)에 \(+\omega_e\psi_f\)가 들어간다.

### 2.1 Feed-forward가 완전한 decoupling이 아닌 이유

실제 제어기는 추정 파라미터 \(\hat L_d,\hat L_q,\hat\psi_f\)를 사용한다. d축 잔류 교차항 크기는

\[
|\Delta v_{d,cpl}|=|\omega_e(\hat L_q-L_q)i_q|
\]

q축 잔류항은

\[
\Delta v_{q,cpl}=\omega_e(\hat L_d-L_d)i_d+
\omega_e(\hat\psi_f-\psi_f)
\]

로 평가한다.

- \(\hat\psi_f\) 오차는 속도에 비례하는 q축 voltage bias를 만든다.
- inductance 오차는 current·speed에 비례하는 cross-coupling residual을 만든다.
- \(R_s\) 오차는 PI plant의 pole/zero cancellation과 저속 전압 강하 예측을 바꾼다.
- feed-forward는 feedback PI를 대체하지 않는다. 파라미터가 불확실하거나 speed estimate가 invalid이면 feed-forward를 제한하거나 보수적으로 줄여야 한다.
- feed-forward를 잘못된 좌표계 각도·상순서·극성에 적용하면 오차를 상쇄하는 대신 증폭할 수 있다.

## 3. 연속시간 PI 유도

두 축의 decoupled plant를 일반형으로 쓴다.

\[
G(s)=\frac{1}{Ls+R}
\]

Parallel PI:

\[
C(s)=K_p+\frac{K_i}{s}
=K_p\frac{s+K_i/K_p}{s}
\]

PI zero를 plant pole과 일치시키는 ideal cancellation 조건은

\[
\frac{K_i}{K_p}=\frac{R}{L}
\]

이다. 그러면

\[
C(s)G(s)=
K_p\frac{s+R/L}{s}\frac{1}{Ls+R}
=\frac{K_p}{Ls}
\]

가 되어 이상 모델에서 plant의 \(R/L\) pole이 상쇄된다. 이 결과는 정확한 \(R,L\), 무시 가능한 delay, 충분한 voltage headroom, 선형 동작을 가정한다. 실제 시스템에서 완전한 pole-zero cancellation을 보장하는 공식은 아니다.

### 3.1 Delay-aware magnitude-optimum 초기값

총 지연을 \(T_d\)로 근사하고, 이상적인 delay-free open-loop가 \(K_p/(Ls)\)라면 delay를 포함한 open-loop는

\[
L_o(s)\approx\frac{K_p}{Ls}e^{-sT_d}
\]

이다. magnitude crossover는 \(\omega_c=K_p/L\)이고, phase는 crossover에서 \(-90^\circ-\omega_cT_d\)다. magnitude-optimum 초기값

\[
K_p=\frac{L}{2T_d},\qquad
K_i=\frac{R}{2T_d}
\]

을 선택하면

\[
\omega_c=\frac{1}{2T_d},\qquad
f_c=\frac{1}{4\pi T_d}
\]

이고, idealized phase margin은

\[
PM\approx90^\circ-0.5\text{ rad}\times\frac{180^\circ}{\pi}
\approx61.35^\circ
\]

이다.

이 식은 **초기 튜닝 기준**이다. 실제 phase margin은 ZOH, PWM update mode, sensor/filter poles, computation jitter, discrete-time frequency warping, current-loop cross-coupling, saturation, deadtime, parameter variation을 포함한 loop transfer function에서 다시 계산해야 한다.

d/q 축별 초기 gain:

\[
K_{p,d}=\frac{L_d}{2T_d},\quad
K_{i,d}=\frac{R_s}{2T_d}
\]

\[
K_{p,q}=\frac{L_q}{2T_d},\quad
K_{i,q}=\frac{R_s}{2T_d}
\]

단위 검산: \(K_p=L/T_d\)는 H/s = \(\Omega\) = V/A, \(K_i=R/T_d\)는 \(\Omega/s\) = V/(A·s)다.

### 3.2 대역폭 기준으로 설계할 때

delay가 충분히 작고 target current-loop angular bandwidth \(\omega_{ci}\)를 설계 변수로 선택하는 경우, pole cancellation 기반으로

\[
K_p=L\omega_{ci},\qquad K_i=R\omega_{ci}
\]

를 얻는다. 단, \(\omega_{ci}\)를 무작정 높이지 않는다. \(T_d\), sensor bandwidth, PWM frequency, ADC timing, noise, current ripple, voltage saturation과 robust margin이 허용하는 범위 안에서 정한다. \(f_{ci}\)가 PWM frequency의 일정 비율 이하여야 한다는 단일 보편 규칙으로 안정성을 보장할 수는 없다.

## 4. PI 이산화: Forward Euler, Backward Euler, Tustin

\(e[k]=i^*[k]-i[k]\), integral state \(x[k]\), controller output \(u[k]\)라 둔다.

\[
u[k]=K_pe[k]+x[k]
\]

### 4.1 Forward Euler (explicit)

\[
\frac{1}{s}\approx\frac{T_s}{z-1}
\]

이전 sample의 error를 적분:

\[
x[k]=x[k-1]+K_iT_se[k-1]
\]

증분형:

\[
u[k]=u[k-1]+K_p(e[k]-e[k-1])+K_iT_se[k-1]
\]

- 장점: 계산량과 구현이 단순하다.
- 단점: explicit integrator의 discrete stability/phase 특성이 불리할 수 있고, indexing과 한 sample 지연을 명확히 해야 한다.
- saturating actuator에서는 anti-windup 없이는 누적 오차가 커질 수 있다.

### 4.2 Backward Euler (implicit)

\[
\frac{1}{s}\approx\frac{T_sz}{z-1}
=\frac{T_s}{1-z^{-1}}
\]

현재 error를 적분:

\[
x[k]=x[k-1]+K_iT_se[k]
\]

\[
u[k]=u[k-1]+K_p(e[k]-e[k-1])+K_iT_se[k]
\]

- 안정성 면에서 보수적이며 구현이 간단하다.
- 현재 sample error를 사용하므로 output calculation order와 anti-windup update order를 고정해야 한다.
- MathWorks PMSM Current Controller R2026b는 first-order simplicity/stability를 이유로 backward Euler form을 명시한다. 이것은 특정 block implementation 설명이지 모든 drive에 대한 최선의 선택 선언이 아니다.

### 4.3 Tustin (bilinear)

\[
\frac{1}{s}\approx\frac{T_s}{2}\frac{1+z^{-1}}{1-z^{-1}}
\]

\[
x[k]-x[k-1]=\frac{K_iT_s}{2}(e[k]+e[k-1])
\]

따라서

\[
u[k]=u[k-1]+
\left(K_p+\frac{K_iT_s}{2}\right)e[k]
+\left(-K_p+\frac{K_iT_s}{2}\right)e[k-1]
\]

- 연속 안정성을 단위원 내부로 보존하는 bilinear mapping이다.
- frequency warping이 있으므로 높은 normalized frequency에서는 prewarping이나 직접 discrete design을 고려한다.
- 계산/상태가 forward/backward Euler와 다르므로 host golden vectors를 별도로 만든다.

| 방법 | 적분 입력 | 장점 | 주의점 |
|---|---|---|---|
| Forward Euler | \(e[k-1]\) | 최소 연산 | explicit, sample indexing/안정성 |
| Backward Euler | \(e[k]\) | 보수적·간단 | 현재 sample 및 anti-windup 순서 |
| Tustin | \((e[k]+e[k-1])/2\) | frequency response 근사 우수 | 계수·연산 증가, warping |

**중요:** 서로 다른 discretization의 계수와 state update를 혼합하지 않는다. Controller form, saturation point, anti-windup correction location, reset semantics를 코드·시험 벡터·parameter version에 명시한다.

## 5. Voltage vector saturation과 modulation limit

PI와 feed-forward를 합친 unsaturated voltage를

\[
\mathbf v_{dq,u}=
\begin{bmatrix}v_{d,u}\\v_{q,u}\end{bmatrix}
\]

라고 한다. 2-level VSI의 linear SVPWM에서 진폭 불변 Clarke/Park convention의 ideal phase-neutral peak vector limit은

\[
V_{lim,ideal}=\frac{V_{dc}}{\sqrt3}
\]

이다. 실제 limit은 deadtime, minimum pulse, bus ripple, device drop, modulation implementation, overmodulation policy, required reserve에 따라 더 낮아질 수 있다.

### 5.1 Vector scaling (d/q 비율 보존)

\[
V_u=\sqrt{v_{d,u}^2+v_{q,u}^2}
\]

\[
\gamma=\min\left(1,\frac{V_{lim}}{\max(V_u,\epsilon)}\right)
\]

\[
v_{d,sat}=\gamma v_{d,u},\qquad
v_{q,sat}=\gamma v_{q,u}
\]

이는 전압 벡터 방향을 유지한다. \(\epsilon\)은 0 나눗셈 방지용 numerical guard이며 물리적 minimum voltage가 아니다.

### 5.2 Axis priority

특정 operating mode에서 q축 torque voltage 또는 d축 flux/field-weakening voltage에 우선권이 필요할 수 있다. 예를 들어 q-axis 우선이면 먼저

\[
v_{q,sat}=\operatorname{clip}(v_{q,u},-V_{lim},V_{lim})
\]

\[
V_{d,avail}=\sqrt{\max(0,V_{lim}^2-v_{q,sat}^2)}
\]

\[
v_{d,sat}=\operatorname{clip}(v_{d,u},-V_{d,avail},V_{d,avail})
\]

로 제한한다. d-axis 우선은 역할을 바꾼다. Axis priority는 torque/flux objective와 operating region에 맞춰 요구사항으로 결정해야 하며 무조건 q 우선이 정답은 아니다.

### 5.3 DC bus variation

\[
V_{lim}(k)=m\frac{V_{dc,meas}(k)}{\sqrt3}
\]

여기서 \(0<m<1\)은 design reserve. DC bus measurement가 stale/invalid이면 마지막 값을 무한정 신뢰하지 말고 정의된 conservative fallback/fault policy를 사용한다. \(m\), Vdc range와 ADC scale은 AEL-002 TBD다.

### 5.4 Saturation을 PWM 후단에서만 처리하면 안 되는 이유

- PI가 만든 요청 전압과 실제 적용 전압이 달라진다.
- integral state는 unsaturated command와 실제 plant input 차이를 누적해 windup할 수 있다.
- SVPWM duty clamp, minimum pulse, deadtime compensation이 후단에 있으면 PI가 보는 saturation residual이 실제 actuator residual과 달라질 수 있다.
- anti-windup은 가능하면 **실제 적용 가능한 d/q voltage estimate**를 기준으로 feedback한다. Inverse modulation/voltage reconstruction의 정확도와 update timestamp도 명시한다.

## 6. Anti-windup, integrator reset 및 invalid data

### 6.1 Back-calculation

Parallel PI의 integral state가 voltage 단위인 경우:

\[
u_u[k]=K_pe[k]+x[k]
\]

\[
u_s[k]=\operatorname{sat}(u_u[k]+\mathrm{FF})
\]

\[
x[k+1]=x[k]+K_iT_se[k]
+\frac{T_s}{T_t}(u_s[k]-u_u[k])
\]

\(T_t\)는 tracking time constant이며 \(K_{aw}=1/T_t\)다. Feed-forward가 saturation 앞/뒤 어느 지점에 포함되는지 구현 정의를 고정하고, anti-windup residual은 controller contribution과 actuator-applied command 사이의 차이로 일관되게 구성한다. Vector saturation이면 d/q residual을 함께 사용한다.

### 6.2 Conditional integration

포화 중 error가 더 깊은 포화를 유발하는 방향이면 integrator update를 막는다. Error가 포화에서 빠져나오도록 돕는 방향이면 적분을 허용한다. Vector limiter에서는 d/q 각 축을 독립 clip하는 방식이 vector direction을 깨뜨릴 수 있으므로, vector saturation residual 또는 constrained integrator update를 권장한다.

### 6.3 Reset/hold 정책

- Drive disabled, startup, shutdown, mode transition: integrator reset 또는 bumpless transfer를 정의한다.
- Current sample invalid/stale/saturated: 잘못된 값을 PI에 넣지 않는다. 정해진 정책으로 integrator freeze/reset, voltage command safe behavior, fault latch를 적용한다.
- PWM update miss / deadline overrun: 이전 command를 무기한 재사용하지 않는다. system fault policy에 따라 output inhibit 요청 및 기록.
- Current reference step: torque/current slew limiter와 current limit supervisor가 PI 앞에서 제한한다.
- Fault clear: 통신 명령만으로 integrator와 drive fault를 clear/re-arm하지 않는다. 11–14장의 supervised explicit acknowledgement/re-arm 계약을 유지한다.

## 7. ADC-to-PWM delay와 phase margin

총 지연은 CPU 실행 시간 하나가 아니다.

\[
T_d=T_{sensor}+T_{AFE}+T_{ADC}+T_{transfer}
+T_{compute}+T_{write}+T_{PWM}+T_{switch}
\]

실제 일부 항목은 서로 겹치거나 같은 지연을 다른 이름으로 표현할 수 있으므로 timing diagram으로 **중복 합산하지 않는다**. Chapter 10의 event chain과 Chapter 15의 analog filter/sensor delay를 기준으로 sample aperture부터 실제 inverter voltage update까지 추적한다.

- sensor/AFE delay: sensor bandwidth, analog pole, digital filter, group delay.
- ADC: aperture, conversion complete, result visibility, DMA transfer.
- compute: interrupt latency, control calculation, worst-case execution time.
- PWM: shadow register write deadline, shadow-load event, carrier update semantics, single/double update.
- power stage: driver propagation, deadtime and switching transition (small-signal model applicability).

Single-rate triangular PWM update에서 sample phase와 compute completion에 따라 control delay가 \(0.5T_s,T_s,1.5T_s\)처럼 달라질 수 있다. Imperix PN142는 sampling, acquisition, processing, write, modulator delay를 분리해 예를 든다. 이 값들을 AEL-002 timing으로 복사하지 않는다.

### 7.1 Delay phase

Pure delay의 phase contribution:

\[
\phi_d(\omega)=-\omega T_d\quad[\mathrm{rad}]
\]

\[
\phi_d[^\circ]=-360^\circ fT_d
\]

예를 들어 \(f_c=1.0\,\mathrm{kHz}\), \(T_d=75\,\mu s\)이면 delay phase는 \(-27.0^\circ\)다. \(T_d\)가 125 µs이면 같은 crossover에서 \(-45^\circ\)다. 다른 plant/filter phase lag를 더해야 실제 phase margin이 된다.

### 7.2 Timing jitter

지연의 평균만으로 충분하지 않다. \(T_d\in[T_{d,min},T_{d,max}]\)이면 worst-case phase lag는 최대 delay에서 계산한다. Jitter가 random이든 bounded deterministic이든 sample-to-actuation timestamp 분포를 보존하고 WCET/deadline을 따로 검증한다.

## 8. 파라미터 불확도와 robust tuning

실제 motor parameter는 operating point에 따라 변한다.

- \(R_s\): winding temperature에 따라 증가한다.
- \(L_d,L_q\): current magnitude, rotor position, saturation, cross-saturation에 따라 달라질 수 있다.
- \(\psi_f\): magnet temperature와 operating condition에 따라 달라질 수 있다.
- \(V_{dc}\): source impedance, ripple, regen, supply range에 따라 변한다.
- \(T_d\): PWM update phase, compute load, filtering, ADC/DMA route에 따라 변한다.

### 8.1 Corner set

최소한 아래 조합을 평가한다.

| Parameter | Example sweep only | Main effect |
|---|---|---|
| \(R_s\) | 0.8, 1.0, 1.2 × nominal | electrical pole, resistive drop, PI zero mismatch |
| \(L_d,L_q\) | 0.8, 1.0, 1.2 × nominal | current plant gain/time constant, decoupling residual |
| \(\psi_f\) | 0.9, 1.0, 1.1 × nominal | q-axis back-EMF feed-forward error |
| \(V_{dc}\) | min, nominal, max | available voltage vector |
| \(T_d\) | measured min, nominal, worst | phase margin and crossover |
| \(\omega_e\) | min, nominal, max operating points | coupling and back-EMF |
| sensor gain/offset | calibrated tolerance corners | current feedback error/noise |

The multipliers are educational sweep suggestions, not AEL tolerance or environmental limits. If measured/model uncertainty is asymmetric, use evidence-based min/max rather than symmetric percentages.

### 8.2 Robust evaluation outputs

For each corner, store:
- open-loop gain/phase and crossover;
- phase/gain margin and delay phase;
- closed-loop current step overshoot/settling and tracking error;
- noise gain and current ripple;
- vector saturation duration and integrator state;
- voltage headroom and modulation clipping;
- feed-forward residual;
- worst-case CPU/WCET and PWM deadline margin;
- invalid sensor/current sample reaction and fault latency.

A nominally excellent response is not robust if one plausible hot-resistance/high-speed/low-bus corner causes sustained saturation or negative phase margin.

---

## 9. 완전 풀이 가상 설계 예제

**가정:** 아래 수치는 계산법 설명만을 위한 임의 예제다. 실제 AEL-002 모터·전원·전류 제한·PWM 주기·제어 이득과 무관하다.

\[
R_s=0.35\,\Omega,\quad L_d=0.80\,mH,\quad
L_q=1.00\,mH,\quad \psi_f=0.035\,Wb
\]

\[
T_s=50\,\mu s,\quad T_d=75\,\mu s,\quad
V_{dc}=48\,V,\quad m=0.90
\]

### Example 1 — d/q PI gains

\[
K_{p,d}=\frac{0.0008}{2(75\times10^{-6})}
=\frac{0.0008}{0.00015}=5.333\,V/A
\]

\[
K_{p,q}=\frac{0.0010}{0.00015}=6.667\,V/A
\]

\[
K_{i,d}=K_{i,q}=\frac{0.35}{0.00015}
=2333.3\,V/(A\cdot s)
\]

Plant time constants:

\[
\tau_d=\frac{L_d}{R_s}=\frac{0.0008}{0.35}=2.286\,ms
\]

\[
\tau_q=\frac{L_q}{R_s}=\frac{0.0010}{0.35}=2.857\,ms
\]

Idealized crossover:

\[
\omega_c=\frac{1}{2T_d}=6666.7\,rad/s
\]

\[
f_c=\frac{6666.7}{2\pi}=1061\,Hz
\]

Idealized delay-only phase margin:

\[
PM\approx90^\circ-0.5\frac{180^\circ}{\pi}=61.35^\circ
\]

**해석:** 이 값은 \(e^{-sT_d}\)만 추가한 pole-cancelled ideal model 결과다. 실제 loop PM이라고 부르면 안 된다.

### Example 2 — Tustin coefficients

\[
K_iT_s/2=2333.3(50\times10^{-6})/2=0.05833
\]

d축:

\[
b_{0,d}=K_{p,d}+K_iT_s/2=5.3917
\]

\[
b_{1,d}=-K_{p,d}+K_iT_s/2=-5.2750
\]

q축:

\[
b_{0,q}=6.7250,\qquad b_{1,q}=-6.6083
\]

따라서 \(u[k]=u[k-1]+b_0e[k]+b_1e[k-1]\)이며, 실제 구현에서는 saturation과 anti-windup state를 별도로 유지한다.

Backward Euler의 integral increment는 \(K_iT_s=0.11667\)이고, d축 incremental coefficients는 \(b_0=5.4500,b_1=-5.3333\)이다. Tustin 계수와 섞어 쓰지 않는다.

### Example 3 — decoupling voltage

가상 operating point:

\[
\omega_e=600\,rad/s,\quad i_d=-1\,A,\quad i_q=4\,A
\]

\[
v_{d,FF}=-\omega_eL_qi_q
=-600(0.001)(4)=-2.40\,V
\]

\[
v_{q,FF}=\omega_eL_di_d+\omega_e\psi_f
=600(0.0008)(-1)+600(0.035)
=-0.48+21=20.52\,V
\]

**검산:** \(L\cdot A\cdot rad/s\)는 H·A/s = V이며 \(\omega_e\psi_f\)도 V다. \(v_q\)의 PM back-EMF가 q축 전압 여유 대부분을 차지할 수 있음을 보여주는 예다.

### Example 4 — SVPWM voltage circle

\[
V_{lim}=m\frac{V_{dc}}{\sqrt3}
=0.9\frac{48}{1.73205}=24.942\,V
\]

PI+feed-forward가 만든 가상 요청이

\[
v_{d,u}=18\,V,\quad v_{q,u}=20\,V
\]

라면

\[
V_u=\sqrt{18^2+20^2}=\sqrt{724}=26.907\,V
\]

\[
\gamma=24.942/26.907=0.9270
\]

\[
v_{d,sat}=16.686\,V,\qquad v_{q,sat}=18.540\,V
\]

벡터 크기는 \(24.942\,V\)로 제한되고 방향은 유지된다.

### Example 5 — back-calculation anti-windup

가상 tracking time constant \(T_t=2\,ms\), \(T_s=50\,\mu s\)라면

\[
K_{aw}=1/T_t=500\,s^{-1}
\]

\[
\alpha_{aw}=T_s/T_t=0.025
\]

\[
\Delta x_d=0.025(16.686-18)=-0.0329\,V
\]

\[
\Delta x_q=0.025(18.540-20)=-0.0365\,V
\]

다음 integral update에 saturation residual이 반영되어 unsaturated request 방향으로 계속 누적되는 windup을 줄인다. \(T_t\)는 튜닝 변수이며 이 예의 2 ms를 AEL-002에 복사하지 않는다.

### Example 6 — delay phase

\[
\phi_d=-360^\circ fT_d
=-360^\circ(1000)(75\times10^{-6})
=-27^\circ
\]

\(T_d=125\,\mu s\)라면 \(-45^\circ\)다. 1 kHz crossover에서 delay가 50 µs 늘면 phase margin을 추가로 18° 소모한다.

### Example 7 — feed-forward uncertainty

\(\psi_f\) nominal \(0.035\,Wb\), hypothetical error ±10%, \(\omega_e=600\,rad/s\):

\[
|\Delta v_{q,\psi}|=\omega_e|\Delta\psi_f|
=600(0.0035)=2.10\,V
\]

\(L_q\) error ±10%, \(i_q=4A\)라면 d-axis coupling residual magnitude:

\[
|\Delta v_{d,Lq}|=600(0.0001)(4)=0.24\,V
\]

\(L_d\) error ±10%, \(|i_d|=1A\)라면 q-axis inductive residual:

\[
|\Delta v_{q,Ld}|=600(0.00008)(1)=0.048\,V
\]

이는 한 번에 하나의 오차를 바꾼 민감도 계산이며 total worst-case는 부호·상관관계를 포함해 corner별로 합산한다.

### Example 8 — DC bus variation

같은 \(m=0.9\)에서:

| \(V_{dc}\) | \(V_{lim}=0.9V_{dc}/\sqrt3\) |
|---:|---:|
| 43.2 V | 22.448 V |
| 48.0 V | 24.942 V |
| 52.8 V | 27.436 V |

저전압 bus corner에서 고속 back-EMF feed-forward가 voltage circle을 더 빨리 소진한다. current reference가 정상이어도 전압 포화로 tracking이 불가능해질 수 있다.

---

## 10. 연습문제와 전체 풀이

### 문제 1 — q축 PI gain

\(L_q=0.75\,mH\), \(R_s=0.42\,\Omega\), \(T_d=60\,\mu s\)인 가상 plant의 magnitude-optimum 초기 gain을 계산하라.

**풀이**

\[
K_{p,q}=0.00075/(120\times10^{-6})=6.25\,V/A
\]

\[
K_{i,q}=0.42/(120\times10^{-6})=3500\,V/(A\cdot s)
\]

### 문제 2 — target bandwidth에서 gain

\(L=1.2\,mH\), \(R=0.3\,\Omega\), \(f_{ci}=800\,Hz\)를 가정한다. pole cancellation 기반 \(K_p,K_i\)를 구하라.

**풀이**

\[
\omega_{ci}=2\pi(800)=5026.55\,rad/s
\]

\[
K_p=L\omega_{ci}=0.0012(5026.55)=6.032\,V/A
\]

\[
K_i=R\omega_{ci}=0.3(5026.55)=1508.0\,V/(A\cdot s)
\]

이 값은 delay 검토 전 후보이며, \(T_d\)가 커서 목표 crossover에서 phase margin이 부족하면 bandwidth를 낮춘다.

### 문제 3 — Tustin 계수

\(K_p=4.0\), \(K_i=1200\), \(T_s=100\,\mu s\)일 때 incremental Tustin 계수를 구하라.

**풀이**

\[
K_iT_s/2=1200(0.0001)/2=0.06
\]

\[
b_0=4.06,\quad b_1=-3.94
\]

따라서 \(u[k]=u[k-1]+4.06e[k]-3.94e[k-1]\)다.

### 문제 4 — decoupling 부호

\(\omega_e=400\,rad/s\), \(L_q=0.8\,mH\), \(i_q=5A\)에서 d축 feed-forward를 구하라.

**풀이**

\[
v_{d,FF}=-400(0.0008)(5)=-1.6\,V
\]

d축 plant의 \(+\omega_eL_qi_q\)를 상쇄하므로 음수다.

### 문제 5 — PM back-EMF

\(\omega_e=500\,rad/s\), \(\psi_f=0.04\,Wb\)일 때 q축 PM feed-forward를 구하라.

**풀이**

\[
v_{q,PM}=\omega_e\psi_f=500(0.04)=20\,V
\]

단위는 rad/s·Wb = V다.

### 문제 6 — vector saturation

\(V_{lim}=20V\), \(v_{d,u}=12V\), \(v_{q,u}=16V\)일 때 vector scaling 결과를 구하라.

**풀이**

\[
V_u=\sqrt{144+256}=20V
\]

이미 한계와 같으므로 \(\gamma=1\), 출력은 \(12V,16V\)다.

### 문제 7 — voltage priority

\(V_{lim}=24V\), q축 우선 \(v_{q,u}=20V\), \(v_{d,u}=15V\)일 때 제한된 d축 값을 구하라.

**풀이**

\[
V_{d,avail}=\sqrt{24^2-20^2}=\sqrt{176}=13.266V
\]

\[
v_{d,sat}=13.266V
\]

q축은 20 V로 유지하고 d축만 제한한다.

### 문제 8 — delay phase

\(f=1.5kHz\), \(T_d=80\,\mu s\)일 때 delay phase를 계산하라.

**풀이**

\[
\phi=-360(1500)(80\times10^{-6})=-43.2^\circ
\]

이는 전체 plant phase margin이 아니라 pure delay가 소모하는 위상이다.

### 문제 9 — flux mismatch

\(\omega_e=800rad/s\), flux linkage uncertainty가 ±5 mWb일 때 q축 voltage residual magnitude를 구하라.

**풀이**

\[
|\Delta v_q|=\omega_e|\Delta\psi|=800(0.005)=4V
\]

속도가 높을수록 flux estimation error가 voltage headroom에 크게 반영된다.

### 문제 10 — resistance temperature corner

가상 \(R_s=0.4\Omega\)가 hot corner에서 25% 증가한다. 실제 \(R_s\)와 기존 \(K_i\) cancellation 가정의 영향을 설명하라.

**풀이**

\[
R_{hot}=0.4(1.25)=0.5\Omega
\]

기존 nominal \(K_i/K_p=R_{nom}/L\)는 hot plant의 pole \(R_{hot}/L\)와 일치하지 않는다. 따라서 pole-zero cancellation이 완전하지 않고, 저항성 voltage drop 및 loop response가 달라진다. 실제 튜닝은 hot/cold corner에서 재평가한다.

### 문제 11 — DC bus corner

\(V_{dc}=36V\), \(m=0.92\)에서 ideal SVPWM circle에 reserve를 적용한 한계를 계산하라.

**풀이**

\[
V_{lim}=0.92(36)/\sqrt3=19.122V
\]

정확한 implementation에서는 bus measurement error, deadtime, minimum pulse와 modulation policy를 더 반영한다.

### 문제 12 — invalid sample

current ADC sample이 stale/invalid인데 이전 정상 값을 PI에 반복 입력하면 어떤 문제가 생기는가?

**풀이**

이전 전류를 현재 전류로 오인하여 error·Park angle·feed-forward가 시간적으로 어긋난다. 실제 전류가 바뀌어도 제어기는 변화를 보지 못하고 잘못된 전압을 계속 요청할 수 있다. sample validity/timestamp를 control interface에 포함하고 invalid 시 integrator update와 PWM request를 명시된 safe policy로 전환하며 fault를 기록한다. zero current로 대체해 정상 데이터처럼 위장하지 않는다.

---

## 11. 구현 가능한 제어 task 의사코드

다음은 구조 설명용 의사코드이며 특정 MCU/SDK용 컴파일 가능한 코드가 아니다. 실제 code review에서는 11장의 fixed-point range, overflow, atomicity, DMA ownership 및 ISR budget을 적용한다.

~~~text
on_current_control_tick:
    sample = acquire_current_sample()
    if !sample.valid || sample.stale || sample.saturated:
        freeze_or_reset_integrators(per_fault_policy)
        request_defined_safe_output()
        latch_measurement_fault()
        record_timestamp_and_status()
        return

    theta = validated_electrical_angle_at_sample_aperture()
    idq = park(clarke(sample.ia, sample.ib, sample.ic), theta)

    refs = current_reference_supervisor()
    error_d = refs.id - idq.id
    error_q = refs.iq - idq.iq

    vd_pi = pi_d.update(error_d, applied_voltage_feedback, enable=true)
    vq_pi = pi_q.update(error_q, applied_voltage_feedback, enable=true)

    vd_ff = -omega_e * Lq_hat * idq.iq
    vq_ff =  omega_e * (Ld_hat * idq.id + psi_hat)

    vd_unsat = vd_pi + vd_ff
    vq_unsat = vq_pi + vq_ff

    v_limit = validated_bus_voltage_limit(vdc, modulation_policy)
    vdq_sat = vector_or_priority_limit(vd_unsat, vq_unsat, v_limit)

    pi_d.apply_anti_windup(vdq_sat.d - vd_unsat)
    pi_q.apply_anti_windup(vdq_sat.q - vq_unsat)

    duty = inverse_park_and_svpwm(vdq_sat, theta)
    if !pwm_shadow_deadline_available():
        latch_control_deadline_fault()
        request_defined_safe_output()
        return

    publish_pwm_shadow(duty)
    record_sample_to_apply_timestamp()
~~~

설계상 주의:
- anti-windup은 실제 actuator에 적용되는 voltage와 일치하는 saturation residual을 사용해야 한다.
- invalid current/angle/bus data에 대한 각기 다른 fault policy를 정의한다.
- deadline check는 PWM register write 이후가 아니라 shadow-load deadline 전에 이뤄져야 한다.
- request_defined_safe_output()의 구체 동작은 independent hardware inhibit/gate-driver safety architecture와 함께 검토한다. 이 pseudocode는 hardware safety function을 증명하지 않는다.
- 파라미터는 runtime update 시 range, version, CRC, cross-field validation을 거쳐 atomic snapshot으로 전달한다.

## 12. Host/SIL 검증 전략

### 12.1 Host deterministic unit tests

- Continuous plant derivative equation sign tests.
- d/q decoupling sign and unit tests.
- Euler/Backward Euler/Tustin golden-vector tests.
- PI reset, enable, freeze, saturation, anti-windup recurrence tests.
- vector scaling invariant: \(\|\mathbf v_{sat}\|\le V_{lim}\).
- axis priority invariant: priority axis remains within scalar limit and secondary axis fits remaining circle.
- finite/NaN/Inf/range checks; division-by-zero and square-root guard.
- current sample validity, timestamp monotonicity and stale rejection.
- coefficient update versioning and atomic parameter snapshot.
- fixed-point overflow/saturation and rounding tests if target uses fixed point.

### 12.2 SIL model tests

SIL plant should include:
- d/q PMSM electrical equations, mechanical speed trajectory and electrical angle;
- PWM/ZOH and sample-to-actuation delay;
- sensor gain/offset/noise, analog filter and quantization;
- voltage circle, DC bus ripple, deadtime/voltage drop approximation;
- parameter sweeps and operating-point changes;
- current/voltage limit supervisor and invalid sensor fault path.

SIL is a model-level result. It does not validate actual board parasitics, gate driver, ADC pin mux, sensor CMTI, thermal performance, physical current limits or STO.

### 12.3 Acceptance criteria template

| ID | Requirement | Test / metric | Evidence required |
|---|---|---|---|
| FOC-IL-001 | d/q current loop stable over approved parameter corners | gain/phase margin, bounded response | model hash, parameter set, Bode data |
| FOC-IL-002 | current step follows approved response envelope | overshoot, settling, steady error | test vector and waveform |
| FOC-IL-003 | voltage command never exceeds validated modulation limit | \(\|\mathbf v_{dq}\|\le V_{lim}\) | property test and corner log |
| FOC-IL-004 | integrator remains bounded during saturation | integral state max and recovery | anti-windup regression |
| FOC-IL-005 | invalid current/angle/bus sample cannot be used as valid feedback | rejection and safe transition | fault-injection trace |
| FOC-IL-006 | control output meets PWM update deadline | worst-case sample-to-shadow write | target timing capture, not host estimate |
| FOC-IL-007 | parameter mismatch retains defined stability margin | worst-corner PM/GM | sweep report |
| FOC-IL-008 | parameter update cannot create torn d/q coefficients | atomic old-or-new parameter set only | concurrency test |

실제 acceptance 숫자(최소 PM/GM, maximum overshoot, settling time, current tracking error, allowed saturation duration, WCET deadline)는 system requirements와 evidence가 확정되기 전까지 TBD다.

## 13. Fault injection matrix

| ID | Injected condition | Expected detection / response | Evidence |
|---|---|---|---|
| FI16-01 | \(R_s\) low/high mismatch | gain/response deviation bounded; diagnostic sweep | corner log |
| FI16-02 | \(L_d\) ± range | d-axis plant/coupling residual bounded | Bode/step sweep |
| FI16-03 | \(L_q\) ± range | q-axis plant/coupling residual bounded | Bode/step sweep |
| FI16-04 | \(\psi_f\) mismatch | q-axis feed-forward residual bounded | voltage residual trace |
| FI16-05 | DC bus droop | dynamic vector limit follows validated Vdc | saturation property log |
| FI16-06 | DC bus stale/invalid | reject stale bus value and enter defined policy | state trace |
| FI16-07 | \(\omega_e\) sign reversed | feed-forward sign plausibility catches mismatch | sign test |
| FI16-08 | d/q current polarity reversed | sign/torque plausibility fault | transform regression |
| FI16-09 | current ADC stale sample | sample rejected; no false PI update | timestamp trace |
| FI16-10 | current sample saturated | mark invalid; no normal control update | status trace |
| FI16-11 | angle timestamp shifted | phase error and response impact bounded/detected | delay sweep |
| FI16-12 | compute delay + one missed PWM load | deadline fault and defined inhibit request | timing trace |
| FI16-13 | PI output sustained saturation | anti-windup prevents unbounded integral | integral-state plot |
| FI16-14 | mode transition during nonzero integral | bumpless transfer/reset policy applied | state-transition test |
| FI16-15 | NaN/Inf in parameter or feedback | reject before controller math | host unit test |
| FI16-16 | coefficient update during control tick | atomic old-or-new parameter set only | concurrency test |
| FI16-17 | quantized/fixed-point coefficient overflow | range guard and saturation diagnostic | static/property test |
| FI16-18 | sensor noise near loop crossover | noise gain/response remains within requirement | spectral/SIL result |
| FI16-19 | hot \(R_s\), low \(L\), max delay combined | robust corner remains within margin or derates | worst-corner report |
| FI16-20 | low bus, high speed, max torque request | voltage saturation supervisor limits current request | saturation duration log |

Host/SIL fault injection does not prove physical OCP, gate disable, STO, EMC immunity or actual inverter behavior.

## 14. AEL-002 design intake — all unresolved

| Parameter / decision | Current status | Evidence required |
|---|---|---|
| Motor exact model and winding connection | TBD | nameplate + manufacturer datasheet |
| \(R_s\) and measurement temperature | TBD | exact datasheet or approved identification report |
| \(L_d,L_q\), saturation dependence | TBD | manufacturer data or bounded identification |
| \(\psi_f\), pole pairs, electrical angle convention | TBD | motor data and validated feedback alignment |
| continuous/peak phase-current envelope | TBD | motor + inverter + thermal/system requirement |
| DC bus min/nominal/max and regen envelope | TBD | source and power-stage requirements |
| PWM frequency, carrier, shadow-load event | TBD | exact MCU/SDK/board configuration |
| ADC aperture, sensor/filter delay, DMA/ISR timing | TBD | Chapter 10/15 target evidence |
| sample-to-actuation delay distribution | TBD | timing capture over worst-case load |
| SVPWM implementation and voltage reserve | TBD | exact modulation implementation |
| current PI discretization and gains | TBD | approved design calculation and host/SIL evidence |
| anti-windup/reset/invalid sample policy | TBD | system state/fault requirements |
| fixed/floating-point format and compiler behavior | TBD | exact target compiler/ABI/build |
| minimum phase/gain margin and response limits | TBD | system requirements/risk analysis |
| safety function and independent inhibit path | TBD | separate safety architecture and applicable conformity assessment |

## 15. Claim/source boundary

- Imperix TN111/TN106/TN105/PN142 are professional application/technical notes. They support conventional PMSM equations, RL plant approximation, decoupling, magnitude-optimum example, discrete PI alternatives and timing decomposition; they are not normative standards and use their own controller hardware.
- MathWorks R2026b PMSM Current Controller documentation is an independent implementation reference for backward-Euler PI, feed-forward, voltage saturation and anti-windup. Its block assumptions and signal conventions must be checked before comparing numeric gains.
- TI C2000 Software Guide documents that MC SDK includes sensored FOC, multiple current-sensing techniques and Fast Current Loop examples. It does not certify an AEL-002 F280039C configuration or prescribe our gains.
- The 2025 Energies article reports a parameter/delay identification and frequency-sweep tuning method with experimental results. It supports the need to verify model and delay rather than blindly trust nominal parameters; its proposed method is not a universal guarantee.
- IEC 61800-5-1:2022 (corrected 2025-12) concerns electrical, thermal, energy and related drive-system hazards. IEC 61800-5-2:2016+AMD1:2026 concerns functional safety of safety-related PDS. These standards do **not** provide the PI gain formulas in this chapter. Public catalogue scope is not a clause-by-clause compliance assessment.
- No AEL-002 design, safety compliance, STO certification or physical validation is established by this educational chapter.

## 16. 장 완료 기준

- [ ] PMSM d/q equations and sign convention can be re-derived.
- [ ] Decoupling feed-forward signs can be checked from the plant equations.
- [ ] Continuous PI gains and their units can be derived.
- [ ] Forward Euler, Backward Euler and Tustin recurrences can be implemented without mixing states.
- [ ] Voltage vector limit and axis priority can be calculated from a validated bus voltage.
- [ ] Anti-windup and integrator reset/freeze semantics are explicit.
- [ ] Sensor/ADC/compute/PWM delay is decomposed without double counting.
- [ ] Pure delay phase and actual loop margin are distinguished.
- [ ] \(R_s,L_d,L_q,\psi_f,V_{dc},T_d\) corner sweeps are defined.
- [ ] Host/SIL/fault-injection evidence boundaries are understood.
- [ ] AEL-002 unresolved values remain TBD and **NO STACK / NO POWER** is maintained.

**현재 판정:** Chapter 16은 이론·가상 계산·검증 설계 자료다. 실제 AEL-002 motor parameters, current limits, PWM/ADC timing, target PI coefficients, controller stability margin, firmware build, SIL/HIL, motor test 또는 hardware safety verification을 수행했다고 주장하지 않는다.

**다음 장 연결:** Chapter 17은 speed/position outer loops, trajectory/reference shaping, torque/current limiting and command arbitration를 다루며, Chapter 16 current-loop contract 위에 cascade control을 구축한다. 실제 inertia, torque/current envelope, encoder limits and loop rates remain TBD.

**안전 상태: NO STACK / NO POWER.**
