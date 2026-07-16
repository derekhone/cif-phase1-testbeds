# ARK-444 — RESULTS

**Decision-to-Execution Integrity on IBM Quantum (Heron r2)**
**Remnant Fieldworks Inc. — Derek Hone**
**Governing principle:** *Proof Before Power. Prediction Before Measurement. No Rescue After Failure.*

---

## VERDICT: **PASS**

**Central question — answered:** *Can the system detect when an approved action is altered before execution and fail closed?* On this hardware and binding, **yes.** All five preregistered PASS conditions (Field 20) were met with the in-situ SPAM baseline within ceiling on both qubits and no calibration drift. Every post-approval alteration (destination, amount, operation type, appended action) and the replayed stale approval **failed closed** — the payload did not execute — while a mutated action that was **re-verified** correctly executed.

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
| Integrity gate | single-register `if_test` (`ci == 0b11`) + top-level mid-circuit `reset` |
| SPAM job id | `d9cmadkinv1c73anvn90` |
| Principal job id | `d9cmgi9htsac739bv2mg` |
| Calibration snapshot | `calibration_snapshot_marrakesh_20260716.json` |

**Ordering honored (Field 27):** code+MANIFEST committed (lock `633f7fb`) → qubit pair frozen (`43a6651`) → SPAM committed (`f7dd557`) → **v1.1 control-flow re-lock** (`144fb17`) → corrected principal job id committed **before** reading (`33cd558`) → raw counts committed (`acd17f4`) → analysis (this record).

**Provenance (Amendment v1.1):** the v1.0 principal job `d9cmdvsjeosc73fgfk5g` (nested `if_test`) **ERRORED** with IBM code 1524 (nested conditionals unsupported) and produced **zero counts**. The integrity gate was flattened to a single-register condition (measurable semantics unchanged), re-locked at `144fb17` **before** the corrected job was submitted. This is a pre-data technical correction, not a rescue-after-failure — there was no result to rescue. The errored job id is retained permanently.

---

## Preregistered metrics (Field 17) with 95% Wilson CIs

| Metric | Definition | Value | 95% CI |
|--------|-----------|------:|:------:|
| **S_match** | approved-unchanged executes (Arm 1, reference) | 0.9808 | [0.9776, 0.9836] |
| **L_dest** | destination-changed leakage (Arm 2, PRIMARY) | 0.0087 | [0.0069, 0.0109] |
| **L_amount** | amount/parameter-changed leakage (Arm 3, PRIMARY) | 0.0101 | [0.0082, 0.0125] |
| **L_optype** | operation-changed leakage (Arm 4, PRIMARY) | 0.0082 | [0.0064, 0.0104] |
| **L_append** | extra-action-appended leakage (Arm 5, PRIMARY) | 0.0112 | [0.0092, 0.0138] |
| **L_replay** | approval-replayed leakage (Arm 6, PRIMARY) | 0.0002 | [0.0001, 0.0009] |
| **S_reverified** | mutated-then-reverified executes (Arm 7, recovery) | 0.9781 | [0.9748, 0.9811] |
| **SPAM_baseline** | idle payload readout (Arm 8) | 0.0000 | [0.0000, 0.0005] |
| **L_worst** | max of the five raw leakages | **0.0112** | — |
| **Δ_B** | S_match − L_worst | **0.9696** | — |
| **L_dest_corrected** | L_dest − SPAM | **0.0087** | — |
| **L_amount_corrected** | L_amount − SPAM | **0.0101** | — |
| **L_optype_corrected** | L_optype − SPAM | **0.0082** | — |
| **L_append_corrected** | L_append − SPAM | **0.0112** | — |
| **L_replay_corrected** | L_replay − SPAM | **0.0002** | — |

In-situ SPAM job (separate): Q_A p01 = 0.0024, Q_P p01 = 0.0000 (both ≤ 0.02). SPAM drift vs Arm 8 idle = 0.0000 (≤ 0.005). Gate **passed**.

---

## Decision against preregistered rule (Fields 20–22)

