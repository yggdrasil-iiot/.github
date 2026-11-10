# Yggdrasil 로드맵
기준일 2026-11-11.

## 이 문서를 읽는 법

각 제품 절은 네 가지 상태 어휘로 작업을 분류한다.

- **최근 완료**: 기본 브랜치(default branch)에 병합된 작업.
- **지금·다음**: 명명된 다음 단계 작업.
- **보류 (재개 조건)**: 명시된 재개 조건이 충족될 때까지 미룬 작업, 또는 확약 없는 후보.
- **설계상 하지 않음**: 의도적으로 제외한 항목.

이 조직의 어떤 소프트웨어도 실제 공장에서 실행된 적이 없다. 게이트와 시뮬레이터는 공장의 동작이 아니라 거버넌스 루프를 검증한다. 각 항목은 근거 문서로 연결된다. 연결된 문서의 수치와 이 문서의 내용이 다를 때는 연결된 문서가 우선한다.

## 제품 간 경계

제품 사이에 공유 코드는 없다. 제품들은 공유 라이브러리 없이 오직 공개 계약(파일, Sparkplug B, OPC UA)으로만 결합한다.

| 제품 | 역할 | 저장소 |
| :--- | :--- | :--- |
| Bifrost (Heimdall 포함) | 거버넌스 코어. 스키마 호환성, 공정 사양 적합성, git 출처 검증, 기본 거부 명령 인가, 앵커드 활성화 원장. Heimdall은 런타임 쓰기 경계 데몬. | [yggdrasil-iiot/bifrost](https://github.com/yggdrasil-iiot/bifrost) |
| Mimir | 설계 시점 생산자. OPC UA 타입 브라우징 및 벤더 설정 해석 스냅샷 발행. | [yggdrasil-iiot/mimir](https://github.com/yggdrasil-iiot/mimir) |
| Tyr | PLC별 접근 정의와 상위 의미 매핑 작성·검토 작업대. | [yggdrasil-iiot/tyr](https://github.com/yggdrasil-iiot/tyr) |
| Muninn | 거버넌스된 정의 검증 후 OPC UA 인스턴스 데이터를 Sparkplug B / MQTT로 UNS에 공급. | [yggdrasil-iiot/muninn](https://github.com/yggdrasil-iiot/muninn) |
| Huginn | 수동 관측. 패킷과 로그를 정책과 대조해 미선언 통신 보고. | [yggdrasil-iiot/huginn](https://github.com/yggdrasil-iiot/huginn) |
| Vor | MCP 서버 및 에이전트 명령 제안 서명. | [yggdrasil-iiot/vor](https://github.com/yggdrasil-iiot/vor) |
| Forseti | 공정 샘플과 스테이션 점유 결합, 품질 사고 영향 단위 판정. | [yggdrasil-iiot/forseti](https://github.com/yggdrasil-iiot/forseti) |
| Hermod | 엔진 중립, 계약 기반 durable saga 플랫폼으로 IT/OT 통합 트랜잭션 관리. | [yggdrasil-iiot/hermod](https://github.com/yggdrasil-iiot/hermod) |

## 지금 진행 중인 흐름

Forseti 구현 단계:

- 0단계 스펙 v13 (forseti) — 완료 2026-11-06
- 1단계 Bifrost 매핑 계약 2.27.0, 귀속·영향 규칙 — 완료 2026-11-07
- 2단계 Tyr 규칙 작성 — 완료 2026-11-08
- 3단계 엔진 독립 코어와 독립 오라클 — 구현 계획만 병합(2026-11-10), PR 0 미착수
- 4단계 Bifrost 시뮬레이터 `Line2` — 미착수
- 5~8단계 브리지, Flink 작업, Kafka Streams 작업, 두 엔진 비교 — 미착수
- 9단계 Bifrost ENTERPRISE.md·INTEGRATION.md 문서 — 미착수

## 제품별 로드맵

### Bifrost (Heimdall 포함)

거버넌스 코어. 스키마 호환성, 공정 사양 적합성, git 출처 검증, 기본 거부 명령 인가, 앵커드 활성화 원장을 맡는다. Heimdall은 그 안의 런타임 쓰기 경계 데몬이다. Java 17, Maven 기반으로 동작한다.

**최근 완료**
- 승인 증명(Rego v1, in-toto/DSSE)과 레시피 발행 증명(SLSA v1), 활성화를 발행에 연결 (2026-10-29~30).
- 서명된 헤드의 신선도 규칙, 90일 만료 (2026-10-31).
- 계약 2.23.0 ISA-95 설비 계층, 2.24.0 파생 지표 정의 (2026-10-31, 2026-11-01).
- 거버넌스된 읽기(M1)와 AI 에이전트의 거버넌스된 쓰기(M2): 시뮬레이터 Method, 명령 제안과 `gates command approve|verify`, OPA `command_method`, Heimdall `op=method`, 게이트 M1–M7 (2026-11-02~03).
- 엣지 신원·명령 바인딩 1~5단계: 서버 신뢰, 계약 2.25.0 명령 바인딩, Heimdall을 독립 Sparkplug 명령 노드로 분리, `endpointRef` 2.26.0 (2026-11-04~05).
- Forseti 1단계 매핑 계약 2.27.0 (2026-11-07).
- 패키지 이름을 `yggdrasil.*`로 통일 (2026-11-10, 모든 저장소 공통).

**지금·다음**
- Forseti 4단계 시뮬레이터 `Line2`(스테이션 유형, 너트러너 공구 유형, 제어 노드).
- Forseti 9단계 문서(`ENTERPRISE.md`, `INTEGRATION.md`).

**보류 (재개 조건)**
- `commandBindingRef` (재개 조건: 중복 명령 엣지).
- 아직 구현하지 않은 항목: 기존 NCMD 쓰기·호출 경로를 OPA로 통합, 다중 입력 Method, 공유 예약, 명령 break-glass, 결과 대사.
- [Enterprise 보드](https://github.com/yggdrasil-iiot/bifrost/blob/main/docs/ENTERPRISE.md) 14개 축 현황:

| 축 | 상태 | 남은 것 |
| :--- | :--- | :--- |
| 1 다중 사이트 권한 | 구현 | — |
| 2 사이트로 거버넌스 전파 | 구현 | 경계 있음: 사이트의 다음 Heimdall 재시작 때 적용 |
| 3 연결이 끊겨도 사이트 운영 | 구현 | — |
| 4 위변조 탐지·내부자 롤백 | 구현 | 명령 원장은 체인만 있어 끝부분 삭제를 탐지하지 못함 |
| 5 통신 경로 목록(IEC 62443 SR 6.2) | 부분 구현 | 빈도, 소유자, TCP 이외 통신 경로 없음 |
| 6 신원 수명주기 | 보류 | 실제 하드웨어의 두 번째 사이트, 또는 첫 인증서 만료 |
| 7 공급망·EU CRA | 부분 구현 | 취약점 처리 절차 없음 |
| 8 기존 현장의 벤더 다양성 | 부분 구현 | 인입 어댑터만 있음 |
| 9 AAS/IDTA 적합성 | 보류 | IDTA 서브모델 템플릿을 요구하는 고객 |
| 10 인증서 만료·키 교체 | 부분 구현 | CA·등록 절차 없음 |
| 11 대규모 감사 조회 | 실측 | 명령 원장은 실측하지 않음 |
| 12 쓰기 경로 독점 | 부분 구현 | 벤더 서버·네트워크 설정은 사이트 몫, Modbus/TCP는 강제하지 않음 |
| 13 거버넌스 모델 대 벤더 런타임 | 부분 구현 | 실시간 가져오기 없음, 생성 방향 없음, Kepware 어댑터 없음 |
| 14 에이전트의 거버넌스된 쓰기 | 부분 구현 | 전체 검사는 Method 경로에만 적용 |

### Mimir

설계 시점 생산자. OPC UA 타입 공간을 브라우징해 AAS 정렬 UDT 정의를 도출하고, 벤더 설정의 유일한 해석기로서 해석 스냅샷(계약 1.0.0, 1.1.0)을 발행한다.

**최근 완료**
- Ignition 8.3 태그 내보내기 해석기 (2026-10-28).
- 모르는 제품 버전 거부(`--product-version`), 브라우징 시 NodeId와 namespace URI 보존 (2026-10-30).
- [VENDOR-INTERPRETATION.md](https://github.com/yggdrasil-iiot/mimir/blob/master/docs/VENDOR-INTERPRETATION.md)에 제3자 내보내기 10건의 정확도 공개.

**지금·다음**
- Bifrost와의 대사 연결.
- 스냅샷 이력·비교·되돌리기.

**보류 (재개 조건)**
- Kepware, BEAN PIO / TAG MANAGER 해석기 (재개 조건: 내보내기 자료 확보).
- 실시간 읽기 (아직 계획 없음).
- 호출 가능한 Method 정의 도출 (Vor의 M3 전망).

### Tyr

PLC별 접근 정의와 상위 의미의 매핑을 작성하고 검토하는 작업대. Bifrost에 파일로 제출하며 승인 권한은 없다. Python 기반으로 동작한다.

**최근 완료**
- 스냅샷 인입과 계약 1.1.0 소비.
- AAS 내보내기.
- ISA-95 계층 작성 화면 (2026-10-31).
- 파생 지표 정의 (2026-11-02).
- 명령 바인딩, `endpointRef`와 인증서 가져오기 (2026-11-04~05).
- Forseti 귀속·영향 규칙 작성 (2026-11-08).

**지금·다음**
- Forseti 3단계 PR 6 이후 실제 `format.schemaSha256`와 사고 토픽 `quality.incidents`로 규칙 묶음 다시 작성.

**보류 (재개 조건)**
- 현장 가치 검증 (아직 하지 않음).

**설계상 하지 않음**
- 장치 통신, 외부 SQL, 쓰기 실행, 런타임 활성화, 승인.

### Muninn

거버넌스된 정의의 바이트를 검증한 뒤 OPC UA 인스턴스 데이터를 Sparkplug B / MQTT로 UNS에 공급한다.

**최근 완료**
- ISA-95 `--hierarchy` 장치 경로, 지속 Sparkplug B 3.0 세션 `--session` (2026-11-01).
- 샘플에 OPC UA 상태 코드와 원본 시각 포함 (2026-11-02).

**보류 (재개 조건)**
- 재시작 사이 `bdSeq` 유지 (후보).
- [Muninn README](https://github.com/yggdrasil-iiot/muninn/blob/master/README.md)에 명시된 현재 한계:
  - 브로커 연결을 잃으면 스스로 다시 연결하지 않음 (감독 프로세스가 재시작).
  - 저장 후 전달(store-and-forward) 없음.
  - 송출 검증은 구조와 타입까지이며, 범위 검증은 하지 않음.
  - 출처는 자체 선언 매니페스트 대비 콘텐츠 해시이며 Bifrost의 헤드 서명은 검사하지 않음.

### Huginn

수동 관측 도구. pcap에서 Modbus/TCP·S7comm을 해독하고, Zeek ICSNPP 로그에서 S7comm-plus를 읽어 선언된 통신 정책과 대조해 미선언 통신을 보고한다. 통신을 차단하지 않는다.

**최근 완료**
- Modbus/TCP·S7comm 해독과 프로토콜별 커버리지 (2026-09).
- Bifrost에서 정책 생성 (2026-09-10).
- Zeek ICSNPP 로그 입력과 S7comm-plus (2026-11-01).

**보류 (재개 조건)**
- 실시간 캡처를 입력 어댑터로 사용 (후보).

**설계상 하지 않음**
- [Huginn README](https://github.com/yggdrasil-iiot/huginn/blob/master/README.md)에 명시된 항목:
  - 능동 스캔.
  - 자동 차단 및 교정.
  - OPC UA 및 Sparkplug 해독.
  - pcap에서 S7comm-plus 해독.
  - TCP 공백 뒤 재동기화.
  - 게이트웨이 뒤 unit-ID별 판정.

### Vor

MCP 서버. 도구는 `read_governed` 하나다. 발행된 Bifrost 릴리스에 묶인 값과 Muninn의 실시간 샘플로 답하거나 결정적으로 거절한다. 내장 LLM은 없다. `vor-propose`가 에이전트 명령 제안에 서명한다.

**최근 완료**
- M1 거버넌스된 읽기 (2026-11-02).
- M2 거버넌스된 쓰기 (2026-11-03).
- 엣지 신원 바인딩 (2026-11-05).

**지금·다음**
- M3(Mimir의 Method 정의 도출) 전망.

**보류 (재개 조건)**
- [M1 스펙](https://github.com/yggdrasil-iiot/vor/blob/main/docs/superpowers/specs/2026-11-01-vor-m1-governed-read-design.md)과 [M2 스펙](https://github.com/yggdrasil-iiot/vor/blob/main/docs/superpowers/specs/2026-11-02-vor-m2-governed-write-design.md)의 열린 설계 질문:
  - 다중 입력의 시각 차이 정의.
  - record-mapping 읽기 (런타임 없음).
  - 신뢰할 수 있는 엣지 시계.
  - 결과를 알 수 없는 명령의 대사.
  - 중복 명령 엣지.
- 아직 구현하지 않은 항목: 읽기 인가(OPA), 운영용 PKI/HSM, 다중 인자 Method, 재시도, 분산 예약.

### Forseti

공정 샘플과 스테이션 점유를 이벤트 시각으로 결합(1단계)하고, 늦게 도착한 품질 사고를 그 증거와 대조해 영향받은 단위를 판정(2단계)한다. Apache Flink와 Kafka Streams 두 엔진에 같은 게이트로 구현할 계획이다. 공장 쓰기 경로는 없다.

저장소에는 아직 문서만 있고 코드는 없다.

**최근 완료**
- [스펙 v13](https://github.com/yggdrasil-iiot/forseti/blob/main/docs/superpowers/specs/2026-11-05-forseti-design.md) (2026-11-06).
- 3단계 구현 계획 병합 (2026-11-10).

**지금·다음**
- [3단계 구현 계획](https://github.com/yggdrasil-iiot/forseti/blob/main/docs/superpowers/plans/2026-11-10-forseti-step3-core-and-oracle.md) (PR 7개):
  - PR 0: 고정 버전과 3단계 해석을 스펙에 기록 (미착수). 고정 버전은 Kafka Streams 4.2.2, Flink 2.2.1.
  - PR 1~6: 엔진 독립 코어와 독립 오라클.

**보류 (재개 조건)**
- 4~9단계 (위 흐름 참조).

**설계상 하지 않음**
- 공장 쓰기, 자동 보류·해제, 계보(genealogy), 실제 MES, HA/Kubernetes, Avro/Schema Registry.

### Hermod

엔진 중립, 계약 기반 durable saga 플랫폼으로 IT/OT 통합 트랜잭션을 다룬다. 블록 계약에서 멱등성, saga 보상, 사람 승인 게이트를 도출한다. Temporal과 Conductor에서 실행된다. Kotlin, JDK 21 기반이다. 생산 라인을 롤백하는 것이 아니라, 완료된 통합 단계의 보상과 사람 승인 게이트를 다룬다.

**최근 완료**
- 조직 합류 및 Apache-2.0 라이선스 적용 (2026-11-10).
- 적용 경로가 기본으로 Bifrost Heimdall을 거쳐 Sparkplug NCMD로 쓰도록 변경 (`HERMOD_APPLY_MODE=ncmd`).

**지금·다음**
- 열린 PR #20: OPC UA 및 outbound emit 게이트가 `AWAITING_APPROVAL`을 기다리도록 수정.
- `docs/reference-architecture.md`를 Bifrost를 포함한 현재 구성으로 갱신.

**보류 (재개 조건)**
- [Hermod README](https://github.com/yggdrasil-iiot/hermod/blob/main/README.md)에 명시된 후보: PLC 커넥터, 인증서 기반 OPC UA 보안, Double 이외 타입 쓰기, 현장 장비 첫 실행, 실행 상태 영속화, 게이트 스크립트 CI, 운영자 사용성 검증.
- 미검증 가설: 수요, 개발자가 아닌 사람의 saga 작성.

## 결정 대기

[Forseti 3단계 구현 계획의 미결 사항(Open points)](https://github.com/yggdrasil-iiot/forseti/blob/main/docs/superpowers/plans/2026-11-10-forseti-step3-core-and-oracle.md) 목록:

- `line2-attribution`의 `coverage.maxMissingPeriods` 규칙 변경 — 현재 3 / 제안 4 — 주입 20 시험 (유지관리자 결정)
- 게이트 실행이 15분을 넘을 때 CI 구성 — 제안 `build` 작업을 둘로 분할 — 3단계 CI (유지관리자 결정)
- 승격 범위 플래그 명칭 — 제안 `--accept-scope core` 확정 — 3단계 검증 (유지관리자 결정)
- 스테이션 수 — 현재 2 / 제안 3단계는 2개 유지 및 5단계에서 확장(시뮬레이터는 3) — 3단계 및 5단계 (유지관리자 결정)

## 표준 정렬

현재 다음 표준을 정렬해 적용한다.

- OpenLineage
- in-toto/DSSE
- SLSA
- ODCS
- UCUM
- ISA-95
- AAS

ENTERPRISE.md, INTEGRATION.md 및 Huginn README에 접점별 표준 형식을 명시하는 작업은 보류한다.

## 이 문서의 갱신

각 단계를 병합할 때 이 문서를 갱신한다. 테스트 횟수와 같은 수치는 이 문서에 나열하지 않으며, 각 저장소의 CI가 기준이다.
