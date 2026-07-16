# ARK-442 — PREREGISTRATION
**Authorization Boundary Degradation Under Verification-to-Execution Delay on IBM Quantum (Heron r2)**
**Remnant Fieldworks Inc. — Derek Hone**
**Governing principle:** *Proof Before Power. Prediction Before Measurement. No Rescue After Failure.*

> This document is the LOCK. It is committed to GitHub (derekhone/uip-phase1-testbeds, folder `ark-442/`) with SHA-256 hashes of all code files **before any IBM Quantum job is submitted**. The preregistration commit hash is recorded in `RUN_LOG.md`. Nothing below — hypotheses, delay points, qubit pair selection rule, shot count, metrics, or pass/fail/kill windows — may be altered after any result is observed.

---

### Field 1 — Experiment title
Authorization Boundary Degradation Under Verification-to-Execution Delay on IBM Heron hardware: a preregistered metrological characterization of how the VBE authorization boundary erodes as the separation between authorization measurement and payload execution increases.

### Field 2 — Experiment ID
ARK-442 (Remnant Fieldworks Inc. / Derek Hone).

### Field 3 — Research question
How does the boundary discrimination `Δ_B` decay as a function of the verification-to-execution delay (0 µs / 0.5 µs / 1.0 µs / 2.0 µs)? At what delay does an *expired* authorization transition from effectively ALLOW to DENY? And do the adversarial handling paths — replay of a stale classical authorization bit, and fresh reverification after expiry — behave as expected (replay must not authorize; reverification must restore ALLOW)? This is a **metrological characterization of decoherence-driven boundary degradation** (T1/T2 decay of Q_A between measurement and payload execution) — **NOT new physics** and **NOT a cryptographic claim**.

### Field 4 — Primary hypothesis H1
On the calibration-selected, connected qubit pair (Field 10):
- **Expired auth (Arm 5)** produces `L_D_corrected ≤ 0.02` (an expired authorization does not execute the payload);
- **Replayed auth (Arm 6)** produces `L_D_corrected ≤ 0.02` (replaying a stale `ca=1` bit does not execute the payload);
- **Reverified auth (Arm 7)** produces `S_reverified ≥ 0.90` (fresh reverification restores ALLOW fidelity);
- **Boundary discrimination** `Δ_B` between Arm 1 (ALLOW immediate) and Arm 5 (expired DENY) is `≥ 0.70`.

### Field 5 — Null hypothesis H0
`Δ_B(Arm 1 vs Arm 5)` is statistically indistinguishable from zero and/or expired/replayed authorizations leak the payload at rates indistinguishable from ALLOW; equivalently, the boundary does not degrade in an ordered, decoherence-consistent way with delay, and reverification does not restore ALLOW.

### Field 6 — Secondary hypotheses
- **H2a (monotone decay):** ALLOW survival `S_A(delay)` is non-increasing across delay points 0 → 0.5 → 1.0 → 2.0 µs, consistent with T1/T2 decay of Q_A (descriptive; reported as a decay curve, not a pass/fail gate).
- **H2b (replay ≈ expiry):** `P(Q_P=1 | Arm 6)` (replayed) is statistically indistinguishable from `P(Q_P=1 | Arm 5)` (expired) — a replayed stale bit is no better than an expired one.
- **H2c (reverification concordance):** `S_reverified` (Arm 7) is statistically indistinguishable from the immediate ALLOW reference `S_A_0` (Arm 1) within its 95% Wilson interval.

### Field 7 — Circuit architecture
Two-qubit dynamic circuits. Virtual q0 = Q_A (authorization), virtual q1 = Q_P (payload). Core mechanism: `measure(Q_A) → ca`; a controlled delay (barrier + idle of the specified duration) is inserted between the authorization measurement and the payload conditional; `if ca == 1: X(Q_P)`; `measure(Q_P) → cp`. The delay is realized as an idle/`delay` instruction of the nominal duration on Q_A (and Q_P where applicable) so that decoherence accrues during the verification-to-execution separation. The payload register `cp` is the primary readout. Full per-arm definitions in Field 8.

### Field 8 — Arms (8 arms)
| Arm | Q_A prep | Feedforward | Delay | Purpose | Endpoint |
|-----|----------|-------------|-------|---------|----------|
| 1 `arm1_allow_immediate` | \|1⟩ | ON | 0 µs | ALLOW reference | S_A_0 = P(Q_P=1) |
| 2 `arm2_allow_short_delay` | \|1⟩ | ON | ~0.5 µs | ALLOW, short delay | S_A_short = P(Q_P=1) |
| 3 `arm3_allow_medium_delay` | \|1⟩ | ON | ~1.0 µs | ALLOW, medium delay | S_A_medium = P(Q_P=1) |
| 4 `arm4_allow_long_delay` | \|1⟩ | ON | ~2.0 µs | ALLOW, long delay (→T1 limit) | S_A_long = P(Q_P=1) |
| 5 `arm5_expired_auth_deny` | \|1⟩, result discarded (auth expired) | OFF | — | expired-auth must DENY (**PRIMARY**) | L_expired = P(Q_P=1) |
| 6 `arm6_replayed_after_expiry` | \|0⟩ then attempt replay of stale `ca=1` | ON (bound to stale bit) | — | replayed-after-expiry must DENY (**PRIMARY**) | L_replayed = P(Q_P=1) |
| 7 `arm7_reverified_after_expiry` | \|1⟩ measured fresh (reverification) | ON (fresh result) | — | reverification must restore ALLOW | S_reverified = P(Q_P=1) |
| 8 `arm8_idle_spam` | Q_A=Q_P=\|0⟩, no ops | none | — | idle SPAM baseline | SPAM_baseline = P(Q_P=1) |

