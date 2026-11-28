# 14장 — 전력 반도체와 게이트 드라이버 아키텍처

> **핵심 질문:** MCU의 작은 논리 신호로 어떻게 큰 모터 전류를 안전하게 스위칭할까? 전력 스위치, 게이트 드라이버, 전원, PCB 기생성분, 보호회로를 하나의 동적 시스템으로 이해한다.

이 장은 silicon MOSFET, enhancement-mode GaN HEMT, IGBT의 일반 특성과 게이트 구동을 비교한다. SiC MOSFET은 비교가 필요한 곳에서만 언급한다. 특정 AEL-002 전력소자나 드라이버를 선정하지 않는다. 실제 DC bus, phase current, gate voltage, gate resistance, deadtime, protection threshold, thermal design은 모두 TBD다.

## 1. 학습 목표와 안전 경계

학습 후 다음을 할 수 있어야 한다.

1. MOSFET, e-mode GaN, IGBT의 전도·스위칭 특성과 주요 손실 항목을 구분한다.
2. gate charge, Miller plateau, source/sink current와 switching time의 관계를 계산한다.
3. gate loop, power loop, common-source/emitter inductance, dv/dt·di/dt를 설명한다.
4. deadtime의 shoot-through 방지와 reverse-conduction 손실 trade-off를 계산한다.
5. bootstrap, isolated bias, low-side supply 구조의 장단점을 설명한다.
6. UVLO, Miller clamp, OCP, DESAT, soft turn-off, fault latch의 역할과 한계를 구분한다.
7. 가상 conduction/switching/gate-drive/bootstrap/fault-energy 계산을 수행한다.
8. double-pulse 및 gate waveform 검증 템플릿을 작성한다.
9. 핵심 주장을 여러 공식·전문 자료로 교차검증하고 적용 범위를 기록한다.

**NO STACK / NO POWER.** 이 장의 계산과 시험 계획은 보드를 쌓거나 전원을 인가하는 허가가 아니다. BOOSTXL/SENS007 실물 리비전·배선·점퍼·접지 상태는 확인되지 않았다. 어떤 gate waveform 측정이나 double-pulse test도 승인·수행하지 않는다.

## 2. 세 가지 전력 스위치의 차이

전력 스위치는 모터 전류를 흐르게 하거나 막는 전자식 밸브다. Gate driver는 이 밸브의 gate에 필요한 전하를 빠르게 넣고 빼는 구동기다. gate pin의 논리 전압만 맞추면 끝나는 것이 아니라 전하, 전류, 전압 한계, 기생 인덕턴스, 절연, 고장 동작까지 고려해야 한다.

| 특성 | Silicon MOSFET | e-mode GaN HEMT | IGBT |
|---|---|---|---|
| 제어 단자 | insulated gate | insulated gate | insulated gate |
| 정상 도통 모델 | \(I^2R_{DS(on)}\) | \(I^2R_{DS(on)}\) | 대략 \(V_{CE(sat)}I\) |
| 역방향 전류 | body diode/channel | reverse channel conduction; conventional Si body diode와 다름 | 보통 antiparallel diode와 함께 사용 |
| 스위칭 특성 | gate charge와 diode recovery 영향 | 매우 빠른 edge 가능, low gate margin | tail current 영향으로 MOSFET보다 turn-off가 느릴 수 있음 |
| 구동 주의 | Qg, Miller, VGS limit, body diode | 좁은 gate voltage window, low threshold, low-inductance loop | VGE, DESAT, short-circuit withstand, soft turn-off |
| 일반 적용 경향 | 저·중전압부터 고전압까지 폭넓음 | 고주파·고효율, layout/drive 민감 | 높은 전압·전류 영역에서 활용 |

표는 기술적 경향이며 모든 소자에 대한 보편적인 정격 비교가 아니다. 실제 선택은 exact part의 datasheet, safe operating area, switching energy, thermal impedance, avalanche/repetitive rating, short-circuit data를 확인해야 한다.

### 2.1 Silicon MOSFET

MOSFET의 on-state conduction은 대략 \(R_{DS(on)}\)으로 모델링한다.

\[
P_{cond}\approx I_{D,rms}^{2}R_{DS(on)}(T_J,V_{GS})
\]

RDS(on)은 junction temperature와 gate voltage에 따라 달라진다. datasheet의 25°C typical 값만 사용해 worst-case 손실을 계산하면 안 된다. body diode reverse recovery와 output capacitance charge/discharge도 switching loss에 영향을 준다.

### 2.2 Enhancement-mode GaN HEMT

e-mode GaN은 매우 낮은 gate charge와 빠른 switching이 가능하지만 gate voltage 허용 범위가 silicon MOSFET과 다를 수 있다. 일부 device는 권장 on voltage가 약 5 V 수준이고 absolute gate limit이 훨씬 좁다. 이 숫자를 다른 GaN part에 복사하지 않는다.

