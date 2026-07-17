# ARK-443 — PREREGISTRATION
**Two-of-Three (M-of-N) Quorum Authorization on IBM Quantum (Heron r2)**
**Remnant Fieldworks Inc. — Derek Hone**
**Governing principle:** *Proof Before Power. Prediction Before Measurement. No Rescue After Failure.*

> This document is the LOCK. It is committed to GitHub (derekhone/uip-phase1-testbeds, folder `ark-443/`) with SHA-256 hashes of all code files **before any IBM Quantum job is submitted**. The preregistration commit hash is recorded in `RUN_LOG.md`. Nothing below — hypotheses, arm definitions, qubit selection rule, shot count, metrics, or pass/fail/kill windows — may be altered after any result is observed.

---

### Field 1 — Experiment title
Two-of-Three quorum authorization on IBM Heron hardware: a preregistered test of whether a payload executes **only when at least two of three independent authorizers approve**, and whether **one authorizer acting alone — honest, replayed, or compromised — can cause execution** (it must not). This is a metrological characterization of a quorum-gated execution rule realized in a dynamic circuit by classical feedforward.

### Field 2 — Experiment ID
ARK-443 (Remnant Fieldworks Inc. / Derek Hone).

### Field 3 — Research question
Can a verify-then-execute (VBE) authorization boundary enforce **separation of duties** through an M-of-N (here 2-of-3) quorum: the payload fires **iff at least two of three independent authorization channels approve**, and **no single channel — including a compromised or post-vote-tampered one — can unilaterally cross the boundary**, while a legitimate two-authorizer quorum is **tolerant of a degraded third channel**? Concretely: three authorizer qubits are prepared per each arm, measured into a 3-bit authorization register, and a **classical majority (≥2 of 3)** conditions an X on the payload qubit; the payload readout is the primary endpoint. This is a **metrological characterization of a quorum-gated execution rule on this hardware** — **NOT new physics** and **NOT a cryptographic guarantee** (no signature/MAC security, no Byzantine-agreement claim; "authorizer" is a single prepared+measured qubit, and "quorum" is a classical majority of measured bits realized in a dynamic circuit).

### Field 4 — Primary hypothesis H1
On the calibration-selected qubits (Field 10), with the payload fired iff the classical majority of the three measured authorization bits is ≥ 2:
- **0-of-3 (Arm 1)** produces `L_corrected ≤ 0.02` (no approvals → no execution);
- **1-of-3 honest (Arm 2)** produces `L_corrected ≤ 0.02` (**no unilateral approval / separation of duties**);
- **1-of-3 alternate channel (Arm 5)** produces `L_corrected ≤ 0.02` (no-unilateral holds regardless of which single channel approves);
- **post-vote single-channel tamper / replay (Arm 7)** produces `L_corrected ≤ 0.02` (a channel flipped after its vote is recorded cannot manufacture approval);
- **2-of-3 (Arm 3)** produces `S_2of3 ≥ 0.90` (a genuine quorum executes);
- **degraded-channel quorum (Arm 6)** produces `S_degraded ≥ 0.90` (a two-authorizer quorum tolerates a fully noisy third channel);
- **Boundary discrimination** `Δ_B` between the **weakest ALLOW arm** (min of Arms 3, 4, 6) and the **worst-case DENY arm** (max of Arms 1, 2, 5, 7) is `≥ 0.70`.

### Field 5 — Null hypothesis H0
`Δ_B (weakest ALLOW vs worst-case DENY)` is statistically indistinguishable from zero, and/or a single approving channel executes the payload at a rate indistinguishable from a genuine two-authorizer quorum; equivalently, the quorum gate does not enforce separation of duties (one channel suffices) and/or a genuine quorum does not execute.

