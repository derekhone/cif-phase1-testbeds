"""
ARK-DM-1 : Preregistered open-data test of a decaying-exponential
           inheritance term on SPARC galaxy rotation curves.

Locked protocol:
  Model    : V^2 = V_bar^2 * (1 + alpha * exp(-r / R_disk)), single GLOBAL alpha
  Metric   : median fractional velocity error |V_pred - V_obs| / V_obs
  Kill     : FAIL unless err_ark <= 0.90 * err_visible  (>=10% improvement)
  Novelty  : even if passed, verdict is LIMITED/NON-NOVEL unless it beats a
             per-galaxy 2-parameter pseudo-isothermal halo baseline
  Sample   : first 25 galaxies alphabetically passing quality filters
             (>=5 radial points, Rdisk present in Table 1, Vobs > 0)

Data: SPARC (Lelli, McGaugh & Schombert 2016, AJ 152, 157)
      http://astroweb.cwru.edu/SPARC/
Inputs expected (adjust paths as needed):
  SPARC Table 1.txt        (SPARC Table 1, MRT text)
  Rotmod_LTG.zip           (rotation-curve mass models)
Outputs:
  results/ark_dm1_results.json     (machine-readable, full detail)
  RESULTS.md                       (human-readable, full per-galaxy table)

Result of the single locked run (2026-07-14 UTC): FAIL
  err_visible = 0.4145 | err_ark = 0.3826 (alpha* = 2.13) | err_halo = 0.0305
  improvement = 7.69% < 10% threshold -> kill-condition fired.
"""

import os, glob, json, zipfile, datetime
import numpy as np

# ----------------------------- configuration -----------------------------
EPS         = 1e-6
N_GALAXIES  = 25
ALPHAS      = np.arange(0.00, 5.00 + 1e-9, 0.01)      # global alpha grid
HALO_V0S    = np.arange(5, 405, 5.0)                   # km/s
HALO_RCS    = np.arange(0.1, 20.1, 0.1)                # kpc
TABLE1_PATH = "SPARC Table 1.txt"
ZIP_PATH    = "Rotmod_LTG.zip"
DATA_DIR    = "sparc_data"
OUT_DIR     = "results"

# ----------------------------- data loading ------------------------------
def extract_zip():
    os.makedirs(DATA_DIR, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH) as zf:
        zf.extractall(DATA_DIR)

def parse_table1():
    """Parse SPARC Table 1. Data rows are whitespace-delimited:
    Galaxy T D e_D f_D Inc e_Inc L36 e_L36 Reff SBeff Rdisk ...
    Rdisk is the 12th token (index 11). Returns {galaxy: Rdisk_kpc}."""
    rdisk = {}
    with open(TABLE1_PATH, errors="replace") as f:
        for ln in f:
            p = ln.split()
            if len(p) < 18:
                continue
            try:
                vals = [float(x) for x in p[1:12]]
            except ValueError:
                continue                                # header / notes line
            rd = vals[10]
            if rd > 0:
                rdisk[p[0]] = rd
    return rdisk

def load_rotmod(path):
    """Columns: Rad Vobs errV Vgas Vdisk Vbul SBdisk SBbul"""
    rows = []
    for ln in open(path, errors="replace"):
        if ln.strip().startswith("#") or not ln.strip():
            continue
        p = ln.split()
        try:
            rad, vobs, errv, vgas, vdisk, vbul = map(float, p[0:6])
        except (ValueError, IndexError):
            continue
        rows.append((rad, vobs, vgas, vdisk, vbul))
    return np.array(rows) if rows else None

def build_sample(rdisk):
    sample, excluded = [], []
    for fp in sorted(glob.glob(os.path.join(DATA_DIR, "*_rotmod.dat"))):
        if len(sample) >= N_GALAXIES:
            break
        gal = os.path.basename(fp).replace("_rotmod.dat", "")
        arr = load_rotmod(fp)
        if arr is None or arr.shape[0] < 5:
            excluded.append((gal, "insufficient radial points")); continue
        if gal not in rdisk:
            excluded.append((gal, "no Rdisk in Table 1")); continue
        if np.any(arr[:, 1] <= 0):
            excluded.append((gal, "non-positive Vobs")); continue
        sample.append((gal, arr, rdisk[gal]))
    return sample, excluded

