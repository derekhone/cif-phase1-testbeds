"""Analyze EXP-1 frontier results: per-scenario tables, Pareto frontier across
the 7 operating modes, and the operating-envelope classification
(WIN / NEUTRAL / LIABILITY) of CIF-LAAD vs the frozen baseline.

Reads out/exp1_frontier.json only. Writes EXP1_RESULTS.md. No numbers invented.
"""
from __future__ import annotations
import json, hashlib, math

SRC = "experiments/laad_series/out/exp1_frontier.json"
OUT = "experiments/laad_series/EXP1_RESULTS.md"

d = json.load(open(SRC))
R = d["results"]
MODES = list(R.keys())
SCEN = list(R["M_batch"].keys())


def m(mode, s, side, k):
    return R[mode][s][side][k]["mean"]


def sd(mode, s, side, k):
    return R[mode][s][side][k]["std"]


def f(x, nd=2):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "  -  "
    return f"{x:.{nd}f}"


# ---- Pareto frontier across modes (per scenario) --------------------------
# Objectives (all minimized): RMSE, id_switches, false_track_frames,
# (1 - continuity), reacq (0 if nan == no reacq needed).
OBJ = ["position_rmse_m", "id_switches", "false_track_frames", "continuity", "mean_reacq_s"]


def obj_vec(mode, s):
    v = []
    for k in OBJ:
        x = m(mode, s, "cif", k)
        if k == "continuity":
            x = 1.0 - x
        if k == "mean_reacq_s" and (x is None or math.isnan(x)):
            x = 0.0
        v.append(x)
    return v


def dominates(a, b):
    # a dominates b if a <= b on all and < on at least one
    le = all(ai <= bi + 1e-9 for ai, bi in zip(a, b))
    lt = any(ai < bi - 1e-9 for ai, bi in zip(a, b))
    return le and lt


def pareto(scen):
    vecs = {mode: obj_vec(mode, scen) for mode in MODES}
    front = []
    for mode in MODES:
        dom = False
        for other in MODES:
            if other != mode and dominates(vecs[other], vecs[mode]):
                dom = True
                break
        if not dom:
            front.append(mode)
    return front


# ---- Envelope classification (default mode M_batch vs baseline) -----------
DEFAULT = "M_batch"


def classify(scen):
    """Return dict of metric-family -> (verdict, cif, base)."""
    out = {}
    # localization
    cr, br = m(DEFAULT, scen, "cif", "position_rmse_m"), m(DEFAULT, scen, "baseline", "position_rmse_m")
    out["localization_rmse"] = ("LIABILITY" if cr > br * 1.15 else ("WIN" if cr < br * 0.85 else "NEUTRAL"), cr, br)
    # id stability
    ci, bi = m(DEFAULT, scen, "cif", "id_switches"), m(DEFAULT, scen, "baseline", "id_switches")
    out["id_stability"] = ("WIN" if ci < bi * 0.85 else ("LIABILITY" if ci > bi * 1.15 else "NEUTRAL"), ci, bi)
    # false tracks
    cf, bf = m(DEFAULT, scen, "cif", "false_track_frames"), m(DEFAULT, scen, "baseline", "false_track_frames")
    out["false_tracks"] = ("WIN" if cf < bf * 0.85 else ("LIABILITY" if cf > bf * 1.15 else "NEUTRAL"), cf, bf)
    # continuity
    cc, bc = m(DEFAULT, scen, "cif", "continuity"), m(DEFAULT, scen, "baseline", "continuity")
    out["continuity"] = ("WIN" if cc > bc * 1.03 else ("LIABILITY" if cc < bc * 0.97 else "NEUTRAL"), cc, bc)
    # dropout continuity (only meaningful for dropout scenario)
    cd = m(DEFAULT, scen, "cif", "dropout_continuity")
    bd = m(DEFAULT, scen, "baseline", "dropout_continuity")
    if cd is not None and not math.isnan(cd):
        out["dropout_continuity"] = ("WIN" if cd > bd + 0.05 else ("LIABILITY" if cd < bd - 0.05 else "NEUTRAL"), cd, bd)
    return out


L = []
w = L.append
w("# EXP-1 - Accuracy / Continuity Frontier (frozen results)\n")
w(f"- Series: CIF-LAAD preregistered validation series (simulation-only, TRL 3, RESEARCH ONLY)")
w(f"- Experimental unit: EXP-1. Held-out seeds {d['meta']['seeds'][0]}-{d['meta']['seeds'][-1]} (n={len(d['meta']['seeds'])}), disjoint from the published seeds 0-24.")
w(f"- numpy {d['meta']['numpy']}, python {d['meta']['python']}, wallclock {d['meta'].get('wallclock_s','?')} s")
w(f"- 7 preregistered operating modes x 6 frozen scenarios x {len(d['meta']['seeds'])} seeds. Nothing retuned to win; the falsified coherence-gate mode (M_gated) is kept for honesty.\n")

w("## Baseline (frozen single-hypothesis tracker), per scenario\n")
w("| scenario | RMSE m | continuity | id switches | false-track frames | reacq s |")
w("|---|---|---|---|---|---|")
for s in SCEN:
    w(f"| {s} | {f(m(DEFAULT,s,'baseline','position_rmse_m'))} | {f(m(DEFAULT,s,'baseline','continuity'))} | {f(m(DEFAULT,s,'baseline','id_switches'))} | {f(m(DEFAULT,s,'baseline','false_track_frames'),1)} | {f(m(DEFAULT,s,'baseline','mean_reacq_s'))} |")
w("")

for mode in MODES:
    w(f"## CIF - mode {mode}\n")
    w("| scenario | RMSE m | continuity | dropout-cont | id switches | false-track frames | reacq s |")
    w("|---|---|---|---|---|---|---|")
    for s in SCEN:
        w(f"| {s} | {f(m(mode,s,'cif','position_rmse_m'))} | {f(m(mode,s,'cif','continuity'))} | {f(m(mode,s,'cif','dropout_continuity'))} | {f(m(mode,s,'cif','id_switches'))} | {f(m(mode,s,'cif','false_track_frames'),1)} | {f(m(mode,s,'cif','mean_reacq_s'))} |")
    w("")

w("## Pareto frontier across operating modes (per scenario)\n")
w("Objectives minimized: RMSE, id switches, false-track frames, (1 - continuity), reacq. A mode is on the frontier if no other mode is at least as good on all five and strictly better on one.\n")
w("| scenario | non-dominated modes |")
w("|---|---|")
for s in SCEN:
    w(f"| {s} | {', '.join(pareto(s))} |")
w("")

w("## Operating-envelope classification (default mode M_batch vs baseline)\n")
w("WIN = CIF clearly better; LIABILITY = CIF clearly worse; NEUTRAL = within +/-15% (continuity +/-3%).\n")
w("| scenario | localization RMSE | id stability | false tracks | continuity | dropout continuity |")
w("|---|---|---|---|---|---|")
for s in SCEN:
    c = classify(s)
    def cell(key):
        if key not in c:
            return "  -  "
        v, ci, bi = c[key]
        return f"{v} ({f(ci)} vs {f(bi)})"
    w(f"| {s} | {cell('localization_rmse')} | {cell('id_stability')} | {cell('false_tracks')} | {cell('continuity')} | {cell('dropout_continuity')} |")
w("")

txt = "\n".join(L) + "\n"
open(OUT, "w").write(txt)
h = hashlib.sha256(open(SRC, "rb").read()).hexdigest()
print("wrote", OUT)
print("exp1_frontier.json sha256:", h)