GaN의 threshold가 낮으면 common-source inductance, ground bounce, Miller current가 만드는 작은 gate disturbance도 false turn-on을 유발할 수 있다. datasheet가 정한 exact gate voltage, clamp, negative bias 허용 여부를 따른다.

GaN은 silicon MOSFET의 conventional body diode와 동일한 구조가 아니다. reverse conduction voltage가 커질 수 있고, deadtime 동안 reverse conduction이 길면 손실이 증가할 수 있다. 반대로 reverse-recovery charge가 매우 낮은 device도 있지만 COSS charge와 reverse conduction loss가 사라지는 것은 아니다.

### 2.3 IGBT

IGBT는 gate로 제어하지만 bipolar conduction 특성이 있어 on-state drop을 \(V_{CE(sat)}\)로 표현하는 경우가 많다.

\[
P_{cond}\approx V_{CE(sat)} I_{C,avg}
\]

정확한 계산은 current waveform과 switching state별 duty를 사용한다. IGBT turn-off tail current, short-circuit withstand time, DESAT blanking, gate turn-off strategy가 중요하다. IGBT용 gate voltage/UVLO/negative bias를 MOSFET이나 GaN에 그대로 적용하지 않는다.

### 2.4 기술 선택 전에 비교할 데이터

- \(V_{DS}/V_{CE}\) rating과 transient overshoot margin
- continuous/pulsed current의 case/PCB/temperature 조건
- RDS(on) 또는 VCE(sat) 대 temperature/current
- Qg, Qgd, Qgs, Ciss/Coss/Crss와 측정 조건
- Eon/Eoff, reverse recovery, Qrr, Qoss/Eoss
- SOA, short-circuit withstand, avalanche 조건
- thermal resistance/impedance, transient Zth, package/layout
- gate absolute maximum, recommended on/off bias, leakage
- driver source/sink capability, propagation delay, CMTI, UVLO
- lifecycle, qualification, package, supply chain

## 3. Gate charge와 Miller plateau

### 3.1 Gate는 전하를 요구한다

MOSFET/IGBT gate는 단순한 logic input이 아니라 capacitance와 비선형 charge 특성을 가진다. datasheet는 보통 gate charge curve를 특정 drain/collector voltage, drain/collector current, gate voltage 조건에서 제시한다.

- \(Q_{GS}\): gate-source charge 구간
- \(Q_{GD}\): gate-drain Miller charge 구간
- \(Q_G\): 전체 gate charge
- \(C_{ISS}, C_{OSS}, C_{RSS}\): 소신호 capacitance 표기. 전압에 따라 달라지며 Qg와 동일한 값이 아니다.

Miller plateau 동안 gate voltage가 비교적 일정한 동안 drain-source/collector-emitter voltage가 변한다. 이 구간의 driver current가 switching transition time과 loss에 큰 영향을 준다.

### 3.2 1차 gate current 근사

전체 charge를 transition time에 이동시키는 평균 current의 첫 근사:

\[
I_{G,avg}\approx \frac{Q_G}{t_{transition}}
\]

Miller 구간의 단순 근사:

\[
I_{G,M}\approx
\frac{V_{DRV}-V_{PL}}
{R_{DRV}+R_{G,ext}+R_{G,int}}
\]

\[
t_M\approx\frac{Q_{GD}}{I_{G,M}}
\]

여기서 driver output resistance는 source/sink 방향과 출력전류·전압·온도에 따라 다르다. 실제 gate waveform은 비선형 Cgd, gate loop inductance, common-source inductance, driver current limit, Miller plateau, parasitic ringing에 의해 달라진다.

### 3.3 Gate resistor trade-off

- Rg를 낮추면 gate current가 증가하고 switching이 빨라질 수 있다. switching loss가 줄 수 있지만 dv/dt·di/dt, overshoot, ringing, EMI, false turn-on, diode recovery stress가 커질 수 있다.
- Rg를 높이면 edge가 느려져 ringing/EMI가 줄 수 있지만 switching transition time과 switching loss가 증가한다.
- turn-on과 turn-off resistor를 분리하면 서로 다른 최적점을 조정할 수 있다. diode 또는 split-output driver 구조가 필요할 수 있다.
- external resistor는 가능한 한 gate pin 가까이에 배치하고 Kelvin source/emitter return을 검토한다.

Rg는 계산 한 번으로 확정하지 않는다. exact device, driver, PCB, bus voltage, load current, temperature, switching frequency, EMI 목표에서 측정·검증한다.

## 4. Gate loop, power loop, Miller false turn-on

### 4.1 서로 연결된 두 loop

**Gate loop:** driver supply bypass → driver output → gate resistor → gate → Kelvin source/emitter return → driver ground.