### Field 6 — Secondary hypotheses
- **H2a (unanimity confirms quorum):** `S_3of3` (Arm 4) is statistically indistinguishable from `S_2of3` (Arm 3) within its 95% Wilson interval — three approvals execute no worse than two.
- **H2b (uniform fail-closed below quorum):** the sub-quorum DENY arms (1 = 0-of-3, 2 = 1-of-3, 5 = 1-of-3 alt, 7 = replay) are mutually statistically indistinguishable in payload activation (each ≈ SPAM baseline); no sub-quorum construction leaks more than the others (descriptive; 99% Wilson intervals).
- **H2c (degraded tolerance):** `S_degraded` (Arm 6) is statistically indistinguishable from `S_2of3` (Arm 3) within its 95% Wilson interval — a noisy third channel does not degrade a legitimate two-authorizer quorum (because two honest approvals already meet the threshold).

### Field 7 — Circuit architecture
Four-qubit dynamic circuits. Virtual q0 = Q_P (payload — primary endpoint); virtual q1,q2,q3 = Q_A1, Q_A2, Q_A3 (three independent authorizers). Core mechanism — a **classical-feedforward quorum gate** (no inter-qubit two-qubit gates; the quorum is a classical majority of measured authorization bits):
```
Authorization phase:  prepare Q_A1,Q_A2,Q_A3 per arm ; measure -> ca[0],ca[1],ca[2]   (3-bit vote register)
Quorum gate (>=2 of 3):  for v in {0b011, 0b101, 0b110, 0b111}:  if (ca == v):  X(Q_P)
Payload readout:      measure(Q_P) -> cp                                                (PRIMARY endpoint)
```
The four register values with popcount ≥ 2 are `{3,5,6,7}`; because `ca` holds exactly one value per shot, **at most one** `if_test` block fires, applying a single X to the payload (initialized `|0⟩`) iff the majority condition holds. The majority set `{3,5,6,7}` is the set of all ≥2-bit values and is **invariant to bit-to-qubit mapping** (majority is symmetric), so the fire/no-fire decision depends only on the number of approvals, not on endianness. There are **no CX/CZ gates between the authorizers and the payload** — the quorum is realized purely by classical feedforward, which (i) matches the "measure the authorizers, then classically decide" doctrine and (ii) avoids the large two-qubit-gate error a quantum-majority (Toffoli) construction would incur. Named classical registers (`ca` 3-bit, `cp` 1-bit) let SamplerV2 expose per-register counts so payload readout is unambiguous despite mid-circuit measurement. The four sequential single-register `if_test` blocks use the flattened, non-nested control-flow pattern proven to run on this backend in ARK-442/ARK-444. Full per-arm definitions in Field 8.

### Field 8 — Arms (8 arms)
| Arm | A1 | A2 | A3 | Approvals | Quorum gate | Purpose | Endpoint |
|-----|----|----|----|-----------|-------------|---------|----------|
| 1 `arm1_0of3_deny` | \|0⟩ | \|0⟩ | \|0⟩ | 0 | withheld | no approvals (**DENY baseline, PRIMARY**) | L_0of3 = P(Q_P=1) |
| 2 `arm2_1of3_deny` | \|1⟩ | \|0⟩ | \|0⟩ | 1 | withheld | one honest approver — no unilateral (**PRIMARY**) | L_1of3 = P(Q_P=1) |
| 3 `arm3_2of3_allow` | \|1⟩ | \|1⟩ | \|0⟩ | 2 | fires | genuine two-authorizer quorum (**PRIMARY**) | S_2of3 = P(Q_P=1) |
| 4 `arm4_3of3_allow` | \|1⟩ | \|1⟩ | \|1⟩ | 3 | fires | unanimous approval | S_3of3 = P(Q_P=1) |
| 5 `arm5_1of3_altchannel_deny` | \|0⟩ | \|0⟩ | \|1⟩ | 1 | withheld | one approver on a **different** channel — no unilateral (**PRIMARY**) | L_1of3_alt = P(Q_P=1) |
| 6 `arm6_degraded_quorum_allow` | \|1⟩ | \|1⟩ | H (noisy) | 2 (+noise) | fires | two honest approvals + fully noisy third channel (**degraded tolerance**) | S_degraded = P(Q_P=1) |
| 7 `arm7_replay_tamper_deny` | \|0⟩→meas→X | \|0⟩ | \|0⟩ | 0 (recorded) | withheld | one channel flipped **after** its vote is recorded (**post-vote tamper/replay, PRIMARY**) | L_replay = P(Q_P=1) |
| 8 `arm8_idle_spam` | — | — | — | — | none | idle SPAM baseline on payload | SPAM_baseline = P(Q_P=1) |

