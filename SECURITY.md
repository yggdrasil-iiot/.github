# Security policy — Yggdrasil

This is the default policy for repositories in this organisation that do not carry their own.
**Bifrost** and **Huginn** each have a `SECURITY.md` with a threat model specific to what they do;
if you are looking at one of those, read that file instead. This one governs **Mímir** and
**Muninn**.

## What these projects are

Yggdrasil is a **systems-architecture reference implementation** of governance for the IT↔OT
boundary. Nothing here is distributed as a binary, published to a package registry, or running in
a plant. This policy describes how a security report is handled; it is not a commercial support
commitment or a CE-marked manufacturer's vulnerability-handling process under the EU Cyber
Resilience Act.

## Reporting a vulnerability

Use GitHub's **private vulnerability reporting** on the repository in question: its *Security* tab
→ *Report a vulnerability*. It is enabled on every repository here. Please do not open a public
issue for something exploitable.

**What to expect.** Maintained by one person; there is no on-call rotation, so no SLA is promised.
Acknowledgement within a few days, then a fix or a documented decision. If a report goes
unanswered for two weeks, opening a public issue that says only "unacknowledged private report,
see Security tab" is reasonable and will not be treated as bad faith.

## Mímir and Muninn — where the surface actually is

Both are **OPC UA clients**. They browse or sample a server and act on what it returns, which
means a hostile or compromised server is the input they cannot choose. Both also parse JSON from
the registry.

**Muninn carries two actual security controls, and those are the things worth attacking:**

- **Provenance verification.** It recomputes SHA-256 over the raw registry bytes, compares it to
  the sibling `manifest.json`, and **refuses to birth on mismatch**. Any way to make it birth a
  definition whose bytes were not the ones verified — verify one, publish another — is a finding.
- **Egress validation.** It checks every live sample against the governed definition and **drops**
  non-conformant metrics before publishing NDATA. Any way to get a non-conformant metric onto the
  bus past that check is a finding.

For **Mímir**, the equivalent is that it only ever *proposes*: a derived definition is not
canonical until Bifrost's gate admits it. A path by which Mímir's output is treated as governed
without passing that gate is a finding.

Beyond those: crashes, hangs or memory exhaustion driven by a crafted server response, a crafted
registry document, or a crafted Sparkplug payload.

## Already known, and by design

- **Demo scale.** Single broker, single edge, localhost. There is no hardened deployment posture
  to bypass, because there is no deployment posture.
- **No transport security story.** Broker credentials and TLS are whatever the local harness sets
  up. "The demo connects to MQTT without TLS" is the configuration, not a vulnerability.
- **No authentication between components.** They compose through a published data and wire
  contract with zero shared code, and that contract does not carry identity. Identity lives in
  Bifrost's activation ledger, and its limits are documented in
  [bifrost/docs/ENTERPRISE.md](https://github.com/yggdrasil-iiot/bifrost/blob/main/docs/ENTERPRISE.md) §6.
- **ISA-95 and AAS are alignments, not certifications.**

## Out of scope

- Findings in third-party libraries with no exploit path through this code. Mímir depends on
  Eclipse Milo and Jackson; Muninn adds Eclipse Tahu, Paho and Logback. Those belong upstream.
- Anything requiring write access to the registry or the machine.
- The `sim` module in Bifrost, which is a test fixture.

## Supported versions

Pre-1.0. Only the default branch, and the latest tag where one exists.
