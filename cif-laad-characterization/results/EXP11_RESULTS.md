# EXP-11 Results: narrow remediation of the fixable RMSE slice

Status: Reviewed and approved for public release as part of the CIF-LAAD characterization package, September 2, 2026.\
Scope: CIF-LAAD simulation only (TRL 3). No hardware, no real-sensor data.\
Pre-registration: EXP11_PREREGISTRATION.md, written before any EXP-11 number
existed. Both kill tests below were fixed in advance and are applied verbatim.

## What EXP-11 tested and why

EXP-9 measured a 23 to 24 m RMSE penalty for CIF-LAAD versus a Stone-Soup
baseline in the two contested scenarios (heavy_clutter, many_targets_6). EXP-10
root-caused that penalty as PREDOMINANTLY STRUCTURAL: it is the cost of CIF
keeping coasting tracks alive through gaps that a delete-happy tracker drops.
EXP-10 also isolated two small slices that are NOT part of that structural
tradeoff and might be independently fixable:

1. process noise (q). A lower q reduced RMSE in the EXP-10 ablation.
2. cross-target contamination. In many_targets_6, about 10 percent of folded
   observations came from a different target than the track's own.

EXP-11 attacked only these two slices. Part A is a config-only change to the
frozen v1 engine. Part B is an engine source change and was therefore built as a
separate, clearly-labeled v2 candidate.

## Governance and freeze integrity

The published v1 engine (ciflaad/, SHA-256 manifest 8712f113...7ad45) was not
modified by either part.

* Part A changes only FusionConfig.q, a runtime knob. No source file changed.
* Part B was developed in a separate package, ciflaad_v2/, a copy of v1 with one
  added, off-by-default field (fold_nis_gate_p). With the field disabled,
  ciflaad_v2 reproduces frozen v1 exactly (verified: identical RMSE to 1e-9 on
  many_targets_6, seed 100). The v1 files under ciflaad/ remain byte-identical.

v2 is a candidate only. Even had it passed, it would still require its own full
pre-registered validation and freeze before it could supersede v1 in any public
record.

## Part A: low process noise (q=2.0 vs q=8.0)

Method: frozen v1 engine, FusionConfig.q knob only. Full earned-envelope
scenario set (11 scenarios), 30 held-out seeds (100 to 129). The scenario is
rebuilt per q with the same seed so the simulation RNG stream is identical across
the two configs (paired comparison at the aggregate level).

Pre-registered kill test: ADOPT q=2.0 as the new default ONLY IF, across ALL
scenarios, (a) RMSE is lower or within 1 sigma; (b) dropout continuity is not
reduced beyond 1 sigma; (c) false-track frames are not increased beyond 1 sigma.

Result (mean over 30 seeds), q=8.0 to q=2.0:

| scenario | RMSE m | dropout continuity | false-track frames |
|---|---|---|---|
| clean_single | 6.19 to 5.56 | n/a | 10.77 to 12.97 |
| sensor_dropout | 9.39 to 8.50 | 1.000 to 1.000 | 8.07 to 8.90 |
| dropout_2s | 7.36 to 7.01 | 1.000 to 1.000 | 8.80 to 11.43 |
| dropout_5s | 9.39 to 8.50 | 1.000 to 1.000 | 8.07 to 8.90 |
| dropout_10s | 11.71 to 10.69 | 0.600 to 0.600 | 6.53 to 6.83 |
| degrade_1 | 10.47 to 9.46 | n/a | 7.13 to 6.70 |
| degrade_2 | 25.39 to 22.86 | n/a | 9.37 to 10.30 |
| degrade_3 | 32.77 to 29.37 | n/a | 2.37 to 3.13 |
| heavy_clutter | 23.04 to 20.28 | n/a | 14.60 to 7.70 |
| many_targets_6 | 23.49 to 20.93 | n/a | 28.37 to 29.40 |
| identity_conflict | 6.19 to 5.64 | n/a | 11.83 to 20.03 |

Pre-registered verdict: PASS. All 11 scenarios pass all three kill conditions as
written (applied scenario-by-scenario; a single violation would have forced
REJECT). See the reconciliation immediately below before reading this as a clean
ADOPT: a stronger paired test, run after the principal investigator flagged the identity_conflict
rise, shows the pre-registered rule was too lenient to catch one real cost.

Honest reading of Part A:

