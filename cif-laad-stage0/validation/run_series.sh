#!/usr/bin/env bash
# One-command reproduction of the CIF-LAAD validation series.
# Simulation-only, TRL 3, RESEARCH ONLY. Deterministic given the frozen engine
# and the seeds baked into each runner. Re-running must reproduce the SHA-256
# values in EXPECTED_OUTPUTS.sha256 (bitwise, on the same numpy/python).
set -euo pipefail
cd "$(dirname "$0")/../.."          # repo root (parent of experiments/)

echo "[1/8] EXP-1 accuracy-continuity frontier (longest, ~15 min)"
python3 -m experiments.laad_series.exp1_frontier
echo "[2/8] EXP-2 dropout-duration stress"
python3 -m experiments.laad_series.exp2_dropout
echo "[3/8] EXP-3 sensor-degradation matrix"
python3 -m experiments.laad_series.exp3_degradation
echo "[4/8] EXP-4 dense-crossing identity"
python3 -m experiments.laad_series.exp4_dense
echo "[5/8] EXP-5 false-observation resilience"
python3 -m experiments.laad_series.exp5_false_obs
echo "[6/8] EXP-6 evidence tamper challenge"
python3 -m experiments.laad_series.exp6_tamper
echo "[7/8] EXP-8 scale test"
python3 -m experiments.laad_series.exp8_scale
echo "[8/8] synthesize RESULTS.md + EXP1_RESULTS.md + expected-output SHAs"
python3 -m experiments.laad_series.analyze_exp1
python3 -m experiments.laad_series.analyze_all
echo
echo "Verifying expected-output hashes:"
sha256sum -c experiments/laad_series/EXPECTED_OUTPUTS.sha256 || {
  echo "WARNING: outputs differ from the frozen record (numpy/python mismatch?)." >&2; exit 1; }
grep -v "^combined" experiments/laad_series/FREEZE_MANIFEST.txt | sha256sum -c || { echo "WARNING: engine files differ from the freeze manifest." >&2; exit 1; }
echo "OK - series reproduced and hashes match."
