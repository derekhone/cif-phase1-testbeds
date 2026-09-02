"""EXP-2 Dropout-duration stress. All sensors blind for D seconds; 40 held-out
seeds per D. dt=0.5 s so 0.25 s is below resolution and excluded (honest)."""
from __future__ import annotations
import json, sys, time
import numpy as np
from experiments.laad_series.common import run_once, agg, METRIC_KEYS
from experiments.laad_series import scenarios_ext as sx

SEEDS = list(range(100, 140))
DURATIONS = [0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 15.0]


def main():
    t0 = time.time()
    out = {"meta": {"experiment": "EXP-2 dropout-duration stress",
                    "seeds": SEEDS, "durations_s": DURATIONS,
                    "numpy": np.__version__, "python": sys.version.split()[0],
                    "note": "simulation-only; all sensors blind for D s; held-out seeds"},
           "results": {}}
    for D in DURATIONS:
        cif = {k: [] for k in METRIC_KEYS}
        base = {k: [] for k in METRIC_KEYS}
        for s in SEEDS:
            scen, drop = sx.dropout_duration(s, D)
            cm, bm = run_once(scen, drop)
            for k in METRIC_KEYS:
                cif[k].append(cm[k]); base[k].append(bm[k])
        out["results"][f"{D:g}s"] = {"cif": {k: agg(v) for k, v in cif.items()},
                                     "baseline": {k: agg(v) for k, v in base.items()}}
        print(f"[done] D={D:g}s  ({time.time()-t0:.1f}s)")
    out["meta"]["wallclock_s"] = round(time.time() - t0, 2)
    with open("experiments/laad_series/out/exp2_dropout.json", "w") as f:
        json.dump(out, f, indent=2)
    print("wrote exp2_dropout.json  wallclock", out["meta"]["wallclock_s"], "s")


if __name__ == "__main__":
    main()
