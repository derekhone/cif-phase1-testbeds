"""Run the CIF-vs-baseline experiment suite and write the evidence ledger.

Usage:
    python -m experiments.run_experiments [--seeds N]

For every scenario it runs N seeded realisations through BOTH the CIF-LAAD
FusionEngine and the fair BaselineTracker, scores each with the same metrics,
and writes:
    experiments/ledger.json            (machine-readable, full detail)
    experiments/EXPERIMENT_LEDGER.md   (human-readable summary tables)

No numbers are hand-entered. Everything in the ledger is produced here.
"""
from __future__ import annotations
import argparse
import json
import statistics
import sys
import time
from typing import Dict, List, Any

import numpy as np

from ciflaad.fusion import FusionEngine, FusionConfig
from ciflaad.baseline import BaselineTracker
from sim import metrics
from experiments import scenarios
from experiments.adapters import cif_estimates, baseline_estimates


def run_once(scen, dropout_windows, cfg=None):
    eng = FusionEngine(cfg or FusionConfig())
    base = BaselineTracker()
    cif_timeline: List[Dict[str, Any]] = []
    base_timeline: List[Dict[str, Any]] = []
    cif_latencies: List[float] = []
    for t, truth, obs in scen.frames():
        r = eng.process(obs, t)
        cif_latencies.append(r.latency_s)
        base.process(obs, t)
        truth_np = {k: np.asarray(v) for k, v in truth.items()}
        cif_timeline.append({"t": t, "truth": truth_np,
                             "estimates": cif_estimates(eng)})
        base_timeline.append({"t": t, "truth": truth_np,
                              "estimates": baseline_estimates(base)})
    cif_m = metrics.evaluate(cif_timeline, dropout_windows=dropout_windows)
    base_m = metrics.evaluate(base_timeline, dropout_windows=dropout_windows)
    cif_m["mean_latency_ms"] = float(np.mean(cif_latencies) * 1e3)
    cif_m["evidence_ok"] = eng.verify_all_evidence()
    return cif_m, base_m


def _agg(values: List[float]) -> Dict[str, float]:
    vals = [v for v in values if v == v]  # drop nan
    if not vals:
        return {"mean": float("nan"), "std": float("nan"), "n": 0}
    return {"mean": float(statistics.mean(vals)),
            "std": float(statistics.pstdev(vals)) if len(vals) > 1 else 0.0,
            "n": len(vals)}


METRIC_KEYS = ["position_rmse_m", "id_switches", "continuity",
               "dropout_continuity", "false_track_frames", "mean_reacq_s",
               "nees_mean", "nees_p95_ok"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=25)
    ap.add_argument("--mode", type=str, default="gated",
                    choices=["legacy", "batch", "gated"],
                    help="inheritance algorithm under test")
    ap.add_argument("--out", type=str, default="experiments/ledger",
                    help="output path prefix (.json / .md appended)")
    args = ap.parse_args()
    cfg = FusionConfig(inherit_mode=args.mode,
                       coherence_gated_inherit=(args.mode == "gated"))

    t_start = time.time()
    results: Dict[str, Any] = {}
    for name, factory in scenarios.ALL.items():
        cif_runs: Dict[str, List[float]] = {k: [] for k in METRIC_KEYS + ["mean_latency_ms"]}
        base_runs: Dict[str, List[float]] = {k: [] for k in METRIC_KEYS}
        evidence_all_ok = True
        for seed in range(args.seeds):
            scen, drop = factory(seed)
            cif_m, base_m = run_once(scen, drop, cfg)
            for k in METRIC_KEYS:
                cif_runs[k].append(cif_m[k])
                base_runs[k].append(base_m[k])
            cif_runs["mean_latency_ms"].append(cif_m["mean_latency_ms"])
            evidence_all_ok = evidence_all_ok and cif_m["evidence_ok"]
        results[name] = {
            "seeds": args.seeds,
            "cif": {k: _agg(v) for k, v in cif_runs.items()},
            "baseline": {k: _agg(v) for k, v in base_runs.items()},
            "evidence_all_ok": evidence_all_ok,
        }
        print(f"[done] {name}  ({args.seeds} seeds)")

    meta = {
        "generated_by": "experiments/run_experiments.py",
        "seeds_per_scenario": args.seeds,
        "wallclock_s": round(time.time() - t_start, 2),
        "numpy": np.__version__,
        "python": sys.version.split()[0],
        "note": "All values simulation-only. No hardware, no real sensor data.",
        "inherit_mode": cfg.inherit_mode,
        "coherence_gated_inherit": cfg.coherence_gated_inherit,
        "inherit_gate_p": cfg.inherit_gate_p,
        "inherit_min_support": cfg.inherit_min_support,
    }
    out = {"meta": meta, "results": results}
    with open(args.out + ".json", "w") as f:
        json.dump(out, f, indent=2)
    _write_markdown(out, args.out + ".md")
    print(f"\nWrote {args.out}.json and {args.out}.md")
    print(f"Wallclock {meta['wallclock_s']}s")


def _fmt(agg):
    if agg["n"] == 0:
        return "n/a"
    return f"{agg['mean']:.3g} +/- {agg['std']:.2g}"


def _write_markdown(out, md_path="experiments/EXPERIMENT_LEDGER.md"):
    lines = []
    lines.append("# CIF-LAAD Experiment Ledger\n")
    mode = out["meta"].get("inherit_mode", "gated")
    lines.append(f"Inheritance mode: **{mode}** "
                 f"(inherit_gate_p={out['meta'].get('inherit_gate_p')}, "
                 f"inherit_min_support={out['meta'].get('inherit_min_support')}).\n")
    lines.append("All values below are produced by `experiments/run_experiments.py`. "
                 "They are SIMULATION-ONLY. No hardware, no real sensor data, no "
                 "field trial. Reproduce with:\n")
    lines.append("```\npython -m experiments.run_experiments --seeds %d\n```\n"
                 % out["meta"]["seeds_per_scenario"])
    m = out["meta"]
    lines.append(f"Environment: Python {m['python']}, numpy {m['numpy']}, "
                 f"{m['seeds_per_scenario']} seeds/scenario, "
                 f"wallclock {m['wallclock_s']}s.\n")
    metric_labels = {
        "position_rmse_m": "Position RMSE (m) [lower better]",
        "id_switches": "ID switches [lower better]",
        "continuity": "Track continuity [higher better]",
        "dropout_continuity": "Continuity during dropout [higher better]",
        "false_track_frames": "False-track frames [lower better]",
        "mean_reacq_s": "Mean reacquisition time (s) [lower better]",
        "nees_mean": "NEES mean (ideal ~3.0)",
        "nees_p95_ok": "NEES fraction <= chi2.95 (ideal ~0.95)",
    }
    for name, res in out["results"].items():
        lines.append(f"\n## Scenario: {name}\n")
        lines.append("| Metric | CIF-LAAD | Baseline |")
        lines.append("|---|---|---|")
        for k in METRIC_KEYS:
            lines.append(f"| {metric_labels[k]} | {_fmt(res['cif'][k])} | "
                         f"{_fmt(res['baseline'][k])} |")
        lines.append(f"| CIF mean latency/cycle (ms) | {_fmt(res['cif']['mean_latency_ms'])} | - |")
        lines.append(f"| Evidence chain verified | {res['evidence_all_ok']} | n/a |")
    with open(md_path, "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
