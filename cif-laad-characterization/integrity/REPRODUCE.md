# CIF-LAAD Validation Series - Reproducibility Package

Simulation-only. TRL 3. RESEARCH ONLY. This package lets anyone re-run the
entire preregistered validation series and check the results bit-for-bit against
the frozen record. It does NOT claim any independent validation was performed -
no outside engineer or third party reran this series. It is here so that anyone
who wants to rerun it can, and get the same numbers.

## What is frozen

- Engine: 14 files. The authoritative integrity check is the set of per-file
  SHA-256 hashes in `FREEZE_MANIFEST.txt`. Verify them directly with:
  ```bash
  grep -v '^combined' experiments/laad_series/FREEZE_MANIFEST.txt | sha256sum -c
  ```
  The single `combined` value
  `8712f1138bdd20090b9a1b6eda58cebc5c274a843b960d6784e8650b7ea7ad45` is the
  SHA-256 of those per-file hash lines (a manifest fingerprint), not a hash of
  the concatenated file bytes; it changes if any per-file hash changes.
- Environment: Python 3.11.6, numpy 2.2.6, scipy 1.14.1.
- Preregistration (written and hashed BEFORE the runs): `PREREGISTRATION.md`.
- Held-out seeds start at 100 (disjoint from the published seeds 0-24). Seeds are
  baked into each runner; they are replications within an experimental unit, not
  separate experiments.
- Expected machine outputs: `EXPECTED_OUTPUTS.sha256` (SHA-256 of every
  `out/*.json`).

## One-command reproduction

Note: the scripts referenced in this section (`run_series.sh`, the
`experiments.laad_series.*` modules, and the CIF-LAAD engine they import) are
part of the controlled CIF-LAAD implementation repository. They are NOT included
in this public research packet. The commands are documented here for provenance
and for reviewers granted controlled-repository access; they will not run against
the public packet alone.

```bash
# from the repo root (parent of experiments/)
bash experiments/laad_series/run_series.sh
```

This runs EXP-1..EXP-8 in order, regenerates `RESULTS.md`, `EXP1_RESULTS.md`
and the per-experiment JSON, then runs `sha256sum -c` against
`EXPECTED_OUTPUTS.sha256`. On the frozen environment every hash must match.
Total wallclock is roughly 25-30 minutes (EXP-1 ~15 min and EXP-4 N=32 ~6 min
dominate; the pure-Python engine is single-threaded).

Run a single unit instead:

```bash
python3 -m experiments.laad_series.exp1_frontier   # writes out/exp1_frontier.json
```

## Experimental units

| unit | file | what it answers |
|---|---|---|
| EXP-1 | exp1_frontier.py | accuracy/continuity frontier over 7 operating modes x 6 scenarios x 30 seeds |
| EXP-2 | exp2_dropout.py | how long CIF holds continuity as the blind-gap duration grows |
| EXP-3 | exp3_degradation.py | advantage vs baseline as K sensors are degraded |
| EXP-4 | exp4_dense.py | id-stability / false-track behavior vs target density N |
| EXP-5 | exp5_false_obs.py | typed rejection of hostile obs; resilience to a plausible spoof |
| EXP-6 | exp6_tamper.py | evidence-chain tamper-evidence (4 tamper ops) |
| EXP-7 | (folded into RESULTS.md) | benchmark-matrix comparator honesty |
| EXP-8 | exp8_scale.py | per-cycle latency / memory vs track count |

## Claim limits (read before citing any number)

- Everything here is a discrete-time simulation. No hardware, no real sensor
  feeds, no fielded deployment. Numbers do not transfer to a real RF/EO/IR
  environment without further work.
- Historical note (retained verbatim, superseded 2026-09-02): "The comparator
  is the frozen in-tree single-hypothesis `BaselineTracker`. No certified
  third-party library (Stone-Soup, SORT/DeepSORT) was run. Wins are relative to
  a reasonable in-house baseline only. Comparative-performance language ('better
  than,' 'outperforms,' 'state-of-the-art') is BLOCKED until a Stone-Soup or
  equivalent benchmark runs on the identical frozen scenarios."
- Current status (2026-09-02): the blocking precondition above has been
  discharged. Two certified third-party trackers from the DSTL Stone Soup
  library were run on the identical frozen scenarios and seeds: the Stone Soup
  GNN tracker (EXP-9) and the Stone Soup JPDA tracker (EXP-14). Comparative
  statements are therefore permitted only where they are supported by those
  head-to-head benchmarks, must cite EXP-9 or EXP-14, and must report the
  associated costs (see the preserved-failures ledger). Absolute
  "state-of-the-art" claims remain BLOCKED: all results are simulation-only
  (TRL 3) and have received no independent third-party validation.
- CIF trades localization RMSE (roughly 1.3x-4x worse under clutter) for
  continuity, id-stability and provenance. Report the cost with every win.
- The id-stability advantage is bounded to low target density (N<=4) and
  inverts at N>=8. The dropout-continuity advantage is bounded to ~5s gaps.
  Real-time throughput is bounded to ~50 tracks in this pure-Python build.
- Provenance is tamper-EVIDENT, not tamper-proof. Uncertainty is not claimed to
  be better-calibrated than the baseline (NEES does not support that).
- The coherence-gate inheritance mode is FALSIFIED and kept in the record; it is
  not a recommended configuration.

Built in faith. Tested in public. Claims kept narrower than the evidence.