**Power loop:** DC-link capacitor → high-side/low-side switch → load/commutation path → DC-link capacitor.

두 loop는 gate capacitance와 shared source/emitter inductance를 통해 결합한다. gate return을 power current가 흐르는 길과 공유하면 common-source inductance가 gate reference를 흔든다.

### 4.2 Miller current와 source inductance

Drain voltage가 빠르게 변하면 gate-drain capacitance를 통해 변위 전류가 흐른다.

\[
I_{Miller}\approx C_{GD}\frac{dV_{DS}}{dt}
\]

Off-state gate impedance에 이 전류가 흐르면 gate voltage가 올라가 false turn-on을 일으킬 수 있다.

Shared source inductance는

\[
V_L=L_S\frac{di}{dt}
\]

전압을 만들어 gate-source 기준을 흔든다. 실제 polarity는 current direction과 layout reference에 따라 달라진다.

대응책:
- power source와 Kelvin source/emitter를 분리해 사용
- gate loop를 짧고 작게 구성
- driver를 switch 가까이 배치
- turn-off sink impedance와 Rg,off 검토
- 필요하면 active Miller clamp 또는 negative off-bias 검토
- driver CMTI, input filtering, UVLO, output clamp 확인
- switch-node dv/dt를 gate waveform과 함께 측정

Negative gate bias는 모든 device에 안전한 해결책이 아니다. gate absolute maximum과 driver supply range를 모두 확인한다.

### 4.3 가상 Miller current 계산

가정: \(C_{GD}=40\ pF\), \(dV_{DS}/dt=20\ V/ns\).

\[
I_M=40\times10^{-12}\times20\times10^9=0.8\ A
\]

순간적으로 0.8 A 수준의 displacement current가 흐를 수 있다는 단순 계산이다. 실제 current는 voltage-dependent capacitance, layout, driver clamp, gate impedance에 좌우된다. 이 수치는 특정 AEL 소자나 실제 측정값이 아니다.

가상으로 off-path impedance가 1.5 Ω라고 단순화하면 \(V=IR=1.2 V\)가 된다. gate threshold가 낮은 device에서는 큰 disturbance일 수 있으므로 clamp와 layout을 검토해야 한다. 이 단순 모델은 transient waveform 예측을 대체하지 않는다.

## 5. Deadtime과 shoot-through

### 5.1 왜 deadtime이 필요한가

Half-bridge의 high-side와 low-side switch가 동시에 도통하면 DC bus를 직접 short하는 shoot-through가 발생할 수 있다. PWM logic의 두 edge가 서로 겹치지 않아도 실제 device turn-off가 늦거나 propagation delay가 다르면 cross-conduction이 생길 수 있다.

반대로 deadtime을 너무 길게 하면 load current가 body diode 또는 reverse-conduction path로 흐르는 시간이 길어진다. diode drop/reverse conduction loss, current distortion, torque ripple이 커질 수 있다.

### 5.2 Worst-case deadtime budget

정의:
- \(t_{off,path,max}\): outgoing device의 input command부터 실제 current conduction이 충분히 종료될 때까지 worst-case time
- \(t_{on,path,min}\): incoming device의 input command부터 conduction이 시작될 때까지 minimum time
- \(t_{skew}\): driver channel/device propagation mismatch
- \(t_{jitter}\): timer/logic timing uncertainty
- \(t_{margin}\): 추가 설계 margin

\[
t_{dead,min}\ge
t_{off,path,max}-t_{on,path,min}
+t_{skew}+t_{jitter}+t_{margin}
\]

이 식은 개념적 worst-case budget이다. datasheet의 propagation delay와 rise/fall time 정의를 읽어 같은 기준점으로 환산해야 한다. device current extinction은 gate voltage threshold 하나만으로 정확히 정의되지 않을 수 있다. 실제 waveform과 load current를 고려한다.

Fixed deadtime은 단순하지만 모든 조건에서 충분하면서도 효율적인 값 찾기가 어렵다. Adaptive deadtime은 VGS sensing/handshake를 이용할 수 있으나 센싱 노이즈, blanking, fault behavior와 device-specific timing 검증이 필요하다.

### 5.3 가상 deadtime 계산

가정:
- outgoing off path worst case 120 ns
- incoming on path minimum 65 ns
- channel skew/jitter 합 25 ns
- 추가 margin 20 ns

\[
t_{dead,min}=120-65+25+20=100\ ns
\]

100 ns는 이 가상 조건에서의 계산 결과다. 실제 AEL-002 deadtime 설정값이 아니다. 실제 값은 exact switch/driver, temperature, current, voltage, gate resistance, PWM timing, propagation tolerance로 결정한다.

## 6. Gate driver topology와 bias supply