DENY class (must fail closed): Arms 1, 2, 5, 7. ALLOW class (must execute): Arms 3, 4, 6. Arm 8 is the idle readout baseline. In Arm 7 the compromised authorizer is measured into `ca` (recording an honest `0`) **before** a reset+X drives its qubit to `|1⟩`; because the quorum gate reads the *recorded vote* `ca`, the post-vote flip cannot cross the boundary.

### Field 9 — Backend selection rule (preregistered, not cherry-picked)
Priority: (1) **ibm_marrakesh** (preferred); (2) ibm_fez (fallback if marrakesh non-operational or queue-prohibitive). Selected backend fixed before submission and recorded in `RUN_LOG.md`.

### Field 10 — Qubit selection rule (preregistered)
Four qubits are required (three authorizers + one payload). All four must have `readout_error < 0.020` from today's calibration snapshot. **No inter-qubit connectivity constraint is imposed**, because the quorum gate is realized by classical feedforward (mid-circuit measurement of the three authorizer qubits followed by a classical-majority-conditioned X on the payload) and uses **no two-qubit gates between any of the four qubits**; each qubit only needs a single-qubit preparation and its own measurement. Selection is deterministic: among all qubits with `readout_error < 0.020`, take the four with the lowest readout error (ties broken by ascending physical index); **assign the lowest-readout-error qubit to Q_P** (the payload is the primary endpoint and receives the best qubit); assign the remaining three, in ascending physical-qubit index, to Q_A1, Q_A2, Q_A3. The specific quadruple is selected at execution time from the live calibration snapshot of the selected backend, then frozen and recorded in `RUN_LOG.md` before submission; it may not be changed thereafter.

### Field 11 — Shot count
8,192 shots per arm × 8 arms = 65,536 shots (principal job). SPAM job: 2,048 shots × 8 circuits (|0⟩ and |1⟩ preparation on each of the four selected qubits) = 16,384 shots.

### Field 12 — Repetitions
1 (one principal run). No re-runs to rescue an unfavorable result (No Rescue After Failure). A protocol-deviation re-run, if ever needed, is flagged and is not primary evidence.

### Field 13 — Transpiler settings
`optimization_level=1`; `initial_layout=[Q_P, Q_A1, Q_A2, Q_A3]`; **no dynamical decoupling**; IBM Heron basis gates {cz, id, rz, sx, x}; `reset` (Arm 7, top level only) and flattened single-register `if_test` used for the quorum gate. Identical settings for SPAM and principal jobs.

### Field 14 — Readout mitigation decision
**No readout mitigation on the primary endpoint.** Raw counts are primary. The in-situ SPAM job characterizes readout error, and `L_corrected` subtracts the idle baseline analytically — but no measurement-error mitigation is applied to the primary counts. Any mitigated figures, if produced, are reported separately and labeled SECONDARY only.

### Field 15 — Inclusion criteria
Principal-job results are included as primary evidence iff: (a) SPAM job completed and readout error ≤ 0.02 on **all four** selected qubits; (b) principal job completed and returned counts for all 8 arms; (c) in-situ SPAM baseline (Arm 8) ≤ 0.02 and drift between SPAM and principal jobs ≤ 0.005 on the payload; (d) no protocol deviation from this document.

### Field 16 — Exclusion criteria
Exclude / flag as non-primary: backend change after submission; qubit change after freeze; shot-count change; arm-definition change; calibration drift > 0.005 between jobs; any circuit alteration; job failure or partial return.