# ----------------------------- physics -----------------------------------
def vbar_sq(arr):
    """Baryonic V^2 with SPARC signed-gas convention (M/L = 1 at 3.6um)."""
    vgas, vdisk, vbul = arr[:, 2], arr[:, 3], arr[:, 4]
    return vgas * np.abs(vgas) + vdisk**2 + vbul**2

def frac_err(vpred, vobs):
    return np.abs(vpred - vobs) / np.maximum(vobs, EPS)

def ark_velocity(arr, rd, alpha):
    vb2 = np.maximum(vbar_sq(arr), 0)
    return np.sqrt(np.maximum(vb2 * (1 + alpha * np.exp(-arr[:, 0] / rd)), 0))

def halo_velocity_sq(r, v0, rc):
    """Pseudo-isothermal halo circular velocity squared."""
    return v0**2 * (1 - (rc / r) * np.arctan(r / rc))

# ----------------------------- analysis ----------------------------------
def run():
    extract_zip()
    rdisk = parse_table1()
    sample, excluded = build_sample(rdisk)
    assert len(sample) == N_GALAXIES, f"expected {N_GALAXIES}, got {len(sample)}"

    per_gal = {}

    # 1. visible-only baseline
    vis_errs = []
    for gal, arr, rd in sample:
        e = frac_err(np.sqrt(np.maximum(vbar_sq(arr), 0)), arr[:, 1])
        vis_errs.append(e)
        per_gal[gal] = {"n": int(len(arr)), "Rdisk": rd,
                        "err_vis": float(np.median(e))}
    err_visible = float(np.median(np.concatenate(vis_errs)))

    # 2. Ark term -- single global alpha, grid search
    def ark_pooled_err(alpha):
        es = [frac_err(ark_velocity(arr, rd, alpha), arr[:, 1])
              for _, arr, rd in sample]
        return float(np.median(np.concatenate(es)))
    errs = [ark_pooled_err(a) for a in ALPHAS]
    bi = int(np.argmin(errs))
    alpha_star, err_ark = float(ALPHAS[bi]), float(errs[bi])

    # 3. halo baseline -- per-galaxy 2-parameter grid fit
    halo_errs = []
    for gal, arr, rd in sample:
        vb2 = np.maximum(vbar_sq(arr), 0)
        r, vobs = arr[:, 0], arr[:, 1]
        best = (np.inf, None, None)
        for v0 in HALO_V0S:
            for rc in HALO_RCS:
                v = np.sqrt(np.maximum(vb2 + halo_velocity_sq(r, v0, rc), 0))
                m = float(np.median(frac_err(v, vobs)))
                if m < best[0]:
                    best = (m, v0, rc)
        v = np.sqrt(np.maximum(vb2 + halo_velocity_sq(r, best[1], best[2]), 0))
        halo_errs.append(frac_err(v, vobs))
        per_gal[gal]["halo"] = {"v0": best[1], "rc": round(best[2], 2),
                                "err": round(best[0], 4)}
    err_halo = float(np.median(np.concatenate(halo_errs)))

    # 4. breadth check at alpha*
    improved = 0
    for gal, arr, rd in sample:
        ea = float(np.median(frac_err(ark_velocity(arr, rd, alpha_star),
                                      arr[:, 1])))
        per_gal[gal]["err_ark"] = ea
        per_gal[gal]["improved"] = bool(ea < per_gal[gal]["err_vis"])
        improved += per_gal[gal]["improved"]

    # 5. verdict (preregistered)
    passes = err_ark <= 0.90 * err_visible
    verdict = ("FAIL" if not passes else
               "LIMITED / NON-NOVEL" if err_halo <= err_ark else "PASS")

    return {
        "experiment": "ARK-DM-1",
        "timestamp_utc": datetime.datetime.utcnow().isoformat(),
        "sample": [g for g, _, _ in sample],
        "excluded": excluded,
        "alpha_star": alpha_star,
        "err_visible": err_visible,
        "err_ark": err_ark,
        "err_halo": err_halo,
        "improvement_pct": 100 * (1 - err_ark / err_visible),
        "galaxies_improved": improved,
        "kill_condition": "err_ark <= 0.90 * err_visible",
        "verdict": verdict,
        "per_galaxy": per_gal,
    }