### 6.1 Low-side, half-bridge level-shift, isolated driver

| 구조 | 장점 | 주의점 |
|---|---|---|
| Ground-referenced low-side | 단순, low-side MOSFET 구동에 적합 | high-side floating reference에는 직접 사용 불가 |
| Half-bridge level-shift | high-side/low-side 통합, bootstrap 사용 가능 | duty/on-time refresh 제한, high-side transient/negative VS rating |
| Isolated single/dual channel | galvanic isolation과 독립 floating supply 가능 | isolation rating/lifetime, CMTI, creepage/clearance, isolated supply |
| Transformer/pulse drive | isolation 및 high dv/dt 환경에서 활용 가능 | pulse width/duty, reset, magnetics, startup |

Isolation voltage 숫자 하나만으로 working voltage나 안전 절연을 판정하지 않는다. reinforced/basic insulation, creepage, clearance, pollution degree, altitude, material group, transient, lifetime, certification과 PCB 구현을 확인한다.

### 6.2 Bootstrap supply

전형적인 bootstrap은 diode와 capacitor로 high-side driver의 floating supply를 만든다. Low-side switch가 on되고 switch node가 낮아질 때 capacitor를 충전한다. High-side가 켜져 switch node가 올라가면 capacitor가 high-side gate driver를 공급한다.

장점: 간단하고 비용이 낮을 수 있다. 제한:
- capacitor charge를 refresh할 low-side conduction interval 필요
- 100% duty 또는 긴 high-side on-time에 제한
- driver quiescent current, gate charge, level-shift charge, leakage로 전압 droop
- startup/low-frequency/burst condition에서 UVLO 가능
- bootstrap diode/resistor의 voltage/current/recovery 조건

최소 charge budget:

\[
Q_{total}=Q_G+I_{QBS}t_{ON}+Q_{LS}+Q_{leak}
\]

\[
C_{BOOT}\ge\frac{Q_{total}}{\Delta V_{BS,allow}}
\]

실제 설계는 capacitor tolerance/DC bias derating/temperature/aging, ESR, peak recharge current, diode drop, resistor drop, driver UVLO, maximum duty/on-time을 포함한다.

### 6.3 가상 bootstrap 계산

가정:
- switch gate charge \(Q_G=60\ nC\)
- high-side driver quiescent current \(I_{QBS}=0.2\ mA\)
- high-side on-time \(t_{ON}=1\ ms\)
- level-shift/leakage allowance \(Q_{LS}+Q_{leak}=20\ nC\)
- 허용 droop \(\Delta V=1.0\ V\)

\[
Q_{total}=60nC+(0.2mA)(1ms)+20nC
=60+200+20=280nC
\]

\[
C_{BOOT,min}=280nC/1V=280nF
\]

교육용으로 tolerance/derating margin 2배를 가정하면 560 nF 이상의 nominal candidate를 검토할 수 있다. 이는 최종 부품 선택이 아니다. 실제 capacitor의 DC bias derating, ESR, peak current, recharge time, driver vendor equation을 적용해야 한다.

### 6.4 Isolated bias supply

Isolated supply는 high-side 또는 각 switch gate에 독립 bias를 제공할 수 있어 100% duty나 긴 on-time 제약을 완화할 수 있다. 대신 isolation barrier, creepage/clearance, transformer coupling capacitance, CMTI, bias UVLO, startup sequencing, isolated supply fault를 검증한다.

## 7. UVLO, Miller clamp, OCP, DESAT와 soft turn-off

### 7.1 UVLO — Undervoltage Lockout

Driver supply가 충분하지 않으면 switch를 완전히 켜지 못해 conduction loss와 열이 급증할 수 있다. UVLO는 supply가 threshold 아래일 때 output을 inhibit한다. rising/falling threshold hysteresis, output state, fault pin, recovery behavior를 datasheet에서 확인한다.

MCU reset, driver supply ramp, isolated bias startup 중 gate output은 기본적으로 off가 되도록 설계한다. 입력이 floating/unknown인 상태에서 active-high enable이 우연히 켜지지 않도록 hardware pull state와 input logic를 검토한다.

### 7.2 Active Miller clamp

Gate voltage가 off threshold 아래로 내려간 뒤 low-impedance clamp path를 연결해 Miller current를 sink한다. clamp의 효과는 switch gate와 clamp 사이의 parasitic R/L에 크게 좌우된다. driver 내부 clamp가 멀리 있으면 external clamp보다 덜 효과적일 수 있다.

Miller clamp는 layout, turn-off sink, negative bias, device threshold, dv/dt와 함께 평가한다. 모든 design에 필수라고 단정하지 않는다.

### 7.3 Overcurrent protection

