# 12장 — 임베디드 통신과 진단 서비스

## 핵심 질문과 학습 목표

통신으로 수신한 데이터는 곧바로 실행 가능한 제어 명령이 아니다. 물리 신호, frame, serialization, 무결성, 신선도, 운전 상태, 안전 권한을 각각 확인해야 한다. 통신은 fault를 임의 해제하거나 PWM을 직접 허가할 수 없다.

이 장을 마치면 UART/RS-485, CAN/CAN-FD, framing/serialization, endian/version/length/CRC, sequence/timestamp/timeout, command·telemetry·diagnostic·parameter 서비스 분리, explicit arm과 fault latch/re-arm을 설명하고 검증할 수 있다.

## 1. 통신 계층과 권한 경계

택배에 비유하면 물리계층은 도로와 차량, link는 상자와 배송 규칙, 응용 프로토콜은 문서 형식과 업무 규칙, safety policy는 현재 이 요청을 실행해도 되는지 판단하는 승인 절차다. 도로가 정상이고 상자 CRC가 맞아도 내용이 안전하다는 뜻은 아니다.

| 계층 | 책임 | 책임지지 않는 것 |
|---|---|---|
| PHY | 전기 신호, 전압, 차동, 케이블, 종단, 절연 | 명령 의미 |
| Link/controller | bit/frame, arbitration, link CRC, ACK, error confinement | 모터 운전 허가 |
| Transport | framing, sequence, timeout, 재조립 | fault 해제 |
| Application protocol | message ID, version, length, unit, range | 하드웨어 차단 보장 |
| Service/state policy | arm, command acceptance, parameter transaction, 진단 | 독립 하드웨어 보호 대체 |

**경계 규칙:** ISR/driver는 수신 frame을 bounded buffer에 전달한다. 통신 task는 parse·검증 후 mailbox에 게시한다. 제어 task는 정해진 control-cycle 경계에서 현재 state, 센서 validity, command limits, fault latch를 다시 확인한다. 통신 ISR은 FOC를 실행하거나 PWM register를 직접 쓰지 않는다.

## 2. UART 비동기 직렬 통신

### 2.1 8-N-1 frame

UART(Universal Asynchronous Receiver/Transmitter)는 별도 clock 선 없이 송수신기가 약속한 baud rate와 frame 형식으로 bit를 주고받는다.

8-N-1은 idle logic 1, start bit 0 1개, data 8개(흔히 LSB first), parity 없음, stop bit 1개다. payload 8 bit를 보내기 위해 총 10 bit가 필요하므로 payload 효율은 8/10=80%다. parity를 추가하면 8/11≈72.7%다. header, CRC, delimiter, escaping, inter-frame gap과 응답 대기는 별도 overhead다.

Baud는 symbol/s다. 일반적인 UART NRZ에서는 1 symbol=1 bit이므로 bit/s와 수치가 같지만, 다른 변조 방식까지 항상 같다고 일반화하면 안 된다. 수신기는 start edge를 기준으로 정해진 sample point에서 data/parity/stop을 읽는다. clock 오차, jitter, noise, rise/fall time, sampling 설정이 framing error를 만든다.

UART peripheral은 byte stream을 제공할 뿐 응용 message 경계를 자동으로 정의하지 않는다. 고정 길이, length prefix, delimiter+escaping, COBS 등으로 frame을 정의해야 한다. parity/framing/overrun error와 application CRC error는 각각 별도 카운터로 관리한다. overrun은 byte 손실 가능성이 있으므로 현재 frame을 이어 붙이지 말고 parser를 재동기화한다.

## 3. RS-485 차동 물리계층과 half-duplex

### 3.1 차동 전송

RS-485는 차동 전기 인터페이스다. 수신기는 두 선 사이의 차동 전압을 판정한다. 두 선에 비슷하게 결합되는 공통모드 잡음에 강하지만, 허용 common-mode 범위, 절연, 접지·shield 설계가 필요하다. UART는 논리 데이터/주변장치이고 RS-485는 케이블의 물리계층이다. 둘은 함께 쓰일 수 있지만 같은 프로토콜이 아니다.

트랜시버는 MCU TX/RX 논리 신호와 차동 버스 신호를 변환한다. A/B 이름의 극성은 자료마다 혼동될 수 있으므로 정확한 부품의 진리표와 회로 net name을 확인한다.

### 3.2 Half-duplex 방향 제어

2-wire half-duplex는 하나의 차동 pair를 송신과 수신이 시간 분할해 공유한다. 일반적인 제어 신호는 DE(Driver Enable), /RE(Receiver Enable; active-low 표기가 흔함)다. 실제 polarity는 선택한 transceiver datasheet로 확인한다.

송신 순서:
1. bus가 idle이고 프로토콜이 송신 권한을 허용하는지 확인한다.
2. DE를 켜고 transceiver enable propagation time을 기다린다.
3. UART byte를 전송한다.
4. TX FIFO empty가 아니라 shift register의 마지막 stop bit까지 완료된 transmission-complete(TC)를 확인한다.
5. transceiver disable timing을 만족한 뒤 DE를 끈다.
6. 수신 모드로 전환하고 응답을 기다린다.

FIFO empty만 보고 DE를 내리면 마지막 byte가 잘릴 수 있다. 반대로 DE를 오래 유지하면 peer 응답을 막는다. 둘 이상의 driver가 동시에 활성화되면 contention이 발생한다.

