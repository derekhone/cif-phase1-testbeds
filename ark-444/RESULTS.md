# ARK-444 — RESULTS

**Decision-to-Execution Integrity on IBM Quantum (Heron r2)**
**Remnant Fieldworks Inc. — Derek Hone**

> **STATUS: PENDING_EXECUTION** · **VERDICT: PENDING_EXECUTION**
> No results have been observed yet. This placeholder is committed as part of the preregistration record and will be filled after execution.

---

## Provenance

| Item | Value |
|------|-------|
| Preregistration lock commit | *(recorded in RUN_LOG.md at commit time)* |
| SPAM results commit | TBD |
| Job-ID record commit | TBD |
| Raw results commit | TBD |
| Backend | `ibm_marrakesh` (Heron r2) *(or ibm_fez fallback)* |
| Qubits (Q_A, Q_P) | TBD — selected at execution from live calibration (Field 10) |
| SPAM job ID | TBD |
| Principal job ID | TBD |
| Execution date (UTC) | TBD |

---

## In-situ SPAM gate

| Qubit | SPAM_baseline (p01) | ≤ 0.02 ? |
|-------|---------------------|----------|
| Q_A | TBD | TBD |
| Q_P | TBD | TBD |

---

## Raw results — all 8 arms

| Arm | Endpoint | P(Q_P=1) | 95% Wilson CI |
|-----|----------|----------|---------------|
| 1 `arm1_approved_unchanged` | S_match | TBD | TBD |
| 2 `arm2_destination_changed` | L_dest | TBD | TBD |
| 3 `arm3_amount_changed` | L_amount | TBD | TBD |
| 4 `arm4_operation_changed` | L_optype | TBD | TBD |
| 5 `arm5_extra_action_appended` | L_append | TBD | TBD |
| 6 `arm6_approval_replayed` | L_replay | TBD | TBD |
| 7 `arm7_mutated_then_reverified` | S_reverified | TBD | TBD |
| 8 `arm8_idle_spam` | SPAM_baseline | TBD | TBD |

---

## Primary metrics

| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| L_dest_corrected | TBD | ≤ 0.02 | TBD |
| L_amount_corrected | TBD | ≤ 0.02 | TBD |
| L_optype_corrected | TBD | ≤ 0.02 | TBD |
| L_append_corrected | TBD | ≤ 0.02 | TBD |
| L_replay_corrected | TBD | ≤ 0.02 | TBD |
| S_reverified | TBD | ≥ 0.90 | TBD |
| Δ_B (unchanged vs worst altered) | TBD | ≥ 0.70 | TBD |

---

## Interpretation boundaries

A PASS would demonstrate that, on this qubit pair, backend, and calibration, the verify-then-execute boundary detects every tested class of post-approval alteration (destination, amount, operation type, appended action, replayed approval) and **fails closed** (payload not executed), while a re-verified mutated action correctly executes. This is a **metrological characterization of a tamper-evident decision-to-execution binding**, **not** new physics and **not** a cryptographic integrity guarantee. "Leakage" = unauthorized payload activation. Findings do not generalize without replication.

*Dependencies: `ARK_444_preregistration.md` (protocol and thresholds).*
