# 11장 — 임베디드 C 아키텍처와 견고한 펌웨어 기반

## 안전·범위 경계

이 장은 C 언어와 펌웨어 구조를 설계·검증하는 교육 자료다. 특정 MCU용으로 빌드되거나 AEL-002 보드에서 실행된 코드가 아니다. 실제 MCU 주문 코드/revision, compiler·ABI·C dialect, SDK, startup, linker command file, memory map, FPU, cache, atomic lock-free 여부, build flags와 peripheral driver는 정확한 보드·SDK 근거를 확인하기 전까지 **TBD**다.

AEL-002는 계속 **NO STACK / NO POWER**다. 코드 예제는 일반적인 C 개념을 보여주며 실제 게이트 출력·fault pin·STO·PWM 안전을 보장하지 않는다.

## 학습 목표와 선수 지식

앞선 장과의 연결:
- 06장: PMSM 전기·기계·열 모델과 단위가 있는 물리량
- 07장: DC 링크, 인버터, 전압·전류 한계
- 08장: amplitude-invariant Clarke/Park 규약, FOC 전류 루프와 포화
- 09장: 엔코더/Hall/Resolver의 각도·속도·timestamp·validity
- 10장: ISR latency/jitter, DMA buffer ownership, ADC aperture, PWM update event, WCET

이 장을 마치면 다음을 할 수 있어야 한다.
1. 정수형의 범위·signedness·integer promotion·overflow를 분석한다.
2. fixed-point Q format과 floating-point의 오차·범위·연산 비용을 비교한다.
3. C object lifetime, memory map, stack/heap, linker/startup의 역할을 설명한다.
4. const/volatile/atomic의 보장 범위를 구분한다.
5. HAL·driver·middleware·control·application 경계를 설계한다.
6. 상태기계, fault latch, parameter validation/CRC/versioning을 설계한다.
7. 하드웨어 없이 시험할 수 있는 unit-test seam을 만든다.
8. 정적 분석과 코드 리뷰의 증거를 남긴다.

## 1. 임베디드 C를 안전하게 보는 직관

MCU 펌웨어는 센서에서 숫자를 받아 계산하고 출력 레지스터에 숫자를 쓰는 프로그램이다. 그러나 숫자는 메모리의 비트 패턴으로 저장되고, CPU와 주변장치가 그 메모리를 서로 다른 시점에 읽고 쓸 수 있다.

견고한 펌웨어는 네 질문에 답해야 한다.
- **표현:** 이 값은 몇 비트이고 어떤 단위·범위·부호인가?
- **소유:** 지금 누가 이 메모리를 읽거나 쓸 권한이 있는가?
- **시점:** 이 값은 어느 측정 시각의 값이고 언제 유효해지는가?
- **실패:** 범위 초과·통신 오류·deadline miss가 생기면 어떤 상태로 이동하는가?

비유의 한계: 변수는 단순한 종이 쪽지가 아니다. compiler 최적화, CPU memory ordering, interrupt preemption, DMA, cache, peripheral bus가 실제 관측 순서를 바꿀 수 있다. C 언어의 보장과 MCU 하드웨어 보장을 함께 확인해야 한다.

## 2. 정수형·범위·signedness

### 2.1 비트 수와 표현 범위

n-bit unsigned 정수는 0부터 \(2^n-1\)까지 표현한다.

\[
0\le x\le 2^n-1
\]

n-bit signed two's-complement 정수의 흔한 범위는

\[
-2^{n-1}\le x\le 2^{n-1}-1
\]

이다. C의 정확한 표현·폭은 타깃과 표준 버전을 확인한다. int가 반드시 32-bit라고 가정하지 않는다.

stdint.h의 uint8_t, int16_t, uint32_t 등 exact-width typedef는 해당 폭을 padding 없이 제공할 수 있을 때만 정의된다. int_least32_t, int_fast16_t는 각각 최소 폭/빠른 폭 목적이 다르다. 메모리·통신 포맷에는 명시적 폭을, 일반 산술에는 표현 범위와 성능을 확인한 타입을 선택한다.

size_t는 객체 크기/배열 길이, ptrdiff_t는 pointer 차이를 표현하는 데 사용한다. 고정된 하드웨어 레지스터 폭은 제조사 헤더와 ABI를 확인한다.

| 타입 예 | 폭 가정 시 범위 예 | 사용 주의 |
|---|---:|---|
| uint8_t | 0…255 | byte field, 작은 counter |
| int16_t | −32768…32767 | ADC 보정값, 곱셈 중간 폭 확인 |
| uint16_t | 0…65535 | raw sample, bit field |
| int32_t | −2,147,483,648…2,147,483,647 | 누산기, 위치 누적값 |
| uint32_t | 0…4,294,967,295 | timestamp tick, modular counter |
| size_t | 구현 정의 | object size/index |

### 2.2 Signed와 unsigned를 섞으면 생기는 문제

C는 integer promotion과 usual arithmetic conversions를 적용한다. 작은 정수는 int 또는 unsigned int로 승격될 수 있고, signed/unsigned 혼합 비교가 예상과 다를 수 있다.

~~~c
int32_t temperature_c = -1;
uint32_t limit = 10U;

/* 위험: usual arithmetic conversions 때문에 -1이 큰 unsigned로 변환될 수 있다. */
if (temperature_c < limit) {
    /* 사람이 예상한 비교와 다를 수 있음 */
}
~~~

의미가 맞는 타입으로 입력을 검증한 뒤 비교한다.

~~~c
bool temperature_is_below_limit(int32_t temp_c, int32_t limit_c)
{
    return temp_c < limit_c;
}
~~~

외부 입력의 부호·범위를 확인하지 않고 unsigned로 cast하지 않는다. char는 signed/unsigned가 구현 정의일 수 있으므로 숫자 데이터에는 int8_t 또는 uint8_t를 명시한다.

### 2.3 Overflow와 wraparound

Unsigned 산술은 \(2^n\) modulo로 wrap한다. 이것이 C에서 정의된 동작이어도 제어량·길이·배열 index가 wrap하면 안전하지 않다.

Signed 정수 overflow는 C에서 undefined behavior(UB)다. compiler는 signed overflow가 일어나지 않는다고 가정해 최적화할 수 있다. INT32_MAX + 1이 반드시 INT32_MIN으로 wrap한다고 가정하면 안 된다.

~~~c
/* 안전하지 않은 검사: a+b 자체가 이미 overflow일 수 있음 */
if (a + b > INT32_MAX) { }

