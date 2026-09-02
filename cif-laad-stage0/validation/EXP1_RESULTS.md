# EXP-1 - Accuracy / Continuity Frontier (frozen results)

- Series: CIF-LAAD preregistered validation series (simulation-only, TRL 3, RESEARCH ONLY)
- Experimental unit: EXP-1. Held-out seeds 100-129 (n=30), disjoint from the published seeds 0-24.
- numpy 2.2.6, python 3.11.6, wallclock 939.12 s
- 7 preregistered operating modes x 6 frozen scenarios x 30 seeds. Nothing retuned to win; the falsified coherence-gate mode (M_gated) is kept for honesty.

## Baseline (frozen single-hypothesis tracker), per scenario

| scenario | RMSE m | continuity | id switches | false-track frames | reacq s |
|---|---|---|---|---|---|
| clean_single | 6.19 | 0.99 | 2.60 | 10.8 |   -   |
| crossing_two | 6.24 | 0.99 | 3.47 | 16.2 |   -   |
| sensor_dropout | 6.99 | 0.89 | 3.20 | 8.3 | 4.00 |
| heavy_clutter | 6.24 | 0.99 | 5.07 | 61.1 |   -   |
| identity_conflict | 6.18 | 0.99 | 2.30 | 11.8 |   -   |
| many_targets_6 | 6.23 | 0.99 | 14.63 | 89.9 | 1.00 |

## CIF - mode M_legacy

| scenario | RMSE m | continuity | dropout-cont | id switches | false-track frames | reacq s |
|---|---|---|---|---|---|---|
| clean_single | 6.19 | 0.99 |   -   | 2.60 | 10.8 |   -   |
| crossing_two | 8.06 | 0.99 |   -   | 2.73 | 11.9 |   -   |
| sensor_dropout | 9.29 | 0.99 | 1.00 | 2.00 | 8.0 |   -   |
| heavy_clutter | 25.45 | 0.80 |   -   | 3.10 | 90.6 | 1.74 |
| identity_conflict | 6.19 | 0.99 |   -   | 2.30 | 11.8 |   -   |
| many_targets_6 | 24.50 | 0.89 |   -   | 6.97 | 84.0 | 1.59 |

## CIF - mode M_batch

| scenario | RMSE m | continuity | dropout-cont | id switches | false-track frames | reacq s |
|---|---|---|---|---|---|---|
| clean_single | 6.19 | 0.99 |   -   | 2.60 | 10.8 |   -   |
| crossing_two | 8.06 | 0.99 |   -   | 2.73 | 11.9 |   -   |
| sensor_dropout | 9.39 | 0.99 | 1.00 | 2.03 | 8.1 |   -   |
| heavy_clutter | 23.04 | 0.91 |   -   | 0.57 | 14.6 | 1.75 |
| identity_conflict | 6.19 | 0.99 |   -   | 2.30 | 11.8 |   -   |
| many_targets_6 | 23.49 | 0.92 |   -   | 5.33 | 28.4 | 2.12 |

## CIF - mode M_gated

| scenario | RMSE m | continuity | dropout-cont | id switches | false-track frames | reacq s |
|---|---|---|---|---|---|---|
| clean_single | 6.19 | 0.99 |   -   | 2.60 | 10.8 |   -   |
| crossing_two | 8.07 | 0.99 |   -   | 2.77 | 12.1 |   -   |
| sensor_dropout | 9.38 | 0.99 | 1.00 | 2.10 | 8.1 |   -   |
| heavy_clutter | 31.97 | 0.83 |   -   | 6.10 | 52.4 | 1.91 |
| identity_conflict | 6.19 | 0.99 |   -   | 2.30 | 11.8 |   -   |
| many_targets_6 | 28.79 | 0.87 |   -   | 16.10 | 95.8 | 2.34 |

## CIF - mode M_batch_short

| scenario | RMSE m | continuity | dropout-cont | id switches | false-track frames | reacq s |
|---|---|---|---|---|---|---|
| clean_single | 6.19 | 0.99 |   -   | 2.60 | 10.8 |   -   |
| crossing_two | 8.06 | 0.99 |   -   | 2.73 | 11.7 |   -   |
| sensor_dropout | 8.12 | 0.95 | 0.80 | 3.20 | 8.5 | 1.50 |
| heavy_clutter | 22.84 | 0.90 |   -   | 1.30 | 5.0 | 2.50 |
| identity_conflict | 6.19 | 0.99 |   -   | 2.30 | 11.8 |   -   |
| many_targets_6 | 23.51 | 0.90 |   -   | 7.50 | 16.5 | 2.37 |

## CIF - mode M_batch_long