### 3.3 종단·bias·stub

- 케이블 특성 임피던스에 맞춘 종단으로 반사를 줄인다. 일반적인 trunk는 양 끝 종단을 검토한다. 모든 node에 종단을 달면 부하가 과도해진다.
- stub를 짧게 유지한다. 허용 길이는 edge rise time과 cable propagation에 좌우된다.
- idle/open/short에서 수신 출력이 불확정이 되지 않도록 receiver fail-safe 또는 bias network를 검토한다.
- bias 저항은 종단, receiver load, driver load, idle differential margin과 저항 공차를 함께 계산한다.
- shield, signal reference, chassis/earth 결선은 EMC·절연 설계의 일부다. 접지 방식은 보편 규칙 하나로 단정하지 않는다.

TI RS-485 Design Guide는 120 Ω 케이블의 양 끝 종단, 짧은 stub, half-duplex에서 한 번에 한 driver만 활성화해야 하는 점을 설명한다. 실제 값은 케이블·트랜시버·토폴로지에 맞춰 확정한다.

### 3.4 가상 bias 계산

교육용으로 케이블 특성 임피던스 120 Ω, 양 끝 종단 각각 120 Ω이라 가정하면 단순 DC 등가 종단은

\[
R_{eq}=120\parallel120=60\ \Omega
\]

bias network가 5 V—680 Ω—차동 60 Ω 부하—680 Ω—GND의 단순 직렬 등가라고 가정하면

\[
I=5/(680+60+680)=3.52\ mA
\]
\[
V_{diff}=I\times60=0.211\ V
\]

약 211 mV다. 수신기 threshold와 저항·전원 공차를 고려하면 margin이 부족할 수 있다. 이 예제는 교육용 단순 모델이며 실제 bias 저항 선정값이 아니다.

## 4. CAN frame, identifier와 arbitration

### 4.1 기본 개념

CAN(Controller Area Network)은 multi-master broadcast bus다. identifier는 주로 메시지 의미와 우선순위를 표현한다. 수신 node는 acceptance filter 등으로 관심 frame을 선택한다.

Classical CAN은 최대 8 byte payload, 11-bit base identifier 또는 29-bit extended identifier를 지원한다. frame은 SOF, arbitration, control, data, CRC, ACK, EOF 등의 field로 구성된다. 실제 길이는 ID format, DLC, bit stuffing에 따라 달라진다.

### 4.2 Non-destructive arbitration

CAN bus에서 dominant bit는 recessive bit를 덮는다. 여러 node가 동시에 전송하면 각 node가 송신 bit와 bus bit를 비교한다. arbitration field에서 recessive를 보냈는데 dominant를 읽은 node는 전송을 멈추고 수신자로 남는다. 우선순위가 높은 frame은 중단 없이 계속된다.

동일한 frame format과 arbitration 조건에서는 숫자가 작은 identifier가 보통 더 높은 우선순위를 갖는다. 그러나 base/extended format의 IDE/SRR/RTR 위치도 arbitration에 관여하므로 서로 다른 format을 단순 정수 ID 비교로만 정렬하면 안 된다.

ID 설계에서는 시간 민감 제어/보호 상태 메시지를 높은 우선순위로, 대량 진단 dump와 parameter transfer를 낮은 우선순위로 배치하고 낮은 우선순위의 worst-case delay도 계산한다. CAN ACK는 최소 한 node가 frame을 정상 수신했다는 link-level 확인이다. 의도한 application peer가 명령을 실행했다는 확인이 아니므로 application ACK를 별도 정의한다.

### 4.3 Bit timing

Nominal bit time은 개념적으로 다음 구간의 합이다.

\[
t_{bit}=t_{SYNC}+t_{PROP}+t_{PH1}+t_{PH2}
\]

SYNC_SEG는 edge 동기화, PROP_SEG는 cable/transceiver propagation 보상, PHASE_SEG1/2는 sample point 전후의 위상 보정에 쓰인다. 실제 prescaler, time quantum, SJW, sample point, oscillator tolerance, transceiver delay, cable topology를 MCU reference manual과 network design으로 확인한다. bitrate 숫자만 맞춘다고 통신이 안정적이지 않다.

### 4.4 CAN-FD

CAN FD(Flexible Data-rate)는 최대 64 byte payload를 지원한다. BRS(Bit Rate Switch)를 사용하면 arbitration phase의 nominal bit rate와 data phase의 faster bit rate를 분리할 수 있다. FDF, BRS, ESI 등 확장 control field가 있으며 CAN FD는 remote frame을 지원하지 않는다.

ISO CAN FD의 CRC는 payload 길이에 따라 17 bit 또는 21 bit다. FD CRC 영역에는 고정 stuff bit 등 추가 보호가 있다. 따라서 CAN-FD는 단순히 Classical CAN payload 길이만 늘린 형식이 아니다. Controller와 transceiver의 ISO CAN-FD 지원, topology, cable, sample point margin을 확인한다. Classical-only node와 FD node의 혼합 운용은 상호운용성을 검토하지 않고 가정하지 않는다.

CAN FD data phase 속도는 controller뿐 아니라 모든 node transceiver, cable, topology, ringing과 clock tolerance가 지원해야 한다. CiA의 CAN FD system design 자료는 bit timing과 clock tolerance를 별도 설계 항목으로 다룬다.

