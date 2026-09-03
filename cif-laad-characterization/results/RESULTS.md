# CIF-LAAD Validation Series - Complete Results

Simulation-only. TRL 3. RESEARCH ONLY. Not a security proof or a fielded system.

One coherent preregistered series, eight experimental units (EXP-1..EXP-8). Seeds are replications within a unit, not separate experiments; this series does not increase the public experiment count.

Engine frozen at combined SHA-256 8712f1138bdd20090b9a1b6eda58cebc5c274a843b960d6784e8650b7ea7ad45 (14 files). numpy 2.2.6, python 3.11.6. Held-out seeds start at 100, disjoint from the published seeds 0-24. Nothing was retuned to win; the falsified coherence-gate mode is kept in the record.

## EXP-1 - Accuracy / continuity frontier

Full per-mode tables in EXP1_RESULTS.md. Envelope verdict (default mode M_batch vs frozen baseline):

- WIN: id-switch suppression and false-track suppression under clutter and many targets (heavy_clutter id 5.07 -> 0.57, false 61.1 -> 14.6; many_targets id 14.6 -> 5.3, false 89.9 -> 28.4); continuity through sensor dropout (0.30 -> 1.00, reacq 4.0s -> none).
- LIABILITY: localization RMSE in clutter / many targets (~6m -> ~23m) and a modest RMSE cost in crossing and dropout.
- NEUTRAL: clean_single and identity_conflict (CIF identical to baseline; no cost, no measurable win).

## EXP-2 - Dropout-duration stress (bounds the dropout win)

All sensors blind for a fixed window; how long can CIF coast before continuity breaks?

| dropout | CIF RMSE m | CIF dropout-cont | CIF reacq s | baseline dropout-cont | baseline reacq s |
|---|---|---|---|---|---|
| 0.5s | 6.24 | 1.00 |   -   | 1.00 |   -   |
| 1s | 6.42 | 1.00 |   -   | 1.00 |   -   |
| 2s | 7.47 | 1.00 |   -   | 0.75 | 1.01 |
| 3s | 7.73 | 1.00 |   -   | 0.50 | 2.01 |
| 5s | 9.37 | 1.00 |   -   | 0.30 | 4.01 |
| 10s | 11.55 | 0.60 | 4.50 | 0.15 | 9.01 |
| 15s | 12.19 | 0.40 | 9.50 | 0.10 | 14.01 |

Envelope bound: CIF holds full continuity (1.00) through ~5s blind gaps while the baseline decays to 0.30; beyond ~10s CIF continuity itself degrades (0.60 at 10s, 0.40 at 15s). The honest claim is bounded: continuity advantage through multi-second dropout, not indefinite coasting.

## EXP-3 - Sensor-degradation matrix

K sensors simultaneously degraded (x4 position sigma + Pd 0.4 + a mid-run dropout).

| K degraded | CIF RMSE | CIF cont | CIF id sw | base RMSE | base cont | base id sw |
|---|---|---|---|---|---|---|
| K=0 | 6.19 | 0.99 | 2.60 | 6.19 | 0.99 | 2.60 |
| K=1 | 10.47 | 0.99 | 0.67 | 10.46 | 0.99 | 0.73 |
| K=2 | 25.39 | 0.98 | 0.93 | 25.52 | 0.98 | 1.07 |
| K=3 | 32.77 | 0.97 | 0.30 | 30.59 | 0.85 | 1.30 |

Envelope bound: at light degradation (K<=2) CIF and baseline are indistinguishable. The continuity/identity advantage only appears at heavy degradation (K=3: continuity 0.97 vs 0.85, id switches 0.30 vs 1.30), and even there CIF pays a small RMSE cost (32.8 vs 30.6).

## EXP-4 - Dense-crossing identity challenge

Crossing lanes with modest clutter; sweep target count N.

| N targets | CIF RMSE | CIF id sw | CIF false | base RMSE | base id sw | base false |
|---|---|---|---|---|---|---|
| N=2 | 11.84 | 1.30 | 13.4 | 6.23 | 4.07 | 28.8 |
| N=4 | 18.08 | 3.20 | 17.6 | 6.26 | 9.40 | 56.8 |
| N=8 | 30.24 | 34.57 | 90.9 | 6.39 | 21.77 | 125.1 |
| N=16 | 37.11 | 101.33 | 181.6 | 6.71 | 43.97 | 228.9 |
| N=32 | 37.57 | 194.63 | 305.6 | 7.81 | 108.73 | 540.4 |

Envelope bound (important, honest): CIF suppresses false tracks at every density, but its id-switch advantage holds only at low density (N<=4: 1.3 vs 4.1, 3.2 vs 9.4). At N>=8 the id-switch count inverts - CIF has MORE id switches than the baseline (N=32: 195 vs 109) while still holding fewer false tracks (306 vs 540). The identity-stability claim is therefore bounded to modest target counts; it does not scale to dozens of simultaneous crossers.

## EXP-5 - False-observation resilience

Part A - typed-reject unit check: all_correct = True. Each malformed / stale / future / replay / bad-field observation was rejected with the correct typed error code:

| case | expected code | rejected as expected |
|---|---|---|
| malformed_nan_pos | E_POS | True |
| malformed_cov_not_pd | E_COV_PD | True |
| stale_ts | E_TS_STALE | True |
| future_ts | E_TS_FUTURE | True |
| bad_class_conf | E_CLASS_CONF | True |
| rfid_on_non_rf | E_RFID | True |
| unknown_sensor_type | E_SENSOR_TYPE | True |
| replay_seq | E_REPLAY | True |

