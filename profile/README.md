<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/yggdrasil-iiot/.github/master/profile/hero.dark.svg">
  <img alt="Yggdrasil — IIoT 거버넌스 스파인: Mímir가 모델을 도출하고, Bifrost가 이를 거버넌스하며, Heimdall이 쓰기 경계를 방어하고, Muninn이 통합 네임스페이스로 데이터를 피드합니다" src="https://raw.githubusercontent.com/yggdrasil-iiot/.github/master/profile/hero.svg">
</picture>

# Yggdrasil

**산업용 IIoT 시스템의 OT/IT 경계를 위한 닫힌 루프 거버넌스 스파인 (Closed-Loop Governance Spine)**

</div>

Yggdrasil(위그드라실)은 설비 현장(OT)에서 통합 네임스페이스(IT/UNS)로 흘러가는 설비 모델과 공정 사양, 그리고 상위에서 현장으로 내려오는 역방향 제어 명령(Command)의 흐름을 엄격하게 통제하는 **산업용 거버넌스 스파인 플랫폼**입니다.

본 플랫폼의 핵심 불변식은 **"출처가 검증되고 거버넌스를 통과한 엄격한 계약 외에는 그 어떤 데이터나 명령도 OT/IT 경계를 넘을 수 없다"**는 것입니다. Yggdrasil을 구성하는 모든 서브시스템은 **공유 코드 0 (Zero Shared Code)** 원칙을 준수하며, 오직 명세화된 데이터 및 통신 회선 계약(Data & Wire Contract)을 통해서만 상호작용합니다.

그러나 경계 게이트는 *게이트를 통과하는 트래픽*만을 통제할 수 있을 뿐입니다. 따라서 본 스파인은 실제 산업 회선 자체를 직접 감시합니다. **Huginn**은 현장에 실제로 흐른 원시 통신 패킷(pcap)을 수동 캡처 및 해독하여 사전에 선언된 통신 정책과 실시간 대조합니다. Yggdrasil에서 *계약은 곧 화이트리스트(Allowlist)*이며, 게이트를 우회하는 모든 미선언 트래픽은 머신러닝으로 학습해야 할 이상 징후가 아니라 **즉각 시정해야 할 계약 위반(Discrepancy)**입니다.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/yggdrasil-iiot/.github/master/profile/system-context.dark.svg">
  <img alt="시스템 컨텍스트: 변경 제안자/승인자, Git 호스팅, 벤더 툴링, OT 설비 및 UNS 소비자 사이에 위치한 Yggdrasil과 명시적으로 표시된 2개의 미해결 개방 축" src="https://raw.githubusercontent.com/yggdrasil-iiot/.github/master/profile/system-context.svg">
</picture>