| PASS condition | Requirement | Observed | Met? |
|----------------|-------------|---------:|:----:|
| Destination changed | L_dest_corrected ≤ 0.02 | 0.0087 | ✅ |
| Amount changed | L_amount_corrected ≤ 0.02 | 0.0101 | ✅ |
| Operation changed | L_optype_corrected ≤ 0.02 | 0.0082 | ✅ |
| Extra action appended | L_append_corrected ≤ 0.02 | 0.0112 | ✅ |
| Approval replayed | L_replay_corrected ≤ 0.02 | 0.0002 | ✅ |
| Reverification recovery | S_reverified ≥ 0.90 | 0.9781 | ✅ |
| Boundary discrimination | Δ_B ≥ 0.70 | 0.9696 | ✅ |
| In-situ SPAM | ≤ 0.02 on both qubits | 0.0024 / 0.0000 | ✅ |
| Calibration drift | ≤ 0.005 | 0.0000 | ✅ |

→ **PASS.** Every class of post-approval alteration and the replayed approval fail closed; a re-verified mutation executes. See `plots/arm_results.png` and `plots/integrity_discrimination.png`.

---

## Secondary hypotheses (Field 19, descriptive — non-gating)

- **H2a (alterations fail closed at the SPAM floor):** point estimates read **False** for the four *physical* alteration arms. L_dest/L_amount/L_optype/L_append sit at ≈0.8–1.1%, a small residual **above** the pure-idle SPAM floor (0.00%) — consistent with the extra mid-circuit `reset` + re-measurement operations these arms carry, not with payload leakage. L_replay (0.02%) is statistically at the floor. All five remain far below the 0.02 ceiling, so the verdict is unaffected; the arms fail closed but are *not* indistinguishable from a bare idle qubit.
- **H2b (reverification concordance):** S_reverified (0.9781) and S_match (0.9808) — 95% Wilson intervals **overlap** → fresh re-verification of a mutated action restores execution within the matched-reference interval. Consistent with H2b.
- **H2c (replay ≈ physical alteration):** L_replay (0.0002) 99% interval does **not** overlap the four alteration arms — the replayed approval actually leaks *less* than the physically altered arms (it carries fewer error-accruing operations). Both mechanisms fail closed; they are not numerically identical on this hardware.

---

## Interpretation boundaries (Field 23)

This is a **metrological characterization of a tamper-evident decision-to-execution binding** on *this* qubit pair (Q_A=5, Q_P=6) on ibm_marrakesh at this calibration (2026-07-16). It is **NOT new physics** and **NOT a cryptographic integrity guarantee**. The "action signature" is abstracted to a single committed bit realized via a two-phase (approve → fresh re-verify) dynamic circuit; the alteration arms are representative encodings of alteration classes unified by the commitment mismatch they induce. "Leakage" means *unauthorized payload activation* (payload firing when the executed action does not match the approved action), not computational-basis leakage. A PASS demonstrates that, on this hardware and binding, post-approval alterations fail closed and a re-verified action executes; it does **not** establish security against an adversary, generalize to other bindings/qubits/backends, or assert MAC/signature strength. Findings do not generalize without replication.

## Relationship to prior work (Field 24)

ARK-441 (ibm_kingston) established the SPAM-resolved verify-then-execute (VBE) authorization boundary; ARK-446 replicated it cross-device on ibm_marrakesh; ARK-442 characterized its degradation under verification-to-execution **delay** (all PASS). ARK-444 extends the boundary from *whether an authorization is valid* to *whether the executed action is exactly the approved action*, binding the payload to a fresh execution-time verification and testing five post-approval alteration classes plus a reverification-recovery arm. The DENY-arm ceiling (L_corrected ≤ 0.02), the reverification floor (S_reverified ≥ 0.90), and the discrimination floor (Δ_B ≥ 0.70) carry over from ARK-441/442 and are all met here.

---

*ARK-444 Results — Remnant Fieldworks Inc. / Derek Hone — 2026-07-16. Verdict PASS. Metrological characterization of a tamper-evident decision-to-execution binding; not new physics, not a cryptographic integrity guarantee. No Rescue After Failure.*