Part B - in-scenario spoof (schema-VALID false observations at plausible positions):

| metric | control (no spoof) | spoofed |
|---|---|---|
| continuity | 0.99 | 0.99 |
| RMSE m | 6.26 | 9.70 |
| false-track frames | 14.67 | 78.27 |
| confirmed tracks | 1.40 | 1.07 |
| rejected obs | - | 64.40 |

Honest limitation (reported, not hidden): the frozen defences reject malformed, stale, future, and replayed observations by construction, but a lone schema-valid spoof at a plausible position is NOT rejected by validation/lineage alone - it inflates false-track frames (14.7 -> 78.3). The legitimate track still survives (continuity unchanged). CIF-LAAD is an assurance/provenance layer, not a spoof-authentication layer; sensor-level authentication is out of scope.

## EXP-6 - Evidence / provenance tamper challenge

Real hash-linked evidence chain of length 83; pristine verify = True. Four tamper operations applied to copies:

| tamper op | verify after | detected |
|---|---|---|
| mutate_payload | False | True |
| reorder_records | False | True |
| delete_record | False | True |
| substitute_record | False | True |

All tampers detected = True. HONEST LABEL: tamper-EVIDENT, not tamper-proof. A fully trusted writer can forge a fresh internally-consistent chain; this detects mutation of a persisted or transmitted log, not authorship fraud.

## EXP-7 - Benchmark matrix (comparator honesty)

The comparator throughout this series is the frozen in-tree single-hypothesis BaselineTracker (a nearest-neighbour Kalman tracker). No certified third-party tracking library (e.g. Stone-Soup, a SORT/DeepSORT config) was run in this series. That is a real gap: the wins reported here are relative to a reasonable in-house baseline, not to a published state-of-the-art system.

**PRECONDITION (BLOCKING):** Running a Stone-Soup GNN/JPDA configuration and a SORT baseline on the identical frozen scenarios, seeds, and metrics is the explicit precondition before any comparative-performance language ("better than," "outperforms," "state-of-the-art") may appear in any public surface. Until that benchmark runs, all claims use the framing "relative to the in-house single-hypothesis tracker" only.

## EXP-8 - Scale test (throughput envelope)

Pure-Python single-thread, CIF engine only, real-time budget 50.0 ms/cycle.

| N targets | mean cycle ms | worst-seed mean ms | peak mem MB | meets 50ms real-time |
|---|---|---|---|---|
| N=1 | 3.64 | 4.15 | 0.06 | True |
| N=10 | 14.39 | 15.29 | 0.19 | True |
| N=50 | 44.12 | 49.44 | 0.47 | True |
| N=100 | 71.89 | 76.15 | 0.73 | False |
| N=500 | 236.90 | 247.31 | 2.57 | False |
| N=1000 | 435.39 | 450.80 | 4.81 | False |

Envelope bound: the pure-Python engine meets a 50 ms/cycle real-time budget up to ~50 tracks (44 ms); at 100 tracks it is 72 ms (over budget) and grows roughly linearly to 435 ms at 1000. Real-time claims are bounded to <=50 tracks in this implementation; larger scales are a compiled-implementation future-work item, not a current claim.

## Series synthesis - the defensible operating envelope

Judged by the preregistered success/kill test (is there a defensible envelope where CIF-LAAD buys measurable continuity/identity/evidence advantage without an unacceptable localization-accuracy cost?), the answer is a qualified YES, with sharp boundaries:

- EARNED (survived): (1) continuity through multi-second sensor dropout, bounded to ~5s full / degrading past ~10s (EXP-1, EXP-2); (2) false-track suppression under clutter and dense crossing, at every density tested (EXP-1, EXP-4); (3) id-switch suppression, bounded to clutter and LOW target density N<=4 (EXP-1, EXP-4) and to heavy sensor degradation K=3 (EXP-3); (4) tamper-EVIDENT provenance (EXP-6); (5) typed rejection of malformed/stale/future/replayed observations (EXP-5).
- COST (always reported alongside): localization RMSE penalty of roughly 1.3x-4x versus the baseline whenever the environment is contested; the penalty is structural, not a tuning bug.
- KILLED / NARROWED: the coherence-gate inheritance mode stays falsified on held-out seeds; the id-stability advantage does NOT scale past a handful of simultaneous crossers (inverts at N>=8); no advantage at all in clean single-target or the identity_conflict scenario; real-time only to ~50 tracks; a lone plausible spoof is not rejected; no certified third-party benchmark was run.

Headline earned by this evidence: CIF-LAAD - a sensor-agnostic low-altitude assurance layer for maintaining track continuity, false-track suppression, uncertainty and evidence provenance when observations degrade or conflict - explicitly trading localization precision for continuity, provenance and clutter resilience inside a bounded degraded/contested envelope. Track-identity stability (id-switch suppression) is a bounded secondary benefit at low target density (N<=4) and heavy sensor degradation, not a primary claim.

PRECONDITION FOR COMPARATIVE CLAIMS: no certified third-party tracking library (Stone-Soup GNN/JPDA, SORT/DeepSORT) was run on the identical frozen scenarios in this series. All wins stated above are relative to the frozen in-tree single-hypothesis BaselineTracker only. Comparative-performance language ("better than," "state-of-the-art," "outperforms") is BLOCKED until a Stone-Soup or equivalent configuration runs on the same scenarios, seeds, and metrics. This is the top future-work item.

