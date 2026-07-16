# ARK-442 — RESULTS

**Authorization Boundary Degradation Under Verification-to-Execution Delay on IBM Quantum (Heron r2)**
**Remnant Fieldworks Inc. — Derek Hone**
**Governing principle:** *Proof Before Power. Prediction Before Measurement. No Rescue After Failure.*

---

## VERDICT: **PASS**

All four preregistered PASS conditions (Field 20) were met with the in-situ SPAM baseline within ceiling on both qubits and no calibration drift. Expired and replayed authorizations did **not** execute the payload; fresh reverification restored ALLOW.

---

## Execution record

| Item | Value |
|------|-------|
| Backend | **ibm_marrakesh** (Heron r2, 156 qubits) |
| Instance | open-instance |
| Selected qubit pair (Field 10) | **Q_A = 5** (RE 0.4883%), **Q_P = 6** (RE 0.4028%), sum 0.8911% |
| Qualifying connected pairs | 92 (min-sum rule; next best [140,141]=0.9033%) |
| Shots | 8,192 / arm × 8 arms (principal); 2,048 × 4 (SPAM) |
| Transpiler | optimization_level=1, initial_layout=[5,6], **no dynamical decoupling** |
| SPAM job id | `d9clmusjeosc73fgeo10` |
| Principal job id | `d9clom4jeosc73fgeq3g` |
| Calibration snapshot | `calibration_snapshot_marrakesh_20260716.json` |

**Ordering honored (Field 27):** code+MANIFEST committed (lock `74212534`) → qubit pair frozen (`86e0432e`) → SPAM committed (`4aef0834`) → principal job id committed **before** reading (`1a58d554`) → raw counts committed (`63a5dceb`) → analysis (this record).

---

## Preregistered metrics (Field 17) with 95% Wilson CIs

| Metric | Definition | Value | 95% CI |
|--------|-----------|------:|:------:|
| **S_A_0** | ALLOW, 0 µs (Arm 1) | 0.9878 | [0.9852, 0.9900] |
| **S_A_short** | ALLOW, ~0.5 µs (Arm 2) | 0.9884 | [0.9858, 0.9905] |
| **S_A_medium** | ALLOW, ~1.0 µs (Arm 3) | 0.9866 | [0.9838, 0.9888] |
| **S_A_long** | ALLOW, ~2.0 µs (Arm 4) | 0.9832 | [0.9801, 0.9857] |
| **L_expired** | expired-auth leakage (Arm 5, PRIMARY) | 0.0001 | [0.0000, 0.0007] |
| **L_replayed** | replayed-auth leakage (Arm 6, PRIMARY) | 0.0015 | [0.0008, 0.0026] |
| **S_reverified** | reverified ALLOW fidelity (Arm 7) | 0.9916 | [0.9894, 0.9933] |
| **SPAM_baseline** | idle readout (Arm 8) | 0.0001 | [0.0000, 0.0007] |
| **Δ_B** | S_A_0 − L_expired | **0.9877** | — |
| **L_expired_corrected** | L_expired − SPAM_baseline | **0.0000** | — |
| **L_replayed_corrected** | L_replayed − SPAM_baseline | **0.0013** | — |

In-situ SPAM job (separate): Q_A p01 = 0.0039, Q_P p01 = 0.0005 (both ≤ 0.02). SPAM drift vs Arm 8 idle = 0.0004 (≤ 0.005). Gate **passed**.

---

## Decision against preregistered rule (Fields 20–22)

| PASS condition | Requirement | Observed | Met? |
|----------------|-------------|---------:|:----:|
| Expired DENY | L_expired_corrected ≤ 0.02 | 0.0000 | ✅ |
| Replayed DENY | L_replayed_corrected ≤ 0.02 | 0.0013 | ✅ |
| Reverification | S_reverified ≥ 0.90 | 0.9916 | ✅ |
| Boundary discrimination | Δ_B ≥ 0.70 | 0.9877 | ✅ |
| In-situ SPAM | ≤ 0.02 on both qubits | 0.0039 / 0.0005 | ✅ |
| Calibration drift | ≤ 0.005 | 0.0004 | ✅ |

→ **PASS.**

---

## Delay-decay characterization (H2a — descriptive, non-gating)

ALLOW survival vs verification-to-execution delay:

| Delay | S_A | 95% CI |
|-------|----:|:------:|
| 0.0 µs | 0.9878 | [0.9852, 0.9900] |
| 0.5 µs | 0.9884 | [0.9858, 0.9905] |
| 1.0 µs | 0.9866 | [0.9838, 0.9888] |
| 2.0 µs | 0.9832 | [0.9801, 0.9857] |

The ALLOW survival erodes by ≈0.5 percentage points from 0 → 2.0 µs — a small, decoherence-consistent decline (the payload T1 on Q_P is long relative to the 2 µs probe window, so the boundary degrades only slightly on this timescale). The strict point-estimate ordering is not monotone (Arm 2 sits marginally above Arm 1, within overlapping CIs — statistical noise at the 8,192-shot level), so the preregistered monotonicity flag (H2a) reads **False**; H2a is descriptive and carries no pass/fail weight (Fields 6, 20). See `plots/delay_decay.png`.

## Secondary hypotheses (Bonferroni, Field 19)

- **H2b (replay ≈ expiry):** L_replayed (0.0015) and L_expired (0.0001) — 99% Wilson intervals **overlap** → a replayed stale bit is statistically no better than an expired one. Consistent with H2b.
- **H2c (reverification concordance):** S_reverified (0.9916) and S_A_0 (0.9878) — 95% Wilson intervals **overlap** → fresh reverification is concordant with the immediate ALLOW reference. Consistent with H2c.

---

## Interpretation boundaries (Field 23)

This is a **metrological characterization of decoherence-driven erosion** of a verify-then-execute authorization boundary as the verification-to-execution separation increases. It is **NOT new physics** and **NOT a cryptographic claim**. "Leakage" means *unauthorized payload activation*, not computational-basis leakage. Findings apply only to this boundary implementation on this qubit pair (Q_A=5, Q_P=6) on ibm_marrakesh at this calibration (2026-07-16) and do not generalize without replication. The delay arms measure how ALLOW survival decays with idle time; the expired/replayed arms show a stale authorization is correctly not honored; the reverification arm shows ALLOW is restored with a fresh measurement.

## Relationship to prior work (Field 24)

ARK-442 extends the single ~1 µs stale-auth arm of ARK-441 into a delay-resolved characterization (0/0.5/1.0/2.0 µs) and adds explicit expired-auth, replay-after-expiry, and reverification arms. The DENY-arm thresholds (L_D_corrected ≤ 0.02, Δ_B ≥ 0.70) carry over from ARK-441 and are met here. ARK-446 (cross-device replication on ibm_marrakesh, same Q_A=5/Q_P=6 pair) returned PASS concurrently; ARK-442 characterizes the boundary's degradation under delay on that same pair.

---

*ARK-442 Results — Remnant Fieldworks Inc. / Derek Hone — 2026-07-16. Verdict PASS. Metrological characterization of decoherence-driven boundary erosion; not new physics, not a cryptographic claim. No Rescue After Failure.*