| scenario | RMSE m | continuity | dropout-cont | id switches | false-track frames | reacq s |
|---|---|---|---|---|---|---|
| clean_single | 6.19 | 0.99 |   -   | 2.60 | 10.8 |   -   |
| crossing_two | 8.06 | 0.99 |   -   | 2.73 | 12.3 |   -   |
| sensor_dropout | 9.39 | 0.99 | 1.00 | 2.03 | 8.3 |   -   |
| heavy_clutter | 23.04 | 0.91 |   -   | 0.57 | 21.7 | 1.75 |
| identity_conflict | 6.19 | 0.99 |   -   | 2.30 | 11.8 |   -   |
| many_targets_6 | 23.52 | 0.92 |   -   | 5.43 | 55.9 | 1.95 |

## CIF - mode M_batch_patient

| scenario | RMSE m | continuity | dropout-cont | id switches | false-track frames | reacq s |
|---|---|---|---|---|---|---|
| clean_single | 6.19 | 0.99 |   -   | 2.60 | 10.8 |   -   |
| crossing_two | 8.08 | 0.99 |   -   | 2.83 | 11.9 |   -   |
| sensor_dropout | 16.35 | 0.99 | 1.00 | 2.00 | 7.7 |   -   |
| heavy_clutter | 21.93 | 0.93 |   -   | 0.60 | 47.8 | 1.45 |
| identity_conflict | 6.19 | 0.99 |   -   | 2.30 | 11.8 |   -   |
| many_targets_6 | 22.11 | 0.92 |   -   | 5.70 | 42.1 | 1.81 |

## CIF - mode M_batch_eager

| scenario | RMSE m | continuity | dropout-cont | id switches | false-track frames | reacq s |
|---|---|---|---|---|---|---|
| clean_single | 6.17 | 0.99 |   -   | 2.50 | 10.6 |   -   |
| crossing_two | 8.09 | 0.99 |   -   | 2.57 | 13.5 |   -   |
| sensor_dropout | 11.31 | 0.99 | 1.00 | 1.97 | 8.3 |   -   |
| heavy_clutter | 23.28 | 0.91 |   -   | 0.43 | 11.5 | 1.48 |
| identity_conflict | 6.16 | 0.99 |   -   | 2.03 | 11.1 |   -   |
| many_targets_6 | 23.63 | 0.91 |   -   | 5.93 | 39.5 | 1.91 |

## Pareto frontier across operating modes (per scenario)

Objectives minimized: RMSE, id switches, false-track frames, (1 - continuity), reacq. A mode is on the frontier if no other mode is at least as good on all five and strictly better on one.

| scenario | non-dominated modes |
|---|---|
| clean_single | M_batch_eager |
| crossing_two | M_legacy, M_batch_short, M_batch_eager |
| sensor_dropout | M_legacy, M_batch_short, M_batch_patient, M_batch_eager |
| heavy_clutter | M_batch, M_batch_short, M_batch_patient, M_batch_eager |
| identity_conflict | M_batch_eager |
| many_targets_6 | M_legacy, M_batch, M_batch_short, M_batch_long, M_batch_patient, M_batch_eager |

## Operating-envelope classification (default mode M_batch vs baseline)

WIN = CIF clearly better; LIABILITY = CIF clearly worse; NEUTRAL = within +/-15% (continuity +/-3%).

| scenario | localization RMSE | id stability | false tracks | continuity | dropout continuity |
|---|---|---|---|---|---|
| clean_single | NEUTRAL (6.19 vs 6.19) | NEUTRAL (2.60 vs 2.60) | NEUTRAL (10.77 vs 10.77) | NEUTRAL (0.99 vs 0.99) |   -   |
| crossing_two | LIABILITY (8.06 vs 6.24) | WIN (2.73 vs 3.47) | WIN (11.93 vs 16.20) | NEUTRAL (0.99 vs 0.99) |   -   |
| sensor_dropout | LIABILITY (9.39 vs 6.99) | WIN (2.03 vs 3.20) | NEUTRAL (8.07 vs 8.30) | WIN (0.99 vs 0.89) | WIN (1.00 vs 0.30) |
| heavy_clutter | LIABILITY (23.04 vs 6.24) | WIN (0.57 vs 5.07) | WIN (14.60 vs 61.13) | LIABILITY (0.91 vs 0.99) |   -   |
| identity_conflict | NEUTRAL (6.19 vs 6.18) | NEUTRAL (2.30 vs 2.30) | NEUTRAL (11.83 vs 11.83) | NEUTRAL (0.99 vs 0.99) |   -   |
| many_targets_6 | LIABILITY (23.49 vs 6.23) | WIN (5.33 vs 14.63) | WIN (28.37 vs 89.87) | LIABILITY (0.92 vs 0.99) |   -   |

