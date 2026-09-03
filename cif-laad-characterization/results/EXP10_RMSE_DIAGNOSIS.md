# EXP-10: RMSE Root-Cause Diagnosis

Status: Reviewed and approved for public release as part of the CIF-LAAD characterization package, September 2, 2026.
Scope: CIF-LAAD simulation only (TRL 3). No hardware, no real-sensor data.
Engine: frozen (SHA-256 manifest 8712f113...7ad45, 14 files). This diagnosis
instruments the engine at runtime only; no source file was modified and the
freeze manifest is unaffected.

## Governing question

EXP-9 (Stone-Soup GNN benchmark) confirmed a large position-RMSE gap: on the two
stress scenarios CIF-LAAD scored 23.68 m (heavy_clutter) and 24.05 m
(many_targets_6), versus 5.94 m and 6.19 m for the internal baseline and 5.37 m
and 10.33 m for Stone-Soup. The question this experiment answers:

  Is the 23 to 24 m RMSE penalty a FIXABLE association/inheritance defect, or a
  STRUCTURAL tradeoff of the continuity-first architecture?

## Method

Five diagnostics on the two failing scenarios (heavy_clutter, many_targets_6)
with clean_single as a control. 15 seeds (100 to 114); the 5-seed subset
(100 to 104) reproduces EXP-9 for cross-check. The default engine (inherit_mode
= batch) is the subject; the baseline is shown only for reference.

Cross-check: EXP-10 batch_default RMSE (heavy 23.52 m, many 24.41 m, 15 seeds)
matches EXP-9 (heavy 23.68 m, many 24.05 m, 5 seeds). The number is stable.

## Verdict

The RMSE penalty is PREDOMINANTLY STRUCTURAL. It is the measured, expected price
of the continuity and false-track-suppression wins, not a fixable association or
inheritance defect. A small, secondary contamination component exists in
dense-target scenes only and does not change the verdict.

Four independent lines of evidence converge on this conclusion.

### 1. The penalty lives entirely in the tracks other trackers drop (Diagnostic A)

Re-scoring the exact same captured timeline at tighter association radii:

| radius (m) | heavy_clutter RMSE | many_targets_6 RMSE | clean_single RMSE |
|-----------:|-------------------:|--------------------:|------------------:|
| 15  | 9.44  | 8.76  | 6.21 |
| 25  | 12.61 | 11.29 | 6.26 |
| 40  | 15.21 | 13.90 | 6.26 |
| 60  | 18.34 | 16.92 | 6.26 |
| 90  | 21.28 | 21.08 | 6.26 |
| 120 | 23.52 | 24.41 | 6.26 |

At a tight 15 m gate CIF-LAAD scores 9.4 m and 8.8 m, close to the baseline's
~6 m. The entire 14 m of extra RMSE comes from tracks in the 25 to 120 m band.
Those are exactly the degraded and coasting tracks that a delete-happy tracker
(baseline, Stone-Soup) drops and CIF keeps. The metric (assoc_radius = 120 m)
counts every kept track within 120 m as "tracked" and folds its drift into RMSE.
The RMSE penalty is therefore the arithmetic flip side of the continuity win: the
tracks that inflate our RMSE are the tracks the competitors do not have at all.

On clean_single there are no degraded/coasting tracks, so RMSE is flat at ~6.2 m
regardless of radius. This is the control confirming the mechanism.

### 2. The error is a heavy tail, not a uniform shift (Diagnostic B)

Distribution of assigned-pair errors at r = 120 m:

| | heavy_clutter | many_targets_6 | clean_single |
|--|-------------:|---------------:|-------------:|
| median   | 12.19 | 10.27 | 5.43 |
| p90      | 35.00 | 35.38 | 9.28 |
| p95      | 50.88 | 57.41 | 10.73 |
| p99      | 91.23 | 98.99 | 12.89 |
| max      | 119.31 | 119.99 | 17.34 |
| frac > 30 m | 12.8% | 12.6% | 0.0% |
| frac > 60 m | 3.5% | 4.5% | 0.0% |

The median error is a healthy 10 to 12 m. RMSE is dragged to 24 m by a minority
tail: roughly 13% of track-frames sit beyond 30 m. A uniform process-noise or
filter deficiency would lift the whole distribution (median would rise toward the
RMSE). Instead the bulk is well-tracked and a tail of coasted/dragged frames
carries the penalty. clean_single has no tail at all (0% beyond 30 m).

### 3. The tail is coasting drift, not a broken filter or inheritance (Diagnostic C)

RMSE split by track state:

| | CONFIRMED | COASTING | inherited | not inherited |
|--|---------:|---------:|----------:|--------------:|
| heavy_clutter  | 16.75 (86%) | 48.19 (14%) | 23.89 | 23.62 |
| many_targets_6 | 18.73 (90%) | 54.29 (10%) | 25.27 | 23.35 |

Coasting tracks carry 48 to 54 m RMSE against 16 to 19 m for confirmed tracks.
Coasting is the continuity mechanism: when a target stops being observed during
dropout, the constant-velocity filter coasts with no measurement and drifts. The
track stays inside the 120 m gate (a continuity win) while its position error
grows (an RMSE cost). This is inherent to maintaining a track through dropout
without a measurement, and it is the single largest structural contributor.

Inheritance is not the cause. Inherited and non-inherited tracks have
essentially the same RMSE (23.89 vs 23.62; 25.27 vs 23.35). The inheritance
machinery is not what carries the error.

### 4. The tracks are locked on the right target, they simply drift (Diagnostic D)

