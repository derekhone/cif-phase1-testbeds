# ARK-446 — PREREGISTRATION
**Cross-Device Replication of the ARK-441 VBE Authorization Boundary on ibm_marrakesh (Heron r2)**
**Remnant Fieldworks Inc. — Derek Hone**
**Governing principle:** *Proof Before Power. Prediction Before Measurement. No Rescue After Failure.*

> This document is the LOCK. It is committed to GitHub (derekhone/uip-phase1-testbeds, folder `ark-446/`) with SHA-256 hashes of all code files **before any IBM Quantum job is submitted**. The preregistration commit hash is recorded in `RUN_LOG.md`. Nothing below — hypotheses, qubit pair selection rule, shot count, metrics, or pass/fail/kill windows — may be altered after any result is observed.

---

### Field 1 — Experiment title
Cross-Device Replication of ARK-441 VBE Authorization Boundary on ibm_marrakesh (Heron r2): a preregistered, second-device test of whether the SPAM-resolved authorization boundary result is device-specific or reproducible.

### Field 2 — Experiment ID
ARK-446 (Remnant Fieldworks Inc. / Derek Hone).

### Field 3 — Research question
Does ARK-441's result (SPAM-corrected `L_D ≤ 2%`, `Δ_B ≥ 0.70`) replicate on a **second** IBM Heron device (`ibm_marrakesh`), using the same 8-arm circuit design, the same qubit-selection rule (readout error < 2%), the same shot count (8,192/arm), and the same SPAM kill-gate protocol? In other words: is the verify-then-execute authorization boundary a property of the ARK-441 backend/qubit pair alone, or does it reproduce across devices?

### Field 4 — Primary hypothesis H1
On the calibration-selected, connected qubit pair of `ibm_marrakesh` (pair fixed at execution time from the live calibration snapshot per Field 10), the boundary produces `L_D_corrected ≤ 0.02` **and** `Δ_B ≥ 0.70`, with in-situ `SPAM_baseline ≤ 0.02` on **both** qubits — matching the ARK-441 result on ibm_kingston.

### Field 5 — Null hypothesis H0
`L_D_corrected` is statistically indistinguishable from zero on ibm_marrakesh; the boundary provides no measurable suppression of payload execution beyond SPAM. Equivalently, the ARK-441 result does not replicate on a second device and is attributable to the ARK-441-specific backend/qubit pair.

### Field 6 — Secondary hypotheses
- **H2a (stale auth, Arm 5):** `P(Q_P=1)` under a ~1 µs post-authorization delay is statistically indistinguishable from Arm 1 (ALLOW), replicating the ARK-441 stale-auth observation on the new device.
- **H2b (replayed auth, Arm 6):** flipping Q_A to |1⟩ *after* the measurement window does not authorize the payload; `P(Q_P=1 | Arm 6)` is statistically indistinguishable from Arm 2 (DENY).
- **H2c (superposition auth, Arm 7):** an authorization qubit prepared in |+⟩ yields `P(Q_P=1) ≈ 0.50` (measurement collapse), distinguishable from both ALLOW and DENY.
- **H2d (cross-device concordance):** the ibm_marrakesh point estimates for `L_D_corrected` and `Δ_B` lie within the 95% Wilson intervals of the corresponding ARK-441 (ibm_kingston) estimates.

### Field 7 — Circuit architecture
Two-qubit dynamic circuits, **identical to ARK-441**. Virtual q0 = Q_A (authorization), virtual q1 = Q_P (payload). Core mechanism: `measure(Q_A) → ca`; `if ca == 1: X(Q_P)`; `measure(Q_P) → cp`. The payload register `cp` is the primary readout. Full per-arm definitions in Field 8; the circuit generator is a verbatim copy of the ARK-441 circuit code with only the `initial_layout` changed to the ibm_marrakesh selected pair.

### Field 8 — Arms (8 arms, identical to ARK-441)
| Arm | Q_A prep | Feedforward | Purpose | Endpoint |
|-----|----------|-------------|---------|----------|
| 1 `arm1_allow` | \|1⟩ | ON | ALLOW fidelity | S_A = P(Q_P=1) |
| 2 `arm2_deny` | \|0⟩ | ON | DENY leakage (**PRIMARY**) | L_D = P(Q_P=1) |
| 3 `arm3_ungated_control` | — | X unconditional | ungated ALLOW control | L_control |
| 4 `arm4_idle_spam` | — | none | idle SPAM baseline | SPAM_baseline |
| 5 `arm5_stale_auth` | \|1⟩ | ON + ~1 µs delay | stale-auth analogue | P(Q_P=1) |
| 6 `arm6_replayed_auth` | \|0⟩→X after measure | ON (bound to original ca) | replayed-auth analogue | P(Q_P=1) |
| 7 `arm7_superposition_auth` | \|+⟩ | ON | superposition auth | P(Q_P=1) |
| 8 `arm8_payload_readout_ref` | — | Q_P=\|1⟩ direct | in-situ payload readout ref | P(Q_P=1) |

