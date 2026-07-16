# ARK-442 — RUN LOG
Remnant Fieldworks Inc. — Derek Hone

Authorization Boundary Degradation Under Verification-to-Execution Delay on ibm_marrakesh (Heron r2).

## Principal 8-arm job
- **Backend:** ibm_marrakesh
- **Instance:** open-instance
- **Physical qubits (Q_A, Q_P):** [5, 6]
- **Shots per arm:** 8192
- **Arms:** 8 (arm1_allow_immediate, arm2_allow_short_delay, arm3_allow_medium_delay, arm4_allow_long_delay, arm5_expired_auth_deny, arm6_replayed_after_expiry, arm7_reverified_after_expiry, arm8_idle_spam)
- **Delay points (ns):** {'arm1_allow_immediate': 0, 'arm2_allow_short_delay': 500, 'arm3_allow_medium_delay': 1000, 'arm4_allow_long_delay': 2000}
- **Optimization level:** 1 (no dynamical decoupling)
- **JOB ID:** `d9clom4jeosc73fgeq3g`
- **Submission timestamp (UTC):** 2026-07-16T22:33:59.581456+00:00
- **SPAM job id:** `d9clmusjeosc73fgeo10`
- **SPAM baselines:** Q_A=0.0039, Q_P=0.0005
- **Transpiled depths:** {'arm1_allow_immediate': 4, 'arm2_allow_short_delay': 5, 'arm3_allow_medium_delay': 5, 'arm4_allow_long_delay': 5, 'arm5_expired_auth_deny': 2, 'arm6_replayed_after_expiry': 3, 'arm7_reverified_after_expiry': 4, 'arm8_idle_spam': 1}
