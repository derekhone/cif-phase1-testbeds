# ARK-444 — PREREGISTRATION
**Decision-to-Execution Integrity on IBM Quantum (Heron r2)**
**Remnant Fieldworks Inc. — Derek Hone**
**Governing principle:** *Proof Before Power. Prediction Before Measurement. No Rescue After Failure.*

> This document is the LOCK. It is committed to GitHub (derekhone/uip-phase1-testbeds, folder `ark-444/`) with SHA-256 hashes of all code files **before any IBM Quantum job is submitted**. The preregistration commit hash is recorded in `RUN_LOG.md`. Nothing below — hypotheses, arm definitions, qubit pair selection rule, shot count, metrics, or pass/fail/kill windows — may be altered after any result is observed.

---

### Field 1 — Experiment title
Decision-to-Execution Integrity on IBM Heron hardware: a preregistered test of whether the action that executes is exactly the action that was verified, and whether a post-approval alteration of an approved action is detected and **fails closed** (the payload does not execute).

### Field 2 — Experiment ID
ARK-444 (Remnant Fieldworks Inc. / Derek Hone).

### Field 3 — Research question
Can the verify-then-execute (VBE) authorization boundary detect when an **approved action is altered between approval and execution**, and fail closed? Specifically: an approval commits a signature of the approved action; at execution the action's signature is re-verified and the payload fires **only if the executed action's signature matches the approved signature**. Does every class of post-approval alteration — destination changed, amount/parameter changed, operation type changed, an extra action appended, and a replayed stale approval — fail to execute the payload, while a properly **re-verified** (re-approved) mutated action correctly executes? This is a **metrological characterization of a tamper-evident decision-to-execution binding on this hardware** — **NOT new physics** and **NOT a cryptographic integrity claim** (no MAC/signature security is asserted; "integrity" here is a single-bit commitment comparison realized in a dynamic circuit).

### Field 4 — Primary hypothesis H1
On the calibration-selected, connected qubit pair (Field 10), with the payload bound to a fresh execution-time verification that must match the committed approval:
- **Destination changed (Arm 2)** produces `L_corrected ≤ 0.02` (payload does not execute);
- **Amount/parameter changed (Arm 3)** produces `L_corrected ≤ 0.02`;
- **Operation type changed (Arm 4)** produces `L_corrected ≤ 0.02`;
- **Extra action appended (Arm 5)** produces `L_corrected ≤ 0.02`;
- **Original approval replayed (Arm 6)** produces `L_corrected ≤ 0.02`;
- **Mutated-then-reverified (Arm 7)** produces `S_reverified ≥ 0.90` (a re-approved action correctly executes);
- **Boundary discrimination** `Δ_B` between Arm 1 (approved, unchanged) and the **worst-case** altered arm is `≥ 0.70`.

### Field 5 — Null hypothesis H0
`Δ_B (Arm 1 vs worst-case altered arm)` is statistically indistinguishable from zero and/or altered actions execute the payload at rates indistinguishable from the unchanged approved action; equivalently, the binding does not detect post-approval alteration and does not fail closed, and/or a re-verified action does not execute.

### Field 6 — Secondary hypotheses
- **H2a (uniform fail-closed):** the five altered/replayed arms (2–6) are mutually statistically indistinguishable in payload activation (each ≈ SPAM baseline); no single alteration class leaks more than the others (descriptive; reported with 99% Wilson intervals).
- **H2b (replay ≈ mutation):** `P(Q_P=1 | Arm 6 replayed)` is statistically indistinguishable from the mutation arms (2–5) — a replayed stale approval is no better than a fresh mutation at executing the payload.
- **H2c (reverification concordance):** `S_reverified` (Arm 7) is statistically indistinguishable from the unchanged approved reference `S_match` (Arm 1) within its 95% Wilson interval — re-verifying restores full execution fidelity.

### Field 7 — Circuit architecture
Two-qubit dynamic circuits. Virtual q0 = Q_A (approval / integrity-commitment qubit), virtual q1 = Q_P (payload). Core mechanism — a **tamper-evident decision-to-execution binding**:
```
Approval phase:    prepare Q_A per APPROVED action ; measure(Q_A) -> ca   (committed approval signature)
Execution phase:   reset(Q_A) ; prepare Q_A per EXECUTED action ; measure(Q_A) -> ce   (fresh execution verification)
Integrity gate:    if (ca == 1) AND (ce == 1):  X(Q_P)     (payload fires iff executed action matches the committed approval)
Payload readout:   measure(Q_P) -> cp                       (PRIMARY endpoint)
```
The payload is bound to the **fresh execution-time verification** `ce`, not to the stale approval `ca` alone. For an unchanged approved action, `ca = ce = 1` and the payload fires. Any post-approval alteration drives `ce ≠ ca` (here `ce = 0`), so the integrity gate withholds the payload (fail closed). A replayed stale approval provides `ca = 1` but no fresh matching verification (`ce = 0`), so it also fails closed. A mutated action that is **re-verified** re-establishes `ca = ce = 1` and correctly executes. The single-bit commitment is a hardware abstraction of an action signature; the payload register `cp` is the primary readout. Named classical registers (`ca`, `ce`, `cp`) let SamplerV2 expose per-register counts so payload readout is unambiguous despite mid-circuit measurements. Full per-arm definitions in Field 8.

