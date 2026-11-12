# CIF-LAAD Validation Series - Reproducibility Package

Simulation-only. TRL 3. RESEARCH ONLY. This public repository preserves the
historical research record but is **not a complete executable reproduction
package**: only 2 of the 14 frozen engine files are included. The other 12 are
access-controlled. Complete Stage 0 reruns require a separately authorized
implementation tree, access review, and applicable use terms. See the
[controlled-access policy](../../cif-laad-characterization/README.md).
No independent third-party reproduction or validation is claimed.

The repository root LICENSE and LICENSE-SCOPE.md describe existing public
license information; this guide grants no new rights to withheld source.
For results, cite only the unchanged canonical validation/RESULTS.md
(SHA-256 a62eb760f5b77d52a23067fa4b7abe8327ec67c6d9b264b4c1f1882cb6bd1557)
or Zenodo DOI 10.5281/zenodo.22255738. A newly generated RESULTS.md
is not the canonical historical report.

## What is frozen

- Engine: 14 files. The authoritative integrity check is the set of per-file
  SHA-256 hashes in `FREEZE_MANIFEST.txt`. Verify them directly with:
  ```bash
  # This check requires the complete authorized engine and its manifest.
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

## Reproduction in an authorized complete implementation tree

```bash
# from the repo root (parent of experiments/)
bash experiments/laad_series/run_series.sh
```

This runs EXP-1..EXP-8 in order and generates reports and experiment JSON.
It is not runnable from this public checkout. The script also regenerates
`EXPECTED_OUTPUTS.sha256` before its checksum check; therefore that check
must not be described as independent verification against untouched
historical outputs. Compare outputs against the separately preserved frozen
record, treating timing values separately. The regenerated `RESULTS.md`
may omit claim restrictions and must not be cited as canonical.
Total wallclock is roughly 25-30 minutes (EXP-1 ~15 min and EXP-4 N=32 ~6 min
dominate; the pure-Python engine is single-threaded).

Run a single unit instead (authorized complete tree only):

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
- The comparator is the frozen in-tree single-hypothesis `BaselineTracker`. No
  certified third-party library (Stone-Soup, SORT/DeepSORT) was run. Wins are
  relative to a reasonable in-house baseline only. Comparative-performance
  language ("better than," "outperforms," "state-of-the-art") is BLOCKED until
  a Stone-Soup or equivalent benchmark runs on the identical frozen scenarios.
- CIF trades localization RMSE (roughly 1.3x-4x worse under clutter) for
  continuity, id-stability and provenance. Report the cost with every win.
- The id-stability advantage is bounded to low target density (N<=4) and
  inverts at N>=8. The dropout-continuity advantage is bounded to ~5s gaps.
  Real-time throughput is bounded to ~50 tracks in this pure-Python build.
- Provenance is tamper-EVIDENT, not tamper-proof. Uncertainty is not claimed to
  be better-calibrated than the baseline (NEES does not support that).
- The coherence-gate inheritance mode is FALSIFIED and kept in the record; it is
  not a recommended configuration. The original `run_experiments.py` defaults
  to this `gated` mode. Always supply `--mode` explicitly for that harness.

Built in faith. Tested in public. Claims kept narrower than the evidence.
