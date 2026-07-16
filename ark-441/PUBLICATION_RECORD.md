# ARK-441 — Publication Record

**Experiment:** ARK-441 — SPAM-Resolved Authorization Boundary Characterization (Candidate A)
**Owner:** Remnant Fieldworks Inc. — Derek Hone (`derekhone`)
**Verdict:** **PASS**
**Publication date:** 2026-07-16 (UTC)
**Governing principle:** *Proof Before Power. Prediction Before Measurement. No Rescue After Failure.*

---

## 1. Zenodo (production) — published dataset
- **DOI:** `10.5281/zenodo.21398676`
- **DOI URL:** https://doi.org/10.5281/zenodo.21398676
- **Record:** https://zenodo.org/record/21398676
- **Deposition ID:** 21398676
- **Upload type:** dataset
- **State:** published (`submitted: true`)
- **Title:** ARK-441: SPAM-resolved quantum hardware characterization of a verify-then-execute (VBE) authorization boundary — PASS verdict
- **Related identifier:** isSupplementTo `10.5281/zenodo.21246246` (UIP Phase 1) — citation lineage only; ARK-441 is an independent supplemental experiment.

## 2. GitHub
- **Repository:** https://github.com/derekhone/uip-phase1-testbeds
- **Experiment folder (on `main`):** https://github.com/derekhone/uip-phase1-testbeds/tree/main/ark-441
- **PR #1 (merged):** https://github.com/derekhone/uip-phase1-testbeds/pull/1
  - Merge commit: `d038aa089daceccfcb4657c83f4800663ba896ef`
  - Merge method: merge commit (preserves full preregistration history)
- **Release:** https://github.com/derekhone/uip-phase1-testbeds/releases/tag/ark-441-v1.0
  - Tag: `ark-441-v1.0` (annotated tag at verified analysis commit `65cc524`)
  - Release id: 355192877
  - Title: ARK-441 v1.0 — PASS: SPAM-resolved VBE authorization boundary characterization
- **DOI badge added to README:** commit on `main` — see `ark-441/README.md`

## 3. Provenance (proof-before-power chain)
- **Preregistration LOCK commit:** `fd1c7fad7c290ee04fc564575f9d7bc12000c3b7` (committed before any quantum job)
- **Commit chain:** `fd1c7fa` (prereg lock) → `341b66d` (independence notice) → `cb947cf` (SPAM results) → `58641f0` (principal job ID, before reading results) → `8a5d260` (raw results) → `65cc524` (analysis + proofrecord + plots) → `d038aa0` (merge to main)

## 4. IBM Quantum jobs
- **In-situ SPAM job (kill gate):** `d9c7lf7ngvls73a941jg` — Q5 readout error 0.29%, Q6 0.15% (both ≤ 2% → gate passed)
- **Principal job:** `d9c8ij41osis73bjhldg` — 8 arms × 8192 shots
- **Hardware:** `ibm_kingston` (Heron r2), qubits Q_A=5, Q_P=6, open-instance

## 5. Key results (raw counts, no readout mitigation on primary endpoint)
| Metric | Value | Threshold | Status |
|---|---|---|---|
| L_D (raw DENY-leakage) | 0.33% | ≤ 2% | PASS |
| L_D_corrected (SPAM-corrected) | 0.21% (upper-95 ≈ 0.41%) | ≤ 2% | PASS |
| Δ_B (S_A − L_D) | 0.979 | ≥ 0.70 | PASS |
| In-situ SPAM Q5 / Q6 | 0.29% / 0.15% | ≤ 2% | PASS |
| S_A (ALLOW fidelity) | 0.982 | — | — |
| I_L (leakage integrity) | 0.9967 | — | — |

Adversarial arms (no differential vulnerability): stale=0.981, replay=0.0033, superposition=0.505.

## 6. Files deposited on Zenodo (24)
ARK_441_results.md, ARK_441_preregistration.md, proofrecord.json, INDEPENDENCE_NOTICE.md, README.md,
RUN_LOG.md, MANIFEST.txt, ark_441_circuits.py, ark_441_spam_job.py, ark_441_submit_ibm.py,
ark_441_retrieve.py, ark_441_analysis.py, ark_441_finalize_proofrecord.py,
calibration_snapshot_20260716.json, requirements.txt, arm_results.png, spam_corrected_LD.png,
principal_job_id.txt, principal_job_meta.json, raw_results.json, spam_results.json,
submit.log, retrieve.log, spam_job.log.

Credentials were **never** uploaded or logged.

## 7. Independence statement
ARK-441 is a **separate, independent supplemental experiment**. It is **not** part of the UIP Phase 1/2
program. See `INDEPENDENCE_NOTICE.md`.