### Field 8 — Arms (8 arms)
| Arm | Approval (ca) | Execution verify (ce) | Integrity gate | Purpose | Endpoint |
|-----|---------------|-----------------------|----------------|---------|----------|
| 1 `arm1_approved_unchanged` | \|1⟩→1 | reset,\|1⟩→1 (matches) | fires | approved action executed unchanged (**reference**) | S_match = P(Q_P=1) |
| 2 `arm2_destination_changed` | \|1⟩→1 | reset,\|0⟩→0 (dest ≠ bound) | withheld | destination changed after approval (**PRIMARY**) | L_dest = P(Q_P=1) |
| 3 `arm3_amount_changed` | \|1⟩→1 | reset, idle→0 (param ≠) | withheld | amount/parameter changed after approval (**PRIMARY**) | L_amount = P(Q_P=1) |
| 4 `arm4_operation_changed` | \|1⟩→1 | reset, X·X=I→0 (op type ≠) | withheld | operation type changed after approval (**PRIMARY**) | L_optype = P(Q_P=1) |
| 5 `arm5_extra_action_appended` | \|1⟩→1 | reset,\|1⟩ then appended X→0 | withheld | extra action appended after verification (**PRIMARY**) | L_append = P(Q_P=1) |
| 6 `arm6_approval_replayed` | \|0⟩→0, replay flip post-measure | reset,\|0⟩→0 | withheld (bound to original) | original approval replayed (**PRIMARY**) | L_replay = P(Q_P=1) |
| 7 `arm7_mutated_then_reverified` | \|1⟩→1 (fresh re-approval) | reset,\|1⟩→1 (matches) | fires | mutated payload re-verified before execution | S_reverified = P(Q_P=1) |
| 8 `arm8_idle_spam` | — | — | none | idle SPAM baseline | SPAM_baseline = P(Q_P=1) |

Arms 1 and 7 share the matched (fires) construction; arms 2–6 are the fail-closed alteration/replay class (each a distinct construction that drives a commitment mismatch); arm 8 is the idle readout baseline.

### Field 9 — Backend selection rule (preregistered, not cherry-picked)
Priority: (1) **ibm_marrakesh** (preferred); (2) ibm_fez (fallback if marrakesh non-operational or queue-prohibitive). Selected backend fixed before submission and recorded in `RUN_LOG.md`.

### Field 10 — Qubit selection rule (preregistered)
Both qubits must have `readout_error < 0.020` from today's calibration snapshot; must be directly connected in the coupling map; among qualifying connected pairs, select the minimum sum of readout errors — the **same rule used in ARK-441, ARK-446, and ARK-442**. The specific pair is selected at execution time from the live calibration snapshot of the selected backend, then frozen and recorded in `RUN_LOG.md` before submission; it may not be changed thereafter. Lower physical index → Q_A (deterministic).

### Field 11 — Shot count
8,192 shots per arm × 8 arms = 65,536 shots (principal job). SPAM job: 2,048 shots × 4 circuits = 8,192 shots.

### Field 12 — Repetitions
1 (one principal run). No re-runs to rescue an unfavorable result (No Rescue After Failure). A protocol-deviation re-run, if ever needed, is flagged and is not primary evidence.

### Field 13 — Transpiler settings
`optimization_level=1`; `initial_layout=[Q_A, Q_P]` (the selected pair); **no dynamical decoupling**; IBM Heron basis gates {cz, id, rz, sx, x}; `reset` and nested `if_test` used for the two-phase commitment. Identical settings for SPAM and principal jobs.

### Field 14 — Readout mitigation decision
**No readout mitigation on the primary endpoint.** Raw counts are primary. The in-situ SPAM job characterizes readout error, and `L_corrected` subtracts the idle baseline analytically — but no measurement-error mitigation is applied to the primary counts. Any mitigated figures, if produced, are reported separately and labeled SECONDARY only.

### Field 15 — Inclusion criteria
Principal-job results are included as primary evidence iff: (a) SPAM job completed and `SPAM_baseline ≤ 0.02` on **both** selected qubits; (b) principal job completed and returned counts for all 8 arms; (c) SPAM baseline drift between SPAM and principal jobs ≤ 0.005; (d) no protocol deviation from this document.

