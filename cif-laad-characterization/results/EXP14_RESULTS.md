# EXP-14: Second External Tracker Comparator (Stone Soup JPDA)

**Status:** Reviewed and approved for public release as part of the CIF-LAAD characterization package, September 2, 2026.

**Kind:** Descriptive benchmark. No ADOPT or REJECT verdict. No engine change.

**Purpose:** Add a second, architecturally different open-source tracker to the
comparison established in EXP-9. EXP-9 compared CIF-LAAD against Stone Soup's
Global Nearest Neighbour (GNN) associator. EXP-14 adds Stone Soup's Joint
Probabilistic Data Association (JPDA), a soft-association tracker whose decision
logic is fundamentally different from GNN's hard nearest-neighbour assignment.
The result is a three-way descriptive picture: CIF-LAAD (batch inheritance,
frozen engine) vs Stone Soup GNN vs Stone Soup JPDA, over the identical frozen
scenarios, seeds, metrics, and fusion preprocessing.

**Engine integrity:** CIF-LAAD frozen engine (SHA-256 manifest 8712f113...7ad45,
14 files). No modifications. q=8 frozen default. JPDA is an external comparator
only; it does not touch the CIF-LAAD engine.

**Comparator note (IMM):** The pre-registration recorded that an Interacting
Multiple Model (IMM) tracker was considered but is not available in Stone Soup
1.9.1 (no interacting-model predictor module). JPDA was selected as the second
comparator before any evaluation seed was run. Selection rationale is in
EXP14_PREREGISTRATION.md.

## Method

**Identical to EXP-9 wherever feasible.** Same six base scenarios, same held-out
seeds (100 to 114 for fast scenarios, 100 to 104 for compute-heavy scenarios),
same eight metrics, same covariance-weighted multi-sensor fusion preprocessing,
same frozen CIF-LAAD engine. CIF-LAAD and GNN were re-run on the same seeds as a
reproducibility check: their EXP-14 numbers reproduce EXP-9 exactly (for example,
CIF clean_single RMSE 6.26 and GNN clean_single RMSE 6.00 match EXP-9 to two
decimals).

**JPDA configuration (locked before evaluation, not retuned after):**
- Established-track association: JPDA with a PDA hypothesiser
- Clutter spatial density: 1e-6; probability of detection: 0.9; gate probability: 0.99
- Transition model: constant velocity, process noise sigma 2.0 m/s^2 (same as EXP-9)
- Measurement model: per-detection covariance, 10 m reference noise (same as EXP-9)
- Track initiation: MultiMeasurementInitiator with a GNN associator, 3 measurements
  required. A GNN initiator is used because JPDA's multiple-hypothesis output is
  incompatible with the initiator, which requires single hypotheses. This is the
  standard Stone Soup pattern for JPDA tracking.
- Deleter: 3 missed steps (1.5 s coast budget), same as EXP-9
- Update rule: for each track, the highest-probability real-detection hypothesis
  is applied only when its association probability exceeds the missed-detection
  probability; otherwise the track coasts. This prevents JPDA from smearing track
  state toward clutter and is what makes the false-track count a fair comparison.

**No retuning after evaluation.** Every JPDA parameter above was fixed in the
pre-registration. Nothing was adjusted after evaluation seeds were run.

## Correction to the pre-registration: heavy_clutter is FEASIBLE for JPDA

The pre-registration predicted that JPDA would be computationally infeasible on
heavy_clutter, based on exploratory timing in which an earlier, non-final
configuration aborted after roughly two frames and exceeded 120 s. That
prediction was WRONG. Under the final locked configuration (with a bounded PDA
gate at 0.99 and the best-hypothesis update rule that suppresses track
proliferation), JPDA completed all five heavy_clutter seeds. Per-seed wall time
was 8.6, 12.0, 12.7, 72.6, and 91.3 s (mean 39.4 s per seed).

This correction is reported openly, and heavy_clutter is kept as a three-way
tradeoff rather than reframed to hide any single property. All three facts belong
together:

On heavy_clutter, JPDA was feasible under the frozen configuration but
computationally expensive, averaging 39.4 seconds per seed. It achieved much
lower positional RMSE than CIF-LAAD, 5.33 m versus 23.68 m, while producing
approximately 435.6 false-track frames versus CIF-LAAD's 3.6. This is not scored
as an overall CIF-LAAD win. It exposes a sharp tradeoff between positional
accuracy, false-track suppression, and compute cost.

Feasibility, speed, positional accuracy, and false-track behavior are four
distinct properties of the two systems, and the reader should see all of them.
Per the standing pre-registration guardrail, the comparator's compute limits are
never scored as CIF-LAAD wins.

## Results

### Three-way summary table

Winner column marks the best value on that metric across the three trackers.
RMSE, false-track frames (FTF), and ID switches: lower is better. Continuity and
dropout continuity: higher is better.

