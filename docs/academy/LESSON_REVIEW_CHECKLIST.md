# Engineering Academy — 강의노트 품질 검토 체크리스트

새 장을 작성하거나 기존 장을 수정할 때마다 아래 항목을 검토한다. 확인하지 못한 항목은 통과 처리하지 않고 미확인으로 기록한다.

## A. 교육 품질
- [ ] 학습 목표가 구체적이고 측정 가능하다.
- [ ] 중학교 수준의 직관적 설명이 먼저 있고 전문적 정의가 뒤따른다.
- [ ] 비유의 한계를 설명해 비유를 물리적 사실로 오해하지 않게 한다.
- [ ] 용어·약어를 처음 등장할 때 풀어 쓴다.
- [ ] 앞 장의 선수지식과 다음 장의 연결을 설명한다.

## B. 수학·물리 정확성
- [ ] 모든 기호를 정의하고 첨자·부호·기준 방향을 설명한다.
- [ ] 모든 식의 단위와 차원을 검산한다.
- [ ] 수식 유도에서 생략한 가정과 초기조건을 적는다.
- [ ] 미분·적분·좌표변환의 변수와 범위를 정의한다.
- [ ] 근사값과 정확한 값, 이상 모델과 실제 모델을 구분한다.
- [ ] 예제 계산의 중간 단계와 반올림 기준을 보여준다.
- [ ] 극한값·초기값·정상상태 등 경계 조건으로 결과를 검산한다.

## C. 부품·데이터시트 품질
- [ ] 부품 종류와 동작 원리를 설명한다.
- [ ] 정격과 권장 동작 조건을 구분한다.
- [ ] 공차·온도·주파수·열·수명·레이아웃 영향 중 해당 항목을 검토한다.
- [ ] 제조사·정확한 부품번호·문서 개정·페이지/표를 기록한다.
- [ ] 부품 선정 근거가 없으면 수치를 확정하지 않고 TBD로 둔다.

## D. 프로젝트 연결
- [ ] AEL-002의 어느 설계 결정/산출물에 적용되는지 명시한다.
- [ ] 첫 프로토타입 범위와 미래 산업용 확장 범위를 혼동하지 않는다.
- [ ] 교육용 예제 수치를 실제 하드웨어 정격으로 오인하지 않게 표시한다.
- [ ] 실제 보드/SDK/부품에서 확인하지 않은 사항은 미확인으로 둔다.
- [ ] 하드웨어 안전 게이트와 기존 NO STACK / NO POWER 경계를 유지한다.

## E. 학습 평가
- [ ] 직접 풀 수 있는 연습문제가 있다.
- [ ] 정답에 풀이와 단위가 포함된다.
- [ ] 시뮬레이션/실습의 조건과 한계를 명시한다.
- [ ] 장을 완료했다고 판단할 객관적 기준이 있다.

## F. 출처·저작권
- [ ] 핵심 주장에 권위 있는 출처가 있다.
- [ ] 제조사 1차 문서와 교과서/강의 자료를 구분한다.
- [ ] 외부 출처의 긴 문장을 복제하지 않고 독자적으로 설명한다.
- [ ] 링크가 실제 해당 주제를 뒷받침하는지 확인한다.
- [ ] 핵심 주장마다 출처 역할(규격/제조사 1차/전문기관/학술)을 구분한다.
- [ ] 안전·정격·핀맵·절연·보호 시간 등 핵심 주장은 원문 규격 또는 정확한 제조사 1차 문서와 독립적인 전문 자료/구현 근거를 교차 확인한다.
- [ ] 동일 원문을 복제한 여러 웹페이지를 독립 출처 여러 개로 세지 않는다.
- [ ] 정확한 문서 번호·개정·발행일·조항/페이지/표/그림·확인일을 기록한다.
- [ ] 표준의 normative requirement와 informative guide/application note를 구분한다.
- [ ] 문서 간 불일치는 숨기거나 평균하지 않고 적용 조건·개정 차이로 기록한다.
- [ ] 계산은 단위/차원과 독립 재계산으로 검산한다.
- [ ] 출처 전문을 확인하지 못했으면 공개 초록/범위 이상으로 주장하지 않는다.
- [ ] 출처를 확인하지 못한 사실을 출처가 있는 것처럼 쓰지 않는다.

## H. 전류 센싱·아날로그 프런트엔드 (해당 장에 적용)
- [ ] shunt 위치별 전류 관측 창과 blind window를 PWM 상태별로 검토했다.
- [ ] shunt 전력·pulse energy·TCR·공차·terminal temperature·기생 인덕턴스를 검토했다.
- [ ] Kelvin sense node와 differential input routing, 입력 RC 대칭성을 검토했다.
- [ ] amplifier common-mode/transient/CMTI, recovery, output swing, bandwidth, offset/gain drift를 정확한 조건으로 검토했다.
- [ ] anti-alias filter phase delay와 ADC S+H settling/kickback/source impedance를 함께 계산했다.
- [ ] PWM edge/blanking/valid sample window/ADC capture timestamp/FOC deadline을 연결했다.
- [ ] offset/gain/polarity/phase calibration과 uncertainty budget의 가정을 기록했다.
- [ ] fast hardware comparator trip과 ADC/software diagnostic을 분리하고 latch/re-arm을 검토했다.
- [ ] exact MCU datasheet/TRM/errata 및 silicon revision 적용성을 확인하거나 TBD로 남겼다.

## I. FOC 전류 루프·디지털 제어기 (해당 장에 적용)
- [ ] PMSM d/q 부호·Park convention·극쌍수·전기각속도 규약을 고정했다.
- [ ] decoupling/feed-forward 부호를 plant 식에 대입해 검산했다.
- [ ] continuous PI plant assumptions, pole-zero cancellation 및 gain 단위를 검산했다.
- [ ] Forward Euler/Backward Euler/Tustin의 recurrence와 state indexing을 혼합하지 않았다.
- [ ] 실제 inverter voltage vector limit, DC bus measurement, modulation reserve와 axis priority를 검토했다.
- [ ] anti-windup residual이 feed-forward 포함 applied voltage와 일관되며 reset/freeze semantics가 명시됐다.
- [ ] sensor/AFE/ADC/ZOH/compute/PWM delay를 중복 없이 합산하고 worst-case jitter를 검토했다.
- [ ] idealized delay phase와 실제 loop phase/gain margin을 구분했다.
- [ ] Rs/Ld/Lq/flux/Vdc/speed/delay corner sweep을 정의했다.
- [ ] host/SIL 결과와 target timing/physical evidence의 경계를 구분했다.

## G. 변경 및 CI
- [ ] 기존 장의 수식·기호·단위와 용어 일관성을 확인했다.
- [ ] 변경된 링크와 목차를 확인했다.
- [ ] 기존 CI/테스트 정의를 불필요하게 바꾸지 않았다.
- [ ] 최종 커밋 SHA와 해당 SHA에서 실행된 CI 결과를 기록했다.
- [ ] CI 성공을 물리적 하드웨어 검증 성공으로 표현하지 않았다.

## 승인 기준

모든 필수 항목이 체크되거나, 미확인 사항과 그 이유가 명확하게 기록되어야 한다. 안전·정격·핀맵에 영향을 주는 미확인 사항은 설계 확정의 근거로 사용하지 않는다.