### Field 16 — Exclusion criteria
Exclude / flag as non-primary: backend change after submission; qubit-pair change after freeze; shot-count change; arm-definition change; calibration drift > 0.005 between jobs; any circuit alteration; job failure or partial return.

### Field 17 — Metric definitions (mathematical)
```
S_match         = P(Q_P = 1 | Arm 1)                       # approved-unchanged execution (reference)
L_dest          = P(Q_P = 1 | Arm 2)                       # destination-changed leakage (primary)
L_amount        = P(Q_P = 1 | Arm 3)                       # amount/parameter-changed leakage (primary)
L_optype        = P(Q_P = 1 | Arm 4)                       # operation-type-changed leakage (primary)
L_append        = P(Q_P = 1 | Arm 5)                       # appended-action leakage (primary)
L_replay        = P(Q_P = 1 | Arm 6)                       # replayed-approval leakage (primary)
S_reverified    = P(Q_P = 1 | Arm 7)                       # re-verified mutated action execution fidelity
SPAM_baseline   = P(Q_P = 1 | Arm 8)                       # idle readout error
L_worst         = max(L_dest, L_amount, L_optype, L_append, L_replay)   # worst-case altered leakage (raw)
Δ_B             = S_match − L_worst                        # boundary discrimination (Arm 1 vs worst altered arm)
L_x_corrected   = L_x − SPAM_baseline   for x in {dest, amount, optype, append, replay}
```