# ----------------------------- reporting ---------------------------------
def write_results_md(res):
    pg = res["per_galaxy"]
    imp = res["improvement_pct"]
    badge = {"FAIL": "FAIL", "PASS": "PASS",
             "LIMITED / NON-NOVEL": "LIMITED / NON-NOVEL"}[res["verdict"]]

    lines = []
    a = lines.append
    a("# ARK-DM-1 -- RESULTS\n")
    a("**Experiment:** ARK-DM-1 (preregistered open-data test)")
    a(f"**Run date (UTC):** {res['timestamp_utc'][:10]}")
    a("**Data:** SPARC (Lelli, McGaugh & Schombert 2016) -- Table 1 + Rotmod_LTG")
    a("**Status:** COMPLETE -- single locked run, no post-hoc tuning\n")
    a(f"## Verdict: {badge}\n")
    a("## Headline numbers\n")
    a("| Model | Median fractional velocity error |")
    a("|---|---|")
    a(f"| Visible-matter-only baseline | {res['err_visible']:.4f} |")
    a(f"| Ark term (global alpha* = {res['alpha_star']:.2f}) | **{res['err_ark']:.4f}** |")
    a(f"| Pseudo-isothermal halo (per-galaxy, 2 params) | {res['err_halo']:.4f} |\n")
    a(f"- Improvement vs. visible-only: **{imp:.2f}%** (threshold: >=10%) -> **{res['verdict']}**")
    a(f"- Galaxies individually improved by Ark term: {res['galaxies_improved']} / {len(res['sample'])}")
    excl = "; ".join(f"{g} ({r})" for g, r in res["excluded"]) or "none"
    a(f"- Exclusions (documented quality filters): {excl}\n")
    a("## Per-galaxy results (full sample)\n")
    a("| # | Galaxy | N pts | R_disk (kpc) | Err (visible) | Err (Ark) | "
      "Improved | Halo V0 (km/s) | Halo r_c (kpc) | Err (halo) |")
    a("|---|---|---|---|---|---|---|---|---|---|")
    for i, gal in enumerate(res["sample"], 1):
        d = pg[gal]; h = d["halo"]
        mark = "yes" if d["improved"] else "no"
        a(f"| {i} | {gal} | {d['n']} | {d['Rdisk']:.2f} | "
          f"{d['err_vis']:.4f} | {d['err_ark']:.4f} | {mark} | "
          f"{h['v0']:.0f} | {h['rc']:.2f} | {h['err']:.4f} |")
    a("")

    with open("RESULTS.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

# ----------------------------- main --------------------------------------
if __name__ == "__main__":
    res = run()
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "ark_dm1_results.json"), "w") as f:
        json.dump(res, f, indent=2)
    write_results_md(res)

    print("=" * 62)
    print(f"Median frac error, visible-only  : {res['err_visible']:.4f}")
    print(f"Median frac error, Ark (a={res['alpha_star']:.2f}) : {res['err_ark']:.4f}")
    print(f"Median frac error, iso halo      : {res['err_halo']:.4f}")
    print(f"Improvement vs visible-only      : {res['improvement_pct']:.2f}%  (need >=10%)")
    print(f"Galaxies individually improved   : {res['galaxies_improved']}/{len(res['sample'])}")
    print("=" * 62)
    print("VERDICT:", res["verdict"])