Arm definitions are byte-for-byte identical to ARK-441; only the physical qubit mapping differs.

### Field 9 — Backend selection rule (preregistered, not cherry-picked)
Priority: (1) **ibm_marrakesh** (primary — this is the second-device replication target); (2) ibm_fez (only if budget allows and marrakesh is non-operational or queue-prohibitive). ibm_kingston is explicitly excluded here because it is the ARK-441 device and would not constitute a cross-device test. Selected backend fixed before submission and recorded in `RUN_LOG.md`.

### Field 10 — Qubit selection rule (preregistered)
Both qubits must have `readout_error < 0.020` from today's calibration snapshot; must be directly connected in the coupling map; among qualifying connected pairs, select the minimum sum of readout errors. **The specific pair is NOT pre-named in this document — it is selected at execution time from the live ibm_marrakesh calibration snapshot** and then frozen: once selected and recorded in `RUN_LOG.md`, it may not be changed. This mirrors the ARK-441 selection rule exactly (ARK-441 selected Q_A=5, Q_P=6 on ibm_kingston); the rule is fixed in advance even though the pair identity is resolved from live calibration data.

### Field 11 — Shot count
8,192 shots per arm × 8 arms = 65,536 shots (principal job). SPAM job: 2,048 shots × 4 circuits = 8,192 shots. Identical to ARK-441.

### Field 12 — Repetitions
1 (one principal run). No re-runs to rescue an unfavorable result (No Rescue After Failure). A protocol-deviation re-run, if ever needed, is flagged and is not primary evidence.

### Field 13 — Transpiler settings
`optimization_level=1`; `initial_layout=[Q_A, Q_P]` (the ibm_marrakesh selected pair); **no dynamical decoupling**; IBM Heron basis gates {cz, id, rz, sx, x}. Identical settings for SPAM and principal jobs, and identical to ARK-441 except for the physical layout.

### Field 14 — Readout mitigation decision
**No readout mitigation on the primary endpoint.** Raw counts are primary. The in-situ SPAM job characterizes readout error, and `L_D_corrected` subtracts the idle baseline analytically — but no measurement-error mitigation (e.g., M3, matrix inversion) is applied to the primary counts. Any mitigated figures, if produced, are reported separately and labeled SECONDARY only. Identical policy to ARK-441.

### Field 15 — Inclusion criteria
Principal-job results are included as primary evidence iff: (a) SPAM job completed and `SPAM_baseline ≤ 0.02` on **both** selected qubits; (b) principal job completed and returned counts for all 8 arms; (c) SPAM baseline drift between SPAM and principal jobs ≤ 0.005; (d) no protocol deviation from this document.

### Field 16 — Exclusion criteria
Exclude / flag as non-primary: backend change after submission; qubit-pair change after the pair is frozen; shot-count change; calibration drift > 0.005 between jobs; any circuit alteration beyond the layout remap; job failure or partial return.

### Field 17 — Metric definitions (mathematical, identical to ARK-441)
```
L_D            = P(Q_P = 1 | Arm 2)                         # DENY leakage (primary)
S_A            = P(Q_P = 1 | Arm 1)                         # ALLOW fidelity
SPAM_baseline  = P(Q_P = 1 | Arm 4)                         # idle readout error
L_control      = P(Q_P = 1 | Arm 3)                         # ungated control leakage
Δ_B            = S_A − L_D                                  # boundary discrimination
L_D_corrected  = L_D − SPAM_baseline                        # mechanism-only leakage
I_L            = (L_control − L_D) / L_control              # relative improvement vs ungated
```

### Field 18 — Statistical test
Wilson score interval for each binomial proportion. 95% CI (z=1.96) reported for all endpoints; 99% CI (z=2.576) used for the L_D-vs-SPAM distinguishability diagnostic. One-sided interpretation on the primary ceiling (upper Wilson bound of `L_D_corrected` vs 0.02). Cross-device concordance (H2d) tested by checking whether the ibm_marrakesh point estimates fall inside the ARK-441 95% Wilson intervals.