* RMSE improves everywhere, by roughly 10 percent relative, including about 3 m
  in the two contested scenarios (heavy_clutter 23.04 to 20.28, many_targets_6
  23.49 to 20.93). This does not close the structural gap to the baseline; it
  narrows it.
* Dropout continuity is unchanged to three decimals (1.000 where full, 0.600 at
  the 10 s gap). The primary earned win is not touched.
* False-track frames move both up and down across scenarios (for example
  heavy_clutter improves 14.60 to 7.70; identity_conflict rises 11.83 to 20.03).
  All 11 scenarios sit inside the pre-registered one-sided one-sigma band (which
  uses the q=8 aggregate standard deviation, roughly 10 to 25 frames), which is
  why the pre-registered rule passes. That rule is lenient; the reconciliation
  below tests these deltas properly.

## Part A reconciliation (added after internal adversarial review of identity_conflict)

The principal investigator flagged that identity_conflict false-track frames rose 11.83 to 20.03 and
asked whether that is genuinely within noise, whether the kill test was applied
per scenario or in aggregate, and for the full table with uncertainty. Findings:

1. The kill test was applied SCENARIO-BY-SCENARIO. A single scenario violation
   forces REJECT. Criterion (c) as pre-registered is one-sided: adopt only if
   false_track_frames(q2) <= false_track_frames(q8) + 1 sigma(q8). For
   identity_conflict, 20.03 <= 11.83 + 12.93 = 24.76, so it PASSES as written.
2. That pre-registered rule is lenient (one-sided, uses only the q=8 spread) and
   underpowered. Because q=8 and q=2 are rebuilt from an identical RNG stream per
   seed, the correct test is a PAIRED per-seed test. It was not stored in the
   original run (aggregates only), so Part A was re-run capturing per-seed
   vectors (frozen v1, config knob only; freeze manifest unaffected). Script:
   exp11a_reconcile.py; data: out/exp11a_reconcile.json; 30 seeds.
3. Paired result for false-track frames: the identity_conflict increase IS
   statistically significant (paired t p=0.035, Wilcoxon p=0.026). It is NOT
   noise. heavy_clutter shows a significant DECREASE (-6.90, p=0.028, Wilcoxon
   0.006). dropout_2s is marginal (+2.63, p=0.068). All other scenarios are not
   significant. RMSE improvement is significant in EVERY scenario (paired p from
   0.015 down to below 0.001).

Correction: an earlier draft of this section said the false-track differences
were "not statistically distinguishable from noise" and claimed "no measurable
harm." That was wrong for identity_conflict and is retracted. Low q is a genuine
tradeoff, not a free win: a robust ~10 percent RMSE reduction across the whole
envelope and a significant false-track reduction in heavy_clutter, at the cost of
a significant, localized false-track increase in identity_conflict.

Status of the verdict: the binding pre-registered verdict is PASS/ADOPT and is
not retroactively flipped, because rejecting on a stronger test introduced after
seeing the data would itself break pre-registration discipline. But this is NOT a
clean ADOPT. It is recorded as ADOPT-WITH-DOCUMENTED-COST, and the decision is
handed to internal adversarial review with three honest options:
  (i) ADOPT q=2.0 as the global default and document the identity_conflict
      false-track cost as a characterized, known tradeoff; claim NO false-track
      benefit anywhere; carry identity_conflict as a watch item.
 (ii) REJECT q=2.0 as a global default on the spirit of the "false tracks must
      not rise" rule, since a real rise exists in one scenario.
(iii) Make q scenario-conditional (low q in clean/dropout/clutter, keep q=8 in
      identity-dense scenes). This is a new design lever and would need its own
      pre-registration before adoption; not adopted here.
Recommendation: option (i). The RMSE gain is real and universal, the only
significant false-track cost is confined to one scenario, and continuity is
untouched. But the choice is reserved to internal review, and low q must never be described as a
cost-free improvement.

Full q=8 vs q=2 table with uncertainty (mean plus or minus 1 sigma, 30 seeds):