/* 더 넓은 중간 타입에서 검사 */
bool add_i32_checked(int32_t a, int32_t b, int32_t *out)
{
    int64_t sum = (int64_t)a + (int64_t)b;
    if (sum > INT32_MAX || sum < INT32_MIN) {
        return false;
    }
    *out = (int32_t)sum;
    return true;
}
~~~

곱셈은 더 넓은 중간 타입으로 계산하되 그 중간 타입에도 충분한 범위가 있는지 증명한다. 나눗셈은 0 divisor를 검사하고 INT_MIN / -1 예외를 처리한다. shift count가 음수이거나 operand bit width 이상이면 안 된다. signed 음수의 right shift는 구현 정의일 수 있으므로 fixed-point 연산에 무심코 사용하지 않는다.

### 2.4 Saturation과 range checking

제어 알고리즘에서는 wrap보다 saturation이 적합한 경우가 많다.

~~~c
int32_t saturate_i64_to_i32(int64_t x)
{
    if (x > INT32_MAX) return INT32_MAX;
    if (x < INT32_MIN) return INT32_MIN;
    return (int32_t)x;
}
~~~

단, saturation이 항상 올바른 제어 정책은 아니다. PI 출력 포화는 anti-windup과 함께 설계하고, 센서값·명령값이 물리 한계를 벗어나면 단순 clamp 대신 invalid/fault로 처리해야 할 수 있다. **수치 표현의 saturation과 시스템 안전정책은 별개**다.

## 3. 단위·범위 계약과 수치 변환

각 신호는 타입뿐 아니라 단위와 범위를 가져야 한다.

| 신호 | 표현 예 | 계약 예 |
|---|---|---|
| ADC raw | uint16_t | 0…ADC code max, sample timestamp 포함 |
| phase current | int32_t 또는 float | A, polarity와 gain 정의 |
| electrical angle | fixed-point/float | rad 또는 turn, wrap convention 명시 |
| speed | fixed-point/float | rad/s 또는 rpm, 기계/전기 기준 명시 |
| timestamp | uint32_t | timer tick, clock source/version 명시 |
| duty | normalized/fixed-point | 0…1 또는 0…Qmax, PWM polarity 명시 |
| status | enum/bit mask | valid/fault flags 분리 |

raw ADC code를 Ampere로 바꾸는 한 가지 이상 모델은

\[
I=\frac{(code-code_{offset})V_{ref}}{2^N-1}\frac{1}{G R_{shunt}}
\]

이다. N은 ADC bit 수, Vref는 reference voltage(V), G는 analog gain, Rshunt는 ohm이다. V/Ω=A로 단위가 맞는다. 실제 converter coding, differential range, amplifier topology와 calibration coefficient를 확인해야 한다.

Chapter 08의 Clarke/Park는 입력 상전류가 같은 단위(A), 같은 측정 시각, 같은 polarity/phase mapping convention을 가져야 한다. 단위가 다른 값을 같은 구조체에 넣거나 ADC sample과 오래된 encoder angle을 timestamp 없이 섞지 않는다.

## 4. Fixed-point와 Q format

### 4.1 Fixed-point의 원리

Fixed-point는 정수에 고정된 scale을 곱해 실수를 표현한다.

\[
x_{real}=x_{stored}\times 2^{-F}
\]

F는 fractional bit 수다. signed 16-bit에 F=15를 쓰는 흔한 Q1.15 관례에서는

\[
x_{real}=x_{Q15}/32768,\qquad
-1.0\le x_{real}\le 1-2^{-15}
\]

이다. Qm.n 표기에서 m에 sign bit를 포함하는지 여부가 문헌·도구마다 다를 수 있다. 이 교재는 예제에서 총 폭과 fractional bit F를 직접 명시한다. Q1.15라는 이름만으로 형식을 추정하지 않는다.

### 4.2 덧셈·곱셈의 scale

같은 F의 두 값은 raw integer끼리 더할 수 있다(중간 overflow 검증 필수).

\[
(a2^{-F})+(b2^{-F})=(a+b)2^{-F}
\]

곱하면 fractional bit가 2F가 된다.

\[
(a2^{-F})(b2^{-F})=(ab)2^{-2F}
\]

원래 F scale로 되돌리려면 product를 \(2^F\)로 나누고 rounding/saturation을 적용한다. 중간 곱셈은 넓은 accumulator에서 수행한다.

**가상 Q1.15 계산**
- 0.5 → round(0.5×32768)=16384
- 0.25 → 8192
- raw product = 16384×8192=134,217,728
- Q30 실수값 = product/2³⁰ = 0.125
- Q15로 복원: 134,217,728/32768=4096
- 4096/32768=0.125

정수 곱의 단위는 raw²이며 scale 복원 후 원래 실수 단위의 곱이 된다.

### 4.3 Rounding, truncation, saturation

단순 right shift는 truncation 방향·음수 처리·signed shift semantics에 주의해야 한다. rounding bias를 더할 때 accumulator overflow도 검토한다. nearest-even, away-from-zero 등 rounding mode를 프로젝트에서 정의한다.

아래는 Q15 곱셈 개념 예시다. C signed right shift의 구현 의존성을 피하기 위해 나눗셈을 사용한다. 입력이 int16_t이므로 곱은 int32_t에 들어간다. 실제 DSP에서는 더 빠른 intrinsic을 쓸 수 있지만 동일한 결과·경계 동작을 시험해야 한다.

~~~c
int16_t q15_mul(int16_t a, int16_t b)
{
    int32_t product = (int32_t)a * (int32_t)b;
    int32_t rounded;

    if (product >= 0) {
        rounded = product + 16384;
    } else {
        rounded = product - 16384;
    }

    int32_t result = rounded / 32768; /* C 정수 나눗셈은 0 방향 절삭 */
    if (result > INT16_MAX) result = INT16_MAX;
    if (result < INT16_MIN) result = INT16_MIN;
    return (int16_t)result;
}
~~~

rounding tie 정책과 −1×−1의 포화 동작을 테스트로 고정한다. product의 최댓값은 \((-32768)(-32768)=1,073,741,824\)로 int32_t 범위 안이지만, 다른 누산 연산을 추가하면 재검산한다.

### 4.4 FOC에서 fixed-point가 요구하는 분석

- 전류 A, 전압 V, 속도 rad/s, 각도 rad의 scaling을 문서화한다.
- ADC offset 제거 후 signed 범위를 검증한다.
- Clarke/Park 계수와 곱셈 accumulator의 최대 합을 계산한다.
- PI 적분기와 decoupling term의 내부 범위를 분석한다.
- SVPWM modulation과 duty saturation 범위를 정의한다.
- saturation 시 integrator anti-windup과 fault 판단을 분리한다.
- 모든 곱셈/누산에 intermediate width, rounding, saturation 위치를 기록한다.
- LUT interpolation, CORDIC, trig 함수의 오차와 worst-case latency를 비교한다.

