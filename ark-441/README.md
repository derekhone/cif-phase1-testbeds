# ARK-441 — SPAM-Resolved Authorization Boundary Characterization

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21398676.svg)](https://doi.org/10.5281/zenodo.21398676)

**Remnant Fieldworks Inc. — Derek Hone**
**Backend:** IBM Quantum `ibm_kingston` (Heron r2) · **Qubits:** Q_A=5, Q_P=6 · **Instance:** open-instance
**Governing principle:** *Proof Before Power. Prediction Before Measurement. No Rescue After Failure.*

---

## Scope

ARK-441 characterizes a verify-then-execute authorization boundary on IBM Heron hardware:
a payload gate (X on Q_P) fires **only** when a mid-circuit measurement of an authorization
qubit (Q_A) reads 1. The experiment measures how much the payload *leaks* when authorization
is denied (DENY-leakage `L_D`), how faithfully it fires when allowed (`S_A`), and — critically —
how much of any leakage is just **SPAM (state-preparation-and-measurement) readout error**
rather than a real boundary-mechanism failure.

## Preregistration statement

This is a **preregistered** experiment. The full 28-field preregistration
(`ARK_441_preregistration.md`) and all code were committed to GitHub with SHA-256 hashes
(`MANIFEST.txt`) **before any IBM Quantum job was submitted**. The preregistration commit hash
is the lock and is recorded in `RUN_LOG.md`. Hypotheses, qubit pair, shot count, metrics, and
pass/fail/kill windows were fixed in advance and were not altered after any result was observed.

## Relationship to VBE-1

VBE-1 (ibm_kingston, job `d9ajf3eg26ic73deq3l0`, 2026-07-13) **failed its kill condition**:
DENY-leakage `L_D=12.62%` was statistically indistinguishable from a 13.50% idle baseline —
i.e. SPAM-dominated, not a boundary result. ARK-441 corrects this with:
1. **Calibration-based qubit selection** — both qubits `readout_error < 2%` (Q5=0.50%, Q6=0.67%);
2. **In-situ SPAM job run and committed first**, gating the principal job;
3. **A SPAM-corrected primary metric** (`L_D_corrected = L_D − SPAM_baseline`) plus an explicit
   `L_D`-vs-`SPAM` distinguishability test (non-overlapping 99% Wilson intervals).
Adversarial arms (stale, replayed, superposition authorization) extend beyond VBE-1.

## Metrics

```
L_D            = P(Q_P=1 | Arm 2 DENY)          # primary leakage
S_A            = P(Q_P=1 | Arm 1 ALLOW)         # allow fidelity
SPAM_baseline  = P(Q_P=1 | Arm 4 idle)          # idle readout error
L_control      = P(Q_P=1 | Arm 3 ungated)       # ungated control
Δ_B            = S_A − L_D                       # boundary discrimination
L_D_corrected  = L_D − SPAM_baseline            # mechanism-only leakage
I_L            = (L_control − L_D) / L_control   # relative improvement vs ungated
```

**PASS:** `L_D_corrected ≤ 0.02` AND `Δ_B ≥ 0.70` AND in-situ `SPAM_baseline ≤ 0.02` AND `L_D`
distinguishable from `SPAM_baseline`. **FAIL:** boundary misses either window with SPAM in range.
**KILL/INDETERMINATE:** in-situ `SPAM_baseline > 0.02` on either qubit, or `L_D`≈`SPAM` (VBE-1 mode).

## Files

| File | Purpose |
|------|---------|
| `ARK_441_preregistration.md` | 28-field preregistration (the lock) |
| `ark_441_circuits.py` | 8 arms as Qiskit dynamic circuits (Heron basis, mid-circuit measure + feedforward) |
| `ark_441_spam_job.py` | In-situ SPAM estimation job (runs FIRST) → `spam_results.json` |
| `ark_441_submit_ibm.py` | SPAM-gated principal 8-arm submission → `RUN_LOG.md`, `principal_job_meta.json` |
| `ark_441_retrieve.py` | Retrieve raw counts → `raw_results.json` |
| `ark_441_analysis.py` | Metrics + Wilson CIs + PASS/FAIL/KILL + plots → `proofrecord.json` |
| `requirements.txt` | Pinned dependency versions |
| `MANIFEST.txt` | SHA-256 of all files |
| `calibration_snapshot_20260716.json` | Backend calibration used for qubit selection |
| `RUN_LOG.md` | Preregistration commit hash + job IDs + timestamps |
| `ARK_441_results.md` | Honest per-criterion scoring after results |

## How to reproduce

```bash
pip install -r requirements.txt
export ...  # IBM Quantum token via QiskitRuntimeService (channel=ibm_quantum_platform, instance=open-instance)

# 1) SPAM job first (must pass SPAM_baseline <= 0.02 on both Q5 and Q6)
python ark_441_spam_job.py
# 2) Principal job (aborts unless the SPAM gate passed)
python ark_441_submit_ibm.py
# 3) Retrieve raw counts
python ark_441_retrieve.py
# 4) Analyze + score + plots
python ark_441_analysis.py
```

The token in this run is read from `/home/ubuntu/.config/abacusai_auth_secrets.json`
(`['ibm quantum']['secrets']['api_token']['value']`). Substitute your own credentials to reproduce.
