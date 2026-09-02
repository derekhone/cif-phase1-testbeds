# 07 - Coherence-Gated Inheritance: Pre-Registered Experiment and Result

**Status: SIMULATION-ONLY. TRL 3. No hardware, no real sensor data, no field trial, no independent validation.**

## Why this experiment ran

The pre-experiment CIF prototype had one disqualifying weakness (documented in `docs/01_HOSTILE_SELF_REVIEW.md` and `docs/02_KILL_CRITERIA.md`): in `heavy_clutter`, CIF's track-inheritance re-linked coasting tracks onto clutter false-alarms. Compared to the fair baseline it produced far worse position RMSE (25.5 m vs 6.22 m), lower continuity (0.775 vs 0.986), and MORE false-track frames (103 vs 76). The same inheritance is what produces CIF's one decisive advantage - continuity during total sensor dropout (1.0 vs 0.3) and no permanent track loss.

Governing question (unchanged): *does CIF produce measurable value beyond ordinary fusion, without a disqualifying liability?* The pre-committed next step was to test whether **coherence-gated inheritance** could stop inheritance from adopting clutter WITHOUT losing the dropout win.

## Pre-registered hypothesis (frozen before the held-out runs)

> A coasting track should be revived to CONFIRMED only when the re-link is CORROBORATED: it must fall inside a TIGHTER re-link gate than the association gate (chi-square df=3 at p=0.95 = 7.815, vs p=0.99 = 11.345), **and** be supported by at least `inherit_min_support = 2` independent unassigned observations gating to the same predicted state in the same cycle. Rationale, fixed by engineering not by the test set: a genuine target re-emerging from dropout is seen by >=2 of the 3 simultaneous sensors with high probability, while a lone clutter false-alarm rarely has a co-located corroborator.

The threshold values were fixed from that rationale and NOT swept against the clutter set. Three inheritance modes were then implemented behind one toggle so the same code, same seeds, same metrics compare cleanly:

- **legacy** - the original one-obs-at-a-time revive on the first blip in the wide gate (the pre-experiment CIF, preserved verbatim).
- **batch** - a coasting id may absorb ALL its gated unassigned obs in one cycle, greedy best-fit; wide gate, support 1.
- **gated** - the pre-registered hypothesis: tighter re-link gate + support >= 2.

## Result (25 seeds/scenario, identical seeds across all modes, simulation-only)

Position RMSE (m) and false-track frames are the two metrics the hypothesis targeted; dropout continuity is the win that had to be preserved. Lower is better except continuity.

### heavy_clutter (the regression under test)

| Metric | Baseline | LEGACY (original) | BATCH | GATED (hypothesis) |
|---|---|---|---|---|
| Position RMSE (m) | 6.22 | 25.5 | 24.9 | **32.8** |
| Track continuity | 0.986 | 0.775 | **0.902** | 0.805 |
| False-track frames | 76.1 | 103 | **15.0** | 49.1 |
| ID switches | 6.88 | 3.0 | **0.6** | 5.76 |
| Mean reacquisition (s) | n/a | 1.82 | 1.24 | 2.58 |

### sensor_dropout (the win that had to survive)

| Metric | Baseline | LEGACY | BATCH | GATED |
|---|---|---|---|---|
| Continuity during dropout | 0.3 | 1.0 | **1.0** | **1.0** |
| Position RMSE (m) | 6.91 | 8.79 | 9.08 | 9.1 |
| Track continuity | 0.888 | 0.988 | 0.988 | 0.988 |

### many_targets_6 (the other dense regime)

| Metric | Baseline | LEGACY | BATCH | GATED |
|---|---|---|---|---|
| Position RMSE (m) | 6.24 | 22.9 | 22.0 | 27.1 |
| Track continuity | 0.987 | 0.881 | **0.915** | 0.858 |
| False-track frames | 112 | 77.0 | **29.3** | 86.6 |
| ID switches | 16.8 | 5.88 | **4.56** | 15.0 |

