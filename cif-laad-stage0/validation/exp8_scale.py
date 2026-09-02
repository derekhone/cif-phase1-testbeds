"""EXP-8 Scale test. N in {1,10,50,100,500,1000}; measure per-cycle latency and
throughput. About compute, not tracking quality; 3 seeds each, short duration.
Real-time budget note: dt=0.5 s, target 10 Hz processing => ~50 ms/cycle budget.
"""
from __future__ import annotations
import json, sys, time, tracemalloc
import numpy as np
from ciflaad.fusion import FusionEngine, FusionConfig
from experiments.laad_series import scenarios_ext as sx

SEEDS = [100, 101, 102]
NS = [1, 10, 50, 100, 500, 1000]


def main():
    t0 = time.time()
    out = {"meta": {"experiment": "EXP-8 scale test", "seeds": SEEDS, "n_targets": NS,
                    "numpy": np.__version__, "python": sys.version.split()[0],
                    "realtime_budget_ms": 50.0,
                    "note": "simulation-only; pure-Python single-thread; CIF engine only"},
           "results": {}}
    for n in NS:
        lat_ms = []
        peak_mb = []
        for s in SEEDS:
            scen, _ = sx.scale(s, n, duration=10.0)
            eng = FusionEngine(FusionConfig())
            tracemalloc.start()
            cyc = []
            for t, truth, obs in scen.frames():
                r = eng.process(obs, t)
                cyc.append(r.latency_s * 1e3)
            cur, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            lat_ms.append(float(np.mean(cyc)))
            peak_mb.append(peak / 1e6)
        out["results"][f"N={n}"] = {
            "mean_cycle_ms": float(np.mean(lat_ms)),
            "max_seed_mean_cycle_ms": float(np.max(lat_ms)),
            "peak_mem_mb": float(np.mean(peak_mb)),
            "meets_realtime_50ms": bool(np.mean(lat_ms) <= 50.0)}
        print(f"[done] N={n}  mean_cycle={np.mean(lat_ms):.2f} ms  ({time.time()-t0:.1f}s)")
    out["meta"]["wallclock_s"] = round(time.time() - t0, 2)
    with open("experiments/laad_series/out/exp8_scale.json", "w") as f:
        json.dump(out, f, indent=2)
    print("wrote exp8_scale.json  wallclock", out["meta"]["wallclock_s"], "s")


if __name__ == "__main__":
    main()
