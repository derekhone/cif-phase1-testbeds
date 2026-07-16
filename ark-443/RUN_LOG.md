# ARK-443 — RUN LOG

Remnant Fieldworks Inc. — Derek Hone
Two-of-Three (M-of-N) Quorum Authorization on ibm_marrakesh (Heron r2).
Governing principle: Proof Before Power. Prediction Before Measurement. No Rescue After Failure.

## Preregistration LOCK
- **LOCK commit hash:** `d26679981fd5b3b67ea3c1b68813b04f146d8451`
- **Locked artifacts:** ARK_443_preregistration.md, README.md, MANIFEST.txt, and all six code files, committed BEFORE any IBM Quantum job (Field 27).
- **Pre-lock verification (no hardware):** 8 arms build; ideal aer simulation exact (all 4 DENY arms P(Q_P=1)=0, all 3 ALLOW arms =1, SPAM idle=0); all 8 arms transpile on ibm_marrakesh (4 sequential if_test -> 4 if_else, no error 1524; arm7 top-level reset OK).

## Step 1 — Qubit selection (frozen)
- **Rule:** 4 lowest-RE qubits with RE < 0.020, NO connectivity constraint (classical feedforward, no 2q gates); lowest-RE -> Q_P; remaining three by ascending physical index -> Q_A1,Q_A2,Q_A3.
- **Selected:** Q_P=14 (RE=0.1709%), Q_A1=34 (RE=0.3052%), Q_A2=54 (RE=0.1831%), Q_A3=140 (RE=0.3052%).
- **initial_layout:** [14, 34, 54, 140]  ·  max_RE=0.3052%  ·  qualifying qubits=112/156.
- **Frozen in:** selected_qubits.json, calibration_snapshot_marrakesh_20260716.json.