| Scenario | Metric | CIF-LAAD | SS GNN | SS JPDA | Best |
|----------|--------|----------|--------|---------|------|
| **clean_single** (n=15) | RMSE (m) | 6.26 | 6.00 | 5.60 | JPDA |
| | Continuity | 0.988 | 0.974 | 0.974 | CIF |
| | False-track frames | 14.7 | 20.7 | 9.9 | JPDA |
| | ID switches | 3.5 | 3.3 | 0.0 | JPDA |
| **crossing_two** (n=15) | RMSE (m) | 7.96 | 9.08 | 9.28 | CIF |
| | Continuity | 0.984 | 0.970 | 0.968 | CIF |
| | False-track frames | 15.7 | 38.2 | 27.7 | CIF |
| | ID switches | 3.1 | 3.4 | 3.2 | CIF |
| **sensor_dropout** (n=15) | RMSE (m) | 9.39 | 6.35 | 5.94 | JPDA |
| | Continuity | 0.988 | 0.851 | 0.851 | CIF |
| | Dropout continuity | 1.000 | 0.200 | 0.200 | CIF |
| | False-track frames | 9.2 | 16.1 | 8.0 | JPDA |
| | ID switches | 2.4 | 3.7 | 1.0 | JPDA |
| **identity_conflict** (n=15) | RMSE (m) | 6.31 | 6.07 | 5.64 | JPDA |
| | Continuity | 0.988 | 0.974 | 0.974 | CIF |
| | False-track frames | 12.9 | 21.1 | 9.9 | JPDA |
| | ID switches | 2.7 | 2.5 | 0.1 | JPDA |
| **heavy_clutter** (n=5) | RMSE (m) | 23.68 | 5.37 | 5.33 | JPDA |
| | Continuity | 0.928 | 0.975 | 0.975 | GNN/JPDA |
| | False-track frames | 3.6 | 516.8 | 435.6 | CIF |
| | ID switches | 0.0 | 0.8 | 0.4 | CIF |
| **many_targets_6** (n=5) | RMSE (m) | 24.05 | 10.33 | 10.57 | GNN |
| | Continuity | 0.935 | 0.955 | 0.952 | GNN |
| | False-track frames | 28.8 | 165.6 | 146.6 | CIF |
| | ID switches | 5.2 | 6.4 | 15.2 | CIF |

### Compute cost (mean seconds per seed)

| Scenario | CIF-LAAD | SS GNN | SS JPDA |
|----------|----------|--------|---------|
| clean_single | 0.064 | 0.103 | 0.138 |
| crossing_two | 0.141 | 0.231 | 0.309 |
| sensor_dropout | 0.059 | 0.101 | 0.131 |
| identity_conflict | 0.065 | 0.110 | 0.151 |
| many_targets_6 | 1.336 | 38.255 | 6.629 |
| heavy_clutter | ~0.05 (EXP-9) | slow (EXP-9) | 39.4 |

CIF-LAAD is the fastest tracker in every scenario, by roughly 2x on the easy
cases and by one to three orders of magnitude at scale (heavy_clutter: about
0.05 s vs 39.4 s; many_targets_6: 1.34 s vs 6.63 s for JPDA and 38.3 s for GNN).

### Paired statistics (CIF-LAAD minus JPDA, same seeds)

Positive RMSE difference means CIF-LAAD had the higher (worse) RMSE. Wilcoxon
signed-rank p-values shown; the pattern is confirmed by paired t-tests.

| Scenario | RMSE diff (m) | p | FTF diff | p | ID-switch diff |
|----------|---------------|------|----------|------|----------------|
| clean_single | +0.66 | 0.0003 | +4.8 | 0.52 | +3.5 |
| crossing_two | -1.33 | 0.048 | -12.0 | 0.022 | -0.1 |
| sensor_dropout | +3.45 | 0.0001 | +1.2 | 0.93 | +1.4 |
| identity_conflict | +0.67 | 0.0001 | +3.0 | 0.88 | +2.6 |
| many_targets_6 | +13.48 | 0.063 | -117.8 | 0.063 | -10.0 |

## Honest synthesis: which CIF-LAAD claims survive, which weaken

JPDA is a strong, credible comparator, and it beats CIF-LAAD on positional
accuracy in most scenarios. With heavy_clutter now feasible, JPDA has lower RMSE
than CIF-LAAD in 5 of the 6 scenarios (clean_single, sensor_dropout,
identity_conflict, heavy_clutter, and many_targets_6); CIF-LAAD wins RMSE only in
crossing_two. The three-way picture sharpens, rather than flatters, the CIF-LAAD
story, and we do not soften the positional-accuracy loss.

**Where CIF-LAAD is genuinely better (claims that survive):**

