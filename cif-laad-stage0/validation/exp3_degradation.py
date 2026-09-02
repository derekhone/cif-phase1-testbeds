"""EXP-3 Sensor-degradation matrix. Degrade K in {1,2,3} sensors; 30 held-out
seeds per cell. K=0 included as the benign reference."""
from __future__ import annotations
import json, sys, time
import numpy as np
from experiments.laad_series.common import run_once, agg, METRIC_KEYS
from experiments.laad_series import scenarios_ext as sx

SEEDS = list(range(100, 130))
KS = [0, 1, 2, 3]


def main():
    t0 = time.time()
    out = {"meta": {"experiment": "EXP-3 sensor-degradation matrix",
                    "seeds": SEEDS, "k_degraded": KS,
                    "numpy": np.__version__, "python": sys.version.split()[0],
                    "note": "simulation-only; x4 sigma + Pd 0.4 + mid dropout on K sensors"},
           "results": {}}
    for k in KS:
        cif = {kk: [] for kk in METRIC_KEYS}
        base = {kk: [] for kk in METRIC_KEYS}
        for s in SEEDS:
            scen, drop = sx.degradation(s, k)
            cm, bm = run_once(scen, drop)
            for kk in METRIC_KEYS:
                cif[kk].append(cm[kk]); base[kk].append(bm[kk])
        out["results"][f"K={k}"] = {"cif": {kk: agg(v) for kk, v in cif.items()},
                                    "baseline": {kk: agg(v) for kk, v in base.items()}}
        print(f"[done] K={k}  ({time.time()-t0:.1f}s)")
    out["meta"]["wallclock_s"] = round(time.time() - t0, 2)
    with open("experiments/laad_series/out/exp3_degradation.json", "w") as f:
        json.dump(out, f, indent=2)
    print("wrote exp3_degradation.json  wallclock", out["meta"]["wallclock_s"], "s")


if __name__ == "__main__":
    main()
