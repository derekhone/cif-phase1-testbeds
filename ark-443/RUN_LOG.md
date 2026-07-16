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

## Step 2 — In-situ SPAM gate (RUNS FIRST)
- **SPAM job id:** `d9cmvdkinv1c73ao0g00`  ·  8 circuits x 2048 shots.
- **Baselines (p01):** Q_P=0.0015, Q_A1=0.0005, Q_A2=0.0000, Q_A3=0.0005 — ALL <= 0.02 => GATE PASSED.

## Step 3 — Principal 8-arm job
- **Backend:** ibm_marrakesh
- **Instance:** open-instance
- **Physical qubits [Q_P, Q_A1, Q_A2, Q_A3]:** [14, 34, 54, 140]
- **Shots per arm:** 8192
- **Arms:** 8 (arm1_0of3_deny, arm2_1of3_deny, arm3_2of3_allow, arm4_3of3_allow, arm5_1of3_altchannel_deny, arm6_degraded_quorum_allow, arm7_replay_tamper_deny, arm8_idle_spam)
- **Arm expectations:** {'arm1_0of3_deny': 'DENY', 'arm2_1of3_deny': 'DENY', 'arm3_2of3_allow': 'ALLOW', 'arm4_3of3_allow': 'ALLOW', 'arm5_1of3_altchannel_deny': 'DENY', 'arm6_degraded_quorum_allow': 'ALLOW', 'arm7_replay_tamper_deny': 'DENY', 'arm8_idle_spam': 'SPAM'}
- **Arm classes:** {'arm1_0of3_deny': 'deny_0of3', 'arm2_1of3_deny': 'deny_1of3', 'arm3_2of3_allow': 'allow_2of3', 'arm4_3of3_allow': 'allow_3of3', 'arm5_1of3_altchannel_deny': 'deny_1of3_alt', 'arm6_degraded_quorum_allow': 'allow_degraded', 'arm7_replay_tamper_deny': 'deny_replay', 'arm8_idle_spam': 'idle_spam'}
- **Optimization level:** 1 (no dynamical decoupling)
- **JOB ID:** `d9cn04kjeosc73fgg8cg`
- **Submission timestamp (UTC):** 2026-07-16T23:58:08.546645+00:00
- **SPAM job id:** `d9cmvdkinv1c73ao0g00`
- **SPAM baselines:** Q_P=0.0015, Q_A1=0.0005, Q_A2=0.0000, Q_A3=0.0005
- **Transpiled depths:** {'arm1_0of3_deny': 6, 'arm2_1of3_deny': 7, 'arm3_2of3_allow': 7, 'arm4_3of3_allow': 7, 'arm5_1of3_altchannel_deny': 7, 'arm6_degraded_quorum_allow': 9, 'arm7_replay_tamper_deny': 6, 'arm8_idle_spam': 1}