### Field 17 — Metric definitions (mathematical)
```
L_0of3        = P(Q_P = 1 | Arm 1)                         # 0-of-3 leakage (primary, DENY)
L_1of3        = P(Q_P = 1 | Arm 2)                         # 1-of-3 leakage (primary, DENY, no unilateral)
S_2of3        = P(Q_P = 1 | Arm 3)                         # 2-of-3 execution fidelity (primary, ALLOW)
S_3of3        = P(Q_P = 1 | Arm 4)                         # 3-of-3 execution fidelity (ALLOW)
L_1of3_alt    = P(Q_P = 1 | Arm 5)                         # 1-of-3 alt-channel leakage (primary, DENY)
S_degraded    = P(Q_P = 1 | Arm 6)                         # degraded-channel quorum fidelity (ALLOW, tolerance)
L_replay      = P(Q_P = 1 | Arm 7)                         # post-vote tamper/replay leakage (primary, DENY)
SPAM_baseline = P(Q_P = 1 | Arm 8)                         # idle readout error on payload
L_worst       = max(L_0of3, L_1of3, L_1of3_alt, L_replay)  # worst-case DENY leakage (raw)
S_min         = min(S_2of3, S_3of3, S_degraded)            # weakest ALLOW execution (raw)
Δ_B           = S_min − L_worst                            # boundary discrimination (weakest ALLOW vs worst DENY)
L_x_corrected = L_x − SPAM_baseline   for x in {0of3, 1of3, 1of3_alt, replay}
```

### Field 18 — Statistical test
Wilson score interval for each binomial proportion. 95% CI (z=1.96) reported for all endpoints; 99% CI (z=2.576) used for leakage distinguishability diagnostics. One-sided interpretation on the primary ceilings (upper Wilson bound of each DENY arm's `L_corrected` vs 0.02; lower Wilson bound of each ALLOW arm's `S` vs 0.90).

### Field 19 — Multiple-comparison correction
Bonferroni correction across the secondary hypotheses (H2a, H2b, H2c): family α = 0.05 → per-test α = 0.0167 (~98.3% CIs). The primary endpoints (H1: Arms 1–7 ceilings/floors and Δ_B) are not penalized by the secondary family.

### Field 20 — PASS condition
`L_corrected ≤ 0.02` for **every** DENY arm (1 = 0-of-3, 2 = 1-of-3, 5 = 1-of-3 alt, 7 = replay/tamper) **AND** `S ≥ 0.90` for **every** ALLOW arm (3 = 2-of-3, 4 = 3-of-3, 6 = degraded quorum) **AND** `Δ_B (S_min − L_worst) ≥ 0.70`, with in-situ `SPAM_baseline ≤ 0.02`. A PASS means: the quorum gate enforces separation of duties — no single channel (honest, alternate, or post-vote-tampered) executes the payload, a genuine two-authorizer quorum executes, and a legitimate quorum tolerates a degraded third channel.

### Field 21 — FAIL condition
Any DENY arm (1, 2, 5, 7) leaks `L_corrected > 0.02` while SPAM is clean (`SPAM_baseline ≤ 0.02`) — i.e., a sub-quorum crosses the boundary; **OR** any ALLOW arm (3, 4, 6) executes at `S < 0.90` — i.e., a genuine quorum fails to execute; **OR** `Δ_B < 0.70` — the failure being attributable to the quorum mechanism, not the qubit.

### Field 22 — KILL / INDETERMINATE condition
In-situ `SPAM_baseline > 0.02` on the payload, or SPAM-job readout error > 0.02 on **any** of the four selected qubits → INDETERMINATE / KILLED (qubit/backend disqualified); **stop immediately, submit no principal job, no rescue.** Also INDETERMINATE if SPAM baseline drifts > 0.005 between the SPAM and principal jobs (calibration drift).