실제 AEL-002 fixed-point Q format과 scaling은 motor current/speed/voltage range, ADC scaling, compiler/MCU 연산 특성 확인 전까지 **TBD**다.

## 5. Floating-point의 장점과 위험

Floating-point는 넓은 동적 범위를 편리하게 표현하지만 모든 실수를 정확히 나타내지 않는다. 일반적인 IEEE-754 binary32 float는 24-bit 유효 정밀도(숨은 leading bit 포함), 약 7자리 십진 정밀도를 제공한다. 타깃 ABI와 compiler가 IEEE-754를 어떻게 지원하는지 확인한다.

- 매우 큰 값과 작은 값을 함께 다루기 쉽다.
- 곱셈·나눗셈·sqrt·sin/cos의 실행시간은 MCU/FPU/compiler에 따라 다르다.
- NaN, +∞, −∞, subnormal, signed zero를 처리해야 한다.
- a == b로 실수 결과를 무조건 비교하지 않는다.
- epsilon은 물리 단위와 허용오차 요구사항에 따라 정한다.
- FPU context save/restore가 ISR latency에 영향을 줄 수 있다.
- compiler fast-math 옵션은 NaN/∞/signed-zero 가정을 바꿀 수 있으므로 안전성 검토 없이 켜지 않는다.

가상 예: binary32 float에서 16,777,216보다 큰 모든 정수가 연속적으로 표현되는 것은 아니다. 따라서 32-bit timestamp를 float에 저장하면 tick 단위 구분을 잃을 수 있다. timestamp는 정수 tick으로 유지하고 차분 후 필요한 구간에서 실수 초로 변환한다.

## 6. Memory model, object lifetime와 concurrency

### 6.1 메모리 영역의 개념

~~~text
높은 주소 (개념도 — 실제 배치는 linker/MCU별)
+---------------------------+
| Stack                     | 함수 frame, local, return state
|       ↓ 또는 구현별 방향   |
|                           |
|       free space          |
|                           |
| Heap (사용 시)             | dynamic allocation
|                           |
| .bss / .data              | static/global objects
| .rodata                   | read-only constants
| .text                     | program instructions
+---------------------------+
낮은 주소
~~~

이 그림은 개념도다. Harvard/modified Harvard, flash/RAM/TCM, 여러 RAM bank, CLA/local RAM, DMA-accessible RAM, boot ROM, peripheral address space에 따라 실제 배치는 달라진다.

C의 storage duration:
- automatic: block scope local 등, 보통 stack 사용
- static: 프로그램 실행 기간 동안 존재하는 global/static object
- allocated: malloc 등으로 얻는 dynamic object
- thread: C11 thread storage duration, bare-metal에서는 사용 여부가 구현별

static 키워드는 scope/linkage와 storage duration 맥락에 따라 의미가 달라진다. 함수 내부 static은 호출 사이에 값을 유지한다. 파일 범위 static은 internal linkage를 만든다.

### 6.2 Stack

Stack은 함수 호출·local variable·return address·register spill 등에 사용될 수 있다. 깊은 재귀, 큰 local array, 중첩 ISR, FPU context로 stack이 고갈될 수 있다.

검증 방법:
- call graph와 최대 nesting을 분석한다.
- compiler stack usage report를 검토한다.
- stack watermark/canary를 사용하되 계측 한계를 기록한다.
- interrupt stack과 task stack 분리 여부를 확인한다.
- worst-case path, nested interrupt, fault handler를 포함한다.

큰 DMA buffer나 LUT를 함수 local array로 만들지 않는다. 자동변수의 주소를 함수 밖으로 반환하지 않는다.

### 6.3 Heap

malloc/free는 fragmentation, 실패, 실행시간 변동, ownership 복잡성을 만든다. hard real-time 제어 루프에서는 일반적으로 runtime heap allocation을 피하고 정적·고정 크기 pool을 선호한다. 동적 메모리가 반드시 필요하면 allocation 시점, 최대 개수, 실패 경로, fragmentation, thread/ISR 사용 금지 규칙을 문서화한다. ISR에서 일반 heap allocator를 호출하지 않는다.

### 6.4 Linker와 startup

Linker는 object file과 library를 주소 공간에 배치하고 symbol/section을 연결한다. linker command file/script는 MCU memory map과 RAM/flash 영역, section 배치, stack/heap reserve, entry point를 정의할 수 있다.

일반적인 reset/startup 흐름:

~~~text
Reset vector
 → low-level CPU/core init
 → stack pointer / vector table
 → .data 초기값을 nonvolatile image에서 RAM으로 복사
 → .bss를 0으로 초기화
 → clock/runtime init (순서는 toolchain/SDK에 따라 다름)
 → C runtime constructors (사용 시)
 → main()
~~~

실제 순서는 startup assembly, boot ROM, C runtime, SDK, compiler ABI에 따라 다르다. 일부 MCU는 C runtime 이전에 clock init이 필요하거나 RAM function copy, CLA program/data copy, flash wait-state 설정, ECC/parity 초기화, cache/MPU 설정을 요구한다. 공식 startup code를 확인하지 않고 순서를 재구성하지 않는다.

일반 section 예:
- .text: executable code
- .rodata: read-only constants
- .data: 초기값이 있는 writable static/global
- .bss: zero-initialized static/global
- .noinit: startup에서 초기화하지 않도록 의도된 영역(툴체인별)
- stack/heap: linker reserve
- DMA section: 정렬·접근 가능한 RAM에 배치해야 할 수 있음
- RAM functions: 실행 중 RAM에서 돌아야 하는 함수가 있을 수 있음

.noinit 값을 reset 이후 유효한 persistent data라고 자동 간주하지 않는다. reset 종류, RAM retention, brownout, CRC/version 검증이 필요하다.

### 6.5 Pointer, alignment, aliasing

- pointer가 가리키는 object의 lifetime이 끝나면 dereference하지 않는다.
- array index와 byte length를 먼저 검증한다.
- sizeof(array)와 sizeof(pointer)를 혼동하지 않는다.
- struct padding 때문에 sizeof(struct)가 field 합과 같다고 가정하지 않는다.
- wire protocol을 C struct memory image로 그대로 보내지 않는다.
- alignment와 effective type/strict aliasing 규칙을 지킨다.
- endian 변환을 명시한다.

## 7. const, volatile, atomic — 서로 다른 약속