> **엔지니어링 정직성 선언 — 2개의 미해결 개방 축 (Open Axes)**:  
> 위 아키텍처 다이어그램에서 점선으로 표시된 두 관계는 설계를 누락한 것이 아니라 **현대 산업 제어망의 구조적 한계로 인해 현재 기술적으로 강제되지 못함을 정직하게 명시한 개방 축**입니다:  
> 1. **축 12 (미관리 클라이언트 우회로)**: 거버넌스 엣지를 거치지 않고 PLC나 OPC UA 서버로 직접 세션을 수립하는 임의의 엔지니어링 워크스테이션을 네트워크 레벨에서 완벽히 강제 차단하지 못함.  
> 2. **축 13 (벤더 런타임 역방향 설정 미검증)**: 상용 벤더 툴링(Kepware, Ignition 등)의 런타임 내부 설정을 자동으로 역추출하여 Git 정본 선언문과 실시간 비교하는 폐루프 검증 미연결.  
> 두 축에 대한 엔지니어링 분석 및 대응 로드맵은 [`bifrost/docs/ENTERPRISE.md`](https://github.com/yggdrasil-iiot/bifrost/blob/main/docs/ENTERPRISE.md)에 상세히 수록되어 있습니다.

---

## 1. 컴포넌트 구성 및 아키텍처 역할 (R&R)

| 컴포넌트 | 저장소 링크 | 아키텍처 역할 및 엔지니어링 책임 |
|---|---|---|
| **Bifrost** | [yggdrasil-iiot/bifrost](https://github.com/yggdrasil-iiot/bifrost) | **거버넌스 코어 (The "IAM" for OT)**: 스키마 호환성, 공정 사양 적합성, Git 기반 출처 검증, 명령 인가 및 **앵커드 활성화(Anchored Activation)** 게이트를 호스팅하는 거버넌스 권위체. |
| **Heimdall** | in [yggdrasil-iiot/bifrost](https://github.com/yggdrasil-iiot/bifrost) | **쓰기 경계 런타임 인가 데몬 (Write Boundary Daemon)**: 기본 거부(Deny-by-Default) 원칙에 따라 모든 OPC UA 제어 명령(NCMD)의 인가 권한과 물리적 안전 경계값을 엣지 현장에서 직접 강제. |
| **Mímir** | [yggdrasil-iiot/mimir](https://github.com/yggdrasil-iiot/mimir) | **설비 모델 도출기 (Model Derivation)**: 현장 OPC UA 서버의 타입 공간을 실시간 브라우징하여 자산관리셸(AAS) 정렬 UDT 정의를 자동으로 역추출 및 제안하는 설계 시점 프로듀서. |
| **Muninn** | [yggdrasil-iiot/muninn](https://github.com/yggdrasil-iiot/muninn) | **북향 UNS 데이터 피더 (Northbound Feed)**: 거버넌스를 통과한 설비 정의의 바이트 출처를 암호학적으로 검증하고, Sparkplug B NBIRTH를 발행하며, 매 텔레메트리 샘플의 스키마 적합성을 송출 검증(Egress Validation)하여 UNS로 스트리밍. |
| **Huginn** | [yggdrasil-iiot/huginn](https://github.com/yggdrasil-iiot/huginn) | **수동 관측 및 트래픽 대조 (Observation & Reconciliation)**: 미러링된 pcap 패킷으로부터 Modbus/TCP 및 S7comm 제어 프로토콜을 바이트 단위로 해독하여 선언된 통신 정책과 비교, 게이트를 우회한 미선언 통신을 적발. |

---

## 2. 실증 완료된 핵심 엔지니어링 성과 (What's Proven)

1. **무공유 코드 기반 북향 스파인 파이프라인 (Zero-Shared-Code Spine)**:  
   단일 "Line1 Mixer" 설비 모델이 **Mímir**(모델 도출) → **Bifrost**(거버넌스 승인) → **Muninn**(UNS 송출)으로 흐르는 전 과정을 공통 라이브러리나 공유 의존성 없이 순수한 데이터/회선 계약(Wire Contract)만으로 완벽히 통합 실증하였습니다.
2. **닫힌 제어 피드백 루프 (Closed Feedback Loop)**:  
   단일 MQTT 브로커 환경에서 *관측(Observe) → 제어 명령(Command) → 관측(Observe)*의 완전한 루프를 형성하여, 인가된 설정값 변경 명령이 현장에 적용되고 그 결과가 다시 UNS 텔레메트리로 반영되는 엔드투엔드 인과성을 입증하였습니다.
3. **위변조 방지 앵커드 활성화 수명주기 (Anchored Activation Lifecycle)**:  
   "현재 현장에서 구동 중인 모델/레시피 버전이 정본인가?"를 위변조가 즉시 드러나도록(Tamper-evident) 하고 사후 부인이 불가능하도록(Non-repudiation), 단순 감사 로그를 넘어선 암호학적 이력 체계를 구축하였습니다:  
   `4-eyes 승인` → `해시 체인 불변 원장` → `이중 Ed25519 서명 + 서명된 헤드` → `기본 거부 메이커-체커 인가` → `외부 증인 앵커(External Witness) 대조 크로스체크`.  
   이를 통해 악의적인 내부자에 의한 과거 버전 롤백 공격을 즉각 감지하며, `REQUIRE_SIGNED_ACTIVATION` 및 `REQUIRE_ANCHORED_ACTIVATION` 플래그를 활성화한 경우(두 플래그는 기본값이 꺼짐) 런타임 데몬(Heimdall)은 버전 무결성이 훼손되면 폐쇄형 실패(Fail-Closed)하여 설비 바인딩을 거부합니다.
4. **실제 산업 현장 트래픽(PCAP) 기반 무손실 대조 검증**:  
   Huginn은 공개된 3건의 4SICS ICS 랩 실제 캡처 패킷을 대상으로 산업 표준 네트워크 분석 도구인 **tshark**와 1:1 크로스체크를 수행하였습니다. S7 요청 패킷 수가 **완벽히 일치(23,732 / 86,403 / 53,217건)**함을 확인하였으며, 응답 패킷을 파싱하지 않는 설계 불변식을 실증하고, 미등록 호스트의 PLC 쓰기 시도 및 디바이스 스캔 행위를 성공적으로 적발하였습니다.
5. **가동 중인 기존 공장을 위한 단계적 도입 전략**:  
   - **기록 전용 모드 실증**: 운영 중인 라인을 멈추지 않고 시스템을 도입할 수 있도록, 런타임 엣지에 모든 판정을 기록하되 명령을 차단하지 않는 `ENFORCEMENT_LOG_ONLY` 모드를 탑재하고 실제 브로커 및 OPC UA 서버와 연동하여 안전성을 실증하였습니다.  
   - **6단계 롤아웃 절차 규격화 (공장 실행 이력 없음 · 코드 유도 추론)**: 안전한 단계적 도입을 위한 6단계 롤아웃 절차와 단계별 중단 기준(Abort Criteria)을 [`bifrost/docs/ADOPTION.md`](https://github.com/yggdrasil-iiot/bifrost/blob/main/docs/ADOPTION.md)에 정밀 규격화하였습니다(단, 본 절차는 실제 공장 라인에서 실행된 이력은 없으며 코드베이스 분석으로부터 유도된 엔지니어링 추론 모델입니다).
6. **주장이 아닌 실측 기반 확장성 벤치마크**:  
   원장 증가율, 엔트리당 암호학적 검증 비용, 2개 앵커 저장소 및 100개 사이트 연합 감사(Federated Audit) 성능을 [`bifrost/docs/ENTERPRISE.md`](https://github.com/yggdrasil-iiot/bifrost/blob/main/docs/ENTERPRISE.md) §11에 실측치로 투명하게 공개하였으며, 목표를 달성하지 못한 벤치마크 결과 또한 삭제하지 않고 실패로 명시하였습니다.
7. **재현 가능한 실행 게이트 완비**:  
   본 플랫폼의 핵심 런타임 및 아키텍처 클레임은 단순한 단위 테스트가 아닌 실제 컨테이너 환경에서 검증 가능한 **엔지니어링 통합 게이트 스크립트**(`run-yggdrasil-spine-gate.sh`, `run-yggdrasil-full-loop-gate.sh`, `run-anchored-activation-gate.sh`, `run-ncmd-runtime-gate.sh`)로 뒷받침됩니다. (유일한 예외는 롤아웃 순서 규격으로, 이는 게이트 산출물이 아니라 코드로부터 유도된 엔지니어링 추론이며 해당 문서에 명시되어 있습니다).

---

## 3. 기술 스택 및 아키텍처 표준

- **런타임 환경**: Java 17 LTS, Maven 멀티모듈 아키텍처
- **산업 표준 통신 프로토콜**:
  - **OPC UA**: Eclipse Milo (서버 브라우징, 노드 읽기/쓰기 인가 어댑터)
  - **Sparkplug B**: Eclipse Tahu (v3.0.0 명세 호환 페이로드 인코딩/디코딩)
  - **MQTT**: HiveMQ Community Edition (분산 브로커 및 ACL 프로젝션)
- **독립 패킷 엔진**: 런타임 외부 의존성이 전혀 없는 순수 수제작 PCAP 파서, Modbus/TCP 및 Siemens S7comm 바이너리 프레이밍 엔진
- **암호화 및 무결성 검증**: Ed25519 전자서명, SHA-256 해시 체인 머클 원장
- **라이선스**: [Apache-2.0](LICENSE)

---

<sub>본 프로젝트는 IT/OT 융합 환경을 위한 시스템 아키텍처 레퍼런스 구현체입니다. 각 개별 저장소의 README는 공학적 정직성 원칙에 입각하여 한계점과 경계를 명시하며, 게이트 검증은 물리적 공정 역학이 아닌 거버넌스 루프의 완결성을 증명합니다.</sub>

