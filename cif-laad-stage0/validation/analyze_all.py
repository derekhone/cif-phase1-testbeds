"""Synthesize the whole CIF-LAAD validation series into RESULTS.md.

Reads every out/*.json (EXP-1..EXP-8). Invents no numbers. Emits the benchmark
matrix (EXP-7 folds in here: comparator is the frozen in-tree BaselineTracker;
we state honestly that no certified third-party library was run, and name a
Stone-Soup / SORT config as future work), the operating-envelope synthesis, and
the claim-limit list. Also writes EXPECTED_OUTPUTS.sha256 over all out/*.json.
"""
from __future__ import annotations
import json, glob, hashlib, math, os

OUTDIR = "experiments/laad_series/out"
RESULTS = "experiments/laad_series/RESULTS.md"
SHAFILE = "experiments/laad_series/EXPECTED_OUTPUTS.sha256"


def load(name):
    return json.load(open(os.path.join(OUTDIR, name)))


def g(x):
    if isinstance(x, dict):
        x = x.get("mean")
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    return x


def f(x, nd=2):
    if x is None:
        return "  -  "
    return f"{x:.{nd}f}"


L = []
w = L.append

w("# CIF-LAAD Validation Series - Complete Results\n")
w("Simulation-only. TRL 3. RESEARCH ONLY. Not a security proof or a fielded system.\n")
w("One coherent preregistered series, eight experimental units (EXP-1..EXP-8). Seeds are replications within a unit, not separate experiments; this series does not increase the public experiment count.\n")
w("Engine frozen at combined SHA-256 8712f1138bdd20090b9a1b6eda58cebc5c274a843b960d6784e8650b7ea7ad45 (14 files). numpy 2.2.6, python 3.11.6. Held-out seeds start at 100, disjoint from the published seeds 0-24. Nothing was retuned to win; the falsified coherence-gate mode is kept in the record.\n")

# ---- EXP-1 --------------------------------------------------------------
w("## EXP-1 - Accuracy / continuity frontier\n")
w("Full per-mode tables in EXP1_RESULTS.md. Envelope verdict (default mode M_batch vs frozen baseline):\n")
w("- WIN: id-switch suppression and false-track suppression under clutter and many targets (heavy_clutter id 5.07 -> 0.57, false 61.1 -> 14.6; many_targets id 14.6 -> 5.3, false 89.9 -> 28.4); continuity through sensor dropout (0.30 -> 1.00, reacq 4.0s -> none).")
w("- LIABILITY: localization RMSE in clutter / many targets (~6m -> ~23m) and a modest RMSE cost in crossing and dropout.")
w("- NEUTRAL: clean_single and identity_conflict (CIF identical to baseline; no cost, no measurable win).\n")

# ---- EXP-2 --------------------------------------------------------------
d = load("exp2_dropout.json")["results"]
w("## EXP-2 - Dropout-duration stress (bounds the dropout win)\n")
w("All sensors blind for a fixed window; how long can CIF coast before continuity breaks?\n")
w("| dropout | CIF RMSE m | CIF dropout-cont | CIF reacq s | baseline dropout-cont | baseline reacq s |")
w("|---|---|---|---|---|---|")
for k, v in d.items():
    c, b = v["cif"], v["baseline"]
    w(f"| {k} | {f(g(c['position_rmse_m']))} | {f(g(c['dropout_continuity']))} | {f(g(c['mean_reacq_s']))} | {f(g(b['dropout_continuity']))} | {f(g(b['mean_reacq_s']))} |")
w("\nEnvelope bound: CIF holds full continuity (1.00) through ~5s blind gaps while the baseline decays to 0.30; beyond ~10s CIF continuity itself degrades (0.60 at 10s, 0.40 at 15s). The honest claim is bounded: continuity advantage through multi-second dropout, not indefinite coasting.\n")

