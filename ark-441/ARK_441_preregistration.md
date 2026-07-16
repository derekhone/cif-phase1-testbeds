# ARK-441 — PREREGISTRATION
**SPAM-Resolved Authorization Boundary Characterization on IBM Quantum (Heron r2)**
**Remnant Fieldworks Inc. — Derek Hone**
**Governing principle:** *Proof Before Power. Prediction Before Measurement. No Rescue After Failure.*

> This document is the LOCK. It is committed to GitHub (derekhone/uip-phase1-testbeds, folder `ark-441/`) with SHA-256 hashes of all code files **before any IBM Quantum job is submitted**. The preregistration commit hash is recorded in `RUN_LOG.md`. Nothing below — hypotheses, qubit pair, shot count, metrics, or pass/fail/kill windows — may be altered after any result is observed.

---

### Field 1 — Experiment title
SPAM-Resolved Authorization Boundary Characterization: a preregistered replication and adversarial extension of VBE-1 on IBM Heron hardware.

### Field 2 — Experiment ID
ARK-441 (Remnant Fieldworks Inc. / Derek Hone).

### Field 3 — Research question
On a calibration-selected, connected qubit pair on IBM Heron with readout error < 2% on each qubit, does a verify-then-execute circuit boundary (mid-circuit measurement + classical feedforward) suppress unauthorized payload execution to a **SPAM-corrected** DENY-leakage of ≤ 2%, with boundary discrimination ≥ 0.70 — i.e., is VBE-1's failure a SPAM (readout) problem rather than a boundary-mechanism problem?

### Field 4 — Primary hypothesis H1
On the preregistered pair (Q_A=5, Q_P=6) of ibm_kingston, the boundary produces `L_D_corrected ≤ 0.02` **and** `Δ_B ≥ 0.70`, with in-situ `SPAM_baseline ≤ 0.02` on both qubits. (The `L_D`-vs-`SPAM_baseline` distinguishability at 99% Wilson is computed and reported as a **diagnostic** — it is not a pass/fail gate, because a correctly functioning boundary on a clean qubit is expected to yield `L_D ≈ SPAM_baseline`, both near the readout floor.)

### Field 5 — Null hypothesis H0
`L_D_corrected` is statistically indistinguishable from zero; the boundary provides no measurable suppression of payload execution beyond SPAM. Equivalently, `L_D` and `SPAM_baseline` are statistically indistinguishable (overlapping 99% Wilson intervals) — the VBE-1 failure mode.

### Field 6 — Secondary hypotheses
- **H2a (stale auth, Arm 5):** `P(Q_P=1)` under a ~1 µs post-authorization delay is statistically indistinguishable from Arm 1 (ALLOW).
- **H2b (replayed auth, Arm 6):** flipping Q_A to |1⟩ *after* the measurement window does not authorize the payload; `P(Q_P=1 | Arm 6)` is statistically indistinguishable from Arm 2 (DENY).
- **H2c (superposition auth, Arm 7):** an authorization qubit prepared in |+⟩ yields `P(Q_P=1) ≈ 0.50` (measurement collapse), distinguishable from both ALLOW and DENY.

### Field 7 — Circuit architecture
Two-qubit dynamic circuits. Virtual q0 = Q_A (authorization), virtual q1 = Q_P (payload). Core mechanism: `measure(Q_A) → ca`; `if ca == 1: X(Q_P)`; `measure(Q_P) → cp`. The payload register `cp` is the primary readout. Full per-arm definitions in Field 8 and `ark_441_circuits.py`.

### Field 8 — Arms (8 arms)
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

### Field 9 — Backend selection rule (preregistered, not cherry-picked)
Priority: (1) **ibm_kingston** (preferred — VBE-1 comparability, low queue); (2) ibm_fez (fallback if kingston non-operational or queue > 50); (3) ibm_marrakesh (last resort). Selected backend fixed before submission.

### Field 10 — Qubit selection rule (preregistered)
Both qubits must have `readout_error < 0.020` from today's calibration snapshot; must be directly connected in the coupling map; among qualifying connected pairs, select the minimum sum of readout errors. **Selected:** Q_A=5 (RE=0.50%), Q_P=6 (RE=0.67%), connected (5↔6 verified in coupling map), sum=1.17% — the minimum among qualifying pairs. Selection is fixed before any experimental result is observed.

### Field 11 — Shot count
8,192 shots per arm × 8 arms = 65,536 shots (principal job). SPAM job: 2,048 shots × 4 circuits = 8,192 shots.

### Field 12 — Repetitions
1 (one principal run). No re-runs to rescue an unfavorable result (No Rescue After Failure). A protocol-deviation re-run, if ever needed, is flagged and is not primary evidence.

### Field 13 — Transpiler settings
`optimization_level=1`; `initial_layout=[5, 6]`; **no dynamical decoupling**; IBM Heron basis gates {cz, id, rz, sx, x}. Identical settings for SPAM and principal jobs.

### Field 14 — Readout mitigation decision
**No readout mitigation on the primary endpoint.** Raw counts are primary. The in-situ SPAM job characterizes readout error, and `L_D_corrected` subtracts the idle baseline analytically — but no measurement-error mitigation (e.g., M3, matrix inversion) is applied to the primary counts. Any mitigated figures, if produced, are reported separately and labeled SECONDARY only.

### Field 15 — Inclusion criteria
Principal-job results are included as primary evidence iff: (a) SPAM job completed and `SPAM_baseline ≤ 0.02` on **both** Q5 and Q6; (b) principal job completed and returned counts for all 8 arms; (c) SPAM baseline drift between SPAM and principal jobs ≤ 0.005; (d) no protocol deviation from this document.