| scenario | RMSE q8 | RMSE q2 | RMSE paired p | ftf q8 | ftf q2 | ftf paired p |
|---|---|---|---|---|---|---|
| clean_single | 6.19 +/- 0.64 | 5.56 +/- 0.71 | <0.001 | 10.77 +/- 14.28 | 12.97 | 0.165 |
| sensor_dropout | 9.39 +/- 1.43 | 8.50 +/- 1.01 | <0.001 | 8.07 +/- 9.69 | 8.90 | 0.388 |
| dropout_2s | 7.36 +/- 0.93 | 7.01 +/- 0.79 | 0.015 | 8.80 +/- 10.61 | 11.43 | 0.068 |
| dropout_5s | 9.39 +/- 1.43 | 8.50 +/- 1.01 | <0.001 | 8.07 +/- 9.69 | 8.90 | 0.388 |
| dropout_10s | 11.71 +/- 1.79 | 10.69 +/- 1.28 | <0.001 | 6.53 +/- 8.46 | 6.83 | 0.636 |
| degrade_1 | 10.47 +/- 1.29 | 9.46 +/- 1.41 | <0.001 | 7.13 +/- 12.72 | 6.70 | 0.844 |
| degrade_2 | 25.39 +/- 3.48 | 22.86 +/- 3.55 | <0.001 | 9.37 +/- 11.41 | 10.30 | 0.607 |
| degrade_3 | 32.77 +/- 4.14 | 29.37 +/- 4.41 | <0.001 | 2.37 +/- 6.02 | 3.13 | 0.400 |
| heavy_clutter | 23.04 +/- 4.15 | 20.28 +/- 3.71 | <0.001 | 14.60 +/- 25.16 | 7.70 | 0.028 |
| many_targets_6 | 23.49 +/- 2.72 | 20.93 +/- 2.79 | <0.001 | 28.37 +/- 19.89 | 29.40 | 0.775 |
| identity_conflict | 6.19 +/- 0.51 | 5.64 +/- 0.73 | <0.001 | 11.83 +/- 12.93 | 20.03 +/- 24.30 | 0.035 |

Dropout continuity is identical to 1.000 (full) and 0.600 (10 s gap) at both q
values, with zero seed-to-seed variance, so it is omitted from the table above.

## Part B: cross-target contamination fold filter (v2 candidate)

Mechanism (single, pre-declared): a per-fold motion-consistency check. Before an
observation that the Hungarian assignment placed inside the wide association gate
is folded into a CONFIRMED track, its normalized innovation is re-checked against
a tighter fold gate. A fold that exceeds the tighter gate is rejected as
motion-inconsistent and the observation is returned to the unassigned pool. The
check is applied only to CONFIRMED tracks, so tentative track building and
coasting re-acquisition (the dropout-continuity win) are untouched by
construction.

Method: frozen v1 (ciflaad/) versus v2 candidate (ciflaad_v2/) at the SAME
process noise, so the fold filter's marginal effect is isolated from Part A. The
decision-bearing comparison is v1 versus v2 both at q=2.0 (the adopted default),
primary threshold fold gate p=0.95. A q=8.0 pair is reported for continuity with
EXP-10, and a tighter-threshold sweep (p=0.90, p=0.80) is reported as exploratory
context only. 30 seeds. Cross-target fold fraction is measured by runtime
instrumentation of Track.update_with on both engines identically; no engine
source is modified by the measurement.

Pre-registered kill test: ACCEPT ONLY IF (a) many_targets_6 cross-target fold
fraction drops materially (below 5 percent, from about 10 percent) AND its RMSE
improves; AND (b) dropout continuity, dropout-scenario continuity, and
false-track suppression are all preserved within 1 sigma; AND (c) heavy_clutter
and clean_single are not degraded. Otherwise REJECT and revert to v1.

Result, primary pair v1(q=2.0) to v2(q=2.0, p=0.95), mean over 30 seeds:

| scenario | RMSE m | cross-target fold frac | false-track frames |
|---|---|---|---|
| clean_single | 5.56 to 6.33 | 0.000 to 0.000 | 12.97 to 36.90 |
| sensor_dropout | 8.50 to 8.96 | 0.000 to 0.000 | 8.90 to 28.83 |
| dropout_2s | 7.01 to 7.72 | 0.000 to 0.000 | 11.43 to 33.10 |
| dropout_5s | 8.50 to 8.96 | 0.000 to 0.000 | 8.90 to 28.83 |
| dropout_10s | 10.69 to 11.00 | 0.000 to 0.000 | 6.83 to 23.47 |
| heavy_clutter | 20.28 to 21.08 | 0.012 to 0.011 | 7.70 to 17.33 |
| many_targets_6 | 20.93 to 22.30 | 0.089 to 0.095 | 29.40 to 78.03 |
| identity_conflict | 5.64 to 6.35 | 0.080 to 0.092 | 20.03 to 49.67 |