### 4.5 Bus load 근사

\[
L=\frac{\sum_i N_i f_i}{R}
\]

N_i는 stuffing 등을 반영한 frame wire bit 수, f_i는 초당 전송 frame 수, R은 bus bit/s다.

교육용으로 Classical CAN frame 한 개를 stuffing 포함 130 bit라 가정한다. 500 kbit/s bus에서 1 kHz 메시지 2개와 100 Hz 메시지 4개가 있다면

\[
B=130(2\times1000+4\times100)=260000\ bit/s
\]
\[
L=260000/500000=0.52=52\%
\]

이 값은 평균 부하 근사다. 실제 worst-case response time에는 arbitration, release jitter, burst, stuffing worst case, retransmission, error frame, intermission과 priority blocking을 반영한다. 평균 52%만으로 deadline 충족을 증명할 수 없다. CAN FD는 nominal/data phase bit 수를 각 bitrate로 나눠 전송시간을 계산한다.

## 5. CAN error-active, error-passive, bus-off와 recovery

CAN controller는 TEC(Transmit Error Counter), REC(Receive Error Counter)로 error confinement을 관리한다. 대표 상태는:
- Error-active: 정상 오류 신호를 낼 수 있는 상태.
- Error-passive: TEC 또는 REC가 128 이상인 상태.
- Bus-off: TEC가 256 이상이 되어 node 송신이 차단되는 상태.

세부 counter update 예외와 recovery timing은 적용 ISO 11898-1 edition 및 controller reference manual을 따른다. 애플리케이션이 counter를 임의 초기화할 수 있다고 가정하지 않는다.

주요 원인은 잘못된 bit timing, 종단/배선/극성 오류, 긴 stub, oscillator tolerance, common-mode 초과, EMI, connector 단선/단락, FD/non-FD 설정 불일치다. 진단에는 TEC/REC, controller status, last error code, bus state, restart count, timeout, peer, sequence를 fault record에 남긴다.

Bus-off recovery 정책:
1. bus-off event를 감지하고 통신 상태를 BUS_OFF로 전환한다.
2. 송신 요청과 application command를 중지/무효화한다.
3. command freshness 상실 시 사전 정의된 controlled stop 또는 inhibit policy를 실행한다.
4. TEC/REC와 error code를 fault record에 보존한다.
5. controller가 요구하는 bus idle/recovery 조건과 대기시간을 만족한 뒤 bounded retry로 통신 controller만 재초기화한다.
6. peer, protocol version, heartbeat, session과 sequence baseline을 재검증한다.
7. 통신 복구 후에도 drive는 DISARMED를 유지한다. 새 explicit arm과 interlock 확인이 있어야 한다.
8. 반복 bus-off는 lockout/latched communication fault로 올리고 무한 자동 재시작을 금지한다.

통신 controller의 bus-off 해제는 motor safety fault clear가 아니다.

## 6. Framing, serialization, endian, version, length, CRC

### 6.1 Frame 경계

UART/RS-485는 byte stream이므로 parser가 frame 경계를 복원해야 한다. 방법은 fixed length, length prefix, delimiter+escaping, COBS 등이다. 각 방식은 최대 frame 크기, timeout, 손상 후 재동기화 특성이 다르다.

교육용 frame은 delimiter 0x7E, escape 0x7D, escape 다음 byte XOR 0x20으로 정의한다. parser는 최대 길이와 inter-byte timeout을 가진다.

### 6.2 교육용 wire schema

모든 multi-byte integer는 little-endian이라고 가정한다. C struct를 그대로 memcpy하여 wire format으로 사용하지 않는다. padding, alignment, compiler ABI, enum width, endian이 달라질 수 있기 때문이다.

| 순서 | 필드 | 크기 | 설명 |
|---|---|---:|---|
| 1 | SOF | 1 B | 0x7E |
| 2 | protocol_version | 1 B | 예: 1 |
| 3 | message_type | 1 B | command/telemetry/diag/parameter |
| 4 | flags | 1 B | 예약 bit는 0 |
| 5 | sequence | 2 B | 송신자별 modulo-65536 |
| 6 | sender_time | 4 B | sender monotonic tick |
| 7 | payload_length | 2 B | message별 상한 적용 |
| 8 | payload | 0…N B | message별 schema |
| 9 | CRC16 | 2 B | header+payload |
| 10 | EOF | 1 B | 0x7E, 내부 delimiter escape |

CRC 교육용 선택은 CRC-16/CCITT-FALSE: polynomial 0x1021, init 0xFFFF, refin/refout=false, xorout=0x0000. ASCII "123456789"의 check value는 0x29B1이다. CRC byte wire order도 명시해야 하며 이 예제에서는 high byte first로 전송한다. 실제 구현은 test vector를 코드와 문서에서 고정한다.

CRC는 우발적 손상 검출용이며 sender 인증이 아니다. 공격자는 payload와 CRC를 함께 다시 계산할 수 있다. 위협 모델에 따라 MAC/서명, key lifecycle, replay protection, secure boot와 signed update를 별도로 설계한다.

### 6.3 Parser 검증 순서