| 키워드 | 보장/의미 | 보장하지 않는 것 |
|---|---|---|
| const | 해당 lvalue를 통한 수정 금지 | 물리 메모리가 ROM이라는 뜻 아님 |
| volatile | volatile access를 observable side effect로 취급 | atomicity, lock, inter-thread ordering |
| _Atomic | C atomic object와 memory order 규칙 | 타깃에서 lock-free, ISR-safe 보장 |
| static | scope/linkage/storage duration에 따라 의미 | 자동으로 thread-safe 아님 |

### 7.1 const

const는 API가 값을 변경하지 않는다는 계약에 유용하다. const 포인터와 pointer-to-const의 차이를 구분한다. const object가 flash에 놓일지 RAM에 놓일지는 linker/ABI 결정이다.

### 7.2 volatile

Memory-mapped register나 ISR에서 바뀌는 특정 공유 상태를 compiler가 생략하지 않게 하는 데 필요할 수 있다.

~~~c
#define PERIPH_STATUS (*(volatile uint32_t *)0x40000000U) /* 주소는 설명용이며 타깃 주소가 아님 */
~~~

위 주소를 AEL-002 레지스터 주소로 사용하면 안 된다. 실제 CMSIS/device header/SDK macro를 쓴다. volatile은 read-modify-write를 atomic하게 만들지 않고, CPU cache를 invalidate하지 않으며, DMA와 CPU 사이 ownership을 만들지 않는다.

### 7.3 Atomic과 memory order

C11 stdatomic.h는 atomic object 및 memory order를 정의한다. memory_order_relaxed는 atomicity는 제공하지만 다른 메모리 접근 순서를 publish하지 않는다. release/acquire는 producer가 데이터를 쓴 뒤 index/flag를 release하고 consumer가 acquire로 읽어 선행 write를 관측하게 하는 데 쓸 수 있다.

그러나 MCU ISR에서 _Atomic을 사용하려면:
- 해당 atomic type이 lock-free인지 확인
- compiler runtime helper가 lock을 쓰는지 확인
- interrupt preemption으로 deadlock이 생기지 않는지 확인
- atomic width/alignment와 core instruction을 확인
- DMA는 C CPU memory model의 thread가 아니므로 DMA cache/bus 규칙을 별도로 확인

다중 필드 coherent snapshot이 필요하면 Chapter 10의 ownership 또는 검증된 짧은 critical section을 사용한다. sequence counter로 감싼 non-atomic payload를 C11 data race가 없는 것처럼 취급하면 안 된다. lock-free seqlock은 payload access의 atomicity/ordering을 별도로 설계해야 한다.

### 7.4 SPSC ring buffer의 개념 코드

단일 producer·단일 consumer(SPSC) 구조에서는 producer가 data를 쓴 뒤 head를 release-store하고, consumer가 acquire-load로 head를 읽은 다음 data를 읽는다. 아래 코드는 atomic_uint가 타깃에서 lock-free이고 ISR에서 안전하다는 검증을 통과한 경우에만 사용할 수 있다. 그렇지 않으면 타깃 interrupt mask/critical section 구현으로 대체한다.

~~~c
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>

#define RB_SIZE 8U
#define RB_MASK (RB_SIZE - 1U)

typedef struct {
    uint16_t data[RB_SIZE];
    atomic_uint head; /* producer owns writes */
    atomic_uint tail; /* consumer owns writes */
} sample_ring_t;

bool ring_push_isr(sample_ring_t *r, uint16_t value)
{
    unsigned head = atomic_load_explicit(&r->head, memory_order_relaxed);
    unsigned next = (head + 1U) & RB_MASK;
    unsigned tail = atomic_load_explicit(&r->tail, memory_order_acquire);

    if (next == tail) return false; /* full: caller records overrun */
    r->data[head] = value;
    atomic_store_explicit(&r->head, next, memory_order_release);
    return true;
}

bool ring_pop_task(sample_ring_t *r, uint16_t *value)
{
    unsigned tail = atomic_load_explicit(&r->tail, memory_order_relaxed);
    unsigned head = atomic_load_explicit(&r->head, memory_order_acquire);

    if (tail == head) return false; /* empty */
    *value = r->data[tail];
    atomic_store_explicit(&r->tail, (tail + 1U) & RB_MASK,
                          memory_order_release);
    return true;
}
~~~

RB_SIZE는 2의 거듭제곱이고 producer/consumer는 각각 한 곳이어야 한다. usable capacity는 7개다. 여러 ISR producer가 동시에 쓰면 이 코드는 유효하지 않다. init 시 atomic_init을 수행하고 atomic_is_lock_free 및 compiler/ABI 구현을 확인한다. DMA producer라면 DMA completion과 cache coherency를 포함한 별도 ownership protocol이 필요하다.

## 8. 펌웨어 계층 아키텍처

목표는 알고리즘을 MCU 레지스터와 분리해 host unit test와 target integration test를 모두 가능하게 하는 것이다.

~~~text
Application / Product policy
  ├─ command, operating mode, parameter management
  ├─ state machine, diagnostics, fault policy
  ↓
Control algorithms
  ├─ FOC, PI, transforms, estimator, limiters
  ↓
Middleware / Services
  ├─ protocol, logging, timebase, NVM parameter store
  ↓
Device drivers
  ├─ ADC, PWM, QEP, eCAP, DMA, GPIO, CAN
  ↓
HAL / Platform adaptation
  ├─ pin/peripheral mapping, critical section, clock, reset
  ↓
MCU registers / silicon / board wiring
~~~

| 계층 | 책임 | 하지 말아야 할 일 |
|---|---|---|
| Application | mode/command, system policy, state transition | register 직접 조작 |
| Control | FOC, PI, estimator, saturation | 통신 parser나 flash write |
| Middleware | CAN/UART protocol, NVM, logger, scheduler service | control state를 임의 변경 |
| Driver | ADC/PWM/QEP/DMA peripheral API | 제품 운전 정책 결정 |
| HAL/Platform | board/MCU binding, time, IRQ, reset, memory barrier | motor-control algorithm |
| BSP/Board config | pin/connector/clock routing evidence | 근거 없는 pin assumption |

HAL은 보편적인 API를 제공하고, LL/driver는 더 낮은 수준의 장치 기능을 제공한다. 추상화가 지나치면 timing/feature가 숨겨질 수 있으므로 fast current loop에서는 명시적인 target-specific path를 허용하되 그 구현을 platform layer에 격리한다.

### 8.1 Interface contract

각 함수는 다음을 정의한다.
- 입력 단위·범위·유효성
- 출력 단위·범위·성공/실패 반환
- 호출 context: ISR/task/boot only
- 최대 실행시간 또는 측정해야 할 budget
- ownership/lifetime
- concurrency/atomicity
- side effect와 fault behavior