가능한 방법:
- shunt resistor + current-sense amplifier + comparator
- integrated current sense/MOSFET RDS(on) sensing (device/controller-specific)
- desaturation (주로 IGBT/SiC driver application)
- power module internal sensor/diagnostic

Threshold 설정에는 sensor gain/offset, comparator offset, blanking/filter delay, propagation, temperature drift, current rise rate, short-circuit energy, nuisance-trip immunity를 포함한다. Software ADC protection은 hardware fast path를 대체하지 않는다.

### 7.4 DESAT

DESAT은 switch on-state의 VCE/VDS가 예상보다 높아지는 상태를 감지하는 보호 방식이다. IGBT short-circuit/overcurrent에서 널리 사용되고 일부 SiC driver에도 제공된다. threshold, blanking, filter, high-voltage diode, DESAT capacitor, propagation delay, soft turn-off를 함께 설계한다.

DESAT은 모든 low-voltage MOSFET/GaN stage에 자동으로 적용되는 기능이 아니다. low-voltage MOSFET drive는 shunt/comparator OCP가 더 적절할 수 있다. exact driver datasheet와 device short-circuit behavior를 확인한다.

### 7.5 Soft turn-off / two-level turn-off

Fault가 발생했을 때 gate를 매우 빠르게 끄면 높은 di/dt와 stray inductance로 overvoltage가 커질 수 있다.

\[
V_L=L_{stray}\frac{di}{dt}
\]

Soft turn-off는 gate discharge를 제어해 overvoltage를 줄이지만, switch가 fault current를 흘리는 시간이 늘어나 short-circuit energy가 커질 수 있다. Turn-off speed와 voltage overshoot 사이의 trade-off를 worst-case 조건에서 확인한다. fault energy가 device SOA/short-circuit limit을 초과하지 않는다는 분석이 필요하다.

### 7.6 Gate-driver fault의 안전 권한

- Gate driver fault output은 hardware safety manager/MCU trip input으로 연결할 수 있지만 실제 topology와 polarity는 schematic/part datasheet 확인 전 TBD다.
- Fault 발생 시 PWM input 차단과 gate output inhibit의 독립 경로를 검토한다.
- Fault status와 first-event capture를 기록하고, repeated event와 queue overflow를 처리한다.
- Reset/clear는 cause-absent 확인과 supervised re-arm 절차에 묶는다.
- 통신은 fault를 조회할 수 있어도 driver latch나 system safety latch를 임의 해제할 수 없다.
- Gate driver의 내부 fault latch와 system-level FAULT_LATCH는 서로 다른 상태다.

## 8. 손실과 열의 첫 계산

### 8.1 Conduction loss

Silicon MOSFET 단순 모델:

\[
P_{cond}=I_{D,rms}^{2}R_{DS(on),hot}
\]

IGBT 단순 근사:

\[
P_{cond}\approx V_{CE(sat)}I_{C,avg}
\]

정확한 inverter 손실은 각 switch의 conduction interval, current waveform, modulation, diode/reverse current, temperature를 반영한다.

### 8.2 Switching loss

Datasheet/test bench의 switching energy를 사용할 수 있는 경우:

\[
P_{sw}=(E_{on}+E_{off})f_{sw}
\]

Eon/Eoff는 Vbus, current, gate resistance, gate voltage, temperature, commutation diode, test layout에 따라 달라진다. 다른 조건의 Eon/Eoff를 직접 대입하지 않는다.

### 8.3 Gate-drive power

한 switch의 1차 gate-drive power:

\[
P_{gate}\approx Q_G V_{drive} f_{sw}
\]

여러 switch가 있으면 channel별 Qg·Vdrive·fsw를 합산한다. driver quiescent power, isolated supply efficiency, gate resistor/driver output loss를 추가한다. Gate-drive power가 작아 보여도 peak source/sink current와 loop inductance는 switching quality를 결정한다.

### 8.4 가상 손실 계산

교육용 MOSFET 예:
- \(I_{D,rms}=8 A\)
- hot \(R_{DS(on)}=12 m\Omega\)
- \(E_{on}=0.20 mJ\)
- \(E_{off}=0.15 mJ\)
- \(f_{sw}=20 kHz\)

\[
P_{cond}=8^2\times0.012=0.768 W
\]
\[
P_{sw}=(0.20+0.15)mJ\times20,000=7.0 W
\]
\[
P_{device,approx}=7.768 W
\]

이 예제는 conduction interval과 switching event를 단순화한 가상 계산이다. 실제 3상 인버터에서 모든 switch가 같은 RMS current를 갖거나 매 주기 같은 Eon/Eoff를 갖는다고 가정하면 안 된다.

Gate drive example:
- \(Q_G=60 nC\)
- \(V_{drive}=10 V\)
- \(f_{sw}=20 kHz\)

\[
P_{gate}=60nC\times10V\times20kHz=12mW
\]

