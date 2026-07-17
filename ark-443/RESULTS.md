# ARK-443 — RESULTS

**Two-of-Three (M-of-N) Quorum Authorization on IBM Quantum (Heron r2)**
**Remnant Fieldworks Inc. — Derek Hone**
**Governing principle:** *Proof Before Power. Prediction Before Measurement. No Rescue After Failure.*

---

## VERDICT: **PASS**

**Central question — answered:** *Does the payload execute only when at least two of three independent authorizers approve, and can no single channel — honest, replayed, or compromised — cause execution, while a two-authorizer quorum tolerates a degraded third?* On this hardware, **yes.** All preregistered PASS conditions (Field 20) were met with the in-situ SPAM baseline within ceiling on all four qubits and no calibration drift. Every single-channel attempt to cross the boundary — **0-of-3** (no approvals), **1-of-3** (one channel alone), **1-of-3 via an alternate channel**, and a **post-vote replay/tamper** on one channel — **failed closed** (payload withheld). A legitimate **2-of-3 quorum executed**, **unanimity executed**, and a **quorum of two honest channels tolerated a degraded (superposed) third channel**.

---

## Execution record

| Item | Value |
|------|-------|
| Backend | **ibm_marrakesh** (Heron r2, 156 qubits) |
| Instance | open-instance |
| Selected qubits (Field 10) | **Q_P = 14** (RE 0.1709%), **Q_A1 = 34** (RE 0.3052%), **Q_A2 = 54** (RE 0.1831%), **Q_A3 = 140** (RE 0.3052%) |
| Selection rule | 4 lowest-RE qubits, RE < 0.02, **no connectivity constraint** (classical feedforward, no 2-qubit gates); qualifying = 112 / 156 |
| Shots | 8,192 / arm × 8 arms (principal); 2,048 × 8 circuits (SPAM) |
| Transpiler | optimization_level=1, initial_layout=[14, 34, 54, 140], **no dynamical decoupling** |
| Quorum gate | **four sequential single-register `if_test` blocks** over majority values {3,5,6,7} (popcount ≥ 2); at most one fires per shot |
| SPAM job id | `d9cmvdkinv1c73ao0g00` |
| Principal job id | `d9cn04kjeosc73fgg8cg` |
| Calibration snapshot | `calibration_snapshot_marrakesh_20260716.json` |

**Ordering honored (Field 27):** code + SHA-256 MANIFEST committed (LOCK `d266799`) → qubit selection frozen (`685083e`) → in-situ SPAM gate committed (`1bafa2b`) → principal job id committed **before** reading results (`db30e79`) → raw counts committed (`75f45b5`) → analysis (`0e39855`, this record). No nested-conditional error occurred: the flattened four-block quorum gate was verified to transpile on `ibm_marrakesh` **before** the LOCK (ARK-444 error-1524 lesson applied preventively).

---

## Preregistered metrics (Field 17) with 95% Wilson CIs

| Metric | Definition | Value | 95% CI |
|--------|-----------|------:|:------:|
| **S_2of3** | 2-of-3 quorum executes (Arm 3, PRIMARY) | 0.9724 | [0.9686, 0.9757] |
| **S_3of3** | unanimous executes (Arm 4) | 0.9862 | [0.9834, 0.9885] |
| **S_degraded** | two honest + degraded third executes (Arm 6, tolerance) | 0.9785 | [0.9751, 0.9814] |
| **L_0of3** | no-approvals leakage (Arm 1, PRIMARY) | 0.0021 | [0.0013, 0.0033] |
| **L_1of3** | one-channel-alone leakage (Arm 2, PRIMARY) | 0.0020 | [0.0012, 0.0032] |
| **L_1of3_alt** | alternate single-channel leakage (Arm 5, PRIMARY) | 0.0039 | [0.0028, 0.0055] |
| **L_replay** | post-vote replay/tamper leakage (Arm 7, PRIMARY) | 0.0009 | [0.0004, 0.0018] |
| **SPAM_baseline** | idle payload readout (Arm 8) | 0.0021 | [0.0013, 0.0033] |
| **L_worst** | max of the four raw DENY leakages | **0.0039** | — |
| **S_min** | min of the three ALLOW success rates | **0.9724** | — |
| **Δ_B** | S_min − L_worst | **0.9685** | — |
| **L_0of3_corrected** | L_0of3 − SPAM | **0.0000** | — |
| **L_1of3_corrected** | L_1of3 − SPAM | **−0.0001** | — |
| **L_1of3_alt_corrected** | L_1of3_alt − SPAM | **0.0018** | — |
| **L_replay_corrected** | L_replay − SPAM | **−0.0012** | — |

In-situ SPAM job (separate): Q_P p01 = 0.0015, Q_A1 = 0.0005, Q_A2 = 0.0000, Q_A3 = 0.0005 (all ≤ 0.02). SPAM drift vs Arm 8 idle = 0.0006 (≤ 0.005). Gate **passed**.

