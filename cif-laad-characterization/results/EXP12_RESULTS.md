# EXP-12 Results: adaptive process noise, observable-state controller

Status: Reviewed and approved for public release as part of the CIF-LAAD characterization package, September 2, 2026.
Scope: CIF-LAAD simulation only (TRL 3). No hardware, no real-sensor data.\
Pre-registration: EXP12_PREREGISTRATION.md, written and locked before any EXP-12
number existed. Every threshold, signal definition, and pass/fail rule below was
fixed in advance and is applied verbatim.

## Verdict

REJECT. Keep q=8.0 as the frozen v1 default.

The pre-registered rule was: ADOPT only if ALL of criteria (a) through (e) pass;
any partial pass is a full REJECT. Criteria (a) through (d) passed. Criterion (e),
the mechanism/honesty guard, failed. Under the locked rule this is a clean REJECT,
and it is recorded as one. No outcome number was used to move a threshold or to
rescue the verdict.

## What EXP-12 tested and why

EXP-11 Part A established that a low global process noise (q=2.0) lowers RMSE by
about 10 percent across the whole earned envelope (significant in every scenario
by paired test), but at a real, localized cost: a significant false-track
increase in identity_conflict (paired p=0.035). q=8.0 was kept as the frozen
default for that reason.

EXP-12 asked a narrower question: can the engine use only observable runtime
state to run low q where low q helps (open, clutter, many-target scenes) and
fall back to q=8.0 exactly where low q hurt (identity-dense, contested scenes),
without any oracle knowledge of the scenario label? The hypothesis was that a
contested-state controller would capture the RMSE gain while NOT reproducing the
identity_conflict false-track penalty, and would demonstrably do so by switching
to high q selectively in the contested scenario.

## Governance and freeze integrity

The published v1 engine (ciflaad/, SHA-256 manifest 8712f113...7ad45) was NOT
modified. EXP-12 is an EXTERNAL controller: it wraps the frozen engine and sets
the FusionConfig.q knob per step from observable track state. No engine source
file changed. The freeze manifest is unaffected.

Sanity check (pre-registered, mandatory): with the controller pinned to a
constant q, its output must reproduce plain frozen-engine output bit-for-bit.
Result: PASS, zero mismatches, at both q=8.0 and q=2.0 across the spot scenarios,
to a tolerance of 1e-9. This proves the controller adds nothing but the mode
switch itself; any difference measured below is attributable to the switching
policy, not to a side effect of the wrapper.

## The controller (locked definition)

Process noise is chosen per track per step from observable state only:

* Q_LOW = 2.0, Q_HIGH = 8.0.
* A track is CONTESTED if either (i) its Mahalanobis separation to any other
  confirmed track, on the summed predicted covariance, is at or below
  D_PROX = 11.3449 (chi-square 0.99 quantile, 3 dof), OR (ii) an observation
  gates to two or more confirmed tracks (association contention), gate
  ASSOC_GATE = 11.3449.
* Contested tracks, TENTATIVE tracks, coasting tracks, and new spawns all run
  q_high (fail safe toward the incumbent default). Only uncontested, confirmed,
  actively-updated tracks are eligible for q_low.
* Hysteresis H = 3: a newly confirmed track holds q_high for its first 3
  confirmed cycles before it can drop to q_low.

This controller was experimentally rejected and is not part of the frozen CIF-LAAD implementation.

Contested state is derived only from runtime track geometry and association
state. No scenario label, no ground truth, and no outcome metric enters the
controller. Thresholds were locked before evaluation.

## Signal degeneracy calibration (signal-only, seeds 200 to 214)

Before evaluation, a separate calibration set (15 seeds, disjoint from the 30
held-out evaluation seeds) checked only that the contested signal is not
degenerate: not always on, not always off, and materially more active in the
identity_conflict scenario than in clean_single. This used only the signal firing
rate; no outcome metric was consulted, exactly as pre-registered.

Result: non_degenerate = FALSE.

