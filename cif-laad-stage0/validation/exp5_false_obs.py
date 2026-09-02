"""EXP-5 False-observation resilience.

Exercises the FROZEN defences only (validate() + seq replay + contradiction
log). We craft hostile inputs and record what the engine does; we do not modify
any defence.

Part A - typed-reject unit check: each malformed/stale/future/replay/bad-field
observation must be rejected with the correct error code.
Part B - in-scenario spoof resilience: inject schema-VALID spoofs at plausible
false positions into a benign run and measure whether they create persistent
false tracks (an honest limitation: lineage/schema validation does not by
itself reject a lone plausible spoof) and whether the legit track survives.
"""
from __future__ import annotations
import json, sys, time
import numpy as np
from ciflaad.fusion import FusionEngine, FusionConfig
from ciflaad.observation import SensorObservation
from ciflaad.track import CONFIRMED, COASTING
from experiments.adapters import cif_estimates
from sim import metrics
from experiments.laad_series import scenarios_ext as sx

GOOD_COV = np.eye(3) * 36.0


def _obs(sensor_id, stype, ts, pos, cov=GOOD_COV, seq=None, cls=None,
         conf=0.0, rf_id=None):
    return SensorObservation(sensor_id=sensor_id, sensor_type=stype, timestamp=ts,
                             position=np.asarray(pos, float), position_cov=cov,
                             class_label=cls, class_confidence=conf, rf_id=rf_id,
                             seq=seq, meta={"truth_tid": -99})


def part_a():
    """Feed one hostile obs of each type; assert the reject code."""
    eng = FusionEngine(FusionConfig())
    now = 10.0
    cases = {}
    # establish a seq baseline for replay test
    eng.process([_obs("radar-1", "radar", now, [100, 0, 40], seq=5)], now)
    checks = [
        ("malformed_nan_pos", _obs("radar-1", "radar", now, [np.nan, 0, 40], seq=6), "E_POS"),
        ("malformed_cov_not_pd", _obs("radar-1", "radar", now, [100, 0, 40],
                                      cov=np.array([[1., 0, 0], [0, -1., 0], [0, 0, 1.]]), seq=7), "E_COV_PD"),
        ("stale_ts", _obs("radar-1", "radar", now - 10.0, [100, 0, 40], seq=8), "E_TS_STALE"),
        ("future_ts", _obs("radar-1", "radar", now + 10.0, [100, 0, 40], seq=9), "E_TS_FUTURE"),
        ("bad_class_conf", _obs("eoir-1", "eoir", now, [100, 0, 40], seq=10, cls="drone", conf=1.5), "E_CLASS_CONF"),
        ("rfid_on_non_rf", _obs("radar-1", "radar", now, [100, 0, 40], seq=11, rf_id="EMIT-X"), "E_RFID"),
        ("unknown_sensor_type", _obs("x-1", "lidar", now, [100, 0, 40], seq=12), "E_SENSOR_TYPE"),
        ("replay_seq", _obs("radar-1", "radar", now, [100, 0, 40], seq=3), "E_REPLAY"),
    ]
    for label, ob, expect in checks:
        r = eng.process([ob], now)
        codes = [rej.get("code") for rej in r.rejected]
        cases[label] = {"expected": expect, "got": codes,
                        "rejected_as_expected": expect in codes}
    return cases


def part_b(seed, n_spoof_per_frame=3, inject=(6.0, 30.0)):
    """Benign single-target run; inject schema-valid spoofs during a window.
    Compare legit-track survival + false tracks vs a clean control."""
    scen, _ = sx.benign(seed)
    rng = np.random.default_rng(700 + seed)

    def run(with_spoof):
        eng = FusionEngine(FusionConfig())
        tl = []
        n_rej = 0
        seqbump = {"radar-1": 100000, "eoir-1": 100000, "rf-1": 100000}
        for t, truth, obs in scen.frames():
            obs = list(obs)
            if with_spoof and inject[0] <= t < inject[1]:
                for _ in range(n_spoof_per_frame):
                    p = rng.uniform(-600, 600, size=3); p[2] = rng.uniform(20, 80)
                    seqbump["radar-1"] += 1
                    obs.append(_obs("radar-1", "radar", t, p, seq=seqbump["radar-1"]))
            r = eng.process(obs, t)
            n_rej += len(r.rejected)
            tl.append({"t": t, "truth": {k: np.asarray(v) for k, v in truth.items()},
                       "estimates": cif_estimates(eng)})
        m = metrics.evaluate(tl)
        n_conf = sum(1 for tr in eng.tracks if tr.status in (CONFIRMED, COASTING))
        return m, n_rej, n_conf

    ctrl_m, _, ctrl_conf = run(False)
    trt_m, trt_rej, trt_conf = run(True)
    return {"control": {"continuity": ctrl_m["continuity"], "rmse": ctrl_m["position_rmse_m"],
                        "false_track_frames": ctrl_m["false_track_frames"], "confirmed_tracks": ctrl_conf},
            "spoofed": {"continuity": trt_m["continuity"], "rmse": trt_m["position_rmse_m"],
                        "false_track_frames": trt_m["false_track_frames"], "confirmed_tracks": trt_conf,
                        "rejected_obs": trt_rej}}


def main():
    t0 = time.time()
    a = part_a()
    seeds = list(range(100, 115))
    b_runs = [part_b(s) for s in seeds]
    def mean(key, grp):
        return float(np.mean([r[grp][key] for r in b_runs]))
    b_summary = {
        "seeds": seeds,
        "control": {k: mean(k, "control") for k in ["continuity", "rmse", "false_track_frames", "confirmed_tracks"]},
        "spoofed": {k: mean(k, "spoofed") for k in ["continuity", "rmse", "false_track_frames", "confirmed_tracks", "rejected_obs"]},
    }
    out = {"meta": {"experiment": "EXP-5 false-observation resilience",
                    "numpy": np.__version__, "python": sys.version.split()[0],
                    "note": "simulation-only; frozen validate()+replay+contradiction defences",
                    "wallclock_s": round(time.time() - t0, 2)},
           "part_a_typed_rejects": a,
           "part_a_all_correct": all(v["rejected_as_expected"] for v in a.values()),
           "part_b_spoof_resilience": b_summary}
    with open("experiments/laad_series/out/exp5_false_obs.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("wrote exp5_false_obs.json  part_a_all_correct =", out["part_a_all_correct"])


if __name__ == "__main__":
    main()