Benign scenarios (`clean_single`, `identity_conflict`, `crossing_two`) were unchanged to 3 significant figures across all three modes - inheritance rarely fires when tracks are continuously observed. Full tables: `experiments/ledger_legacy.md`, `experiments/ledger_batch.md`, `experiments/ledger_gated.md`. Per-cycle latency stayed sub-6 ms in the worst (clutter) case for all modes.

## Verdict: the pre-registered hypothesis is FALSIFIED

The coherence gate did **not** fix the clutter regression. On identical seeds it made `heavy_clutter` and `many_targets_6` WORSE than both the original and the plain batch policy: higher RMSE (32.8 vs 25.5), lower continuity (0.805 vs 0.902), and MORE false-track frames than batch (49.1 vs 15.0).

Mechanism, confirmed by the numbers: requiring 2 corroborators plus a tighter gate causes genuine coasting targets - which in many cycles are seen by only one sensor - to FAIL to re-link. They then expire and a brand-new track spawns in their place, which both fragments continuity and increases false-track frames. The gate suppressed the good re-links more than the bad ones.

## The real, honest finding: the win came from BATCHING, not from gating

The one change that helped was letting a single coasting id absorb all of its gated unassigned observations in one cycle (batch, greedy best-fit) instead of one blip reviving it while the remaining co-located obs spawn fresh tracks. On identical seeds, batch inheritance:

- cut `heavy_clutter` false-track frames from 103 (legacy) to 15.0 - now well BELOW the baseline's 76.1;
- cut `many_targets_6` false-track frames from 77.0 to 29.3 - also below baseline (112);
- improved continuity in both dense regimes (0.775 -> 0.902; 0.881 -> 0.915);
- reduced ID switches everywhere;
- and PRESERVED the decisive dropout win (continuity during dropout 1.0 vs baseline 0.3).

`batch` is therefore now the default inheritance mode. This is a de-duplication effect (fewer spurious spawns), not a coherence proof - honest naming matters here.

## What is STILL not fixed - the persistent liability

Batch does NOT resolve the position-accuracy regression. Under clutter and dense multi-target, ALL CIF variants remain roughly 4-5x worse than the baseline on position RMSE (clutter 24.9 vs 6.22; dense 22.0 vs 6.24). Absorbing corroborating-but-noisy observations into a coasting track avoids spawning a new false track, but it still pulls that track's estimate off the truth. The mechanism that buys continuity under dropout is the same mechanism that costs accuracy under clutter - reducing one without the other was not achieved here.

## Effect on the kill criteria (`docs/02_KILL_CRITERIA.md`, `customer/PILOT_ACCEPTANCE.md` A4)

- The clutter false-track / continuity half of the regression is now **bounded** and even beats the baseline. PARTIAL pass.
- The clutter/dense **position-RMSE regression is NOT bounded**. It remains a severe, unresolved liability. The A4 criterion ("CIF's clutter regression is bounded") is therefore only partially met - false-track and continuity yes, RMSE no.

Honest overall read: CIF has exactly one robust, reproducible advantage (continuity through total sensor dropout, plus lower false-track and ID-switch counts under clutter after batching). It carries one robust, reproducible liability (position accuracy under clutter/dense). The pre-registered coherence gate did not remove that liability, and pretending otherwise would violate the standard this program is held to. The next honest decision is a scoping one, not a tuning one: either (a) restrict the claimed operating envelope to dropout-dominated, accuracy-tolerant regimes where CIF wins, or (b) escalate the kill decision for the clutter/dense regimes. No production, certification, or field claim is made or implied.

Reproduce:

```
python -m experiments.run_experiments --seeds 25 --mode legacy --out experiments/ledger_legacy
python -m experiments.run_experiments --seeds 25 --mode batch  --out experiments/ledger_batch
python -m experiments.run_experiments --seeds 25 --mode gated  --out experiments/ledger_gated
```