1. **False-track suppression at scale.** This is the clearest and most robust
   CIF-LAAD advantage. On heavy_clutter, CIF-LAAD produces 3.6 false-track
   frames against JPDA's 435.6 and GNN's 516.8, roughly a 120x reduction. On
   many_targets_6, CIF-LAAD produces 28.8 against JPDA's 146.6 and GNN's 165.6.
   Both external trackers spawn large numbers of phantom tracks in clutter and
   density; CIF-LAAD does not. For an evidence-grade layer whose job is to avoid
   asserting tracks that are not real, this is the property that matters most,
   and it holds against both comparators.

2. **Compute cost.** CIF-LAAD is the fastest tracker in every scenario, and the
   gap widens sharply at scale (about 0.05 s vs 39.4 s on heavy_clutter). This
   survives the second comparator cleanly.

3. **Sensor-dropout continuity.** CIF-LAAD holds dropout continuity at 1.000
   against 0.200 for both GNN and JPDA, and overall continuity at 0.988 against
   0.851. Neither external tracker coasts through a sensor outage the way
   CIF-LAAD does. This is a real, repeated CIF-LAAD strength.

4. **crossing_two.** CIF-LAAD is best on RMSE, continuity, false tracks, and ID
   switches simultaneously. The advantage is modest but consistent.

5. **ID stability under target density.** On many_targets_6, CIF-LAAD holds 5.2
   ID switches against JPDA's 15.2. JPDA's soft association is notably less
   stable when many targets are close together.

**Where CIF-LAAD is weaker (losses that must be preserved):**

1. **Positional RMSE in clean and dropout conditions.** JPDA achieves lower RMSE
   than CIF-LAAD on clean_single (5.60 vs 6.26), identity_conflict (5.64 vs
   6.31), and sensor_dropout (5.94 vs 9.39). The sensor_dropout RMSE gap (3.45 m,
   p=0.0001) is the largest clean-condition loss: JPDA tracks position more
   tightly, though at a heavy dropout-continuity and false-track cost that CIF
   avoids. CIF-LAAD is not a positional-accuracy leader in low-clutter scenes.

2. **ID switches in clean and identity scenes.** JPDA records 0.0 ID switches on
   clean_single and 0.1 on identity_conflict, against CIF-LAAD's 3.5 and 2.7.
   JPDA's probabilistic association is more identity-stable when targets are well
   separated. This is a real CIF-LAAD weakness in easy conditions.

3. **Positional RMSE in dense and cluttered scenes.** On heavy_clutter (23.68 vs
   5.33) and many_targets_6 (24.05 vs 10.57), both external trackers achieve much
   lower positional RMSE than CIF-LAAD. The caveat is important: they do so while
   emitting hundreds of false tracks. CIF-LAAD trades positional tightness for
   refusing to assert phantom tracks. That tradeoff is defensible for an evidence
   layer, but the raw RMSE loss is real and is not hidden here.

**Net reading.** EXP-14 does not establish CIF-LAAD as a superior general-purpose
tracker. It does the opposite: it further separates CIF-LAAD from conventional
accuracy-optimized tracking. JPDA provides substantially better positional
accuracy across most tested scenarios and excellent identity stability in benign
conditions. CIF-LAAD instead retains a different operating profile: stronger
continuity through complete sensor dropout, much stronger false-track suppression
in dense and cluttered conditions, lower compute cost, and bounded association
advantages in selected contested scenarios (crossing_two across the board, and
fewer ID switches than JPDA in many_targets_6 despite much worse RMSE), at the
cost of substantially poorer localization accuracy. That is the emerging identity
of this work, and it is more informative than a claim that CIF-LAAD beats another
tracker. The second comparator confirms the shape of EXP-9 with an independent,
architecturally different tracker rather than overturning it.

## Limitations

- Simulation only. No hardware, no real sensor data. TRL 3.
- Five seeds on the two compute-heavy scenarios (heavy_clutter, many_targets_6);
  fifteen on the four fast scenarios. Same budget as EXP-9.
- JPDA is run with a GNN initiator, per the standard Stone Soup pattern; a
  pure-JPDA initiation path is not available in 1.9.1.
- Descriptive benchmark. No adoption or rejection decision is implied. The result
  characterizes where CIF-LAAD stands against a second independent tracker; it
  does not, by itself, justify any change to the frozen engine.

## Provenance

- Script: experiments/laad_series/exp14_jpda_benchmark.py
- Results: experiments/laad_series/out/exp14_jpda_benchmark.json
- heavy_clutter JPDA raw: experiments/laad_series/out/exp14_heavy_clutter_jpda.json
- Pre-registration: experiments/laad_series/EXP14_PREREGISTRATION.md
- Stone Soup version: 1.9.1. Python 3.11.6, numpy 2.2.6.
- EXP-9 reference: experiments/laad_series/out/exp9_stonesoup_benchmark.json