Delay points: 0 µs (Arm 1), ~0.5 µs (Arm 2), ~1.0 µs (Arm 3, matches ARK-441 Arm 5 stale-auth delay), ~2.0 µs (Arm 4, approaching the T1 limit).

### Field 9 — Backend selection rule (preregistered, not cherry-picked)
Priority: (1) **ibm_marrakesh** (preferred); (2) ibm_fez (fallback if marrakesh non-operational or queue-prohibitive). Selected backend fixed before submission and recorded in `RUN_LOG.md`.

### Field 10 — Qubit selection rule (preregistered)
Both qubits must have `readout_error < 0.020` from today's calibration snapshot; must be directly connected in the coupling map; among qualifying connected pairs, select the minimum sum of readout errors — the **same rule used in ARK-441 and ARK-446**. The specific pair is selected at execution time from the live calibration snapshot of the selected backend, then frozen and recorded in `RUN_LOG.md` before submission; it may not be changed thereafter.

### Field 11 — Shot count
8,192 shots per arm × 8 arms = 65,536 shots (principal job). SPAM job: 2,048 shots × 4 circuits = 8,192 shots.

### Field 12 — Repetitions
1 (one principal run). No re-runs to rescue an unfavorable result (No Rescue After Failure). A protocol-deviation re-run, if ever needed, is flagged and is not primary evidence.

### Field 13 — Transpiler settings
`optimization_level=1`; `initial_layout=[Q_A, Q_P]` (the selected pair); **no dynamical decoupling** (so that the delay arms reflect bare T1/T2 decay, not DD-protected idle); IBM Heron basis gates {cz, id, rz, sx, x}; explicit `delay` instructions carry the per-arm idle durations. Identical settings for SPAM and principal jobs.

### Field 14 — Readout mitigation decision
**No readout mitigation on the primary endpoint.** Raw counts are primary. The in-situ SPAM job characterizes readout error, and `L_D_corrected` subtracts the idle baseline analytically — but no measurement-error mitigation is applied to the primary counts. Any mitigated figures, if produced, are reported separately and labeled SECONDARY only.

### Field 15 — Inclusion criteria
Principal-job results are included as primary evidence iff: (a) SPAM job completed and `SPAM_baseline ≤ 0.02` on **both** selected qubits; (b) principal job completed and returned counts for all 8 arms; (c) SPAM baseline drift between SPAM and principal jobs ≤ 0.005; (d) no protocol deviation from this document.

### Field 16 — Exclusion criteria
Exclude / flag as non-primary: backend change after submission; qubit-pair change after freeze; shot-count change; delay-point change; calibration drift > 0.005 between jobs; any circuit alteration; job failure or partial return.

### Field 17 — Metric definitions (mathematical)
```
S_A_0          = P(Q_P = 1 | Arm 1)                        # ALLOW reference (0 µs)
S_A_short      = P(Q_P = 1 | Arm 2)                        # ALLOW, ~0.5 µs
S_A_medium     = P(Q_P = 1 | Arm 3)                        # ALLOW, ~1.0 µs
S_A_long       = P(Q_P = 1 | Arm 4)                        # ALLOW, ~2.0 µs
L_expired      = P(Q_P = 1 | Arm 5)                        # expired-auth leakage (primary)
L_replayed     = P(Q_P = 1 | Arm 6)                        # replayed-auth leakage (primary)
S_reverified   = P(Q_P = 1 | Arm 7)                        # reverified ALLOW fidelity
SPAM_baseline  = P(Q_P = 1 | Arm 8)                        # idle readout error
Δ_B            = S_A_0 − L_expired                         # boundary discrimination (Arm 1 vs Arm 5)
L_D_corrected  = L_D − SPAM_baseline                       # SPAM-corrected leakage (per DENY arm)
```
Delay-decay characterization: report `S_A(delay)` for delay ∈ {0, 0.5, 1.0, 2.0} µs as a curve (descriptive).

