# ARK-441 — RESULTS
**SPAM-Resolved Authorization Boundary Characterization on IBM Quantum (Heron r2)**
**Remnant Fieldworks Inc. — Derek Hone**
**Governing principle:** *Proof Before Power. Prediction Before Measurement. No Rescue After Failure.*

> **Independence:** ARK-441 is an **independent, supplemental hardware experiment**. It is **NOT** part of the UIP Phase 1/2 program. Its only scientific lineage is VBE-1. See `INDEPENDENCE_NOTICE.md`.

---

## Verdict: **PASS**

The preregistered verify-then-execute authorization boundary held on calibration-selected qubits.
DENY-leakage was at the readout floor; ALLOW fidelity was near-unity; boundary discrimination was
0.979. The in-situ SPAM gate passed decisively, so — unlike VBE-1 — the result is attributable to
the boundary mechanism, not to measurement noise.

---

## Provenance (locked before any job)

| Item | Value |
|------|-------|
| Preregistration lock commit | `fd1c7fad7c290ee04fc564575f9d7bc12000c3b7` |
| SPAM results commit | `cb947cf3883f0725d1811cb53b1c25e72688fea1` |
| Job-ID record commit (RUN_LOG) | `58641f0c7249b9bbd2b7ba7fd71d5e2b9008de7a` |
| Raw results commit | `8a5d26016d4f81091aa2943323c6a1d7c6c1ce48` |
| Backend | ibm_kingston (Heron r2), instance open-instance |
| Qubits | Q_A=5 (RE 0.50%), Q_P=6 (RE 0.67%) — connected, min combined RE |
| SPAM job ID | `d9c7lf7ngvls73a941jg` |
| Principal job ID | `d9c8ij41osis73bjhldg` |
| Shots | 8,192 per arm × 8 arms = 65,536 (principal); 2,048 × 4 = 8,192 (SPAM) |
| Primary endpoint | **RAW counts, no readout mitigation** |

---

## In-situ SPAM gate (ran and committed FIRST)

| Qubit | SPAM_baseline (P(read 1 | prepared 0)) | Ceiling | Pass? |
|-------|----------------------------------------|---------|-------|
| Q5 | **0.29%** (6/2048) | ≤ 2% | ✅ |
| Q6 | **0.15%** (3/2048) | ≤ 2% | ✅ |

Contrast VBE-1's idle baseline of **13.5%**. The SPAM gate is the guard against the VBE-1 failure
mode, and it passed with ~50× margin.

---

## Raw results — all 8 arms (payload register `cp`)

| Arm | Purpose | P(Q_P=1) | 95% Wilson CI | counts (1/total) |
|-----|---------|----------|---------------|------------------|
| 1 `arm1_allow` | ALLOW fidelity S_A | **0.9823** | [0.9792, 0.9849] | 8047/8192 |
| 2 `arm2_deny` | **DENY leakage L_D (PRIMARY)** | **0.0033** | [0.0023, 0.0048] | 27/8192 |
| 3 `arm3_ungated_control` | ungated control L_control | 0.9899 | [0.9875, 0.9918] | 8109/8192 |
| 4 `arm4_idle_spam` | idle SPAM baseline | 0.0012 | [0.0007, 0.0022] | 10/8192 |
| 5 `arm5_stale_auth` | stale-auth analogue | 0.9813 | [0.9782, 0.9840] | 8039/8192 |
| 6 `arm6_replayed_auth` | replayed-auth analogue | 0.0033 | [0.0023, 0.0048] | 27/8192 |
| 7 `arm7_superposition_auth` | superposition auth | 0.5049 | [0.4941, 0.5157] | 4136/8192 |
| 8 `arm8_payload_readout_ref` | payload readout ref | 0.9900 | [0.9876, 0.9919] | 8110/8192 |

---

## Primary metrics

