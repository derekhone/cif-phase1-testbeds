# ARK-446 — RESULTS
**Cross-Device Replication of the ARK-441 VBE Authorization Boundary on ibm_marrakesh (Heron r2)**
**Remnant Fieldworks Inc. — Derek Hone**
**Governing principle:** *Proof Before Power. Prediction Before Measurement. No Rescue After Failure.*

> **PLACEHOLDER — PENDING EXECUTION.** This file is a placeholder committed as part of the
> preregistration record. Values will be filled and the verdict determined **after** IBM job
> execution. No IBM Quantum job has been submitted for ARK-446 at the time of this commit.

> **Independence:** ARK-446 is an **independent, supplemental hardware experiment** — a cross-device
> replication of ARK-441. It is **NOT** part of the UIP Phase 1/2 program. Its only scientific
> lineage is VBE-1 → ARK-441. See ARK-441's `INDEPENDENCE_NOTICE.md`.

---

## Status: **PENDING_EXECUTION**

## Verdict: **PENDING_EXECUTION**

The preregistered verify-then-execute authorization boundary replication on `ibm_marrakesh` has
**not yet been executed**. This document is committed as part of the locked preregistration record.
The verdict (PASS / FAIL / KILLED) will be determined only after the SPAM gate and principal job
run on hardware, per the Field 20–22 conditions of `ARK_446_preregistration.md`. Until then the
status is **PENDING_EXECUTION** — no result has been observed.

---

## Provenance (locked before any job)

| Item | Value |
|------|-------|
| Preregistration lock commit (SHA) | `f4219a4e8332dacf9bb987332a9465ae70c68177` |
| SPAM results commit | TBD (after SPAM job) |
| Job-ID record commit (RUN_LOG) | TBD (after submission) |
| Raw results commit | TBD (after retrieval) |
| Backend | ibm_marrakesh (Heron r2) — *primary target; fallback ibm_fez per Field 9* |
| Qubits | TBD — selected at execution time from live calibration (RE < 2%, connected, min combined RE) per Field 10 |
| SPAM job ID | TBD |
| Principal job ID | TBD |
| Shots | 8,192 per arm × 8 arms = 65,536 (principal); 2,048 × 4 = 8,192 (SPAM) |
| Primary endpoint | **RAW counts, no readout mitigation** |
| Execution date | TBD |

---

## In-situ SPAM gate (runs and committed FIRST)

| Qubit | SPAM_baseline (P(read 1 \| prepared 0)) | Ceiling | Pass? |
|-------|-----------------------------------------|---------|-------|
| Q_A (TBD) | TBD | ≤ 2% | TBD |
| Q_P (TBD) | TBD | ≤ 2% | TBD |

Per Field 22: if `SPAM_baseline > 0.02` on **either** qubit → KILLED / INDETERMINATE; stop
immediately, submit no principal job, no rescue.

---

## Raw results — all 8 arms (payload register `cp`)

| Arm | Purpose | P(Q_P=1) | 95% Wilson CI | counts (1/total) |
|-----|---------|----------|---------------|------------------|
| 1 `arm1_allow` | ALLOW fidelity S_A | TBD | TBD | TBD |
| 2 `arm2_deny` | **DENY leakage L_D (PRIMARY)** | TBD | TBD | TBD |
| 3 `arm3_ungated_control` | ungated control L_control | TBD | TBD | TBD |
| 4 `arm4_idle_spam` | idle SPAM baseline | TBD | TBD | TBD |
| 5 `arm5_stale_auth` | stale-auth analogue | TBD | TBD | TBD |
| 6 `arm6_replayed_auth` | replayed-auth analogue | TBD | TBD | TBD |
| 7 `arm7_superposition_auth` | superposition auth | TBD | TBD | TBD |
| 8 `arm8_payload_readout_ref` | payload readout ref | TBD | TBD | TBD |

---

## Primary metrics

| Metric | Definition | Value | 95% CI / bound |
|--------|-----------|-------|-----------------|
| L_D | P(Q_P=1 \| Arm 2 DENY) | TBD | TBD |
| S_A | P(Q_P=1 \| Arm 1 ALLOW) | TBD | TBD |
| SPAM_baseline | P(Q_P=1 \| Arm 4 idle) | TBD | TBD |
| L_control | P(Q_P=1 \| Arm 3 ungated) | TBD | TBD |
| **Δ_B** | S_A − L_D | TBD | — |
| **L_D_corrected** | L_D − SPAM_baseline | TBD | TBD |
| I_L | (L_control − L_D)/L_control | TBD | — |

---

## Per-criterion scoring (honest, against the preregistered windows)

| Criterion | Window | Observed | Result |
|-----------|--------|----------|--------|
| In-situ SPAM gate (Q_A) | ≤ 0.02 | TBD | TBD |
| In-situ SPAM gate (Q_P) | ≤ 0.02 | TBD | TBD |
| `L_D_corrected` | ≤ 0.02 | TBD | TBD |
| `Δ_B` | ≥ 0.70 | TBD | TBD |
| **PRIMARY H1** | all three above | TBD | **PENDING_EXECUTION** |

**Overall decision: PENDING_EXECUTION.** The PASS / FAIL / KILLED verdict is reserved for
post-execution and will be determined strictly against the preregistered Field 20–22 windows.

---

## Secondary / adversarial arms (H2, Bonferroni-aware)

- **H2a — stale auth (Arm 5):** TBD (compare to ALLOW, Arm 1).
- **H2b — replayed auth (Arm 6):** TBD (compare to DENY, Arm 2).
- **H2c — superposition auth (Arm 7):** TBD (predicted ≈ 0.50).
- **H2d — cross-device concordance:** TBD (marrakesh point estimates vs ARK-441 ibm_kingston 95% Wilson intervals).

---

## Diagnostic: L_D vs SPAM distinguishability

`L_D_vs_SPAM_distinguishable_99`: TBD. Per the preregistration (Fields 18, 20, 22) this is a
**reported diagnostic, not a pass/fail gate**.

---

## Interpretation boundaries (as preregistered)

A PASS, if obtained, would demonstrate **cross-device replicability** of the VBE authorization
boundary on a second, independent Heron device. It does **not** generalize beyond this backend /
calibration / qubit pair, does not establish a general security guarantee, and makes **no**
cryptographic claim. "Leakage" means *unauthorized payload activation*, not computational-basis
leakage. Primary figures are raw counts; no readout mitigation is applied to the primary endpoint.

---

*ARK-446 Results — Remnant Fieldworks Inc. / Derek Hone — Execution date: TBD. Verdict:
PENDING_EXECUTION. This file is a placeholder committed as part of the preregistration record;
values will be filled and the verdict determined after IBM job execution.*
