# CIF-LAAD Validation Series - Preregistration

**Status:** FROZEN before any run. Simulation-only. TRL 3. Research record, not a field result.

**Preregistered:** 2026-09-02 (UTC).
**Author:** Remnant Fieldworks Inc. (RF).

## 0. What this is, and what it is not

This is a preregistered plan for a set of controlled, seeded, reproducible
simulation experiments on CIF-LAAD. It is written and hashed BEFORE the runs so
that the hypotheses, operating modes, seeds, metrics, and kill criteria cannot
be retrofitted to whatever the data happened to show.

Everything here is SIMULATION. There is no hardware, no real sensor feed, no
field trial, and no independent third-party rerun. Results describe behavior
inside this synthetic testbed under the conditions tested. They are NOT a
universal security proof and NOT evidence of real-world performance.

Two experiments from the original 10-point plan are deliberately EXCLUDED
because they cannot be done honestly in-house:

- Independent reproduction by an outside engineer/university (its entire value
  is that it is external; we will not simulate it and call it independent).
- Real-data replay (we do not currently hold rights to a lawful non-sensitive
  low-altitude dataset).

We still FREEZE and ship the reproducibility package (frozen code, seeds,
hashes, one-command replay, expected outputs) so any external party can rerun
it later. We just do not claim that such a rerun has happened.

## 0b. How this series is judged (success / kill test)

This series is NOT judged by "how many PASSes did we get." It is one coherent
validation series with clearly defined experimental units (EXP-1 .. EXP-8).
Seeds are REPLICATIONS within a unit - they are never counted as separate
experiments, and this series does NOT increase RF's public experiment count.

The single question the series must answer:

> Did we identify a defensible OPERATING ENVELOPE in which CIF-LAAD provides
> measurable continuity, identity and evidence advantages WITHOUT an
> unacceptable localization-accuracy cost?

- If YES: define that envelope precisely (which conditions, how much continuity/
  ID/evidence advantage, at what RMSE cost) and keep it. LAAD becomes
  commercially interesting there.
- If NO: narrow or kill the weak parts, retain only what survived, and say so.
  A narrowed, survived-only claim is more credible, not less.

Product identity the series is meant to support (only if earned):
CIF-LAAD is a sensor-agnostic low-altitude ASSURANCE LAYER for maintaining
track identity, continuity, uncertainty and evidence provenance when
observations degrade or conflict. It is NOT a generic drone-fusion product and
is not marketed as "we also fuse sensors."

## 1. Research question (single, falsifiable)

Can CIF-LAAD retain its continuity, identity, provenance and evidence
advantages during degraded/incomplete/contradictory observation conditions
WITHOUT paying an unacceptable position-accuracy penalty relative to a fair
conventional baseline?

We already know from the published 25-seed ledger that CIF pays a real RMSE
penalty in clutter (approx 24.9 m vs 6.2 m baseline). This series maps WHERE
that penalty is worth it and where it is not, honestly, across a preregistered
condition grid.

## 2. Frozen substrate (the inputs we do NOT touch)

The following files are frozen for the whole series. Their combined SHA-256 is
recorded below. If any of them changes, the series is invalidated and must be
re-preregistered.

Frozen engine + simulator + baseline + metrics + existing scenarios:
`ciflaad/observation.py, kalman.py, correlation.py, track.py, coherence.py,`
`confidence.py, evidence.py, fusion.py, baseline.py, sim/scenario.py,`
`sim/metrics.py, experiments/scenarios.py, experiments/adapters.py,`
`experiments/run_experiments.py`

**Combined freeze SHA-256:** `8712f1138bdd20090b9a1b6eda58cebc5c274a843b960d6784e8650b7ea7ad45`

Per-file hashes are in `FREEZE_MANIFEST.txt`.

**Environment:** Python 3.11.6, numpy 2.2.6, scipy 1.14.1.

We do NOT modify: the Kalman filter, the association/gating, the baseline
tracker, the sensor noise models, the metric definitions, the existing six
scenarios, or the published seeds (0-24). New experiments only ADD new seeded
scenarios (built from the frozen sim primitives) and SWEEP already-exposed
FusionConfig knobs. No knob is invented for this series.

**Held-out seeds.** All headline experiments use seeds starting at 100 (100+),
which were never used during any prior tuning. The published ledger used seeds
0-24. This keeps the validation set disjoint from anything that could have been
tuned against.

## 3. Experiments, hypotheses, metrics, kill criteria

Metrics are the frozen `sim.metrics` set: position_rmse_m, id_switches,
continuity, dropout_continuity, false_track_frames, mean_reacq_s, nees_mean,
nees_p95_ok, plus mean_latency_ms and evidence_ok. Lower-is-better and
higher-is-better are as labeled in the ledger.