1. delimiter/escape 처리와 bounded frame 수집.
2. 최대 길이 초과, malformed escape, inter-byte timeout 검사.
3. 최소 header 길이 검사.
4. protocol version과 message type 허용 여부 검사.
5. payload_length가 message 최대값 및 실제 길이와 일치하는지 검사.
6. CRC 검사.
7. sequence/session/freshness 검사.
8. 명시적 endian decode, unit/range/cross-field 검사.
9. 현재 drive state와 safety policy 검사.
10. 검증된 immutable snapshot만 control mailbox에 게시.

length 확인 전에 payload를 읽거나 CRC 범위를 계산하지 않는다. unaligned byte buffer를 struct pointer로 cast하지 않는다. major version 불일치는 reject한다. unknown message type은 무시하고 카운터를 남긴다. reserved flags는 정의된 값만 허용한다. protocol version과 parameter schema version은 별개다.

## 7. Sequence, timestamp, timeout, stale/replay reject

### 7.1 Sequence wrap

16-bit sequence의 modular difference:

\[
\Delta=(new-old)\bmod 2^{16}
\]

0<Δ<32768이면 new가 앞선 것으로 판단한다. Δ=0은 duplicate, Δ=32768은 모호하므로 reject, Δ>32768은 old/replay로 취급한다. 이 방식은 비교 사이 sequence gap이 half-range보다 작다는 가정이 필요하다. 장시간 단절 뒤에는 새 session/handshake로 baseline을 재설정한다.

가상 예: old=65530, new=4이면 Δ=10이므로 새 frame이다. old=100, new=99이면 Δ=65535이므로 old frame이다.

### 7.2 Timestamp clock domain

sender_time은 sender monotonic clock에서 만든다. receiver clock과 동기화되지 않았다면 두 timestamp를 직접 빼서 one-way latency라고 부르면 안 된다. 안전한 freshness는 receiver local monotonic arrival time을 기록해 마지막 유효 update 이후 경과시간으로 판단한다. 검증된 clock sync와 offset/error bound가 있을 때만 sender timestamp age를 사용한다.

Chapter 10의 timer wrap 규칙을 따른다. 32-bit microsecond tick은 약 71.6분마다 wrap한다. modular subtraction을 쓰고 timeout은 반주기보다 짧게 제한한다.

### 7.3 Timeout

message class마다 주기와 timeout을 정의한다. 예를 들어 교육용 command 주기 10 ms, timeout 30 ms는 3-period 정책이다. 실제 timeout은 control bandwidth, inertia, stop distance, network jitter, task scheduling, peer failure analysis로 정한다. timeout 이후 마지막 command를 무기한 유지하지 않는다. link가 복구되어도 이전 torque/speed command를 자동 재개하지 않는다.

가상 계산: 마지막 수신 local tick이 1,000,000 µs이고 timeout=30,000 µs라면 현재 tick 1,029,999 µs에서 age=29,999 µs다. 1,030,000 µs에서 age=30,000 µs다. 정책을 age >= timeout으로 정의하면 정확히 30 ms부터 stale다.

## 8. 서비스 분리

### 8.1 Command service

속도/토크/위치 setpoint, mode request, arm request를 처리한다. 단위, sign convention, range, rate/acceleration/jerk limit을 명시한다. 수신은 acceptance가 아니다. 제어 task가 현재 state와 safety conditions를 확인한 뒤 수락한다. received/validated/accepted/applied/rejected ACK 상태를 구분한다.

### 8.2 Telemetry service

상태, current/voltage, speed/position, temperature, DC bus, control mode, fault summary를 제공한다. 각 값에 timestamp, validity, unit, scale, source를 붙인다. Chapter 08 dq/FOC state, Chapter 09 rotor angle/sensor validity, Chapter 10 ADC aperture timestamp와 연계한다. DMA-owned buffer를 직접 읽지 않고 소유권이 명확한 snapshot을 전송한다. telemetry congestion은 control task를 block하지 않는다.

### 8.3 Diagnostics service

active/latched fault, warning, UART overrun/framing/CRC, CAN TEC/REC/bus-off, timeout, sequence reject, queue overflow, watchdog 상태를 제공한다. Chapter 11 fault record의 code, source, first/last timestamp, occurrence count, operating state, captured measurement를 재사용한다. ISR은 짧은 event만 bounded queue에 넣고 formatting/transmission은 낮은 우선순위 task에서 한다.

### 8.4 Parameter transfer service

Chapter 11의 magic, schema version, length, CRC, range, cross-field validation을 재사용한다. block transfer에는 transaction ID, block index, total length, integrity, timeout, retry limit을 둔다. 수신 중 parameter를 active control values에 덮어쓰지 않는다.

전체 수신 → schema/CRC/range/cross-field/hardware compatibility 검증 → inactive NVM slot 기록 → read-back/CRC 확인 → commit marker 순으로 처리한다. 적용은 DISARMED 또는 승인된 maintenance state에서만 한다. motor pole-pair, encoder direction, current scaling, FOC convention 간 모순도 검사한다.

### 8.5 Firmware update

Firmware update는 parameter transfer와 별도 subsystem이다. signed image, authenticated boot chain, anti-rollback, power-fail-safe slot, compatibility, recovery bootloader가 필요하다. CRC만으로 authenticity를 보장하지 않는다. update 중 drive는 DISARMED/PWM inhibit 상태여야 한다.

## 9. Safe command semantics와 state machine

### 9.1 ACK의 세 단계

- Received: frame 수신/link integrity 확인.
- Accepted: schema, freshness, range, state policy를 통과.
- Applied/Completed: control cycle 또는 transaction에서 실제 적용/완료 확인.