이상적인 한 channel의 charge energy 근사다. 6개 channel이면 72 mW이며 driver quiescent/isolated supply loss는 별도다.

## 9. Fault energy와 보호시간

인덕터에 저장된 에너지:

\[
E_L=\frac12 LI^2
\]

가정: \(L=100\ \mu H\), \(I=10 A\).

\[
E_L=0.5\times100\times10^{-6}\times10^2=5mJ
\]

이 에너지는 fault interruption 시 switch, diode, clamp, snubber, bus capacitor 또는 load path로 이동한다. 에너지의 크기만으로 어느 부품이 흡수할지 판단할 수 없다. 회로의 실제 commutation path와 parasitic inductance를 분석한다.

Protection chain:
1. fault physical quantity rises
2. sensor/comparator/driver detects it
3. filter/blanking completes
4. logic/driver asserts fault
5. gate output reaches safe off condition
6. current commutates to defined path
7. DC bus/other device voltage stays within limits
8. fault state remains latched until supervised clear

Detection latency와 device turn-off time만 계산하고 current decay, energy path, bus overvoltage를 생략하면 보호 검증이 불완전하다.

## 10. 연습문제와 전체 풀이

1. MOSFET conduction loss의 단순식을 쓰고 \(I=5 A, R=20m\Omega\)일 때 계산하라.
2. \(Q_G=80nC\), transition time=40ns일 때 평균 gate current 근사는?
3. \(Q_{GD}=24nC\), Miller current=0.8A일 때 Miller time은?
4. \(C_{GD}=30pF\), \(dv/dt=10V/ns\)일 때 Miller current는?
5. \(L=2nH\), \(di/dt=1A/ns\)일 때 inductive voltage는?
6. \(t_{off,max}=150ns, t_{on,min}=70ns, skew+jitter=30ns, margin=20ns\)이면 deadtime budget은?
7. Deadtime을 너무 길게 하면 어떤 손실/왜곡이 증가할 수 있는가?
8. Bootstrap total charge=350nC, allowed droop=0.7V이면 최소 capacitance는?
9. \(Q_G=50nC, V_{drive}=12V, f=25kHz\)일 때 gate power 근사는?
10. \(E_{on}=0.1mJ, E_{off}=0.12mJ, f=30kHz\)일 때 switching loss는?
11. \(L=200\mu H, I=5A\)일 때 stored energy는?
12. DESAT blanking을 무한히 길게 하면 왜 안 되는가?
13. UVLO가 필요한 이유 두 가지는?
14. Miller clamp가 있어도 layout을 최적화해야 하는 이유는?
15. IGBT용 gate voltage를 GaN에 그대로 적용해도 되는가?
16. Driver FLT pin이 clear됐다고 system FAULT_LATCH도 자동 clear해도 되는가?
17. Gate resistor를 줄일 때 함께 확인해야 할 항목은?
18. Datasheet Eon/Eoff를 다른 Vbus/current/Rg 조건에 그대로 사용하면 안 되는 이유는?

**전체 풀이**

1. \(P=I^2R=25\times0.020=0.5W\).
2. \(I=Q/t=80nC/40ns=2A\).
3. \(t=Q/I=24nC/0.8A=30ns\).
4. \(I=C\,dv/dt=30pF\times10V/ns=0.3A\).
5. \(V=L\,di/dt=2nH\times1A/ns=2V\).
6. \(150-70+30+20=130ns\).
7. body diode/reverse conduction interval과 관련 손실, current distortion, torque ripple이 증가할 수 있다.
8. \(C=Q/\Delta V=350nC/0.7V=500nF\). 실제 nominal은 derating/tolerance/ESR/peak current를 더 고려한다.
9. \(P=50nC\times12V\times25kHz=15mW\).
10. \(P=(0.1+0.12)mJ\times30kHz=6.6W\).
11. \(E=0.5\times200\mu H\times25=2.5mJ\).
12. blanking이 길면 실제 short-circuit/overcurrent 감지가 늦어져 device withstand time과 energy limit을 초과할 수 있다.
13. supply 부족 시 switch가 충분히 on되지 않아 과도한 conduction loss/열이 생길 수 있고, startup/brownout에서 불완전한 gate state가 생길 수 있다.
14. clamp path의 parasitic R/L이 크면 Miller current를 충분히 빨리 sink하지 못한다.
15. 안 된다. 각 기술과 exact part의 recommended/absolute gate voltage, threshold, Qg, UVLO를 확인해야 한다.
16. 안 된다. driver-local fault clear와 system-level safety clear는 권한·원인·interlock이 다르다. supervised clear 후 DISARMED가 기본이다.
17. switching loss, dv/dt/di/dt, VDS/VCE overshoot, gate ringing, EMI, false turn-on, reverse recovery, driver peak current, thermal stress.
18. switching energy는 voltage/current, gate bias, Rg, temperature, diode/commutation path, layout에 종속되므로 operating point가 다르면 값이 달라진다.

