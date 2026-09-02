# CIF-LAAD

**A sensor-agnostic low-altitude assurance layer for maintaining track
continuity, false-track suppression, uncertainty and evidence provenance
when observations degrade or conflict.**

> STATUS: RESEARCH ONLY. TRL 3. SIMULATION-ONLY. Zero hardware, zero real
> sensor data. This is a falsification and validation project - not a market
> entry. See `FINAL_RF_REVIEW.md` for the Stage 0 honest verdict and
> `validation/RESULTS.md` for the preregistered validation series.

## What CIF-LAAD does (and what it costs)

CIF-LAAD adds three things to an ordinary multi-sensor tracker: track
inheritance that survives total sensor dropout, a per-track coherence/confidence
signal that a contradiction can veto (fail-closed), and a tamper-evident
hash-linked evidence chain. It explicitly trades localization precision for
continuity, provenance, and clutter resilience inside a bounded
degraded/contested envelope. It is a cueing/assurance layer that hands off to
something else - not a primary tracker.

## Validation series (preregistered, simulation-only)

A preregistered 8-unit validation series (EXP-1 through EXP-8) with frozen
engine (SHA-256 manifest), held-out seeds (100-129, disjoint from published
0-24), and one-command reproduction. Nothing was retuned to win. The falsified
coherence-gate mode was run and kept in the record.

**Earned envelope:**

- Continuity through multi-second sensor dropout, bounded to ~5s full / degrading past ~10s
- False-track suppression under clutter and dense crossing, at all densities tested
- Id-switch suppression, bounded to clutter and LOW target density (N<=4) and heavy sensor degradation (K=3)
- Tamper-EVIDENT provenance (not tamper-proof)
- Typed rejection of malformed, stale, future, and replayed observations

**Cost (always reported alongside):** localization RMSE penalty of ~1.3x-4x
versus the baseline whenever contested. Structural, not a tuning bug.

**Killed/narrowed:** coherence-gate inheritance stays falsified; id-stability
does NOT scale past ~4 simultaneous crossers (inverts at N>=8); zero advantage
in clean single-target scenarios; real-time throughput bounded to ~50 tracks in
this pure-Python build; a lone schema-valid spoof at a plausible position is not
rejected; no certified third-party benchmark was run.

**PRECONDITION FOR COMPARATIVE CLAIMS:** no certified third-party tracker
(Stone-Soup, SORT/DeepSORT) was run. All wins are relative to the frozen
in-house single-hypothesis baseline only. Comparative language is blocked until
a Stone-Soup or equivalent benchmark runs on the identical frozen scenarios.

**Zenodo DOI:** [10.5281/zenodo.22255738](https://doi.org/10.5281/zenodo.22255738)

Track-identity stability (id-switch suppression) is a bounded secondary
benefit, not a primary claim.

## Layout

```
ciflaad/        core library (observation, kalman, correlation, evidence,
                coherence, confidence, track, fusion, baseline)
sim/            synthetic scenarios + metrics
experiments/    25-seed comparison harness -> EXPERIMENT_LEDGER.md
validation/     preregistered 8-unit validation series (see below)
bench/          latency/memory/overload -> BENCHMARK.md
security/       17-case adversarial harness -> SECURITY.md
api/            data contracts, JSON schemas, real sample JSON, adapter doc
docs/           hostile review, kill criteria, claim discipline, readiness,
                TRL/boundaries, customer reality test
customer/       technical-evaluation packet + per-org variants + pilot criteria
FINAL_RF_REVIEW.md   adversarial 0-100 review and verdict (Stage 0)
```

### Validation series files

```
validation/
  PREREGISTRATION.md     frozen before any runs
  FREEZE_MANIFEST.txt    per-file SHA-256 of the frozen engine
  RESULTS.md             complete series synthesis
  EXP1_RESULTS.md        EXP-1 per-mode tables + Pareto frontier
  REPRODUCE.md           one-command reproduction guide
  EXPECTED_OUTPUTS.sha256  SHA-256 of every out/*.json
  run_series.sh          one-command replay (~25-30 min)
  common.py              shared run utilities
  scenarios_ext.py       extended scenario factories
  exp[1-8]_*.py          individual experiment runners
  analyze_*.py           analysis scripts
  out/*.json             raw machine-readable results
```

## Reproduce everything

### Stage 0 (original 25-seed study)
```
python -m experiments.run_experiments --seeds 25   # EXPERIMENT_LEDGER.md
python -m bench.benchmark                           # BENCHMARK.md
python -m security.harness                          # SECURITY.md (17/17)
python -m api.make_samples                          # api/samples/*.json
```

### Validation series (preregistered)
```
bash validation/run_series.sh
```
Runs all 8 experiments, synthesizes RESULTS.md, and verifies SHA-256 hashes.
Environment: Python 3.11.6, numpy 2.2.6, scipy 1.14.1. All RNG seeded.

## The boundary (Proof Before Power)

SENSE -> CORRELATE -> TRACK -> EVALUATE COHERENCE -> PRODUCE EVIDENCE -> HAND
OFF. CIF-LAAD stops at the C2 handoff. It never authorizes and never executes.
There is no offensive or counter-UAS capability in this codebase, by design. It
may optionally publish a track + evidence head to an external ExecutionProof
authorization layer as read-only evidence; that handoff is a documented stub.

## What to do next

- Run a Stone-Soup GNN/JPDA and SORT baseline on the identical frozen scenarios (the blocking precondition for any comparative claim)
- Run on ONE real recorded dataset (lawful, non-sensitive)
- If the envelope holds under third-party benchmark, pursue a pilot integration

Claims kept narrower than the evidence.