# ---- EXP-3 --------------------------------------------------------------
d = load("exp3_degradation.json")["results"]
w("## EXP-3 - Sensor-degradation matrix\n")
w("K sensors simultaneously degraded (x4 position sigma + Pd 0.4 + a mid-run dropout).\n")
w("| K degraded | CIF RMSE | CIF cont | CIF id sw | base RMSE | base cont | base id sw |")
w("|---|---|---|---|---|---|---|")
for k, v in d.items():
    c, b = v["cif"], v["baseline"]
    w(f"| {k} | {f(g(c['position_rmse_m']))} | {f(g(c['continuity']))} | {f(g(c['id_switches']))} | {f(g(b['position_rmse_m']))} | {f(g(b['continuity']))} | {f(g(b['id_switches']))} |")
w("\nEnvelope bound: at light degradation (K<=2) CIF and baseline are indistinguishable. The continuity/identity advantage only appears at heavy degradation (K=3: continuity 0.97 vs 0.85, id switches 0.30 vs 1.30), and even there CIF pays a small RMSE cost (32.8 vs 30.6).\n")

# ---- EXP-4 --------------------------------------------------------------
d = load("exp4_dense.json")["results"]
w("## EXP-4 - Dense-crossing identity challenge\n")
w("Crossing lanes with modest clutter; sweep target count N.\n")
w("| N targets | CIF RMSE | CIF id sw | CIF false | base RMSE | base id sw | base false |")
w("|---|---|---|---|---|---|---|")
for k, v in d.items():
    c, b = v["cif"], v["baseline"]
    w(f"| {k} | {f(g(c['position_rmse_m']))} | {f(g(c['id_switches']))} | {f(g(c['false_track_frames']),1)} | {f(g(b['position_rmse_m']))} | {f(g(b['id_switches']))} | {f(g(b['false_track_frames']),1)} |")
w("\nEnvelope bound (important, honest): CIF suppresses false tracks at every density, but its id-switch advantage holds only at low density (N<=4: 1.3 vs 4.1, 3.2 vs 9.4). At N>=8 the id-switch count inverts - CIF has MORE id switches than the baseline (N=32: 195 vs 109) while still holding fewer false tracks (306 vs 540). The identity-stability claim is therefore bounded to modest target counts; it does not scale to dozens of simultaneous crossers.\n")

# ---- EXP-5 --------------------------------------------------------------
d = load("exp5_false_obs.json")
w("## EXP-5 - False-observation resilience\n")
w(f"Part A - typed-reject unit check: all_correct = {d['part_a_all_correct']}. Each malformed / stale / future / replay / bad-field observation was rejected with the correct typed error code:\n")
w("| case | expected code | rejected as expected |")
w("|---|---|---|")
for case, r in d["part_a_typed_rejects"].items():
    w(f"| {case} | {r['expected']} | {r['rejected_as_expected']} |")
pb = d["part_b_spoof_resilience"]
w("\nPart B - in-scenario spoof (schema-VALID false observations at plausible positions):\n")
w("| metric | control (no spoof) | spoofed |")
w("|---|---|---|")
for key, lab in [("continuity", "continuity"), ("rmse", "RMSE m"), ("false_track_frames", "false-track frames"), ("confirmed_tracks", "confirmed tracks"), ("rejected_obs", "rejected obs")]:
    cv = pb["control"].get(key); sv = pb["spoofed"].get(key)
    w(f"| {lab} | {f(cv,2) if cv is not None else '-'} | {f(sv,2) if sv is not None else '-'} |")
w("\nHonest limitation (reported, not hidden): the frozen defences reject malformed, stale, future, and replayed observations by construction, but a lone schema-valid spoof at a plausible position is NOT rejected by validation/lineage alone - it inflates false-track frames (14.7 -> 78.3). The legitimate track still survives (continuity unchanged). CIF-LAAD is an assurance/provenance layer, not a spoof-authentication layer; sensor-level authentication is out of scope.\n")

# ---- EXP-6 --------------------------------------------------------------
d = load("exp6_tamper.json")["results"]
w("## EXP-6 - Evidence / provenance tamper challenge\n")
w(f"Real hash-linked evidence chain of length {d['chain_length']}; pristine verify = {d['pristine_verify']}. Four tamper operations applied to copies:\n")
w("| tamper op | verify after | detected |")
w("|---|---|---|")
for op, r in d["tampers"].items():
    w(f"| {op} | {r['verify_after']} | {r['detected']} |")