Verdict: REJECT the v2 fold filter. Revert to v1. It trips every kill condition:

* (a) many_targets_6 cross-target fold fraction did NOT drop; it rose slightly
  (0.089 to 0.095) and stayed above the 5 percent target, and RMSE got worse
  (20.93 to 22.30).
* (b) false-track suppression collapsed. many_targets_6 false-track frames rose
  29.40 to 78.03; identity_conflict 20.03 to 49.67; every dropout scenario
  roughly tripled. All far beyond 1 sigma.
* (c) clean_single RMSE degraded 5.56 to 6.33, beyond 1 sigma.

Context (q=8.0 pair) tells the same story: RMSE worse in every scenario, fold
fraction slightly worse in many_targets_6 (0.089 to 0.101), false tracks up
sharply. The exploratory tighter-threshold sweep makes it worse, not better: at
p=0.90 and p=0.80 the false-track counts explode further (many_targets_6 reaches
129 and 188 frames) and the filter even manufactures contamination in scenarios
that had none (clean_single fold fraction 0.000 rises to 0.12).

## Why the fold filter backfired (mechanism)

The measurement makes the failure mode legible. Rejecting an in-gate fold on a
confirmed track does not simply discard a bad detection. It causes that track to
miss its true update. The rejected observation then falls through to the spawn
path and starts a NEW track. The result is track fragmentation: one true target
now supports two or more track fragments, which is counted as false tracks and
as identity churn. Cross-target contamination does not fall, because the
fragments pick up the same cross-target detections the original track would
have, and at tighter gates MORE true detections are rejected, so contamination
can rise. This is the same blunt collateral EXP-10 already found when it tried
the global gate-tightening lever, reappearing in the per-fold form. The
prediction that a wrong-target detection is reliably motion-inconsistent did not
hold at the innovation scale these confirmed tracks actually carry.

## Combined conclusion (EXP-9, EXP-10, EXP-11)

1. The contested-scenario RMSE penalty is structural, not a simple association
   bug. EXP-10 established this; EXP-11 Part B confirms it from the other side,
   by showing that direct surgery on the association fold does not recover
   accuracy and costs the earned false-track and continuity wins.
2. The one honest, freeze-safe change is Part A: q=2.0 lowers RMSE by about 10
   percent across the whole envelope (significant in every scenario by paired
   test). It is a tradeoff, not a free win: paired testing shows a significant
   false-track reduction in heavy_clutter and a significant false-track increase
   in identity_conflict (p=0.035). It passes the pre-registered kill test but is
   recorded as ADOPT-WITH-DOCUMENTED-COST, pending internal adversarial review (see
   the Part A reconciliation section). It narrows, and does not close, the gap to
   the baseline in contested scenes. Dropout continuity is untouched.
3. The earned envelope and its stated limits are unchanged. CIF-LAAD's validated
   strengths (continuity through multi-second dropout, false-track suppression,
   bounded identity stability, tamper-evident provenance, typed hostile-input
   rejection) and its falsified claims (coherence-gate benefit, identity
   stability at high target counts, clean-scenario accuracy advantage,
   accuracy-match at scale) stand as reported.

## Changes this experiment authorizes

* Proposed (pending internal adversarial review): adopt q=2.0 as the default FusionConfig for
  future v1 runs, documenting the identity_conflict false-track cost as a known,
  characterized tradeoff and claiming no false-track benefit anywhere. This is a
  config default, not a new engine. If applied to the public record it should be
  noted as a configuration change, and the EXP-9 and EXP-10 numbers, which were
  run at q=8.0, remain the numbers of record for those experiments unless re-run.
  Two alternatives internal review may choose instead: reject q=2.0 as a global default on
  the spirit of the no-false-track-rise rule, or make q scenario-conditional
  (which would require its own pre-registration). Not adopted unilaterally here.
* Do not adopt the v2 fold filter. Keep ciflaad_v2/ as a preserved,
  clearly-labeled failed candidate for the record. Do not present it as an
  improvement anywhere.

## Honesty guards honored

* No scenario or metric was added or dropped after seeing results.
* Both kill tests are the ones written in EXP11_PREREGISTRATION.md.
* The Part B failure is preserved and reported as a REJECT, not spun. The v2
  code remains on disk under ciflaad_v2/ exactly as tested.
* Nothing from EXP-9, EXP-10, or EXP-11 has been published. All of it awaits
  combined internal adversarial review.