### Field 16 — Exclusion criteria
Exclude / flag as non-primary: backend change after submission; qubit-pair change; shot-count change; calibration drift > 0.005 between jobs; any circuit alteration; job failure or partial return.

### Field 17 — Metric definitions (mathematical)
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
Wilson score interval for each binomial proportion. 95% CI (z=1.96) reported for all endpoints; 99% CI (z=2.576) used for the L_D-vs-SPAM distinguishability test. One-sided interpretation on the primary ceiling (upper Wilson bound of `L_D_corrected` vs 0.02).

### Field 19 — Multiple-comparison correction
Bonferroni correction applied across the three secondary/adversarial hypotheses (H2a, H2b, H2c): family α = 0.05 → per-test α = 0.0167 (equivalently ~98.3% CIs) for secondary claims. The primary endpoint (H1) is not penalized by the secondary family.

### Field 20 — PASS condition
`L_D_corrected ≤ 0.02` (point estimate; 95% Wilson upper bound also reported) **AND** `Δ_B ≥ 0.70` **AND** in-situ `SPAM_baseline ≤ 0.02` on both qubits. (`L_D`-vs-`SPAM` distinguishability is reported but is not part of the gate.)

### Field 21 — FAIL condition
`L_D_corrected > 0.02` **OR** `Δ_B < 0.70`, while in-situ `SPAM_baseline ≤ 0.02` (so the failure is attributable to the boundary mechanism, not the qubit).

### Field 22 — KILL / INDETERMINATE condition
In-situ `SPAM_baseline > 0.02` on **either** qubit → INDETERMINATE (VBE-1 failure mode; qubit/backend disqualified). **Also INDETERMINATE** if SPAM baseline drifts > 0.005 between the SPAM and principal jobs (calibration drift). The `L_D`-vs-`SPAM` indistinguishability is a *reported diagnostic*, not an independent kill trigger: the SPAM ceiling (0.02) is the guard against the VBE-1 mode, so a clean qubit yielding `L_D ≈ SPAM ≈ 0` is a PASS, not a kill.

### Field 23 — Interpretation boundaries
A PASS characterizes *this boundary implementation on this qubit pair on this backend at this calibration*. It does not establish a general security guarantee, does not generalize to other qubits/backends without replication, and makes no cryptographic claim. This is a metrological/methodological hardware characterization, not a proof of an authorization protocol's security. "Leakage" here means *unauthorized payload activation*, not computational-basis leakage.

### Field 24 — Relationship to prior work (VBE-1)
VBE-1 (ibm_kingston, job d9ajf3eg26ic73deq3l0, 2026-07-13) failed its kill condition: L_D=12.62% was indistinguishable from a 13.50% idle baseline — SPAM-dominated. ARK-441 corrects this with (a) calibration-based qubit selection (RE<2%), (b) an in-situ SPAM job run and committed first, and (c) a SPAM-corrected primary metric with an explicit distinguishability test. Adversarial arms 5–7 extend beyond VBE-1.

### Field 25 — Exact timestamp
Preregistration authored: **2026-07-16T06:24:00Z** (UTC). Effective lock time = the GitHub preregistration commit timestamp recorded in `RUN_LOG.md`.

### Field 26 — Calibration snapshot reference
`calibration_snapshot_20260716.json` (ibm_kingston, Heron r2, retrieved 2026-07-16T06:11:57Z). SHA-256 recorded in `MANIFEST.txt`.

### Field 27 — Ordering constraint (hard)
1. Commit this preregistration + all code files + `MANIFEST.txt` (Fields 28 hashes) to GitHub. Record commit hash.
2. Run in-situ SPAM job → commit `spam_results.json`.
3. Only if `SPAM_baseline ≤ 0.02` on both qubits: submit principal job → record job ID in `RUN_LOG.md` and commit **immediately**, before reading any result.
4. Retrieve raw counts → commit `raw_results.json`.
5. Run analysis → commit `proofrecord.json`, `ARK_441_results.md`, plots. Tag `ark-441-v1.0`.

### Field 28 — SHA-256 hashes of all code files
Authoritative hashes are maintained in `MANIFEST.txt` (committed in the same preregistration commit). The manifest covers: `ark_441_circuits.py`, `ark_441_spam_job.py`, `ark_441_submit_ibm.py`, `ark_441_retrieve.py`, `ark_441_analysis.py`, `requirements.txt`, `README.md`, `ARK_441_preregistration.md`, and `calibration_snapshot_20260716.json`. See placeholder block below (auto-filled at commit time):

```
d54d11bcc573cd0159454127b7f1fa54a2e563e414c854f222d300649b149e8a  ark_441_circuits.py
4487b6c80edc7315a1c662c2f9445c53f098fc52ff6c16e13fe9cf9185bfe072  ark_441_spam_job.py
c52b264afca16f1a5b188b8a12b32c4317cf65ed99a1c346eee5bf87cc156745  ark_441_submit_ibm.py
f7b45b665f3788aa75f5b9c88fae90572987f6fea36c36876c5201a3c7fba8bb  ark_441_retrieve.py
652686678c3f245dadcbe9f78ea8203f9ff17069e2588af2188f7c9a31e3dc05  ark_441_analysis.py
69c83a34200e66573609ad8802000d92d5bb00625f684b784aa52c82ef3db6d8  requirements.txt
82b7febb5d5c86036a7126a0924dbafe32fadc6eb26730960d28fd299fb1d17d  README.md
7374d727235d48734ac4646b95fdcdf8b91387f6d49a608731f2350e0dfdb083  calibration_snapshot_20260716.json
```

---

*ARK-441 Preregistration — Remnant Fieldworks Inc. / Derek Hone — 2026-07-16. No hardware job is submitted until this document and its manifest are committed.*