* not always on: TRUE (max mode share about 0.26).
* not always off: TRUE (min above 0.04).
* materially higher in identity_conflict vs clean_single: FALSE. Calibration
  q_high share was 0.263 in identity_conflict vs 0.195 in clean_single, a
  difference of 0.068, below the 0.10 materiality bar fixed in the
  pre-registration.

This was the first pre-registered warning that the observable signal does not
selectively light up in the crossing scenario. It was recorded and evaluation
proceeded as planned (calibration is a signal-degeneracy check, not a
decision gate).

## Evaluation (30 held-out seeds, 100 to 129)

Three arms were run on an identical per-seed RNG stream: incumbent (constant
q=8.0), adaptive (the controller), and a reference constant-q=2.0 arm for
context. Comparisons are paired per seed. Test: paired t plus Wilcoxon
signed-rank, alpha 0.05. The decision-bearing comparison is adaptive vs
incumbent.

Adaptive vs incumbent, mean over 30 seeds:

| scenario | RMSE inc | RMSE adp | dRMSE | RMSE paired p | FTF inc | FTF adp | dFTF | FTF paired p |
|---|---|---|---|---|---|---|---|---|
| clean_single | 6.19 | 5.59 | -0.59 | <0.001 | 10.77 | 9.33 | -1.43 | 0.050 |
| sensor_dropout | 9.39 | 8.51 | -0.88 | <0.001 | 8.07 | 7.27 | -0.80 | 0.102 |
| dropout_2s | 7.36 | 7.02 | -0.34 | 0.012 | 8.80 | 8.03 | -0.77 | 0.307 |
| dropout_5s | 9.39 | 8.51 | -0.88 | <0.001 | 8.07 | 7.27 | -0.80 | 0.102 |
| dropout_10s | 11.71 | 10.76 | -0.95 | <0.001 | 6.53 | 6.13 | -0.40 | 0.289 |
| degrade_1 | 10.47 | 9.60 | -0.87 | <0.001 | 7.13 | 6.00 | -1.13 | 0.588 |
| degrade_2 | 25.39 | 23.27 | -2.12 | <0.001 | 9.37 | 10.53 | +1.17 | 0.552 |
| degrade_3 | 32.77 | 30.17 | -2.60 | 0.002 | 2.37 | 2.83 | +0.47 | 0.593 |
| heavy_clutter | 23.04 | 21.30 | -1.74 | <0.001 | 14.60 | 11.40 | -3.20 | 0.023 |
| many_targets_6 | 23.49 | 22.43 | -1.06 | <0.001 | 28.37 | 31.63 | +3.27 | 0.259 |
| identity_conflict | 6.19 | 5.59 | -0.60 | <0.001 | 11.83 | 11.00 | -0.83 | 0.631 |

Dropout continuity, adaptive vs incumbent, is identical to three decimals:
sensor_dropout 1.000 to 1.000, dropout_2s 1.000 to 1.000, dropout_5s 1.000 to
1.000, dropout_10s 0.600 to 0.600. Zero seed-to-seed variance. The earned
continuity win is untouched.

Id switches move only within noise (all paired p above 0.05; largest single delta
is -0.60 at dropout_2s, p=0.059; identity_conflict -0.47, p=0.199).

## Criterion-by-criterion result (locked rules)

* (a) RMSE significantly LOWER in the two contested scenarios AND not
  significantly worse anywhere. PASS. heavy_clutter dRMSE -1.74 (p<0.001),
  many_targets_6 dRMSE -1.06 (p<0.001). Every scenario RMSE improved, and every
  RMSE paired p is at or below 0.012. No scenario got worse.
* (b) identity_conflict false-track frames NOT significantly higher than
  incumbent, and within the 1.0-frame identity-conflict guard. PASS. dFTF -0.83
  (a decrease), paired p=0.631 (not significant). The exact test that caught the
  global q=2.0 penalty in EXP-11 (there: +8.20 frames, p=0.035) came back clean
  here.
* (c) dropout continuity preserved. PASS. Identical at all four dropout
  scenarios (deltas 0.000).