### EXP-1 Accuracy-continuity frontier
Freeze everything except inheritance behavior. Sweep a small PREREGISTERED set
of seven named operating modes over all six frozen scenarios, 30 held-out seeds
each:
- `M_legacy`     inherit_mode=legacy
- `M_batch`      inherit_mode=batch (current default; window 6 s, coast 3, delete 8)
- `M_gated`      inherit_mode=gated (the FALSIFIED coherence-gate hypothesis, kept for honest comparison)
- `M_batch_short`   batch, inherit_window_s=3
- `M_batch_long`    batch, inherit_window_s=10
- `M_batch_patient` batch, coast_misses=5, delete_misses=12
- `M_batch_eager`   batch, coast_misses=2, delete_misses=6

Output: the real Pareto frontier of RMSE vs (continuity, false_track_frames,
id_switches). Hypothesis: no single mode dominates; `M_batch` sits on the
frontier and `M_gated` does not (it should be dominated in clutter). This is a
prediction, not a guarantee - whatever the data shows is recorded.

Kill criterion: if `M_gated` turns out to DOMINATE `M_batch` in clutter, the
published falsification story is wrong and must be corrected publicly.

### EXP-2 Dropout-duration stress
Single target, all sensors blind for a window of duration
D in {0.5, 1, 2, 3, 5, 10, 15} s (dt=0.5 s; 0.25 s is below temporal
resolution and is excluded, stated honestly). 40 held-out seeds per D.
Metric of record: dropout_continuity and mean_reacq_s (CIF vs baseline), plus
the RMSE during/after the gap. Find the crossover D where CIF's continuity
advantage begins and where it collapses.

### EXP-3 Sensor-degradation matrix
Baseline benign geometry, then independently degrade K in {1,2,3} of the three
sensors by: inflated position noise (x4 sigma), reduced Pd (0.4), and a mid
dropout window. 30 held-out seeds per cell. Question: how gracefully does each
tracker degrade as sensing gets worse; does CIF hold identity/continuity longer
at the cost of RMSE.

### EXP-4 Dense-crossing identity challenge
N in {2,4,8,16,32} drones on crossing paths, modest clutter. 30 held-out seeds
per N. Metrics of record: id_switches and false_track_frames (fragmentation).
Expectation from the review: engine is pure-Python and starts to strain past
~25-30 simultaneous tracks; N=32 is expected to expose that. Recorded honestly.

### EXP-5 False-observation resilience
Inject hostile observations into a benign scenario: spoofed (plausible but
false position), duplicate/replayed seq, stale timestamp, out-of-order,
malformed (NaN/negative-definite cov), and contradictory class. Measure: reject
rate by typed error code, whether spoofs create/steal tracks, and whether
uncertainty/lineage is preserved. This exercises the FROZEN validate() + seq
replay defence + contradiction log; we only feed inputs, we do not change the
defence.

### EXP-6 Evidence / provenance tamper challenge
Run a benign scenario, take the resulting per-track hash-linked evidence
chains, then programmatically (a) mutate a payload, (b) reorder two records,
(c) delete a record, (d) substitute a record. Show verify() returns True before
and False after each tamper. HONEST LABEL: tamper-EVIDENT, not tamper-proof - a
fully trusted writer can forge a fresh consistent chain; this detects mutation
of a persisted/transmitted log.

### EXP-7 Baseline benchmark
The frozen `BaselineTracker` (nearest-neighbor Kalman with gating) is the fair
in-tree comparator and is reported alongside CIF in every experiment. In
addition we report a documented Global-Nearest-Neighbor (GNN) reference
configuration for context. We do NOT claim a certified third-party library; the
comparator is our implementation of a standard textbook algorithm and is
labeled as such.

### EXP-8 Scale test
N in {1,10,50,100,500,1000} targets, short fixed duration, measure per-cycle
latency (ms), throughput, and where real-time (10 Hz, i.e. 100 ms/cycle at
dt=0.5 s implies a 50 ms compute budget) breaks. Pure-Python single-thread; we
expect and will report the collapse point as a known engineering liability.

## 4. Honesty commitments (RF God Mode)

- Report the RMSE liability in the same breath as every continuity/ID win.
- Preserve and re-report the FALSIFIED coherence-gate result; never quietly
  drop it.
- No retune-until-win: the operating-mode set above is fixed; we do not add
  modes after seeing results to manufacture a winner.
- No claim of "better-calibrated uncertainty" (NEES does not support it); NEES
  is reported as-is.
- Language stays: simulation-only, TRL 3, tamper-EVIDENT (not proof), no
  "certified"/"validated by hardware", no independent validation claimed.
- Kill criteria above are honored: if the data contradicts a prior public
  claim, the public claim gets corrected, not the data.

## 5. Expected outputs

Each experiment writes a machine-readable `<exp>.json` and a human `<exp>.md`
to `experiments/laad_series/out/`. After all runs, `RESULTS.md` synthesizes the
frontier and the honest liability map, and `REPRODUCE.md` gives the exact
one-command replay. Post-run, the SHA-256 of every output json is recorded in
`EXPECTED_OUTPUTS.sha256` so a future rerun can be checked bit-for-bit against
this frozen record.