## 11. AEL-002 gate-drive requirement template

| 항목 | 기록 내용 | 현재 상태 |
|---|---|---|
| Power device | exact manufacturer/order code/package/revision | TBD |
| Technology | Si MOSFET / e-mode GaN / IGBT / other | TBD |
| VDS/VCE and transients | bus, overshoot, repetitive peak | TBD |
| Current/SOA | RMS/peak/pulse, duration, temperature | TBD |
| Gate voltage | recommended on/off and absolute limits | TBD |
| Qg/Qgd | test VDS/ID/VGS and temperature | TBD |
| Driver | exact part, source/sink, output resistance | TBD |
| Topology | low-side/level-shift/isolated | TBD |
| Bias supply | positive/negative rails, UVLO, isolation | TBD |
| Gate resistor | turn-on/off values and layout | TBD |
| Deadtime | worst-case path delay/skew/jitter | TBD |
| Protection | OCP/DESAT/UVLO/Miller clamp/soft-off | TBD |
| Fault path | detection-to-gate-off and current decay | TBD |
| Layout | gate/power loop, Kelvin, decoupling | TBD |
| Thermal | Zth, Rth, cooling, junction margin | TBD |
| Verification | DPT, waveform, temperature, fault injection | Not authorized |

## 12. Verification matrix

| ID | Test/analysis | Expected evidence |
|---|---|---|
| GD-01 | gate voltage vs absolute/recommended limits | exact datasheet + measured VGS |
| GD-02 | gate charge/driver current budget | Qg curve + source/sink calculation |
| GD-03 | gate loop ringing | VGS waveform with probe/layout conditions |
| GD-04 | switch-node dv/dt false turn-on | VGS(off), complementary device current |
| GD-05 | common-source inductance | Kelvin layout review + measured source bounce |
| GD-06 | deadtime worst case | propagation tolerance calculation + double-pulse |
| GD-07 | reverse conduction/deadtime loss | device-specific loss model + waveform |
| GD-08 | bootstrap droop/refresh | VBS waveform at max on-time/low refresh |
| GD-09 | UVLO startup/brownout | driver output safe state and recovery |
| GD-10 | OCP/DESAT blanking and delay | fault injection + current/voltage waveform |
| GD-11 | soft turn-off overshoot/energy | VDS/VCE peak and fault energy |
| GD-12 | gate driver FLT latch/reset | fault status, output inhibit, reset sequence |
| GD-13 | hardware inhibit independent of MCU | schematic review + controlled target test |
| GD-14 | thermal loss estimate | device loss model + measured temperature correlation |
| GD-15 | fault record and re-arm | Chapter 11/13 state trace and negative remote-clear test |

Physical double-pulse testing and power-stage fault injection are high-energy engineering tests. They require an approved test plan, fixture, instrumentation, risk assessment, independent shutdown, current-limited source, guarding and qualified personnel. This chapter does not authorize or perform them.

## 13. Official/professional source cross-check

