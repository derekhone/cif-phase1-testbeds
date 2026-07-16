# ARK-444 — Decision-to-Execution Integrity

**Remnant Fieldworks Inc. — Derek Hone**
**Backend:** IBM Quantum `ibm_marrakesh` (Heron r2) · **Governing principle:** *Proof Before Power. Prediction Before Measurement. No Rescue After Failure.*

ARK-444 is a preregistered test of whether **the action that executes is exactly the action that was verified**. An approval commits a signature of the approved action; at execution the action's signature is re-verified and the payload fires **only if the executed action matches the committed approval**. The central question: *can the boundary detect when an approved action is altered before execution and fail closed?* It is **not** new physics and **not** a cryptographic integrity guarantee — the "action signature" is a single committed bit realized in a two-phase (approve → re-verify) dynamic circuit, and results apply only to this qubit pair, backend, and calibration.

**Eight arms:** approved action executed unchanged (reference); destination changed after approval; amount/parameter changed; operation type changed; extra action appended after verification; original approval replayed; mutated payload re-verified before execution (recovery); and an idle SPAM baseline. The payload is bound to a fresh execution-time verification `ce` (not the stale approval `ca`), so any post-approval alteration drives a commitment mismatch and withholds the payload (fail closed), while a re-verified action re-establishes the match and executes.

**Locked thresholds (from ARK-441/442):** every altered/replayed arm must satisfy `L_corrected ≤ 0.02`; reverification must satisfy `S_reverified ≥ 0.90`; boundary discrimination `Δ_B` (unchanged vs worst-case altered arm) must satisfy `Δ_B ≥ 0.70`; in-situ `SPAM_baseline ≤ 0.02` on both qubits (else KILL/INDETERMINATE).

**Preregistration integrity:** the full preregistration (`ARK_444_preregistration.md`) and all code are committed with SHA-256 hashes (`MANIFEST.txt`) **before any job submission**; the preregistration commit hash is the lock, recorded in `RUN_LOG.md`. Execution order: freeze qubits → in-situ SPAM gate → submit principal job (record job ID before reading) → retrieve raw counts → analysis → tag `ark-444-v1.0`.

Extends ARK-441 (authorization boundary), ARK-446 (cross-device replication), and ARK-442 (delay / expiry / replay / reverification) from *whether an authorization is valid* to *whether the executed action is exactly the approved action*.