### Field 18 — Statistical test
Wilson score interval for each binomial proportion. 95% CI (z=1.96) reported for all endpoints; 99% CI (z=2.576) used for leakage distinguishability diagnostics. One-sided interpretation on the primary ceilings (upper Wilson bound of each altered arm's `L_corrected` vs 0.02; lower Wilson bound of `S_reverified` vs 0.90).

### Field 19 — Multiple-comparison correction
Bonferroni correction across the secondary hypotheses (H2a, H2b, H2c): family α = 0.05 → per-test α = 0.0167 (~98.3% CIs). The primary endpoints (H1: Arms 2–7 and Δ_B) are not penalized by the secondary family.

### Field 20 — PASS condition
`L_corrected ≤ 0.02` for **every** altered/replayed arm (2 dest, 3 amount, 4 optype, 5 append, 6 replay) **AND** `S_reverified(Arm 7) ≥ 0.90` **AND** `Δ_B(Arm 1 vs worst altered arm) ≥ 0.70`, with in-situ `SPAM_baseline ≤ 0.02` on both qubits. A PASS means: the boundary detects every class of post-approval alteration and fails closed, while a re-verified action correctly executes.

### Field 21 — FAIL condition
Any altered/replayed arm (2–6) leaks `L_corrected > 0.02` while SPAM is clean (`SPAM_baseline ≤ 0.02`); **OR** reverification fails to restore execution (`S_reverified < 0.90`); **OR** `Δ_B < 0.70` — the failure being attributable to the binding mechanism, not the qubit.

### Field 22 — KILL / INDETERMINATE condition
In-situ `SPAM_baseline > 0.02` on **either** qubit → INDETERMINATE / KILLED (qubit/backend disqualified); **stop immediately, submit no principal job, no rescue.** Also INDETERMINATE if SPAM baseline drifts > 0.005 between the SPAM and principal jobs (calibration drift).

### Field 23 — Interpretation boundaries
Results characterize a **tamper-evident decision-to-execution binding** on *this* qubit pair on *this* backend at *this* calibration — a **metrological characterization, not a new physical principle** and **not a cryptographic integrity guarantee**. The "action signature" is abstracted to a single committed bit realized via a two-phase (approve → re-verify) dynamic circuit; the alteration arms are representative encodings of alteration classes (destination, amount, operation type, appended action) unified by the commitment mismatch they induce, plus a replayed-approval arm. "Leakage" means *unauthorized payload activation* (payload firing when the executed action does not match the approved action), not computational-basis leakage. A PASS demonstrates that, on this hardware and binding, post-approval alterations fail closed and a re-verified action executes; it does **not** establish security against an adversary, generalize to other bindings/qubits/backends, or assert MAC/signature strength. Findings do not generalize without replication.

### Field 24 — Relationship to prior work (ARK-441 / ARK-446 / ARK-442)
ARK-441 (ibm_kingston, 2026-07-16) established the SPAM-resolved VBE authorization boundary (SPAM-corrected `L_D ≤ 2%`, `Δ_B ≥ 0.70`). ARK-446 (ibm_marrakesh) demonstrated cross-device replication (PASS). ARK-442 (ibm_marrakesh) characterized boundary degradation under verification-to-execution **delay**, plus expiry/replay/reverification (PASS). ARK-444 extends the boundary from *whether an authorization is valid* to *whether the executed action is exactly the approved action* — adding a fresh execution-time verification bound to the payload and testing five post-approval alteration classes and a reverification-recovery arm. The DENY-arm ceiling (`L_corrected ≤ 0.02`), the reverification floor (`S_reverified ≥ 0.90`), and the discrimination floor (`Δ_B ≥ 0.70`) carry over from ARK-441/442.

### Field 25 — Exact timestamp
Preregistration authored: **2026-07-16** (UTC). Effective lock time = the GitHub preregistration commit timestamp recorded in `RUN_LOG.md`.

### Field 26 — Calibration snapshot reference
A calibration snapshot of the selected backend (Heron r2) is retrieved at execution time and committed as `calibration_snapshot_marrakesh_20260716.json`; its SHA-256 is recorded in `MANIFEST.txt`. The selected qubit pair (Field 10) is derived from this snapshot and frozen in `RUN_LOG.md` before submission.

### Field 27 — Ordering constraint (hard)
1. Commit this preregistration + all code files + `MANIFEST.txt` (Field 28 hashes) to GitHub. Record commit hash (the preregistration lock).
2. Retrieve live calibration → select and freeze qubit pair per Field 10 → record in `RUN_LOG.md`.
3. Run in-situ SPAM job → commit `spam_results.json`.
4. Only if `SPAM_baseline ≤ 0.02` on both qubits: submit principal job → record job ID in `RUN_LOG.md` and commit **immediately**, before reading any result. If SPAM fails the gate → KILLED, stop, no rescue.
5. Retrieve raw counts → commit `raw_results.json`.
6. Run analysis → commit `proofrecord.json`, `RESULTS.md`, plots. Tag `ark-444-v1.0`.

### Field 28 — SHA-256 hashes of all code files
Authoritative hashes are maintained in `MANIFEST.txt` (committed in the same preregistration commit). The manifest covers all ARK-444 code files (qubit selection, integrity circuit generator, SPAM job, submission, retrieval, analysis), `README.md`, and `ARK_444_preregistration.md`. Hashes are auto-filled at commit time.

---

## AMENDMENT v1.1 — Control-flow correction (2026-07-16, before any result)

**Status of v1.0 principal job:** ERRORED, **zero counts produced.**

**What happened.** The v1.0 integrity gate was implemented as a **nested** conditional
(`if ca==1: if ce==1: X(Q_P)`). On submission to `ibm_marrakesh`, the principal job
(**`d9cmdvsjeosc73fgfk5g`**, submitted 2026-07-16, committed at LOCK-child commit
`e523654`) failed to execute with **IBM error code 1524 — "Some Dynamic Circuit features
are not supported (classical feedforward and control flow)."** IBM Qiskit Runtime does
**not** support nested `if_test` conditionals. The job returned **no measurement data.**

**Correction.** The integrity gate is flattened to a **single** `if_test` on one 2-bit
integrity register `ci` (`ci[0]`=approval, `ci[1]`=fresh execution-verify), firing the
payload iff `ci == 0b11` (both bits set). This is exactly the **single-register
feedforward pattern proven to run in ARK-442** on the same backend. Mid-circuit `reset`
is retained (top-level only, never inside a conditional — a supported primitive). The
**measurable semantics are identical**: the payload fires iff the approval AND the fresh
execution-time verification are both 1; every alteration/replay arm still fails closed by
driving the execution-verify bit to 0. Register `cp` (payload readout, PRIMARY endpoint)
is unchanged. Verified by real-backend transpilation: exactly 1 non-nested `if_else` and 1
top-level `reset` per arm.

**Scientific-integrity statement.** Because the v1.0 job produced **zero data**, this is a
**pre-data technical correction**, not a post-hoc rescue of an unfavorable result. "No
Rescue After Failure" governs re-running to escape a measured FAIL; here there was no
measurement to rescue. No metric, ceiling, arm definition, qubit selection (Q_A=5, Q_P=6),
shot count, or decision rule (Fields 17/20–22) is changed by this amendment. The errored
job ID above is retained permanently in the record. The re-locked circuit generator
(`ark_444_circuits.py` v1.1) and a refreshed `MANIFEST.txt` are committed **before** the
corrected principal job is submitted. The corrected run is tagged `ark-444-v1.0` (first
run to yield data); this amendment and the errored job ID document the full provenance.

---

*ARK-444 Preregistration — Remnant Fieldworks Inc. / Derek Hone — 2026-07-16. No hardware job is submitted until this document and its manifest are committed. This is a metrological characterization of a tamper-evident decision-to-execution binding, not new physics and not a cryptographic integrity guarantee. No Rescue After Failure.*