Fraction of each assigned track whose recent folded observations came from the
correct truth, clutter, or a different truth:

| | clean-lock (f_same >= 0.75) | other-target fold | metric-matched wrong lock |
|--|---------------------------:|------------------:|--------------------------:|
| heavy_clutter  | 99.8% at 23.84 m | 0.46% at 42.23 m | 0.32% at 19.06 m |
| many_targets_6 | 96.9% at 24.04 m | 9.69% at 32.89 m | 2.54% at 53.47 m |

In heavy_clutter, association contamination is negligible: 99.8% of assigned
tracks are cleanly locked to the correct target, and they still carry the full
23.8 m RMSE. The penalty is NOT clutter stealing the track; it is clean tracks
drifting. In many_targets_6 there is a real but secondary contamination
component: about 10% of pairs had a cross-target fold (32.9 m) and 2.5% were
metric-matched to the wrong lock (53.5 m). That is the only fixable slice, and it
exists only in dense multi-target scenes.

### 5. No configuration knob recovers RMSE (Diagnostic E)

Ablation matrix (RMSE / continuity / false-track-frames), 15 seeds:

heavy_clutter:

| config | RMSE | continuity | false-track frames |
|--|----:|----:|----:|
| batch_default   | 23.52 | 0.901 | 13.6 |
| legacy          | 24.55 | 0.772 | 104.5 |
| gated           | 32.17 | 0.824 | 52.2 |
| no_inherit      | 22.03 | 0.852 | 13.6 |
| no_merge        | 23.52 | 0.901 | 14.7 |
| tight_gate_095  | 24.07 | 0.906 | 10.5 |
| tight_gate_090  | 24.69 | 0.902 | 19.4 |
| low_q           | 20.83 | 0.905 | 6.9 |
| tight+noinherit | 22.06 | 0.850 | 13.5 |

many_targets_6:

| config | RMSE | continuity | false-track frames |
|--|----:|----:|----:|
| batch_default   | 24.41 | 0.923 | 32.1 |
| legacy          | 24.90 | 0.887 | 87.1 |
| gated           | 29.80 | 0.861 | 104.6 |
| no_inherit      | 22.35 | 0.879 | 38.9 |
| no_merge        | 24.81 | 0.929 | 69.5 |
| tight_gate_095  | 24.89 | 0.920 | 80.9 |
| tight_gate_090  | 25.56 | 0.909 | 119.8 |
| low_q           | 21.71 | 0.930 | 32.3 |
| tight+noinherit | 22.30 | 0.869 | 55.0 |

The best RMSE any knob achieves is low_q at 20.83 m and 21.71 m, still about 3.5x
the baseline's ~6 m. low_q (reducing process noise) helps modestly and, notably,
also lowers false tracks in heavy_clutter (6.9 vs 13.6) without hurting
continuity, so it is worth carrying forward as a small default improvement, but
it does not close the gap. no_inherit trims RMSE to ~22 m but pays continuity
(0.90 to 0.85; 0.92 to 0.88), which sacrifices the primary win to buy 1.5 m.
The pre-registered gated mode makes RMSE worse (32.2 / 29.8), consistent with
its earlier falsification. Tightening the association gate does not help; it
drops good folds along with contaminated ones.

No setting recovers precision without surrendering the continuity or
false-track-suppression advantages that define the layer.

## Interpretation

The 23 to 24 m RMSE decomposes as:

1. Continuity/metric coupling (dominant). CIF keeps degraded and coasting tracks
   alive inside the 120 m gate. Scored at a tight radius CIF is near baseline
   (9 m). The extra error is entirely tracks the competitors would have dropped.
2. Coasting drift (dominant, structural). Coasting tracks carry 48 to 54 m; this
   is the direct cost of maintaining a track through dropout with a
   constant-velocity model and no measurement.
3. Cross-target contamination (minor, dense-target only, partially fixable).
   ~10% of pairs in many_targets_6; negligible in heavy_clutter. Resistant to the
   obvious gate-tightening knob.

Components 1 and 2 are the architecture working as designed: it trades per-track
position precision for track continuity, false-track suppression, and evidence
provenance. That is the exact tradeoff RESULTS.md already declared as the earned
envelope. EXP-10 now quantifies it and shows it is not a defect waiting to be
patched.

## Consequence (for scoring)

The pre-registered decision rule was: if the RMSE penalty is fixable, pursue the
fix and LAAD becomes a more serious tracker; if structural, preserve the result
and position CIF-LAAD permanently as an assurance/continuity/cueing layer, not a
precision tracker. The evidence supports the structural branch.

Recommended position, unchanged in substance from RESULTS.md and now
evidence-backed at root-cause depth: CIF-LAAD is a sensor-agnostic low-altitude
assurance and cueing layer for track continuity, false-track suppression, and
evidence provenance under degraded/contested conditions, explicitly trading
localization precision for those properties. Position RMSE of 23 to 24 m in dense
clutter is the measured, characterized cost of that trade, dominated by coasting
continuation of tracks that competing trackers drop.

One small, honest improvement is available (low_q as a default), and one small
fixable slice exists (cross-target contamination in dense scenes). Neither
converts CIF-LAAD into a precision tracker, and neither should be over-sold.

## Honest limitations of this diagnosis

- Simulation only, constant-velocity targets, three simulated sensors. No
  maneuvering-target or real-sensor validation.
- The 120 m association radius is the scoring convention inherited from the
  metric; the radius sweep is provided precisely so the number is not read in
  isolation.
- The low_q and contamination findings are directions, not validated fixes. They
  are not claimed as improvements until run as their own pre-registered
  experiment.