예를 들어 adc_get_latest()는 단순 raw number만 반환하지 않고 sample sequence, aperture timestamp, channel validity, overrun status를 제공해야 한다.

### 8.2 Chapter 08–10과 연결하는 data contract

~~~c
typedef struct {
    uint32_t sequence;
    uint32_t aperture_ticks;
    int32_t phase_a_mA;
    int32_t phase_b_mA;
    int32_t phase_c_mA;
    uint32_t validity_flags;
} current_sample_t;

typedef struct {
    uint32_t sequence;
    uint32_t measurement_ticks;
    int32_t electrical_angle_scaled; /* unit/scale must be defined by project */
    int32_t electrical_speed_scaled; /* rad/s or defined fixed scale */
    uint32_t validity_flags;
} rotor_feedback_t;
~~~

위 구조의 scaled field는 프로젝트에서 단위·scale을 정해야 하는 이름 예시다. 실제 field width/scale/endian/atomic snapshot을 확정한 것이 아니다.

FOC task는:
1. ADC sample이 valid이고 sequence/age가 허용 범위인지 확인
2. DMA buffer ownership이 CPU로 이전됐는지 확인
3. current sample의 aperture timestamp를 기준으로 sensor angle을 예측
4. Chapter 08의 동일한 Clarke/Park normalization, phase order, polarity로 변환
5. PI/decoupling/vector saturation/anti-windup 수행
6. PWM shadow update가 deadline 전에 가능한지 확인
7. result sequence, execution time, fault flags를 기록

센서 timestamp, ADC aperture, ISR entry, PWM shadow write, 실제 PWM active load는 서로 다른 시각이다. 측정 시각을 ISR 실행 시각으로 바꾸어 기록하지 않는다.

## 9. 상태기계와 fault latch

### 9.1 상태기계의 목적

상태기계는 허용된 상태와 전이를 명시한다.

~~~text
RESET
  ↓
BOOT_SAFE (PWM inhibit requested; outputs default-safe)
  ↓
SELF_TEST (clock, memory, ADC/DMA, sensor, parameter checks)
  ↓
CALIBRATION (only permitted calibration actions)
  ↓
READY (PWM remains inhibited)
  ↓ explicit arm + all interlocks healthy
RUN
  ├─ command stop → STOPPING → READY
  └─ any latched fault → FAULT_LATCHED
FAULT_LATCHED
  ↓ diagnose + cause absent + explicit acknowledge
RECOVERY_CHECK
  ↓ supervised re-arm
READY
~~~

이것은 정책 예시다. AEL-002의 실제 hardware inhibit polarity, gate-driver enable, reset state, fault reaction은 확인되지 않았다.

### 9.2 Fault는 event와 latch를 분리한다

- **Event:** 순간적으로 관측된 이상(ADC overrun, sensor CRC fail)
- **Active condition:** 현재도 이상이 지속되는 상태
- **Latched fault:** 운전 중단 후 원인·시점·상태를 보존하는 기록
- **Clear request:** 운영자/상위 제어가 fault 해제를 요청
- **Re-arm:** 모든 조건이 정상임을 확인하고 출력을 다시 허용하는 별도 절차

Set-dominant latch 개념: 같은 cycle에 fault set과 clear가 함께 들어오면 set이 우선한다.

~~~c
typedef uint32_t fault_mask_t;

enum {
    FAULT_ADC_OVERRUN = 1U << 0,
    FAULT_SENSOR_STALE = 1U << 1,
    FAULT_DMA_OWNERSHIP = 1U << 2,
    FAULT_CONTROL_DEADLINE = 1U << 3,
    FAULT_PARAMETER_INVALID = 1U << 4
};

fault_mask_t fault_latch_update(fault_mask_t current,
                                fault_mask_t new_faults,
                                fault_mask_t clear_request,
                                bool clear_permitted)
{
    fault_mask_t next = current | new_faults; /* set wins */
    if (clear_permitted && new_faults == 0U) {
        next &= ~clear_request;
    }
    return next;
}
~~~

이 함수 자체는 thread-safe가 아니다. 여러 context가 동시에 갱신하면 critical section/atomic ownership이 필요하다. 하드웨어 trip latch는 별도 hardware path일 수 있으며 software mask와 동일하다고 가정하지 않는다.

### 9.3 Fault record

최소 기록:
- fault code/mask
- 최초 발생 timestamp와 최근 발생 timestamp
- state/mode
- ADC/encoder sequence와 freshness
- command/feedback snapshot
- control loop execution time/deadline counter
- reset cause와 software build ID
- 원인 해제 여부 및 acknowledge 이력

고장 기록이 fault clear 과정에서 사라지지 않게 한다. 저장장치가 없거나 기록이 손상된 경우에도 안전한 기본 동작이 정의돼야 한다.

## 10. Parameter 관리·검증·CRC·versioning

### 10.1 파라미터는 실행 코드와 다른 신뢰 경계를 가진다

모터 극쌍수, Rs/Ld/Lq, flux linkage, current limit, encoder direction/offset, ADC gain/offset, PI gains, speed limit, thermal threshold는 잘못된 값이 제어 안정성·전력 한계에 영향을 준다. 수신 즉시 적용하지 않는다.

~~~text
Raw bytes
 → length/version/schema check
 → endian decode
 → CRC check
 → range + cross-field validation
 → staging copy
 → safe state + explicit apply
 → active parameter snapshot
 → record version/build/source
~~~

### 10.2 CRC가 보장하는 것과 못하는 것

CRC는 저장/전송 중 우발적인 bit corruption을 검출하는 데 쓰인다. CRC는 암호학적 인증이 아니며 악의적 변경을 방지하지 않는다. CRC polynomial, init, reflect, xorout, byte order, covered length와 stored CRC endian을 명시한다. 송신/수신에서 동일한 test vector로 검증한다.

### 10.3 Versioned serialized format

C struct를 그대로 flash/통신에 쓰면 padding, alignment, endian, compiler ABI 변경에 취약하다. 명시적인 byte serialization을 쓴다.

~~~text
magic | schema_version | payload_length | sequence
payload fields (defined byte order and units)
CRC field (defined polynomial/coverage)
commit marker (programmed last, if storage supports it)
~~~

Validation 순서:
1. magic 일치
2. version 지원 여부
3. length가 최소/최대 및 buffer 범위 내
4. CRC 일치
5. 모든 field range 검증
6. field 간 일관성 검증
7. calibration/build/hardware compatibility 확인
8. staging → controlled activation