CAN ACK bit만으로 application command 실행을 주장하면 안 된다.

### 9.2 Command pipeline

PHY → Frame parser → CRC/length → Sequence/freshness → Schema/range → State/safety policy → Control mailbox.

Control task가 mailbox snapshot을 읽을 때 drive state, fault latch, sensor validity, command limits, session과 deadline을 다시 확인한다.

### 9.3 Drive state

~~~text
BOOT/RESET
    |
    v
INIT_INHIBIT -- self-check/config valid --> DISARMED
                                            |
                              explicit arm + interlocks
                                            v
                                        ARM_PENDING
                                            |
                                   control task confirms
                                            v
                                        ARMED_IDLE
                                            |
                                  fresh bounded command
                                            v
                                         RUNNING
                                            |
                                  stop / command timeout
                                            v
                                         STOPPING
                                            |
                                         DISARMED

Any state -- safety fault / critical sensor invalid /
             hardware trip / watchdog failure --> FAULT_LATCH

FAULT_LATCH -- supervised clear + cause absent + safe interlocks --> DISARMED
~~~

- INIT_INHIBIT: reset 직후 output inhibit, config/self-check.
- DISARMED: 출력 허가 없음.
- ARM_PENDING: explicit arm과 interlock 확인.
- ARMED_IDLE: 준비됐으나 유효 command 없음.
- RUNNING: fresh bounded command로 제어.
- STOPPING: 승인된 stop profile 또는 inhibit sequence.
- FAULT_LATCH: fault 원인을 보존하고 재무장 금지.

통신 단절 시 STOPPING 또는 FAULT_LATCH 선택은 load inertia, stop distance, regeneration, independent hardware inhibit를 포함한 위험 분석으로 정한다. 이 장은 실제 AEL-002 stop profile을 확정하지 않는다.

### 9.4 Fault latch 권한

통신은 fault를 조회하고 acknowledgement(읽음 확인)를 할 수 있다. 하지만 fault 원인 제거, hardware trip release, sensor/DC bus/temperature/current safe state를 증명할 수 없다. 따라서 통신 명령은 FAULT_LATCH를 직접 clear하거나 PWM enable을 set할 수 없다.

clear는 supervised maintenance/commissioning 권한, cause-absent 확인, hardware trip release, sensor validity, DC bus/thermal/current interlock과 operator action을 요구한다. clear 성공은 DISARMED로만 이동한다. RUNNING으로 직접 가지 않는다. Chapter 11처럼 fault set과 clear가 동시에 오면 set이 우선한다.

통신 복구 state:

~~~text
NORMAL -- timeout/bus-off --> COMM_DEGRADED
COMM_DEGRADED -- bounded retry --> LINK_RESTORED
LINK_RESTORED -- peer/version/session/heartbeat valid --> DISARMED
DISARMED -- new explicit arm + interlocks --> ARM_PENDING

Any safety fault -------------------------------> FAULT_LATCH
FAULT_LATCH -- supervised clear only ------------> DISARMED
~~~

이전 setpoint를 자동 재생하지 않는다.

## 10. Chapter 08~11 실시간 통합

- **Chapter 08 FOC:** 통신 task는 PWM/ADC schedule과 독립이다. command를 current/voltage/thermal/speed limits와 sign convention에 맞춰 변환한다. 통신 ISR에서 PI integrator나 PWM compare를 수정하지 않는다.
- **Chapter 09 sensor:** telemetry는 angle/count와 함께 validity, timestamp, sensor mode, diagnostic flags를 제공한다. stale encoder, Hall invalid sector, Resolver amplitude fault를 정상값처럼 전송하지 않는다.
- **Chapter 10 timing/DMA:** DMA-owned RX/TX/telemetry buffer를 CPU가 읽거나 재사용하지 않는다. DMA 완료 후 ownership을 넘기고 필요 시 cache maintenance/alignment를 확인한다. ISR은 bounded queue에 event를 넣고 parse/CRC/formatting은 task에서 한다. queue full, DMA overrun, UART overrun, CAN FIFO overflow를 별도 계측한다.
- **Chapter 11 C/parameter/fault:** endian decode는 명시적 shift/mask, length는 overflow-safe arithmetic, volatile은 ownership/atomicity 대체물이 아니다. protocol schema와 NVM parameter schema는 별도 version이다. communication error counter와 application reject reason을 fault record에 구분해 남긴다.

## 11. 가상 계산 예제와 전체 풀이

### A — UART throughput

8-N-1, 115200 baud, payload 24 byte, header 10 byte, CRC 2 byte, delimiter 2 byte, escaping 없음으로 가정한다. 총 38 byte × 10 bit = 380 bit다.

\[
T=380/115200=0.0032986\ s\approx3.30\ ms
\]

이론상 최대 약 303 frame/s다. turnaround, task scheduling, gap, escaping, retry는 제외했다.

### B — RS-485 byte time과 guard

115200 baud, 8-N-1이면 마지막 byte wire time은 10/115200=86.8 µs다. UART TC 이후 transceiver disable delay 1 µs, peer guard 20 µs라고 가정하면 다음 송신 전에 적어도 21 µs guard가 필요하다. 이 값들은 교육용 가정이며 실제 부품/peer timing으로 결정한다.

### C — CAN load

frame=130 bit, 500 kbit/s, 1 kHz 메시지 2개, 100 Hz 메시지 4개:

\[
B=130(2\times1000+4\times100)=260000\ bit/s
\]
\[
L=260000/500000=52\%
\]

남은 48%가 전부 가용한 것은 아니다. error/retry/burst와 response-time margin을 확보해야 한다.

### D — CAN-FD 구간별 전송시간

교육용으로 arbitration/control 40 bit @500 kbit/s, data+CRC 관련 600 bit @2 Mbit/s, ACK/EOF/intermission 20 bit @500 kbit/s라 가정한다. stuffing은 bit count에 이미 포함했다고 가정한다.

\[
T=40/500000+600/2000000+20/500000
\]
\[
T=80+300+40=420\ \mu s
\]

규격 frame의 실제 bit count가 아니라 서로 다른 bitrate 구간을 계산하는 예다. 실제 계산에는 ID, DLC, CRC, stuff bits, BRS, controller timing을 반영한다.

### E — sequence wrap

old=65530, new=4인 16-bit counter:

\[
\Delta=(4-65530)\bmod65536=10
\]

0<10<32768이므로 새 frame이다. old=100, new=99이면 Δ=65535이므로 old frame으로 reject한다.

### F — CRC test vector

CRC-16/CCITT-FALSE: poly=0x1021, init=0xFFFF, refin/refout=false, xorout=0. "123456789"의 기대값은 0x29B1이다. 다르면 polynomial, bit order, init, reflection, xorout을 확인한다. CRC wire byte order는 별도 규정한다.

## 12. 연습문제와 전체 풀이

1. UART 8-N-1에서 100 byte를 9600 baud로 보내는 최소 시간은?
2. RS-485 120 Ω 종단 2개의 병렬 등가값은?
3. TX FIFO empty만 확인하고 DE를 끄면 왜 위험한가?
4. Classical CAN과 CAN FD의 최대 payload는?
5. 동일 arbitration format에서 ID 0x080과 0x180 중 우선순위가 높은 것은?
6. 250 kbit/s bus에서 125 bit frame 4개가 각각 100 Hz면 단순 평균 load는?
7. TEC=130과 TEC=256의 상태는?
8. old=65534, new=1인 16-bit sequence의 delta는?
9. old=1000, new=500이면 새 frame인가?
10. clock sync 없이 sender/receiver timestamp를 빼면 안 되는 이유는?
11. CRC 정상 command를 그대로 실행하면 안 되는 이유 3가지는?
12. bus-off 해제 직후 이전 torque command를 재개하면 안 되는 이유는?
13. DMA-owned telemetry buffer를 읽을 때 문제는?
14. parameter block CRC 통과만으로 active parameter를 바꿔도 되는가?
15. 통신으로 FAULT_LATCH를 직접 clear하면 안 되는 이유는?

**전체 풀이**

1. byte당 10 bit이므로 100 byte=1000 bit. T=1000/9600=0.10417 s≈104.2 ms다.
2. 120 Ω ∥ 120 Ω=(120×120)/(120+120)=60 Ω다.
3. FIFO empty여도 shift register가 마지막 byte를 전송 중일 수 있다. stop bit 종료 전 DE를 끄면 frame이 잘린다. UART TC를 확인한다.
4. Classical CAN 8 byte, CAN FD 64 byte다.
5. 같은 format이면 숫자가 작은 0x080이 높은 우선순위다. base/extended 형식은 arbitration field 전체를 비교한다.
6. 125×4×100=50,000 bit/s. 50,000/250,000=20%다. stuffing/retry/error 제외.
7. TEC 130은 error-passive 기준 128 이상. TEC 256은 bus-off 조건이다. 실제 controller 상태와 counter update 규칙을 확인한다.
8. (1−65534) mod 65536=3. 0<3<32768이므로 새 frame.
9. (500−1000) mod 65536=65036. 32768보다 크므로 old/replay reject.
10. 두 clock은 origin/rate/offset이 다를 수 있다. sync 없이는 one-way latency/age가 아니다. receiver local arrival time을 사용하거나 검증된 clock sync가 필요하다.
11. stale/replay일 수 있고, 범위를 벗어날 수 있으며, 현재 drive state/interlock/fault에서 허용되지 않을 수 있다. CRC는 sender 인증도 아니다.
12. 통신 복구는 기계 상태, sensor validity, fault cause, command freshness를 복구하지 않는다. DISARMED에서 새 session/explicit arm을 요구한다.
13. DMA 갱신 중 torn snapshot, CRC/length 불일치, cache stale data, ownership race가 발생할 수 있다. DMA 완료 뒤 CPU ownership을 얻어 snapshot을 복사한다.
14. 아니다. 전체 length/version/schema/CRC/range/cross-field/hardware compatibility를 검사하고 inactive NVM slot write/read-back/commit 후 safe state에서 적용한다.
15. 통신 peer는 fault cause, hardware trip release, sensor/DC bus/thermal/current 안전을 보증할 수 없다. supervised clear만 허용하고 clear 후에도 DISARMED에 머문다.

## 13. Fault injection 및 검증 템플릿

### 13.1 Protocol definition record