### 13.1 Silicon MOSFET gate physics and drive
- Infineon, [*Gate drive for power MOSFETs in switching applications*](https://www.infineon.com/assets/row/public/documents/24/42/infineon-gate-drive-for-power-mosfets-in-switchtin-applications-applicationnotes-en.pdf), AN_2203_PL18_2204_004502, V1.0, 2022-04-20. Sections 2–6 cover gate limits, gate charge, drive current and high-side/isolated drivers. Scope explicitly focuses on silicon MOSFETs; it does not cover IGBT/WBG devices.
- Infineon, [Gate Driver Requirements for MOSFETs, IGBTs, SiC MOSFETs and GaN HEMTs](https://www.infineon.com/product-information/gate-driver-requirements-mosfet-igbt-sic-gan) — device-dependent gate voltage, UVLO, source/sink current, CMTI and protection selection overview.
- onsemi, [AND9987/D](https://www.onsemi.com/pub/collateral/and9987-d.pdf) — Miller capacitance induced turn-on and active Miller clamp example for IGBT. Example values are not universal.

### 13.2 GaN drive and layout
- TI, [SLUAAM3, *GaN Driver Schematic and Layout Recommendations*](https://www.ti.com/document-viewer/lit/html/SLUAAM3), August 2022 — GaN half-bridge gate driver schematic, bypassing, bootstrap and low-parasitic layout.
- TI, [SLLA456, *Optimizing Gate Driver Layout for LiDAR Applications*](https://www.ti.com/lit/an/slla456/slla456.pdf), February 2020 — gate/power loop coupling and parasitic inductance; use as layout physics reference, not motor-drive design recipe.
- EPC, [AN003, *Accurately Measuring High Speed GaN Transistors*](https://epc-co.com/epc/Portals/0/epc/documents/product-training/Using_GaN_r4.pdf) and [*Driving eGaN Transistors for Maximum Performance*](https://epc-co.com/epc/Portals/0/epc/documents/articles/EPC_Driving_eGaN_Transistors_fro_Maximum_Performance.pdf) — GaN-specific gate-drive, measurement and reverse conduction considerations. Device-family specifics must not be generalized.
- Infineon, [*Optimizing PCB layout for CoolGaN power transistors*](https://www.infineon.com/row/public/documents/24/42/infineon-coolgan-high-voltage-power-transistors-for-pcb-layout-optimization-applicationnotes-en.pdf) — low gate threshold, Miller current and parasitic-induced false turn-on. Manufacturer technology-specific guidance.

### 13.3 Miller clamp, DESAT, OCP and driver fault
- TI, [SLYA091, *Does My Design Need a Miller Clamp?*](https://www.ti.com/document-viewer/lit/html/SLYA091), December 2024 — clamp selection and parasitic path considerations.
- ST, [STGAP4S datasheet DS13833 Rev. 6](https://www.st.com/resource/en/datasheet/stgap4s.pdf), December 2024 — one isolated driver example with programmable DESAT/OCP, UVLO/OVLO, soft turn-off, Miller clamp and diagnostic outputs. This part is a reference example, not AEL-002 selection.
- onsemi, AND9987/D — IGBT parasitic turn-on/Miller clamp.
- Infineon gate-driver feature and parameter guides — DESAT, soft-off, active shutdown, UVLO, CMTI and propagation-delay selection.

### 13.4 Bootstrap supply
- Infineon, [AN-1123, *Bootstrap Network Analysis*](https://www.infineon.com/dgdl/Infineon-Bootstrap_Network_Analysis-ApplicationNotes-v01_00-EN.pdf?fileId=5546d462533600a40153559692661096), Rev. 1.01, 2024-11-20 — bootstrap charge, refresh limitations, integrated bootstrap behavior.
- ST, [AN5789 Rev. 1](https://www.st.com/resource/en/application_note/an5789-considerations-on-bootstrap-circuitry-for-gate-drivers-stmicroelectronics.pdf), March 2022 — bootstrap capacitor/diode selection.
- Infineon, [*Using monolithic high-voltage gate drivers*](https://www.infineon.com/assets/row/public/documents/24/42/infineon-using-monolithic-high-voltage-gate-drivers-applicationnotes-en.pdf) — bootstrap capacitor and high-side bias constraints.

### 13.5 Drive safety standards
- [IEC 61800-5-1:2022](https://webstore.iec.ch/en/publication/62103), corrected version including corrigenda through 2025-12 — adjustable-speed PDS electrical, thermal, fire, mechanical and energy hazard requirements. Scope catalogue checked; full normative text not reviewed clause-by-clause.
- [IEC 61800-5-2:2016+AMD1:2026](https://webstore.iec.ch/en/publication/117563) — functional safety of safety-related power drive systems. Scope/catalogue only; no STO implementation, certification or compliance is claimed.

출처 적용 원칙:
1. Infineon silicon MOSFET note를 GaN/IGBT의 세부 정격 근거로 사용하지 않는다.
2. GaN voltage, deadtime, reverse conduction은 exact GaN part datasheet와 matching driver manual에서 확인한다.
3. STGAP4S/ISO5851 등의 기능을 AEL-002에 존재한다고 추정하지 않는다.
4. IEC catalogue scope는 규격의 존재·범위를 알려줄 뿐 조항별 적합성 판단을 대신하지 않는다.
5. 제조사 application note는 informative design guidance이며 exact part datasheet와 표준을 대체하지 않는다.
6. 핵심 claim의 source role, revision, clause/page, conditions, cross-check, AEL applicability를 SOURCE_REVIEW_REGISTER에 기록한다.

## 14. 현재 AEL-002 판정

AEL-002는 24–48 VDC 단축 servo-drive concept이며 power-stage exact BOM, motor, load, current, cooling, switching frequency and protection architecture are not frozen. BOOSTXL-3PHGANINV is a candidate evaluation platform in prior research, but no assumption is made that a specific switch/driver or gate-drive schematic is part of the AEL-002 product.

Actual:
- MOSFET/GaN/IGBT order code: TBD
- gate driver part and bias supply: TBD
- VGS/VGE on/off values: TBD
- gate resistance and split output: TBD
- deadtime: TBD
- OCP/DESAT/UVLO thresholds and blanking: TBD
- hardware inhibit routing and latch: TBD
- thermal path and junction limits: TBD
- double-pulse/physical test authorization: NOT AUTHORIZED

**안전 상태: NO STACK / NO POWER.**