예: Imax가 허용 범위 안이어도 Imax ≤ hardware_limit이 성립해야 한다. Ld,Lq > 0, pole pairs는 양의 정수, encoder counts/rev는 0이 아니어야 한다. 실제 threshold는 모두 TBD다.

### 10.4 Power-fail-safe update

Flash/NVM update는 erase/program granularity와 power-fail behavior를 확인한다. 두 slot(A/B) 방식은:
- active slot은 그대로 보존
- inactive slot에 새 record 작성
- read-back 및 CRC 검증
- 마지막에 commit marker/sequence를 기록
- boot 시 유효한 최신 slot 선택

이 방식도 flash erase 단위, atomic program width, brownout behavior, endurance, ECC, write protection 확인이 필요하다. NO STACK / NO POWER 상태에서 실제 NVM update를 수행하지 않는다.

## 11. Unit-test seam과 host test

### 11.1 Hardware-independent core

순수 함수에 가까운 제어·수치 로직을 peripheral driver에서 분리한다.

~~~c
typedef struct {
    int32_t kp_q15;
    int32_t ki_q15;
    int32_t output_min_q15;
    int32_t output_max_q15;
} pi_config_t;

typedef struct {
    int32_t integrator_q15;
} pi_state_t;

int32_t pi_step_q15(const pi_config_t *cfg,
                    pi_state_t *state,
                    int32_t reference_q15,
                    int32_t feedback_q15);
~~~

실제 구현에는 checked multiply/add, output saturation, anti-windup, invalid config 처리, timestep 계약이 필요하다. 이 선언은 완성 PI 구현이 아니다.

### 11.2 Port seam

| 기능 | production adapter | host fake |
|---|---|---|
| ADC | peripheral driver + DMA | 배열에서 가상 sample 제공 |
| PWM | ePWM driver | duty command 기록 |
| QEP | hardware counter snapshot | 가상 position/timestamp |
| clock | timer/cycle counter | deterministic fake time |
| critical section | target IRQ mask/atomic | host mutex/test lock |
| NVM | flash driver | RAM byte array |
| communication | CAN/UART driver | injected frame |
| fault output | independent hardware interface | state transition assertion |

Control module은 MCU 레지스터 함수를 직접 호출하지 않고 정의된 input snapshot을 받아 output command를 반환하도록 설계한다.

### 11.3 필수 단위 테스트

- min/max/zero/negative/overflow 경계
- fixed-point 곱셈 rounding, saturation, −1×−1
- NaN/∞/near-zero denominator (float 사용 시)
- Clarke/Park inverse round-trip와 Chapter 08 convention
- angle wrap, pole pair, direction, offset
- sensor stale timestamp, sequence rollback, timer wrap
- ADC invalid channel/overrun
- DMA buffer ownership state violation
- PI saturation/anti-windup
- parameter wrong version/length/CRC/range/cross-field
- fault set+clear 동시 입력에서 set 우선
- state machine illegal transition/arm rejection
- deadline miss/overrun counter와 recovery
- startup invalid parameter 시 PWM inhibit 정책

### 11.4 Property-based / metamorphic tests

- wrap(wrap(theta)) == wrap(theta)
- angle delta가 지정된 범위에 존재
- Clarke→inverse Clarke에서 허용오차 내 원상 복구
- Park→inverse Park에서 같은 normalization을 쓰면 복구
- saturate 함수 결과는 항상 min/max 범위 안
- CRC test vector는 고정된 expected result
- encoder count 증가와 방향 convention이 일관
- 동일 입력과 동일 state에서 deterministic function 결과가 동일

허용오차는 단위·수치 표현·측정 요구사항에 따라 정한다.

## 12. Static analysis, build hygiene와 compiler 경계

### 12.1 Compiler diagnostics

- 가능한 높은 warning level 사용
- warning을 의미 없이 disable하지 않는다.
- implicit conversion/sign conversion/shift/format/unused/uninitialized 경고 검토
- Werror는 project/compiler별로 도입하되 타깃 SDK의 vendor code와 분리
- strict aliasing, LTO, fast-math, optimization level에 따른 동작 차이를 검증
- host compiler 성공을 target compiler 성공으로 간주하지 않는다.

### 12.2 Static analysis와 동적 검사

도구 후보:
- GCC/Clang warning
- clang-tidy 또는 Cppcheck
- CERT C 규칙 기반 분석
- MISRA C checker(프로젝트에서 채택·버전·deviation 절차 정의 시)
- host ASan/UBSan 등 가능한 sanitizer
- unit test coverage와 mutation testing

MISRA/CERT 준수는 도구 한 번 실행으로 선언하지 않는다. 적용 규칙, 버전, deviation, 분석 범위, third-party 제외 범위, suppression 근거를 기록한다. Host sanitizer는 MCU peripheral/ISR/DMA/cache의 실제 동작을 검증하지 않는다.

### 12.3 Reproducible build

빌드 기록:
- MCU order code/revision
- compiler name/version/ABI
- C standard/dialect
- SDK version/commit
- linker command file, startup, device headers
- optimization/debug/LTO/fast-math flags
- preprocessor definitions/include paths
- source commit SHA/submodule state
- map file, ELF/HEX hash, warning log
- build host/container/tool versions

AEL-002의 실제 compiler/SDK/build system은 TBD다. 현재 저장소 CI의 GCC C11 syntax check는 STM32G0B1 sensor-I/O scaffold에 대한 문법 검사일 뿐, AEL-002 target firmware build가 아니다.

## 13. Code review checklist

### API와 데이터
- [ ] 함수의 단위·범위·부호·timestamp·validity가 명시됐는가?
- [ ] signed/unsigned 혼합과 implicit conversion이 검토됐는가?
- [ ] 모든 overflow, divide-by-zero, shift, index, length가 검토됐는가?
- [ ] pointer lifetime, alignment, aliasing, struct padding이 안전한가?

### Concurrency와 real-time
- [ ] ISR/task/DMA ownership이 명시됐는가?
- [ ] volatile을 atomic/mutex 대용으로 쓰지 않았는가?
- [ ] atomic lock-free/ISR-safe 근거가 있는가?
- [ ] critical section 길이와 interrupt latency를 검토했는가?
- [ ] WCET/deadline/overrun 경로를 검토했는가?

### Control과 safety
- [ ] Chapter 08 normalization/phase order/current sign과 일치하는가?
- [ ] Chapter 09 angle direction/offset/timestamp/validity와 일치하는가?
- [ ] Chapter 10 ADC aperture/DMA ownership/PWM update deadline과 일치하는가?
- [ ] stale/invalid sensor와 parameter를 사용하지 않는가?
- [ ] fault latch set 우선, clear/re-arm 분리가 유지되는가?
- [ ] startup/reset 중 output inhibit의 독립 hardware 조건이 확인됐는가?

