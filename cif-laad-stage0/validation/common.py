"""Shared run helpers for the validation series. Uses only frozen engine APIs."""
from __future__ import annotations
import statistics
from typing import Dict, List, Any
import numpy as np

from ciflaad.fusion import FusionEngine, FusionConfig
from ciflaad.baseline import BaselineTracker
from sim import metrics
from experiments.adapters import cif_estimates, baseline_estimates

METRIC_KEYS = ["position_rmse_m", "id_switches", "continuity",
               "dropout_continuity", "false_track_frames", "mean_reacq_s",
               "nees_mean", "nees_p95_ok"]


def run_once(scen, dropout_windows, cfg=None):
    """Run one seeded realisation through CIF + baseline; return (cif_m, base_m).
    Mirrors experiments/run_experiments.run_once exactly (frozen adapters)."""
    eng = FusionEngine(cfg or FusionConfig())
    base = BaselineTracker()
    cif_tl: List[Dict[str, Any]] = []
    base_tl: List[Dict[str, Any]] = []
    lat: List[float] = []
    for t, truth, obs in scen.frames():
        r = eng.process(obs, t)
        lat.append(r.latency_s)
        base.process(obs, t)
        truth_np = {k: np.asarray(v) for k, v in truth.items()}
        cif_tl.append({"t": t, "truth": truth_np, "estimates": cif_estimates(eng)})
        base_tl.append({"t": t, "truth": truth_np, "estimates": baseline_estimates(base)})
    cif_m = metrics.evaluate(cif_tl, dropout_windows=dropout_windows)
    base_m = metrics.evaluate(base_tl, dropout_windows=dropout_windows)
    cif_m["mean_latency_ms"] = float(np.mean(lat) * 1e3)
    cif_m["evidence_ok"] = eng.verify_all_evidence()
    return cif_m, base_m


def agg(values: List[float]) -> Dict[str, float]:
    vals = [v for v in values if v == v]
    if not vals:
        return {"mean": float("nan"), "std": float("nan"), "n": 0}
    return {"mean": float(statistics.mean(vals)),
            "std": float(statistics.pstdev(vals)) if len(vals) > 1 else 0.0,
            "n": len(vals)}


def fmt(a) -> str:
    if a["n"] == 0:
        return "n/a"
    return f"{a['mean']:.3g} +/- {a['std']:.2g}"
