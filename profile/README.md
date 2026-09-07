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

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/yggdrasil-iiot/.github/master/profile/system-context.dark.svg">
  <img alt="System context: Yggdrasil between the people who propose and approve changes, Git hosting, vendor tooling, OT equipment and UNS consumers, with the two open axes drawn as missing relationships" src="https://raw.githubusercontent.com/yggdrasil-iiot/.github/master/profile/system-context.svg">
</picture>

Two of the relationships above are drawn because they are missing. Nothing makes the governed
edge the only way into the equipment, and nothing reads a vendor runtime's live configuration
back to check it against the declaration. Both are tracked as open axes in
[bifrost/docs/ENTERPRISE.md](https://github.com/yggdrasil-iiot/bifrost/blob/main/docs/ENTERPRISE.md).

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
- **Installable at a plant that already runs** — the runtime edge has an
  `ENFORCEMENT_LOG_ONLY` mode in which it reaches every verdict and refuses nothing, so it can
  be introduced without being able to stop the line; enforcement then arrives by removing
  allowlist rules one reviewable diff at a time. That mode is proven end-to-end against a live
  broker and OPC-UA server, including its reversal by restart. The **rollout order** it belongs
  to — six phases, each with an exit and an abort criterion — is written down in
  [bifrost/docs/ADOPTION.md](https://github.com/yggdrasil-iiot/bifrost/blob/main/docs/ADOPTION.md),
  and is derived from the code's constraints rather than from experience.
- **Scale claims are measured, not asserted** — ledger growth, per-entry verification cost, the
  two anchor stores and a hundred-site federated audit are all benchmarked in
  [bifrost/docs/ENTERPRISE.md](https://github.com/yggdrasil-iiot/bifrost/blob/main/docs/ENTERPRISE.md) §11,
  including the runs that came out unusable, which are reported as failures rather than dropped.
- Every claim above has a **check you can run**, not an assertion — the spine, the loop, the ledger and the rollout mode by integration gates (`run-yggdrasil-spine-gate.sh`, `run-yggdrasil-full-loop-gate.sh`, `run-anchored-activation-gate.sh`, `run-ncmd-runtime-gate.sh`); the reconciliation by regression tests that pin the tshark-matched counts against the captures themselves; the scale figures by benchmark scripts that assert nothing and print numbers. **The one exception is the rollout order** — that is reasoning about the code rather than a result, and it says so where it is written.

## Stack

Java 17 · Eclipse Milo (OPC-UA) · Eclipse Tahu (Sparkplug B) · MQTT / HiveMQ CE · hand-rolled pcap / Modbus-TCP / S7comm framing (no runtime deps) · Maven multi-module · Apache-2.0.

---

<sub>A systems-architecture reference implementation. Each repo's README records honest scope & limitations — the gates prove governance closes the loop, not process physics.</sub>
