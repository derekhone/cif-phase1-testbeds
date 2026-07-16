# ARK-444 — RUN LOG
Remnant Fieldworks Inc. — Derek Hone

Decision-to-Execution Integrity on ibm_marrakesh (Heron r2).

## Principal 8-arm job
- **Backend:** ibm_marrakesh
- **Instance:** open-instance
- **Physical qubits (Q_A, Q_P):** [5, 6]
- **Shots per arm:** 8192
- **Arms:** 8 (arm1_approved_unchanged, arm2_destination_changed, arm3_amount_changed, arm4_operation_changed, arm5_extra_action_appended, arm6_approval_replayed, arm7_mutated_then_reverified, arm8_idle_spam)
- **Arm classes:** {'arm1_approved_unchanged': 'match_reference', 'arm2_destination_changed': 'alteration_destination', 'arm3_amount_changed': 'alteration_amount', 'arm4_operation_changed': 'alteration_optype', 'arm5_extra_action_appended': 'alteration_append', 'arm6_approval_replayed': 'replay', 'arm7_mutated_then_reverified': 'reverified_recovery', 'arm8_idle_spam': 'idle_spam'}
- **Optimization level:** 1 (no dynamical decoupling)
- **JOB ID:** `d9cmdvsjeosc73fgfk5g`
- **Submission timestamp (UTC):** 2026-07-16T23:19:25.786069+00:00
- **SPAM job id:** `d9cmadkinv1c73anvn90`
- **SPAM baselines:** Q_A=0.0024, Q_P=0.0000
- **Transpiled depths:** {'arm1_approved_unchanged': 7, 'arm2_destination_changed': 6, 'arm3_amount_changed': 6, 'arm4_operation_changed': 6, 'arm5_extra_action_appended': 8, 'arm6_approval_replayed': 6, 'arm7_mutated_then_reverified': 7, 'arm8_idle_spam': 1}