### Field 18 — Statistical test
Wilson score interval for each binomial proportion. 95% CI (z=1.96) reported for all endpoints; 99% CI (z=2.576) used for leakage distinguishability diagnostics. One-sided interpretation on the primary ceilings (upper Wilson bound of each DENY arm's `L_D_corrected` vs 0.02; lower Wilson bound of `S_reverified` vs 0.90).

### Field 19 — Multiple-comparison correction
Bonferroni correction across the secondary hypotheses (H2a, H2b, H2c): family α = 0.05 → per-test α = 0.0167 (~98.3% CIs). The primary endpoints (H1: Arms 5, 6, 7 and Δ_B) are not penalized by the secondary family. The delay-decay curve (H2a) is descriptive and carries no pass/fail weight.

### Field 20 — PASS condition
`L_D_corrected(Arm 5, expired) ≤ 0.02` **AND** `L_D_corrected(Arm 6, replayed) ≤ 0.02` **AND** `S_reverified(Arm 7) ≥ 0.90` **AND** `Δ_B(Arm 1 vs Arm 5) ≥ 0.70`, with in-situ `SPAM_baseline ≤ 0.02` on both qubits. The delay-decay arms (2, 3, 4) are reported descriptively and do not gate the verdict.

### Field 21 — FAIL condition
Any DENY arm (5 expired, 6 replayed) leaks `L_D_corrected > 0.02` while SPAM is clean (`SPAM_baseline ≤ 0.02`); **OR** reverification fails to restore ALLOW (`S_reverified < 0.90`); **OR** `Δ_B(Arm 1 vs Arm 5) < 0.70` — the failure being attributable to the boundary mechanism, not the qubit.

### Field 22 — KILL / INDETERMINATE condition
In-situ `SPAM_baseline > 0.02` on **either** qubit → INDETERMINATE / KILLED (qubit/backend disqualified); **stop immediately, submit no principal job, no rescue.** Also INDETERMINATE if SPAM baseline drifts > 0.005 between the SPAM and principal jobs (calibration drift).

### Field 23 — Interpretation boundaries
Results characterize **decoherence-driven erosion** of the verify-then-execute authorization boundary as the verification-to-execution separation increases — a **metrological characterization, not a new physical principle** and **not a cryptographic claim**. The delay arms measure how ALLOW survival decays with idle time (T1/T2 of Q_A between measurement and payload execution); the expired/replayed arms characterize how a stale authorization is (correctly) not honored; the reverification arm characterizes recovery of ALLOW with a fresh measurement. Findings apply only to *this boundary implementation on this qubit pair on this backend at this calibration* and do not generalize without replication. "Leakage" means *unauthorized payload activation*, not computational-basis leakage.

### Field 24 — Relationship to prior work (ARK-441 / ARK-446)
ARK-441 (ibm_kingston, 2026-07-16) established the SPAM-resolved VBE authorization boundary (SPAM-corrected `L_D ≤ 2%`, `Δ_B ≥ 0.70`) and included a single ~1 µs stale-auth arm. ARK-442 extends that stale-auth probe into a **delay-resolved characterization** (0 / 0.5 / 1.0 / 2.0 µs) and adds explicit expired-auth, replay-after-expiry, and reverification-after-expiry arms. The DENY-arm thresholds carry over from ARK-441 (`L_D_corrected ≤ 0.02`, `Δ_B ≥ 0.70`). ARK-446 (concurrent) tests cross-device replication of the ARK-441 result; ARK-442 characterizes its degradation under delay.

### Field 25 — Exact timestamp
Preregistration authored: **2026-07-16** (UTC). Effective lock time = the GitHub preregistration commit timestamp recorded in `RUN_LOG.md`.

### Field 26 — Calibration snapshot reference
A calibration snapshot of the selected backend (Heron r2) is retrieved at execution time and committed as `calibration_snapshot_20260716.json`; its SHA-256 is recorded in `MANIFEST.txt`. The selected qubit pair (Field 10) is derived from this snapshot and frozen in `RUN_LOG.md` before submission.

### Field 27 — Ordering constraint (hard)
1. Commit this preregistration + all code files + `MANIFEST.txt` (Field 28 hashes) to GitHub. Record commit hash (the preregistration lock).
2. Retrieve live calibration → select and freeze qubit pair per Field 10 → record in `RUN_LOG.md`.
3. Run in-situ SPAM job → commit `spam_results.json`.
4. Only if `SPAM_baseline ≤ 0.02` on both qubits: submit principal job → record job ID in `RUN_LOG.md` and commit **immediately**, before reading any result. If SPAM fails the gate → KILLED, stop, no rescue.
5. Retrieve raw counts → commit `raw_results.json`.
6. Run analysis → commit `proofrecord.json`, `ARK_442_results.md`, plots (including the `S_A(delay)` decay curve). Tag `ark-442-v1.0`.

### Field 28 — SHA-256 hashes of all code files
Authoritative hashes are maintained in `MANIFEST.txt` (committed in the same preregistration commit). The manifest covers all ARK-442 code files (delay circuit generator, SPAM job, submission, retrieval, analysis), `requirements.txt`, `README.md`, `ARK_442_preregistration.md`, and the calibration snapshot. Hashes are auto-filled at commit time.

---

*ARK-442 Preregistration — Remnant Fieldworks Inc. / Derek Hone — 2026-07-16. No hardware job is submitted until this document and its manifest are committed. This is a metrological characterization of decoherence-driven boundary erosion, not new physics and not a cryptographic claim. No Rescue After Failure.*
