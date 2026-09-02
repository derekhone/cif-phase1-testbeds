"""EXP-4 Dense-crossing identity challenge. N in {2,4,8,16,32}; 30 held-out
seeds per N. Metrics of record: id_switches, false_track_frames."""
from __future__ import annotations
import json, sys, time
import numpy as np
from experiments.laad_series.common import run_once, agg, METRIC_KEYS
from experiments.laad_series import scenarios_ext as sx

SEEDS = list(range(100, 130))
NS = [2, 4, 8, 16, 32]


def main():
    t0 = time.time()
    out = {"meta": {"experiment": "EXP-4 dense-crossing identity",
                    "seeds": SEEDS, "n_targets": NS,
                    "numpy": np.__version__, "python": sys.version.split()[0],
                    "note": "simulation-only; crossing lanes + modest clutter"},
           "results": {}}
    for n in NS:
        cif = {k: [] for k in METRIC_KEYS + ["mean_latency_ms"]}
        base = {k: [] for k in METRIC_KEYS}
        for s in SEEDS:
            scen, drop = sx.dense_crossing(s, n)
            cm, bm = run_once(scen, drop)
            for k in METRIC_KEYS:
                cif[k].append(cm[k]); base[k].append(bm[k])
            cif["mean_latency_ms"].append(cm["mean_latency_ms"])
        out["results"][f"N={n}"] = {"cif": {k: agg(v) for k, v in cif.items()},
                                    "baseline": {k: agg(v) for k, v in base.items()}}
        print(f"[done] N={n}  ({time.time()-t0:.1f}s)")
    out["meta"]["wallclock_s"] = round(time.time() - t0, 2)
    with open("experiments/laad_series/out/exp4_dense.json", "w") as f:
        json.dump(out, f, indent=2)
    print("wrote exp4_dense.json  wallclock", out["meta"]["wallclock_s"], "s")


if __name__ == "__main__":
    main()
