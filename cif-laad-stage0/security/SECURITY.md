# CIF-LAAD Security Harness

Threat model of the FUSION LAYER ITSELF - not offensive counter-UAS. Every case feeds hostile or degraded input to a live `FusionEngine` and checks it fails visibly and preserves uncertainty. Reproduce:

```
python -m security.harness
```

**Result: 17/17 cases passed.**

| Case | Threat class | Expected defensive behaviour | Observed | Pass |
|---|---|---|---|---|
| stale_observation | stale | reject E_TS_STALE + emit OBS_REJECTED, no track | `{"rejected": ["E_TS_STALE"], "events": ["OBS_REJECTED"]}` | PASS |
| future_timestamp | malformed-time | reject E_TS_FUTURE, no track | `{"rejected": ["E_TS_FUTURE"]}` | PASS |
| nan_position | malformed | reject E_POS, no track | `{"rejected": ["E_POS"]}` | PASS |
| non_positive_definite_cov | malformed | reject E_COV_PD, no track | `{"rejected": ["E_COV_PD"]}` | PASS |
| asymmetric_cov | malformed | reject E_COV_SYM, no track | `{"rejected": ["E_COV_SYM"]}` | PASS |
| unknown_sensor_type | malformed | reject E_SENSOR_TYPE, no track | `{"rejected": ["E_SENSOR_TYPE"]}` | PASS |
| empty_sensor_id | malformed | reject E_SENSOR_ID | `{"rejected": ["E_SENSOR_ID"]}` | PASS |
| rfid_on_non_rf_sensor | impersonation | reject E_RFID (identity field only valid on rf) | `{"rejected": ["E_RFID"]}` | PASS |
| duplicate_replay | replay | second identical seq rejected E_REPLAY | `{"rejected": ["E_REPLAY"], "events": ["OBS_REPLAY_REJECTED"]}` | PASS |
| out_of_order_seq | replay | lower seq than last seen rejected E_REPLAY | `{"rejected": ["E_REPLAY"]}` | PASS |
| position_spoof_no_hijack | spoof | distant spoof cannot capture an existing track id | `{"real_id": 1, "real_track_xy_norm": 22.540860481189036}` | PASS |
| conflicting_identity | conflicting-identity | record contradiction + cap confidence below HIGH | `{"contradiction_kinds": ["identity"], "recent_confidence": ["LOW", "LOW", "LOW"]}` | PASS |
| sensor_outage_no_false_confidence | outage | on total outage track coasts/degrades, no fresh HIGH | `{"last_reported_confidence": "MEDIUM", "status": "CONFIRMED"}` | PASS |
| partial_network_low_diversity | partial-network | single-modality coherence stays below full-diversity ceiling | `{"max_coherence": 0.574}` | PASS |
| corrupted_evidence_detected | corrupted-evidence | verify() True before mutation, False after | `{"verify_before": true, "verify_after": false}` | PASS |
| evidence_reorder_detected | corrupted-evidence | reordered chain fails verification | `{"records": 6}` | PASS |
| mixed_batch_partial_reject | robustness | malformed member rejected every cycle; valid ones still track | `{"cycles_with_rejection": 5, "confirmed_served": true}` | PASS |

## Declared limitations (honest scope)

- **position_spoof_no_hijack**: LIMITATION: a spoof INSIDE the gate with a valid seq is kinematically indistinguishable; detecting it needs sensor authentication (out of scope).

## What this harness does NOT cover

- No sensor-level authentication / PKI: an on-network attacker who forges a valid sequence and plausible kinematics cannot be distinguished by fusion alone. This requires signed sensor feeds and is out of scope for a software fusion prototype.
- Tamper-EVIDENT, not tamper-PROOF: a fully trusted writer can forge a fresh consistent chain. Non-repudiation needs external signatures / trusted timestamps (API stub only).
- No encryption-in-transit, no key management, no supply-chain attestation. These belong to the deployment platform, not this prototype.