### Field 19 — Multiple-comparison correction
Bonferroni correction applied across the secondary/adversarial hypotheses (H2a, H2b, H2c, H2d): family α = 0.05 → per-test α = 0.0125 (equivalently ~98.75% CIs) for secondary claims. The primary endpoint (H1) is not penalized by the secondary family.

### Field 20 — PASS condition
`L_D_corrected ≤ 0.02` (point estimate; 95% Wilson upper bound also reported) **AND** `Δ_B ≥ 0.70` **AND** in-situ `SPAM_baseline ≤ 0.02` on **both** qubits. A PASS constitutes a successful cross-device replication of the ARK-441 VBE authorization boundary.

### Field 21 — FAIL condition
`L_D_corrected > 0.02` **OR** `Δ_B < 0.70`, while in-situ `SPAM_baseline ≤ 0.02` (so the failure is attributable to the boundary mechanism, not the qubit). A FAIL indicates the ARK-441 result did NOT replicate on ibm_marrakesh and may be device-specific.

### Field 22 — KILL / INDETERMINATE condition
In-situ `SPAM_baseline > 0.02` on **either** qubit → INDETERMINATE / KILLED (qubit/backend disqualified); **stop immediately, submit no principal job, no rescue.** Also INDETERMINATE if SPAM baseline drifts > 0.005 between the SPAM and principal jobs (calibration drift). A KILLED verdict means the replication attempt was not evaluable on this device/calibration and carries no bearing on H1.

### Field 23 — Interpretation boundaries
A PASS demonstrates **cross-device replicability** of the VBE authorization boundary — i.e., that the ARK-441 result is reproducible on a second, independent Heron device. It does **not** generalize beyond this backend / calibration / qubit pair, does not establish a general security guarantee, and makes no cryptographic claim. "Leakage" here means *unauthorized payload activation*, not computational-basis leakage. This remains a metrological/methodological hardware characterization.

### Field 24 — Relationship to prior work (ARK-441)
ARK-441 (ibm_kingston, Heron r2, 2026-07-16) passed all preregistered thresholds: SPAM-corrected `L_D ≤ 2%`, `Δ_B ≥ 0.70`, and in-situ `SPAM_baseline ≤ 2%` on both qubits (Q_A=5, Q_P=6). ARK-446 tests whether that result is **device-specific** or **reproducible** by re-running the identical 8-arm design, qubit-selection rule, shot count, and SPAM kill-gate protocol on a second device (ibm_marrakesh). ARK-446 changes only the backend and the (rule-selected) physical qubit pair; everything else is held fixed.

### Field 25 — Exact timestamp
Preregistration authored: **2026-07-16** (UTC). Effective lock time = the GitHub preregistration commit timestamp recorded in `RUN_LOG.md`.

### Field 26 — Calibration snapshot reference
An `ibm_marrakesh` calibration snapshot is retrieved at execution time (Heron r2) and committed as `calibration_snapshot_marrakesh_20260716.json`; its SHA-256 is recorded in `MANIFEST.txt`. The selected qubit pair (Field 10) is derived from this snapshot and frozen in `RUN_LOG.md` before submission.

### Field 27 — Ordering constraint (hard)
1. Commit this preregistration + all code files + `MANIFEST.txt` (Field 28 hashes) to GitHub. Record commit hash (the preregistration lock).
2. Retrieve live ibm_marrakesh calibration → select and freeze qubit pair per Field 10 → record in `RUN_LOG.md`.
3. Run in-situ SPAM job → commit `spam_results.json`.
4. Only if `SPAM_baseline ≤ 0.02` on both qubits: submit principal job → record job ID in `RUN_LOG.md` and commit **immediately**, before reading any result. If SPAM fails the gate → KILLED, stop, no rescue.
5. Retrieve raw counts → commit `raw_results.json`.
6. Run analysis → commit `proofrecord.json`, `ARK_446_results.md`, plots. Tag `ark-446-v1.0`.

### Field 28 — SHA-256 hashes of all code files
Authoritative hashes are maintained in `MANIFEST.txt` (committed in the same preregistration commit). The manifest covers all ARK-446 code files (circuit generator, SPAM job, submission, retrieval, analysis), `requirements.txt`, `README.md`, `ARK_446_preregistration.md`, and the ibm_marrakesh calibration snapshot. Hashes are auto-filled at commit time.

---

*ARK-446 Preregistration — Remnant Fieldworks Inc. / Derek Hone — 2026-07-16. No hardware job is submitted until this document and its manifest are committed. Cross-device replication target: ibm_marrakesh (Heron r2). No Rescue After Failure.*
