<div align="center">

![Yggdrasil — IIoT governance spine](https://raw.githubusercontent.com/yggdrasil-iiot/.github/master/profile/hero.png)

# Yggdrasil

**A governance spine for the OT/IT boundary of industrial IIoT systems.**

</div>

Yggdrasil governs how equipment models and process specs flow from the plant floor (OT)
up to the unified namespace (IT) — and how commands flow back down — so that *nothing
crosses the boundary except a governed, provenance-verified contract*. The components
share **zero code**; they compose only through a data & wire contract.

A governed boundary, though, only governs what passes *through* it. So the spine also
looks at the wire itself: **Huginn** reads the industrial traffic that actually flowed and
reconciles it against what was declared, because *the contract is the allowlist* — bypass
is a difference, not an anomaly to be learned.

## Components

| | Repo | Role |
|---|---|---|
| **Bifrost** | [bifrost](https://github.com/yggdrasil-iiot/bifrost) | Governance core — the "IAM" for the OT governance boundary. Schema · spec · provenance · command authz · **anchored activation** gates over the governed model. |
| **Heimdall** | in [bifrost](https://github.com/yggdrasil-iiot/bifrost) | Runtime authorization at the write boundary. Deny-by-default; enforces authz + bounds on every OPC-UA command. |
| **Mímir** | [mimir](https://github.com/yggdrasil-iiot/mimir) | Model derivation — browses live OPC-UA equipment types into governed, AAS-aligned definitions. |
| **Muninn** | [muninn](https://github.com/yggdrasil-iiot/muninn) | Northbound feed — provenance-verifies the governed def, births it into Sparkplug B, and egress-validates every sample into the UNS. |
| **Huginn** | [huginn](https://github.com/yggdrasil-iiot/huginn) | Observation & reconciliation — decodes Modbus/TCP · S7comm out of a pcap and compares it against the declared communication policy. Finds the traffic that never went through the gate. |

## What's proven

- **Northbound spine** — one "Line1 Mixer" flows **Mímir** (model) → **Bifrost** (govern) → **Muninn** (feed UNS), coupled only by the data/wire contract.
- **Closed feedback loop** — *observe → command → observe*: a governed, authorized setpoint command changes what the UNS observes, end-to-end on a single broker.
- **Anchored activation lifecycle** — *which version is live* is a governed event, hardened from an audit trail into an authenticated, non-repudiable history: four-eyes activation → a tamper-evident hash-chained ledger → **dual Ed25519 signatures + a signed head** → deny-by-default maker-checker authorization → a **four-eyes head cross-checked against an external anchor witness**, which makes insider rollback evident. Each tier is additive and backward-compatible; the edge bars above signing are opt-in (`REQUIRE_SIGNED_ACTIVATION` / `REQUIRE_ANCHORED_ACTIVATION`, both default off), and when raised Heimdall fail-closes before it binds a version.
- **Reconciliation against real traffic** — Huginn was cross-checked against **tshark** on three public 4SICS ICS-lab captures: S7 request counts match **exactly** (23,732 / 86,403 / 53,217), responses are never observed (a design rule, held on real traffic), and the findings include an unregistered host writing to a PLC over S7 and a device-enumeration sweep.
- Every claim above has an **executable proof**, not an assertion — the spine, the loop and the ledger by integration gates (`run-yggdrasil-spine-gate.sh`, `run-yggdrasil-full-loop-gate.sh`, `run-anchored-activation-gate.sh`); the reconciliation by regression tests that pin the tshark-matched counts against the captures themselves.

## Stack

Java 17 · Eclipse Milo (OPC-UA) · Eclipse Tahu (Sparkplug B) · MQTT / HiveMQ CE · hand-rolled pcap / Modbus-TCP / S7comm framing (no runtime deps) · Maven multi-module · Apache-2.0.

---

<sub>A systems-architecture reference implementation. Each repo's README records honest scope & limitations — the gates prove governance closes the loop, not process physics.</sub>
