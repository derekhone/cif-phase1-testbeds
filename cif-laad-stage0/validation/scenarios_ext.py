"""Extended, PREREGISTERED scenario factories for the CIF-LAAD Validation Series.

Every factory here is built ONLY from the frozen sim primitives
(sim.scenario.Scenario/Target/SensorModel). It adds new seeded conditions; it
does not modify the frozen engine, baseline, metrics, or the original six
scenarios. Seeds are held-out (callers use seed >= 100).

All simulation. No hardware. No real sensor data.
"""
from __future__ import annotations
import numpy as np
from sim.scenario import Scenario, Target, SensorModel

DT = 0.5
DUR = 40.0


# ---- frozen sensor builders (same params as the published scenarios) ----
def radar(drop=None, pos_sigma=6.0, pd=0.95):
    return SensorModel("radar-1", "radar", pos_sigma=pos_sigma, pd=pd,
                       dropout_windows=drop or [])


def eoir(drop=None, pos_sigma=10.0, pd=0.85, class_acc=0.9):
    return SensorModel("eoir-1", "eoir", pos_sigma=pos_sigma, pd=pd,
                       gives_class=True, class_acc=class_acc,
                       dropout_windows=drop or [])


def rf(drop=None, pos_sigma=40.0, pd=0.8):
    return SensorModel("rf-1", "rf", pos_sigma=pos_sigma, pd=pd, gives_rf=True,
                       dropout_windows=drop or [])


# ---- EXP-2 dropout-duration stress ----
def dropout_duration(seed, D):
    """Single target; ALL sensors blind for a window of duration D seconds,
    centered in the run."""
    start = 18.0
    win = [(start, start + D)]
    tg = [Target(1, np.array([200., 100., 40.]), np.array([12., -4., 0.5]),
                 "drone", rf_id="EMIT-A")]
    sensors = [radar(win), eoir(win), rf(win)]
    return Scenario(f"dropout_{D:g}s", DUR, DT, tg, sensors,
                    clutter_rate=0.0, seed=seed), win


# ---- EXP-3 sensor-degradation matrix ----
def degradation(seed, k_degraded):
    """Benign single-target geometry; degrade K of the 3 sensors with inflated
    noise (x4 sigma), reduced Pd (0.4), and a mid dropout window."""
    win = [(15.0, 20.0)]
    tg = [Target(1, np.array([200., 100., 40.]), np.array([12., -4., 0.5]),
                 "drone", rf_id="EMIT-A")]
    # order of degradation: radar first, then eoir, then rf
    r = radar(win if k_degraded >= 1 else None,
              pos_sigma=6.0 * (4 if k_degraded >= 1 else 1),
              pd=0.4 if k_degraded >= 1 else 0.95)
    e = eoir(win if k_degraded >= 2 else None,
             pos_sigma=10.0 * (4 if k_degraded >= 2 else 1),
             pd=0.4 if k_degraded >= 2 else 0.85)
    f = rf(win if k_degraded >= 3 else None,
           pos_sigma=40.0 * (4 if k_degraded >= 3 else 1),
           pd=0.4 if k_degraded >= 3 else 0.8)
    return Scenario(f"degrade_{k_degraded}", DUR, DT, tg, [r, e, f],
                    clutter_rate=0.0, seed=seed), []


# ---- EXP-4 dense-crossing identity challenge ----
def dense_crossing(seed, n):
    """N drones on deliberately crossing paths (mirrored left/right lanes) with
    modest clutter, so tracks genuinely cross near one another."""
    rng = np.random.default_rng(5000 + seed)
    tg = []
    for i in range(n):
        side = -1 if i % 2 == 0 else 1
        x0 = side * rng.uniform(300, 500)
        y0 = rng.uniform(-200, 200)
        z0 = rng.uniform(20, 80)
        vx = -side * rng.uniform(15, 22)   # head toward the other side => crossings
        vy = rng.uniform(-4, 4)
        tg.append(Target(i + 1, np.array([x0, y0, z0]),
                         np.array([vx, vy, 0.0]), "drone", rf_id=f"EMIT-{i}"))
    return Scenario(f"dense_{n}", DUR, DT, tg, [radar(), eoir(), rf()],
                    clutter_rate=1.0, seed=seed), []


# ---- EXP-8 scale test ----
def scale(seed, n, duration=10.0):
    """N targets spread over a wide box, short duration - this experiment is
    about compute latency/throughput, not tracking quality."""
    rng = np.random.default_rng(9000 + seed)
    tg = []
    for i in range(n):
        p0 = rng.uniform(-1500, 1500, size=3); p0[2] = rng.uniform(20, 120)
        v0 = rng.uniform(-18, 18, size=3); v0[2] = 0.0
        tg.append(Target(i + 1, p0, v0, "drone", rf_id=f"EMIT-{i}"))
    return Scenario(f"scale_{n}", duration, DT, tg, [radar(), eoir(), rf()],
                    clutter_rate=0.5, seed=seed), []


# ---- EXP-5 / EXP-6 base benign scenario (single clean target) ----
def benign(seed):
    tg = [Target(1, np.array([200., 100., 40.]), np.array([12., -4., 0.5]),
                 "drone", rf_id="EMIT-A")]
    return Scenario("benign", DUR, DT, tg, [radar(), eoir(), rf()],
                    clutter_rate=0.0, seed=seed), []