### Field 23 — Interpretation boundaries
Results characterize a **quorum-gated execution rule** on *these* four qubits on *this* backend at *this* calibration — a **metrological characterization, not a new physical principle** and **not a cryptographic or Byzantine-fault-tolerance guarantee**. Each "authorizer" is a single prepared-and-measured qubit; "quorum" is a classical majority (≥2 of 3) of the measured authorization bits; "leakage" means *unauthorized payload activation* (the payload firing when fewer than two channels legitimately approve), not computational-basis leakage. The compromised/replay arm (7) models one specific tamper channel (a post-vote qubit flip); it does not model an adversary who corrupts the classical vote register or colludes across channels. By construction, the 2-of-3 rule protects against **one** dishonest channel; **two** colluding channels form a legitimate quorum and would execute — this is the intended, honestly-stated boundary of separation-of-duties, not a defect. A PASS demonstrates that, on this hardware and gate, sub-quorum authorization fails closed and a genuine quorum executes; it does **not** establish security against an adversary, generalize to other qubits/backends/M-of-N parameters, or assert cryptographic strength. Findings do not generalize without replication.

### Field 24 — Relationship to prior work (ARK-441 / ARK-446 / ARK-442 / ARK-444)
ARK-441 (ibm_kingston) established the SPAM-resolved VBE authorization boundary (SPAM-corrected `L_D ≤ 2%`, `Δ_B ≥ 0.70`). ARK-446 (ibm_marrakesh) demonstrated cross-device replication (PASS). ARK-442 (ibm_marrakesh) characterized boundary degradation under verification-to-execution **delay** plus expiry/replay/reverification (PASS). ARK-444 (ibm_marrakesh) extended the boundary to **decision-to-execution integrity** — the executed action must match the approved action — testing five post-approval alteration classes and a reverification-recovery arm (PASS). ARK-443 extends the boundary from a *single* authorization to a **quorum of independent authorizations**: it tests **separation of duties** (no unilateral approval), **M-of-N quorum authorization** (≥2 of 3 executes), **compromised/post-vote-tamper resistance** (one bad channel cannot cross the boundary), and **degraded-channel tolerance** (a legitimate quorum survives a noisy third channel). The DENY-arm ceiling (`L_corrected ≤ 0.02`), the ALLOW floor (`S ≥ 0.90`), and the discrimination floor (`Δ_B ≥ 0.70`) carry over from ARK-441/442/444.

### Field 25 — Exact timestamp
Preregistration authored: **2026-07-16** (UTC). Effective lock time = the GitHub preregistration commit timestamp recorded in `RUN_LOG.md`.

### Field 26 — Calibration snapshot reference
A calibration snapshot of the selected backend (Heron r2) is retrieved at execution time and committed as `calibration_snapshot_marrakesh_20260716.json`; its SHA-256 is recorded in `MANIFEST.txt`. The selected qubit quadruple (Field 10) is derived from this snapshot and frozen in `RUN_LOG.md` before submission.

### Field 27 — Ordering constraint (hard)
1. Commit this preregistration + all code files + `MANIFEST.txt` (Field 28 hashes) to GitHub. Record commit hash (the preregistration lock).
2. Retrieve live calibration → select and freeze four qubits per Field 10 → record in `RUN_LOG.md`.
3. Run in-situ SPAM job → commit `spam_results.json`.
4. Only if readout error ≤ 0.02 on all four qubits: submit principal job → record job ID in `RUN_LOG.md` and commit **immediately**, before reading any result. If SPAM fails the gate → KILLED, stop, no rescue.
5. Retrieve raw counts → commit `raw_results.json`.
6. Run analysis → commit `proofrecord.json`, `RESULTS.md`, plots. Tag `ark-443-v1.0`.

### Field 28 — SHA-256 hashes of all code files
Authoritative hashes are maintained in `MANIFEST.txt` (committed in the same preregistration commit). The manifest covers all ARK-443 code files (qubit selection, quorum circuit generator, SPAM job, submission, retrieval, analysis), `README.md`, and `ARK_443_preregistration.md`. Hashes are auto-filled at commit time.

---

*ARK-443 Preregistration — Remnant Fieldworks Inc. / Derek Hone — 2026-07-16. No hardware job is submitted until this document and its manifest are committed. This is a metrological characterization of a quorum-gated execution rule, not new physics and not a cryptographic guarantee. No Rescue After Failure.*