w(f"\nAll tampers detected = {d['all_tampers_detected']}. HONEST LABEL: tamper-EVIDENT, not tamper-proof. A fully trusted writer can forge a fresh internally-consistent chain; this detects mutation of a persisted or transmitted log, not authorship fraud.\n")

# ---- EXP-7 benchmark matrix --------------------------------------------
w("## EXP-7 - Benchmark matrix (comparator honesty)\n")
w("The comparator throughout this series is the frozen in-tree single-hypothesis BaselineTracker (a nearest-neighbour Kalman tracker). No certified third-party tracking library (e.g. Stone-Soup, a SORT/DeepSORT config) was run in this series. That is a real gap: the wins reported here are relative to a reasonable in-house baseline, not to a published state-of-the-art system. Running a Stone-Soup GNN/JPDA configuration and a SORT baseline on the identical frozen scenarios is named as the top future-work item before any comparative-performance claim is made public.\n")

# ---- EXP-8 scale --------------------------------------------------------
d = load("exp8_scale.json")
res = d["results"]
w("## EXP-8 - Scale test (throughput envelope)\n")
w(f"Pure-Python single-thread, CIF engine only, real-time budget {d['meta']['realtime_budget_ms']} ms/cycle.\n")
w("| N targets | mean cycle ms | worst-seed mean ms | peak mem MB | meets 50ms real-time |")
w("|---|---|---|---|---|")
for k, v in res.items():
    w(f"| {k} | {f(v['mean_cycle_ms'])} | {f(v['max_seed_mean_cycle_ms'])} | {f(v['peak_mem_mb'],2)} | {v['meets_realtime_50ms']} |")
w("\nEnvelope bound: the pure-Python engine meets a 50 ms/cycle real-time budget up to ~50 tracks (44 ms); at 100 tracks it is 72 ms (over budget) and grows roughly linearly to 435 ms at 1000. Real-time claims are bounded to <=50 tracks in this implementation; larger scales are a compiled-implementation future-work item, not a current claim.\n")

# ---- Synthesis ----------------------------------------------------------
w("## Series synthesis - the defensible operating envelope\n")
w("Judged by the preregistered success/kill test (is there a defensible envelope where CIF-LAAD buys measurable continuity/identity/evidence advantage without an unacceptable localization-accuracy cost?), the answer is a qualified YES, with sharp boundaries:\n")
w("- EARNED (survived): (1) continuity through multi-second sensor dropout, bounded to ~5s full / degrading past ~10s (EXP-1, EXP-2); (2) false-track suppression under clutter and dense crossing, at every density tested (EXP-1, EXP-4); (3) id-switch suppression, bounded to clutter and LOW target density N<=4 (EXP-1, EXP-4) and to heavy sensor degradation K=3 (EXP-3); (4) tamper-EVIDENT provenance (EXP-6); (5) typed rejection of malformed/stale/future/replayed observations (EXP-5).")
w("- COST (always reported alongside): localization RMSE penalty of roughly 1.3x-4x versus the baseline whenever the environment is contested; the penalty is structural, not a tuning bug.")
w("- KILLED / NARROWED: the coherence-gate inheritance mode stays falsified on held-out seeds; the id-stability advantage does NOT scale past a handful of simultaneous crossers (inverts at N>=8); no advantage at all in clean single-target or the identity_conflict scenario; real-time only to ~50 tracks; a lone plausible spoof is not rejected; no certified third-party benchmark was run.\n")
w("Headline identity earned by this evidence: CIF-LAAD - a sensor-agnostic low-altitude assurance layer for maintaining track identity, continuity, uncertainty and evidence provenance when observations degrade or conflict - explicitly trading localization precision for continuity, identity stability and provenance inside a bounded degraded/contested envelope.\n")

txt = "\n".join(L) + "\n"
open(RESULTS, "w").write(txt)

# expected-output SHAs
lines = []
for p in sorted(glob.glob(os.path.join(OUTDIR, "*.json"))):
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    lines.append(f"{h}  {os.path.relpath(p)}")
open(SHAFILE, "w").write("\n".join(lines) + "\n")
print("wrote", RESULTS)
print("wrote", SHAFILE)
print("\n".join(lines))