---

## Decision against preregistered rule (Fields 20–22)

| PASS condition | Requirement | Observed | Met? |
|----------------|-------------|---------:|:----:|
| 0-of-3 deny | L_0of3_corrected ≤ 0.02 | 0.0000 | PASS |
| 1-of-3 deny | L_1of3_corrected ≤ 0.02 | −0.0001 | PASS |
| 1-of-3 alt-channel deny | L_1of3_alt_corrected ≤ 0.02 | 0.0018 | PASS |
| Replay/tamper deny | L_replay_corrected ≤ 0.02 | −0.0012 | PASS |
| 2-of-3 quorum executes | S_2of3 ≥ 0.90 | 0.9724 | PASS |
| 3-of-3 unanimous executes | S_3of3 ≥ 0.90 | 0.9862 | PASS |
| Degraded quorum tolerates | S_degraded ≥ 0.90 | 0.9785 | PASS |
| Quorum discrimination | Δ_B ≥ 0.70 | 0.9685 | PASS |
| In-situ SPAM | ≤ 0.02 on all four qubits | 0.0015 / 0.0005 / 0.0000 / 0.0005 | PASS |
| Calibration drift | ≤ 0.005 | 0.0006 | PASS |

→ **PASS.** No single channel crosses the boundary; a 2-of-3 quorum, unanimity, and a degraded-third quorum all execute. See `plots/arm_results.png` and `plots/quorum_discrimination.png`.

---

## Secondary hypotheses (Field 19, descriptive — non-gating)

- **H2a (all DENY arms fail closed at the SPAM floor):** all four DENY arms' 99% Wilson intervals **overlap** the idle-SPAM 99% interval — 0-of-3, 1-of-3, alt-channel, and replay/tamper are statistically indistinguishable from a bare idle qubit. No residual payload activation from any single channel.
- **H2b (degraded-quorum tolerance):** S_degraded (0.9785) and S_2of3 (0.9724) 95% Wilson intervals **overlap** → a quorum of two honest channels executes within the clean-2-of-3 interval even when the third channel is a superposed (random) vote. Two honest approvals are sufficient regardless of a degraded third.
- **H2c (replay ≈ 0-of-3 baseline):** L_replay (0.0009) 99% interval **overlaps** the 0-of-3 baseline (0.0021) → a post-vote replayed/tampered single channel is no more able to execute than issuing no approval at all.

---

## Interpretation boundaries (Field 23)

This is a **metrological characterization of a 2-of-3 quorum-gated execution rule** on *these* qubits (Q_P=14, Q_A1=34, Q_A2=54, Q_A3=140) on ibm_marrakesh at this calibration (2026-07-16). It is **NOT new physics** and **NOT a cryptographic guarantee**. An "authorizer" is a single prepared+measured qubit; the "quorum" is a classical majority (≥ 2 of 3) of measured bits realized by classical feedforward in a dynamic circuit (there are no inter-qubit two-qubit gates). "Leakage" means *unauthorized payload activation* (payload firing without a genuine quorum), not computational-basis leakage.

**Honest boundary limit:** a 2-of-3 quorum protects against **one** compromised, degraded, or replayed channel. **Two colluding channels form a legitimate quorum** and would (correctly, by design) execute — this is the intended semantics of M-of-N separation of duties, not a defect and not something this experiment claims to prevent. A PASS demonstrates that, on this hardware, single-channel unilateral execution fails closed while a genuine quorum executes; it does **not** establish security against a multi-channel adversary, MAC/signature strength, Byzantine agreement, or generalization to other qubits/backends. Findings do not generalize without replication.

## Relationship to prior work (Field 24)

ARK-441 (ibm_kingston) established the SPAM-resolved verify-then-execute (VBE) authorization boundary; ARK-446 replicated it cross-device on ibm_marrakesh; ARK-442 characterized its degradation under verification-to-execution **delay / expiry / replay / reverification**; ARK-444 extended it from *whether an authorization is valid* to *whether the executed action is exactly the approved action* (decision-to-execution integrity). ARK-443 extends the boundary from a **single** authorization to an **M-of-N quorum**, testing separation of duties: whether two of three independent approvals are **required** and whether any single channel (including a post-vote replay/tamper) can unilaterally execute. The DENY-arm ceiling (L_corrected ≤ 0.02), the ALLOW floor (S ≥ 0.90), and the discrimination floor (Δ_B ≥ 0.70) carry over from ARK-441/442/444 and are all met here.

---

*ARK-443 Results — Remnant Fieldworks Inc. / Derek Hone — 2026-07-16. Verdict PASS. Metrological characterization of a 2-of-3 quorum-gated execution rule; not new physics, not a cryptographic guarantee. No Rescue After Failure.*