### 유지보수와 증거
- [ ] 계층 경계를 침범하지 않는가?
- [ ] unit test seam과 실패 테스트가 있는가?
- [ ] warning/static-analysis finding이 설명됐는가?
- [ ] build manifest와 commit SHA가 기록됐는가?
- [ ] 교육용 수치와 실제 정격이 구분됐는가?

## 14. 가상 계산 예제와 풀이

### 예제 A — 센서 raw count의 signed 변환

16-bit ADC raw가 32780, offset이 32768이라면 차이는 +12 code다. 두 값을 unsigned끼리 빼면 underflow 가능성이 있으므로 먼저 넓은 signed type으로 변환한다.

\[
d=(int32)32780-(int32)32768=12
\]

ADC code가 1 LSB = 2 mA인 가상 설정이면 I=12×2mA=24mA. 이 gain은 교육용이며 실제 AEL-002 값이 아니다.

### 예제 B — accumulator 범위

가상 제어식에서 16-bit signed 값 4개를 곱하지 않고 합산한다고 하자. 최대 절댓값을 각 30000으로 제한하면 네 항의 최대 합은 120000으로 int16_t 범위를 넘지만 int32_t에는 들어간다. 따라서 각 항을 int32_t로 확장한 후 합산한다. 중간 곱셈이 있으면 곱의 최댓값을 별도로 계산한다.

### 예제 C — Q15 quantization

Q15의 1 LSB는 \(2^{-15}=0.0000305176\). round-to-nearest의 이상적인 양자화 오차는 최대 약 0.5 LSB = 0.0000152588이다(포화 경계·계산 오차 제외).

### 예제 D — FOC timestamp의 정수 표현

Timer tick이 100 MHz라면 tick=10 ns다. sensor와 ADC aperture의 차이가 1200 tick이면 12 μs다. float에 절대 timestamp를 저장하기보다 uint32_t tick을 보존하고 modular subtraction으로 차이를 구한 뒤 12 μs로 변환한다. 32-bit counter wrap은 Chapter 10의 wrap 처리 규약을 따른다.

## 15. 연습문제와 전체 풀이

1. 16-bit signed와 unsigned의 범위를 각각 적어라.
2. int32_t a=-1; uint32_t b=2; a < b가 위험한 이유는?
3. signed overflow와 unsigned wrap의 C 언어상 차이는?
4. int16_t 두 값을 곱할 때 int16_t에 바로 저장하면 안 되는 이유는?
5. Q15에서 raw 값 8192는 얼마인가?
6. Q15의 0.5와 −0.25를 곱한 결과 raw 값은?
7. Q15의 1 LSB와 이상적인 최대 nearest-rounding 오차는?
8. volatile이 ISR 공유 변수의 race를 모두 해결하지 못하는 이유는?
9. _Atomic 변수를 ISR에서 쓰기 전에 확인할 것은?
10. .data와 .bss의 startup 처리는 어떻게 다른가?
11. CRC가 parameter authenticity를 보장하지 못하는 이유는?
12. FOC 알고리즘을 host unit test 가능하게 만들기 위한 계층 분리는?

**풀이**
1. int16_t: −32768…32767. uint16_t: 0…65535.
2. usual arithmetic conversions로 signed −1이 unsigned로 변환되어 큰 양수가 될 수 있어 비교 의도가 깨진다. 동일 signedness로 범위 검증 후 비교한다.
3. unsigned는 modulo \(2^n\)로 wrap하는 정의된 동작이다. signed overflow는 undefined behavior다.
4. 30000×30000은 900,000,000으로 16-bit 범위를 넘는다. operand를 넓은 타입으로 확장하고 충분한 중간 폭을 사용한다.
5. 8192/32768=0.25.
6. 0.5 raw=16384, −0.25 raw=−8192. product=−134,217,728(Q30). Q15 복원은 −4096 raw, 즉 −0.125.
7. \(1/32768=0.0000305176\). 최대 ideal rounding error 약 \(1/65536=0.0000152588\).
8. volatile은 access를 관측 가능하게 할 뿐 atomic read-modify-write, multi-field consistency, mutual exclusion, memory ordering을 보장하지 않는다.
9. atomic width/alignment, atomic_is_lock_free, compiler runtime helper, interrupt preemption/deadlock, ABI와 target-specific memory barrier를 확인한다.
10. .data는 flash image 등 초기값 원본에서 RAM으로 복사한다. .bss는 0으로 초기화한다. 실제 startup 순서는 SDK/compiler에 따른다.
11. CRC는 우발적 오류 검출용이다. 공격자는 payload와 CRC를 함께 다시 계산할 수 있다. 인증에는 MAC/signature와 key management가 필요하다.
12. FOC 수학은 입력 snapshot을 받는 hardware-independent control layer로 분리한다. ADC/PWM/QEP/NVM/clock은 driver/HAL adapter로 두고 host fake로 테스트한다.

## 16. AEL-002 적용 상태: 확정하지 않는 항목

| 항목 | 상태 | 확정에 필요한 근거 |
|---|---|---|
| MCU order code·silicon revision | TBD | BOM/실물 마킹/datasheet |
| Compiler·version·ABI·C standard | TBD | 승인된 toolchain manifest |
| SDK version·commit | TBD | 실제 설치/프로젝트 source |
| startup/vector table/runtime | TBD | SDK startup source와 linker entry |
| flash/RAM/TCM/CLA/DMA memory map | TBD | exact MCU TRM + linker map |
| stack/heap size·ISR stack | TBD | call graph, map, compiler report |
| FPU/CLA support와 context cost | TBD | exact MCU + compiler ABI |
| atomic lock-free/ISR behavior | TBD | compiler docs + generated code |
| fixed-point Q format/scaling | TBD | motor/sensor range와 error budget |
| linker sections/DMA alignment/cache | TBD | linker file + TRM |
| HAL/driver peripheral mapping | TBD | board schematic + exact SDK |
| fault output/reset/re-arm policy | TBD | 회로도, gate driver datasheet, safety review |
| parameter NVM layout/CRC/version | TBD | memory technology + schema decision |
| build flags/static-analysis profile | TBD | toolchain and project policy |

F280039C가 이전 프로젝트 맥락에서 후보로 언급되었더라도, 정확한 보드 revision·compiler·SDK 조합을 다시 확인하기 전에는 위 항목을 확정하지 않는다. 다른 플랫폼의 C ABI·startup·atomic 구현을 혼용하지 않는다.

## 17. 검증 템플릿

### 17.1 Numeric range analysis

