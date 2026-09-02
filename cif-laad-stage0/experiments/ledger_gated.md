# CIF-LAAD Experiment Ledger

Inheritance mode: **gated** (inherit_gate_p=0.95, inherit_min_support=2).

All values below are produced by `experiments/run_experiments.py`. They are SIMULATION-ONLY. No hardware, no real sensor data, no field trial. Reproduce with:

```
python -m experiments.run_experiments --seeds 25
```

Environment: Python 3.11.6, numpy 2.2.6, 25 seeds/scenario, wallclock 108.09s.


## Scenario: clean_single

| Metric | CIF-LAAD | Baseline |
|---|---|---|
| Position RMSE (m) [lower better] | 6.28 +/- 0.62 | 6.28 +/- 0.62 |
| ID switches [lower better] | 3.76 +/- 5.2 | 3.76 +/- 5.2 |
| Track continuity [higher better] | 0.988 +/- 0 | 0.987 +/- 0.0024 |
| Continuity during dropout [higher better] | n/a | n/a |
| False-track frames [lower better] | 14.6 +/- 18 | 14.6 +/- 18 |
| Mean reacquisition time (s) [lower better] | n/a | n/a |
| NEES mean (ideal ~3.0) | 2.59 +/- 0.3 | 2.59 +/- 0.3 |
| NEES fraction <= chi2.95 (ideal ~0.95) | 0.977 +/- 0.024 | 0.977 +/- 0.024 |
| CIF mean latency/cycle (ms) | 0.31 +/- 0.041 | - |
| Evidence chain verified | True | n/a |

## Scenario: crossing_two

| Metric | CIF-LAAD | Baseline |
|---|---|---|
| Position RMSE (m) [lower better] | 8.04 +/- 0.84 | 6.14 +/- 0.48 |
| ID switches [lower better] | 3.32 +/- 4.2 | 3.76 +/- 4.5 |
| Track continuity [higher better] | 0.983 +/- 0.0057 | 0.987 +/- 0.0012 |
| Continuity during dropout [higher better] | n/a | n/a |
| False-track frames [lower better] | 16.2 +/- 18 | 17.9 +/- 20 |
| Mean reacquisition time (s) [lower better] | n/a | n/a |
| NEES mean (ideal ~3.0) | 2.65 +/- 0.26 | 2.57 +/- 0.25 |
| NEES fraction <= chi2.95 (ideal ~0.95) | 0.973 +/- 0.018 | 0.973 +/- 0.02 |
| CIF mean latency/cycle (ms) | 0.586 +/- 0.1 | - |
| Evidence chain verified | True | n/a |

## Scenario: sensor_dropout

| Metric | CIF-LAAD | Baseline |
|---|---|---|
| Position RMSE (m) [lower better] | 9.1 +/- 1.2 | 6.91 +/- 0.61 |
| ID switches [lower better] | 2.96 +/- 4.6 | 4.04 +/- 4.4 |
| Track continuity [higher better] | 0.988 +/- 0 | 0.888 +/- 0.0033 |
| Continuity during dropout [higher better] | 1 +/- 0 | 0.3 +/- 0 |
| False-track frames [lower better] | 11.4 +/- 16 | 11.5 +/- 15 |
| Mean reacquisition time (s) [lower better] | n/a | 4.02 +/- 0.098 |
| NEES mean (ideal ~3.0) | 2.45 +/- 0.23 | 2.55 +/- 0.25 |
| NEES fraction <= chi2.95 (ideal ~0.95) | 0.982 +/- 0.018 | 0.981 +/- 0.017 |
| CIF mean latency/cycle (ms) | 0.251 +/- 0.019 | - |
| Evidence chain verified | True | n/a |

## Scenario: heavy_clutter

| Metric | CIF-LAAD | Baseline |
|---|---|---|
| Position RMSE (m) [lower better] | 32.8 +/- 6.3 | 6.22 +/- 0.43 |
| ID switches [lower better] | 5.76 +/- 1.8 | 6.88 +/- 6.6 |
| Track continuity [higher better] | 0.805 +/- 0.064 | 0.986 +/- 0.0025 |
| Continuity during dropout [higher better] | n/a | n/a |
| False-track frames [lower better] | 49.1 +/- 24 | 76.1 +/- 32 |
| Mean reacquisition time (s) [lower better] | 2.58 +/- 2 | n/a |
| NEES mean (ideal ~3.0) | 2.35 +/- 0.42 | 2.47 +/- 0.24 |
| NEES fraction <= chi2.95 (ideal ~0.95) | 0.967 +/- 0.023 | 0.979 +/- 0.013 |
| CIF mean latency/cycle (ms) | 4.79 +/- 0.39 | - |
| Evidence chain verified | True | n/a |

## Scenario: identity_conflict

| Metric | CIF-LAAD | Baseline |
|---|---|---|
| Position RMSE (m) [lower better] | 6.02 +/- 0.51 | 6.02 +/- 0.51 |
| ID switches [lower better] | 1.92 +/- 3.8 | 1.92 +/- 3.8 |
| Track continuity [higher better] | 0.988 +/- 0 | 0.987 +/- 0.0024 |
| Continuity during dropout [higher better] | n/a | n/a |
| False-track frames [lower better] | 6.72 +/- 11 | 6.72 +/- 11 |
| Mean reacquisition time (s) [lower better] | n/a | n/a |
| NEES mean (ideal ~3.0) | 2.5 +/- 0.29 | 2.5 +/- 0.29 |
| NEES fraction <= chi2.95 (ideal ~0.95) | 0.971 +/- 0.02 | 0.97 +/- 0.02 |
| CIF mean latency/cycle (ms) | 0.281 +/- 0.022 | - |
| Evidence chain verified | True | n/a |

## Scenario: many_targets_6

| Metric | CIF-LAAD | Baseline |
|---|---|---|
| Position RMSE (m) [lower better] | 27.1 +/- 2 | 6.24 +/- 0.3 |
| ID switches [lower better] | 15 +/- 5.1 | 16.8 +/- 11 |
| Track continuity [higher better] | 0.858 +/- 0.039 | 0.987 +/- 0.0014 |
| Continuity during dropout [higher better] | n/a | n/a |
| False-track frames [lower better] | 86.6 +/- 23 | 112 +/- 40 |
| Mean reacquisition time (s) [lower better] | 2.72 +/- 1 | n/a |
| NEES mean (ideal ~3.0) | 2.79 +/- 0.87 | 2.54 +/- 0.18 |
| NEES fraction <= chi2.95 (ideal ~0.95) | 0.969 +/- 0.02 | 0.974 +/- 0.0095 |
| CIF mean latency/cycle (ms) | 3.32 +/- 0.14 | - |
| Evidence chain verified | True | n/a |
