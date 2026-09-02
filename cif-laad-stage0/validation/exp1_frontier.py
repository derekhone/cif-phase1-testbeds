"""EXP-1 Accuracy-continuity frontier.

Freeze everything except inheritance behavior; sweep 7 preregistered operating
modes over the 6 frozen scenarios, 30 held-out seeds (100..129) each.
"""
from __future__ import annotations
import json, sys, time
import numpy as np
from ciflaad.fusion import FusionConfig
from experiments import scenarios
from experiments.laad_series.common import run_once, agg, METRIC_KEYS

SEEDS = list(range(100, 130))

MODES = {
    "M_legacy":       dict(inherit_mode="legacy"),
    "M_batch":        dict(inherit_mode="batch"),
    "M_gated":        dict(inherit_mode="gated", coherence_gated_inherit=True),
    "M_batch_short":  dict(inherit_mode="batch", inherit_window_s=3.0),
    "M_batch_long":   dict(inherit_mode="batch", inherit_window_s=10.0),
    "M_batch_patient":dict(inherit_mode="batch", coast_misses=5, delete_misses=12),
    "M_batch_eager":  dict(inherit_mode="batch", coast_misses=2, delete_misses=6),
}


def main():
    t0 = time.time()
    out = {"meta": {"experiment": "EXP-1 accuracy-continuity frontier",
                    "seeds": SEEDS, "modes": {k: v for k, v in MODES.items()},
                    "numpy": np.__version__, "python": sys.version.split()[0],
                    "note": "simulation-only; held-out seeds 100-129"},
           "results": {}}
    for mode, kw in MODES.items():
        out["results"][mode] = {}
        for name, factory in scenarios.ALL.items():
            cif = {k: [] for k in METRIC_KEYS + ["mean_latency_ms"]}
            base = {k: [] for k in METRIC_KEYS}
            ev_ok = True
            for s in SEEDS:
                scen, drop = factory(s)
                cfg = FusionConfig(**kw)
                cm, bm = run_once(scen, drop, cfg)
                for k in METRIC_KEYS:
                    cif[k].append(cm[k]); base[k].append(bm[k])
                cif["mean_latency_ms"].append(cm["mean_latency_ms"])
                ev_ok = ev_ok and cm["evidence_ok"]
            out["results"][mode][name] = {
                "cif": {k: agg(v) for k, v in cif.items()},
                "baseline": {k: agg(v) for k, v in base.items()},
                "evidence_all_ok": ev_ok}
        print(f"[done] mode {mode}  ({time.time()-t0:.1f}s elapsed)")
    out["meta"]["wallclock_s"] = round(time.time() - t0, 2)
    with open("experiments/laad_series/out/exp1_frontier.json", "w") as f:
        json.dump(out, f, indent=2)
    print("wrote exp1_frontier.json  wallclock", out["meta"]["wallclock_s"], "s")


if __name__ == "__main__":
    main()