| 항목 | 정의/결정 | 현재 상태 |
|---|---|---|
| PHY | UART/RS-485/CAN/CAN-FD | TBD |
| Transceiver/order code | exact part/revision | TBD |
| Connector/pinout | pin, polarity, shield/reference | TBD |
| UART baud/parity/stop | exact config/tolerance | TBD |
| CAN nominal/data bit rate | exact timing | TBD |
| CAN ID map | ID format, priority, cycle, DLC | TBD |
| Network topology | node count, cable, stub | TBD |
| Termination/bias | value, location, load calculation | TBD |
| Isolation/common-mode | barrier, CMTI, grounding | TBD |
| Protocol version/schema | compatibility, message layout | TBD |
| CRC | algorithm, init, reflection, xorout, wire order | TBD |
| Sequence/session | width, wrap, replay policy | TBD |
| Timestamp | clock, tick, synchronization, wrap | TBD |
| Timeout/stop policy | per-message deadline and action | TBD |
| SDK/driver/compiler | exact target and version | TBD |
| Safety authority | arm/clear/re-arm owner | TBD |

### 13.2 Message contract

| Field | Required definition |
|---|---|
| Message ID/type | unique and versioned |
| Producer/direction | node/service |
| Purpose | command/telemetry/diagnostic/parameter/update |
| Payload length | min/max/exact |
| Schema | offset, width, endian, signedness |
| Unit/scale | SI unit, resolution, valid range |
| Sequence | source, width, duplicate/out-of-order policy |
| Timestamp | clock domain, tick, age semantics |
| Integrity | link CRC + application CRC/MAC as needed |
| Timeout | deadline and stale action |
| State permission | states accepting message |
| ACK | received/accepted/applied/rejected |
| Fault behavior | counter, record, safe state |
| Verification | test ID, evidence, commit SHA |

### 13.3 Fault injection matrix

| Test | Injection | Expected behavior |
|---|---|---|
| COM-01 | truncated frame/missing EOF | discard, resync, count |
| COM-02 | malformed escape | reject, bounded parser memory |
| COM-03 | payload length too large | reject before access |
| COM-04 | CRC bit flip | reject, mailbox unchanged |
| COM-05 | unsupported major version | reject |
| COM-06 | reserved flag set | reject |
| COM-07 | duplicate sequence | no double apply |
| COM-08 | old/replay sequence | reject and count |
| COM-09 | sequence wrap | modular compare correct |
| COM-10 | timeout/stale command | invalidate, defined stop/inhibit |
| COM-11 | RX burst/queue full | bounded drop, no FOC deadline miss |
| COM-12 | UART overrun/framing/parity | discard affected frame, resync |
| COM-13 | two RS-485 drivers active | contention prevented by design |
| COM-14 | DE released before UART TC | truncated byte detected |
| COM-15 | wrong CAN timing/termination | error counters visible |
| COM-16 | CAN bus-off | inhibit TX, record, bounded recovery, disarmed |
| COM-17 | repeated bus-off | retry budget exhausted, lockout |
| COM-18 | high-priority CAN burst | lower-priority latency measured |
| COM-19 | DMA ownership violation | consumer rejects snapshot |
| COM-20 | parameter block loss/reorder | abort/retry, active record unchanged |
| COM-21 | valid CRC but out-of-range command | application reject |
| COM-22 | command while fault latched | reject, latch remains |
| COM-23 | remote fault-clear request | reject, no state transition |
| COM-24 | link restored after timeout | drive remains DISARMED |
| COM-25 | link ACK but command not applied | status not falsely marked applied |
| COM-26 | interrupted firmware update | recovery/rollback, no arm |

### 13.4 Timing/load evidence

| 항목 | 기록할 증거 |
|---|---|
| UART throughput | bytes/s, frame length, escaping, turnaround |
| RS-485 DE | waveform vs UART TC and transceiver timing |
| CAN bus load | message matrix, worst-case stuffing/retry assumptions |
| CAN response time | priority, burst, jitter, blocking, deadline |
| CAN-FD timing | nominal/data rate, sample point, clock/cable margin |
| ISR/DMA | latency, ownership, overrun |
| FOC interference | WCET/deadline at maximum communication load |
| Timeout | disconnect injection and detection/action time |
| Recovery | bus-off/restart attempts/final state |
| Safety | set/clear race, explicit arm, no auto-resume |

### 13.5 Acceptance checklist

- [ ] PHY, link framing, application protocol이 분리되어 있다.
- [ ] parser는 bounded length, timeout, escaping, resync를 가진다.
- [ ] RS-485는 UART TC 후 DE를 해제한다.
- [ ] CAN ID, bit timing, bus load, worst-case response time을 분석했다.
- [ ] error-passive/bus-off와 bounded recovery를 검증한다.
- [ ] CAN ACK를 application completion으로 오해하지 않는다.
- [ ] endian/version/length/CRC test vector가 고정됐다.
- [ ] duplicate/old/stale/replay/out-of-range command를 reject한다.
- [ ] telemetry snapshot과 DMA ownership이 보장된다.
- [ ] 통신 부하가 Chapter 10 FOC deadline을 침범하지 않는다.
- [ ] parameter transfer가 active parameter를 부분 갱신하지 않는다.
- [ ] 통신은 FAULT_LATCH clear/PWM enable 권한이 없다.
- [ ] link recovery 뒤 새 explicit arm 전까지 DISARMED다.
- [ ] 실제 설정은 근거가 없으면 TBD다.

## 14. AEL-002 적용 상태 — TBD 유지