| Signal/operation | Unit | Min | Max | Input width | Intermediate width | Rounding/saturation | Evidence |
|---|---|---:|---:|---|---|---|---|
| ADC raw | code | TBD | TBD | TBD | TBD | N/A | ADC spec |
| phase current | A | TBD | TBD | TBD | TBD | TBD | sensor chain |
| Clarke alpha/beta | A | TBD | TBD | TBD | TBD | TBD | derivation |
| Park d/q | A | TBD | TBD | TBD | TBD | TBD | derivation |
| PI integrator | V or normalized | TBD | TBD | TBD | TBD | TBD | controller design |
| PWM duty | ratio | TBD | TBD | TBD | TBD | clamp/fault | PWM spec |
| angle | rad/turn | TBD | TBD | TBD | TBD | wrap | sensor contract |

### 17.2 Module interface

| Field | Definition |
|---|---|
| Module/API | name/version |
| Inputs | type, unit, range, timestamp, validity |
| Outputs | type, unit, range, validity |
| Context | boot/task/ISR |
| Ownership | producer/consumer, lifetime |
| Concurrency | atomic/critical section/none |
| Worst-case time | requirement and measurement |
| Fault behavior | return code/state transition |
| Test seam | fake/fixture |
| Evidence | test ID, compiler, SHA |

### 17.3 Parameter validation

| Test ID | Fault injection | Expected behavior |
|---|---|---|
| PAR-01 | wrong magic | reject, keep safe defaults |
| PAR-02 | unsupported version | reject or explicit migration |
| PAR-03 | length under/overrun | reject before decode |
| PAR-04 | CRC mismatch | reject, preserve previous valid slot |
| PAR-05 | field out of range | reject |
| PAR-06 | cross-field contradiction | reject |
| PAR-07 | interrupted NVM write | boot selects last valid committed slot |
| PAR-08 | duplicate/old sequence | reject per policy |
| PAR-09 | hardware/build incompatibility | reject application |
| PAR-10 | missing calibration | remain non-armed |

### 17.4 Firmware architecture verification

| Test ID | Scenario | Expected |
|---|---|---|
| FW-01 | host FOC test without MCU headers | build/test succeeds |
| FW-02 | ADC sample invalid | FOC output invalid, policy fault |
| FW-03 | DMA buffer still owned by DMA | CPU does not consume |
| FW-04 | stale rotor timestamp | no unqualified Park angle |
| FW-05 | fixed-point overflow boundary | deterministic reject/saturate |
| FW-06 | concurrent fault set and clear | set wins |
| FW-07 | illegal state transition | rejected and logged |
| FW-08 | invalid startup parameter | outputs remain inhibited |
| FW-09 | ring buffer full | explicit overrun, no silent overwrite |
| FW-10 | watchdog supervisor unhealthy | watchdog is not refreshed |
| FW-11 | build with optimization/LTO | tests and target timing re-run |
| FW-12 | compiler/SDK version change | ABI/map/startup regression review |

### 17.5 Evidence record

Record commit SHA, toolchain version, command line, warnings, static-analysis rule set, test seed, expected/actual result, coverage, map/stack report, generated assembly for critical atomic/fixed-point paths, and any deviations. Host unit tests do not validate hardware pin mux, DMA bus arbitration, ADC analog settling, PWM trip behavior, or real-time timing on target.

## 18. 출처와 읽을거리

1. SEI CERT C, [INT32-C — signed integer overflow 방지](https://cmu-sei.github.io/secure-coding-standards/sei-cert-c-coding-standard/rules/integers-int/int32-c/).
2. SEI CERT C, [INT02-C — integer conversion 규칙 이해](https://cmu-sei.github.io/secure-coding-standards/sei-cert-c-coding-standard/recommendations/integers-int/int02-c/).
3. SEI CERT C, [INT30-C — unsigned wraparound 방지](https://cmu-sei.github.io/secure-coding-standards/sei-cert-c-coding-standard/rules/integers-int/int30-c/).
4. SEI CERT C, [INT31-C — integer conversion 손실 방지](https://cmu-sei.github.io/secure-coding-standards/sei-cert-c-coding-standard/rules/integers-int/int31-c/).
5. C11 atomics memory order 개념, [cppreference](https://en.cppreference.com/w/c/atomic/memory_order). 언어 개념 참고이며 타깃 compiler의 ISR 구현 보증은 별도 확인한다.
6. Texas Instruments, [C2000 Code Generation Tools](https://www.ti.com/tool/C2000-CGT) — compiler, assembler, linker 및 version-specific user guide. 최신 릴리스가 AEL-002 승인 버전이라는 뜻은 아니다.
7. [MISRA](https://www.misra.org.uk/) — safety-related embedded C coding guideline. 실제 적용 시 계약한 edition, checker, deviation 절차를 명시한다.

출처는 규칙·도구 개념을 확인하기 위한 것이다. 특정 SDK·MCU의 memory map, compiler ABI, startup, peripheral route를 입증하는 근거로 대체하지 않는다.

## 19. 장 완료 기준

- [ ] exact-width integer와 implementation-defined type의 차이를 설명한다.
- [ ] signed overflow, unsigned wrap, promotion, conversion을 예측한다.
- [ ] checked arithmetic, saturation, range validation을 구현한다.
- [ ] Q format의 scale, product width, rounding, saturation을 계산한다.
- [ ] float의 precision/NaN/∞/timing 한계를 설명한다.
- [ ] stack/heap/static/sections/startup/linker의 역할을 설명한다.
- [ ] const/volatile/atomic의 차이와 ISR lock-free 조건을 설명한다.
- [ ] DMA ownership과 CPU memory model/cache coherency를 구분한다.
- [ ] HAL/driver/middleware/control/application 경계를 설계한다.
- [ ] fault event/active/latched/clear/re-arm을 구분한다.
- [ ] CRC/version/length/range/cross-field 검증과 power-fail-safe update를 설명한다.
- [ ] hardware-independent unit test seam을 만든다.
- [ ] static analysis, build manifest, code review evidence를 기록한다.
- [ ] Chapter 08–10의 sign/normalization/timestamp/aperture/DMA/ISR contract를 유지한다.
- [ ] 실제 AEL-002 MCU/SDK/compiler/build/memory/numeric settings를 근거 없이 확정하지 않는다.

**현재 판정:** Chapter 11은 portable C와 펌웨어 설계 원칙, 테스트 가능한 인터페이스 및 검증 계획을 정의한다. 실제 타깃 빌드, static-analysis 실행, FOC 구현, SIL/HIL, board inspection, measurement 또는 motor test를 수행했다고 주장하지 않는다.

**안전 상태: NO STACK / NO POWER.**