* (d) no significant false-track OR id-switch INCREASE anywhere. PASS. The
  positive FTF deltas (many_targets_6 +3.27, degrade_2 +1.17, degrade_3 +0.47)
  are all non-significant (p=0.259, 0.552, 0.593). All id-switch deltas
  non-significant.
* (e) mode-share honesty guard: q_high share must be materially higher (by at
  least 0.10) in identity_conflict than in clean_single, to demonstrate the
  controller actually switches on the contested scenario rather than switching
  incidentally. FAIL. Evaluation q_high share was 0.256 in identity_conflict vs
  0.207 in clean_single, a difference of 0.049, below the 0.10 bar.

Sole failing criterion: (e). Per the locked "any partial pass is a full REJECT"
rule, the verdict is REJECT.

## Why (e) failed while (a) through (d) passed (post-hoc diagnosis)

This section is a post-hoc mechanism read. It is NOT used to overturn the verdict
and NOT used to move any threshold. The REJECT stands.

The controller ran q_low roughly 74 percent of the time in identity_conflict and
still did not reproduce the EXP-11 false-track penalty. That is a genuine and
favorable outcome, but it is NOT what the hypothesis predicted, and it is not
self-consistent as mechanism evidence:

1. The H=3 hysteresis warm-up forces every newly CONFIRMED track into q_high for
   its first 3 confirmed cycles, regardless of contested state. In clean_single,
   spurious false tracks continually spawn, confirm, and die (about 10
   false-track frames per run), and each one contributes 3 warm-up q_high cycles.
   That warm-up traffic inflates clean_single's q_high share to about 0.21.
2. Because the reported mode-share statistic conflates warm-up q_high with
   contested-driven q_high, it cannot separate scene-appropriate switching from
   incidental churn. The controller's q_high share in identity_conflict is barely
   above clean_single's, so the pre-registered evidence that it switches BECAUSE
   the scene is contested is absent.
3. Honest read of the favorable outcome: the RMSE gains are broadly the same
   universal low-q benefit EXP-11 already measured (low q helps RMSE everywhere),
   applied to the majority of tracks that qualified as uncontested. The clean
   identity_conflict false-track result is real but cannot be attributed to the
   contested signal, because the signal barely fired differentially there.

So EXP-12 cannot support the claim that CIF-LAAD "learned when to favor
localization." The outcomes look good; the pre-registered mechanism evidence does
not clear its own bar. We report the good outcomes and decline the mechanism
claim.

## What does and does not change

* q=8.0 remains the frozen v1 default. No change.
* The v1 engine remains byte-identical and frozen (SHA-256 8712f113...7ad45).
* EXP-11 Part A (ADOPT-WITH-DOCUMENTED-COST, pending internal adversarial review) and Part B (REJECTED,
  preserved in ciflaad_v2/) are unchanged. EXP-9 and EXP-10 verdicts unchanged.
* Nothing is published. This record awaits internal adversarial review,
  in the fixed order Zenodo, then GitHub, then the sites, only after approval.

## Optional follow-up (NOT run; needs a fresh internal go)

A cleaner mechanism diagnostic would separate contested-driven q_high from
warm-up q_high (for example, exclude the H warm-up cycles from the mode-share
statistic, or instrument the specific trigger that set q_high on each step). That
is a NEW hypothesis and would require its own pre-registration (call it EXP-13),
decided fresh by internal review. It is explicitly NOT a redefinition of EXP-12 and has not
been run. EXP-12 as pre-registered is REJECTED and closed.

## Reproduction

* Controller and experiment: exp12_adaptive_q.py
* Full results: out/exp12_adaptive_q.json
* Run log: out/exp12.log
* Pre-registration: EXP12_PREREGISTRATION.md
* Engine: frozen v1 (ciflaad/), external controller only, freeze manifest
  unaffected. numpy 2.2.6. 30 evaluation seeds (100 to 129), 15 calibration seeds
  (200 to 214). Wallclock about 592 s.