| 항목 | 상태 | 확정 근거 |
|---|---|---|
| UART peripheral/instance | TBD | exact MCU/pin mux/SDK |
| RS-485 transceiver | TBD | BOM/schematic/datasheet |
| RS-485 connector/A-B | TBD | schematic/physical revision |
| DE/RE GPIO/polarity | TBD | pin map/transceiver truth table |
| UART baud/config | TBD | peer requirement/clock budget |
| CAN controller/transceiver | TBD | selected MCU/SDK/BOM |
| CAN connector/pinout | TBD | schematic/physical inspection |
| Nominal/data bit rate | TBD | topology/cable/clock/peer |
| CAN ID allocation | TBD | message matrix/priority analysis |
| Network topology/node count | TBD | system requirement |
| Isolation/ground/shield | TBD | safety/EMC architecture |
| Protocol profile | TBD | peer/product requirement |
| Timeout/stop profile | TBD | motor/load/inertia/safety analysis |
| Authentication/key management | TBD | threat model |
| SDK/driver/compiler | TBD | exact target source/build |

F280039C 또는 STM32G4가 후보라는 사실만으로 UART/CAN instance, pin mux, transceiver, driver, bit timing을 확정하지 않는다. 평가보드 후보가 실제 AEL-002 통신 인터페이스가 실장되었다는 증거도 아니다.

**NO STACK / NO POWER.** 문서·계산·host test 계획은 보드 연결, jumper 조작, 전원 인가를 허가하지 않는다.

## 15. 출처와 추가 학습

1. Texas Instruments, [The RS-485 Design Guide (SLLA272D Rev. D)](https://www.ti.com/lit/an/slla272d/slla272d.pdf) — differential signaling, half/full duplex, driver direction, termination/stub, fail-safe.
2. Texas Instruments, [Fail-safe biasing design](https://www.ti.com/document-viewer/lit/html/SSZT656) — open/short/idle bus와 receiver bias.
3. CAN in Automation, [CAN FD — the basic idea](https://can-cia.org/can-knowledge/can-fd-the-basic-idea) — payload, BRS, arbitration/data phase, CRC.
4. CAN in Automation, [Technical documents](https://can-cia.org/cia-groups/technical-documents) — CiA 601 CAN-FD physical interface/controller/system design과 bit timing/clock tolerance.
5. ISO 11898-1:2024, CAN data link layer and physical coding sublayer — 적용 edition과 관련 정오표를 확인한 뒤 frame/arbitration/error confinement의 normative 근거로 사용한다. 공개 CiA 자료는 표준 원문을 대체하지 않는다.
6. Microchip, [MCP25xxFD Family Reference Manual](https://ww1.microchip.com/downloads/en/DeviceDoc/MCP251XXFD-CAN-FD-Controller-Module-Family-Reference-Manual-20005678B.pdf) — CAN FD controller의 TEC/REC와 error-active/error-passive/bus-off 구현 예. 2015 edition과 해당 controller family에 한정된 구현 참고자료다.
7. TI, [ISO15/ISO35 RS-485 transceiver datasheet](https://www.ti.com/lit/ds/symlink/iso15.pdf) — half/full-duplex topology, enable pins, termination application example. 해당 부품군의 예시이지 AEL-002 BOM 근거가 아니다.
8. TI, [RS-485 transceiver FAQ](https://www.ti.com/document-viewer/lit/html/SSZT500) — termination, cable impedance matching에 대한 보조 설명.
9. CAN in Automation, [CiA 601 series: CAN FD guidelines and recommendations](https://can-cia.org/can-knowledge/cia-601-series-can-fd-guidelines-and-recommendations) — physical interface, controller, system design, clock tolerance와 bit-timing evaluation. Technical report와 later drafts의 publication status를 구분한다.

일반 원리 출처는 AEL-002의 실제 MCU peripheral, transceiver, pin mux, wiring, network bit rate, isolation, SDK integration을 입증하지 않는다.

## 16. 장 완료 기준

- [ ] UART 8-N-1과 throughput을 계산한다.
- [ ] UART와 RS-485의 계층 차이를 설명한다.
- [ ] RS-485 DE/RE와 TC 순서를 설명한다.
- [ ] termination/bias/stub를 network-level로 검토한다.
- [ ] CAN arbitration과 ACK 의미를 설명한다.
- [ ] CAN/CAN-FD payload, BRS, bit timing을 설명한다.
- [ ] bus load와 worst-case response-time 한계를 설명한다.
- [ ] error-passive/bus-off와 bounded recovery를 구분한다.
- [ ] endian/version/length/CRC wire schema를 정의한다.
- [ ] sequence wrap, timestamp domain, timeout을 처리한다.
- [ ] command/telemetry/diagnostic/parameter/update를 분리한다.
- [ ] received/accepted/applied ACK를 구분한다.
- [ ] 통신으로 fault latch를 clear하거나 PWM을 직접 허가하지 않는다.
- [ ] DMA ownership과 FOC deadline을 보호한다.
- [ ] 실제 AEL-002 설정을 근거 없이 확정하지 않는다.

**현재 판정:** Chapter 12는 통신·진단 아키텍처, 가상 계산, 상태기계, fault injection 및 검증 템플릿을 정의한다. 실제 AEL-002 통신 하드웨어/배선/SDK 구현, target firmware build, bus timing measurement, SIL/HIL 또는 hardware validation을 수행했다고 주장하지 않는다.

**안전 상태: NO STACK / NO POWER.**