| Metric | Definition | Value | 95% CI / bound |
|--------|-----------|-------|-----------------|
| L_D | P(Q_P=1 \| Arm 2 DENY) | **0.0033** | [0.0023, 0.0048] |
| S_A | P(Q_P=1 \| Arm 1 ALLOW) | **0.9823** | [0.9792, 0.9849] |
| SPAM_baseline | P(Q_P=1 \| Arm 4 idle) | **0.0012** | [0.0007, 0.0022] |
| L_control | P(Q_P=1 \| Arm 3 ungated) | 0.9899 | [0.9875, 0.9918] |
| **Δ_B** | S_A − L_D | **0.9790** | — |
| **L_D_corrected** | L_D − SPAM_baseline | **0.0021** | upper-95 ≈ 0.0041 |
| I_L | (L_control − L_D)/L_control | **0.9967** | — |

---

## Per-criterion scoring (honest, against the preregistered windows)

| Criterion | Window | Observed | Result |
|-----------|--------|----------|--------|
| In-situ SPAM gate (Q5) | ≤ 0.02 | 0.0029 | ✅ PASS |
| In-situ SPAM gate (Q6) | ≤ 0.02 | 0.0015 | ✅ PASS |
| `L_D_corrected` | ≤ 0.02 | 0.0021 (upper-95 ≈ 0.0041) | ✅ PASS |
| `Δ_B` | ≥ 0.70 | 0.9790 | ✅ PASS |
| **PRIMARY H1** | all three above | met | ✅ **PASS** |

**Overall decision: PASS.** All three preregistered PASS conditions are satisfied. No KILL trigger
fired (SPAM ≤ 0.02 on both qubits; no calibration-drift or protocol deviation).

---

## Secondary / adversarial arms (H2, Bonferroni-aware)

- **H2a — stale auth (Arm 5):** P(Q_P=1)=0.9813, indistinguishable from ALLOW (Arm 1, 0.9823).
  A ~1 µs post-authorization delay did **not** degrade granted execution. **Consistent with H2a.**
- **H2b — replayed auth (Arm 6):** P(Q_P=1)=0.0033, **identical** to standard DENY (Arm 2, 0.0033).
  Flipping Q_A to |1⟩ *after* the measurement window did **not** retroactively authorize the payload.
  **Consistent with H2b — the boundary is replay-safe in this configuration.**
- **H2c — superposition auth (Arm 7):** P(Q_P=1)=0.5049, CI [0.4941, 0.5157] — statistically
  consistent with the predicted 0.50 (measurement collapse of |+⟩). **Consistent with H2c.**

The adversarial arms show no differential vulnerability beyond standard DENY.

---

## Diagnostic: L_D vs SPAM distinguishability

`L_D` (0.33%) and the idle `SPAM_baseline` (0.12%) have **overlapping 99% Wilson intervals**
(`L_D_vs_SPAM_distinguishable_99 = false`). Per the preregistration (Fields 4, 20, 22), this is a
**reported diagnostic, not a pass/fail gate**: on a clean qubit a correctly functioning boundary is
*expected* to drive `L_D` down to the readout floor, where it necessarily approaches `SPAM_baseline`.
The VBE-1 guard is the SPAM ceiling itself (0.02), which passed with wide margin. The small residual
`L_D_corrected = 0.0021` is consistent with mechanism-level leakage at or below the noise floor.

---

## Interpretation boundaries (as preregistered)

This PASS characterizes **this** boundary implementation on **this** qubit pair (Q5/Q6) on
**ibm_kingston** at **this** calibration. It does **not** establish a general security guarantee,
does not generalize to other qubits/backends without replication, and makes **no** cryptographic
claim. "Leakage" means *unauthorized payload activation*, not computational-basis leakage. Primary
figures are raw counts; no readout mitigation was applied to the primary endpoint.

## Relationship to VBE-1

VBE-1 failed its kill condition (L_D 12.62% ≈ idle 13.50% — SPAM-dominated). ARK-441 corrected the
method with calibration-based qubit selection, an in-situ SPAM gate committed before the principal
job, and a SPAM-corrected primary metric. The result: on RE<2% qubits the boundary mechanism works;
**VBE-1's failure was a SPAM (readout) problem, not a boundary-mechanism problem.** This is the
scientifically clean PASS anticipated in the design's Scenario 1.

---

*ARK-441 Results — Remnant Fieldworks Inc. / Derek Hone — 2026-07-16. Verdict: PASS. Machine-readable
record in `proofrecord.json`. Plots in `plots/`.*
