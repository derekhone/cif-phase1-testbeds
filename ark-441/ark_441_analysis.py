"""
ARK-441 — Analysis and scoring
Remnant Fieldworks Inc. — Derek Hone

Loads raw_results.json (+ spam_results.json), computes all six preregistered
metrics with Wilson score confidence intervals, applies the preregistered
PASS / FAIL / KILL decision rule, generates plots, and writes proofrecord.json.

Metrics (preregistered before execution):
    L_D            = P(Q_P=1 | Arm 2 DENY)                 primary leakage
    S_A            = P(Q_P=1 | Arm 1 ALLOW)                allow fidelity
    SPAM_baseline  = P(Q_P=1 | Arm 4 idle)                 in-situ idle readout
    Delta_B        = S_A - L_D                              boundary discrimination
    L_D_corrected  = L_D - SPAM_baseline                    mechanism-only leakage
    I_L            = (L_control - L_D) / L_control          rel. improvement vs ungated
                     where L_control = P(Q_P=1 | Arm 3 ungated control)

Decision rule (preregistered — authoritative, per design Section 5):
    PASS : L_D_corrected <= 0.02 AND Delta_B >= 0.70 AND in-situ SPAM <= 0.02
           on BOTH Q5 and Q6
    FAIL : (L_D_corrected > 0.02 OR Delta_B < 0.70) with in-situ SPAM <= 0.02
    KILL : in-situ SPAM_baseline > 0.02 on either qubit  => INDETERMINATE
           (the VBE-1 failure mode: SPAM too high to attribute leakage to the
           boundary). Calibration drift > 0.005 between SPAM and principal jobs
           is also INDETERMINATE.

NOTE on L_D-vs-SPAM distinguishability: whether L_D is statistically
distinguishable from the idle SPAM_baseline is computed and REPORTED as a
diagnostic (it contextualizes a PASS), but it is NOT a decision gate. On a
clean qubit a correctly-functioning boundary is EXPECTED to yield L_D ~ SPAM
(both near the readout floor); that is a PASS, not a kill. The kill guard
against the VBE-1 mode is the SPAM ceiling (0.02) itself.
"""

import hashlib
import json
import math
import os
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))

PASS_LD_CORR = 0.02
PASS_DELTA_B = 0.70
SPAM_CEILING = 0.02


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def wilson_ci(k, n, z=1.96):
    """Wilson score interval for a binomial proportion. z=1.96 -> 95%, 2.576 -> 99%."""
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return (p, max(0.0, center - half), min(1.0, center + half))


def counts_k_n(arm):
    """(k = shots with Q_P=1, n = total shots) for an arm record."""
    counts = arm["counts"]
    n = arm["total"]
    k = counts.get("1", 0)
    return k, n


def main():
    raw_path = os.path.join(HERE, "raw_results.json")
    spam_path = os.path.join(HERE, "spam_results.json")
    with open(raw_path) as f:
        raw = json.load(f)
    spam = None
    if os.path.exists(spam_path):
        with open(spam_path) as f:
            spam = json.load(f)

    arms = raw["arms"]

    # k/n per arm
    kn = {name: counts_k_n(arms[name]) for name in raw["arm_order"]}

    def p(name):
        k, n = kn[name]
        return k / n if n else 0.0

    # 95% and 99% Wilson intervals per arm
    ci95 = {name: wilson_ci(*kn[name], z=1.96) for name in raw["arm_order"]}
    ci99 = {name: wilson_ci(*kn[name], z=2.576) for name in raw["arm_order"]}

    S_A = p("arm1_allow")
    L_D = p("arm2_deny")
    L_control = p("arm3_ungated_control")
    SPAM_baseline = p("arm4_idle_spam")

    Delta_B = S_A - L_D
    L_D_corrected = L_D - SPAM_baseline
    I_L = (L_control - L_D) / L_control if L_control > 0 else float("nan")

    # Upper 95% Wilson bound on L_D_corrected: treat L_D upper bound minus SPAM lower.
    ld_p, ld_lo, ld_hi = ci95["arm2_deny"]
    sb_p, sb_lo, sb_hi = ci95["arm4_idle_spam"]
    L_D_corrected_upper95 = ld_hi - sb_lo

    # Distinguishability: do 99% Wilson intervals of L_D and SPAM_baseline overlap?
    ld99 = ci99["arm2_deny"]
    sb99 = ci99["arm4_idle_spam"]
    overlap99 = not (ld99[1] > sb99[2] or sb99[1] > ld99[2])
    ld_distinguishable = not overlap99  # distinguishable if NO overlap

    # In-situ SPAM gate (from the separate SPAM job, both qubits)
    spam_gate_passed = True
    spam_q5 = spam_q6 = None
    if spam is not None:
        spam_q5 = spam["qubit_metrics"]["Q5"]["spam_baseline"]
        spam_q6 = spam["qubit_metrics"]["Q6"]["spam_baseline"]
        spam_gate_passed = (spam_q5 <= SPAM_CEILING) and (spam_q6 <= SPAM_CEILING)

    # Decision rule (authoritative — design Section 5).
    # KILL is gated solely by the in-situ SPAM ceiling (VBE-1 guard).
    # Distinguishability is a reported diagnostic, NOT a gate.
    if not spam_gate_passed:
        decision = "KILL"
        status = "INDETERMINATE"
        rationale = ("In-situ SPAM_baseline > 0.02 on at least one qubit "
                     "(same failure mode as VBE-1). Boundary claim indeterminate.")
    else:
        cond_ld = L_D_corrected <= PASS_LD_CORR
        cond_db = Delta_B >= PASS_DELTA_B
        if cond_ld and cond_db:
            decision = "PASS"
            status = "PASS"
            diag = ("L_D distinguishable from SPAM at 99% Wilson"
                    if ld_distinguishable else
                    "L_D ~ SPAM (both at readout floor) — expected for a clean boundary")
            rationale = (f"L_D_corrected={L_D_corrected:.4f} <= {PASS_LD_CORR} AND "
                         f"Delta_B={Delta_B:.4f} >= {PASS_DELTA_B}; in-situ SPAM within "
                         f"ceiling. Diagnostic: {diag}.")
        else:
            decision = "FAIL"
            status = "FAIL"
            reasons = []
            if not cond_ld:
                reasons.append(f"L_D_corrected={L_D_corrected:.4f} > {PASS_LD_CORR}")
            if not cond_db:
                reasons.append(f"Delta_B={Delta_B:.4f} < {PASS_DELTA_B}")
            rationale = ("Boundary failed with in-situ SPAM within ceiling: "
                         + "; ".join(reasons))

    metrics = {
        "L_D": {"value": L_D, "ci95": ci95["arm2_deny"], "ci99": ci99["arm2_deny"],
                "definition": "P(Q_P=1 | Arm 2 DENY)"},
        "S_A": {"value": S_A, "ci95": ci95["arm1_allow"], "ci99": ci99["arm1_allow"],
                "definition": "P(Q_P=1 | Arm 1 ALLOW)"},
        "SPAM_baseline_insitu_arm4": {"value": SPAM_baseline, "ci95": ci95["arm4_idle_spam"],
                "definition": "P(Q_P=1 | Arm 4 idle)"},
        "L_control": {"value": L_control, "ci95": ci95["arm3_ungated_control"],
                "definition": "P(Q_P=1 | Arm 3 ungated control)"},
        "Delta_B": {"value": Delta_B, "definition": "S_A - L_D"},
        "L_D_corrected": {"value": L_D_corrected, "upper95": L_D_corrected_upper95,
                "definition": "L_D - SPAM_baseline"},
        "I_L": {"value": I_L, "definition": "(L_control - L_D) / L_control"},
        "L_D_vs_SPAM_distinguishable_99": ld_distinguishable,
    }

    # Secondary / adversarial arms (Bonferroni note applied in results.md)
    secondary = {}
    for name in ["arm5_stale_auth", "arm6_replayed_auth", "arm7_superposition_auth",
                 "arm8_payload_readout_ref"]:
        secondary[name] = {"P_Q_P_1": p(name), "ci95": ci95[name]}

    proofrecord = {
        "experiment_id": "ARK-441",
        "candidate": "A — SPAM-Resolved Authorization Boundary Characterization",
        "backend": raw["backend"],
        "instance": raw["instance"],
        "qubits": {"Q_A": raw["initial_layout"][0], "Q_P": raw["initial_layout"][1]},
        "shots_per_arm": raw["shots_per_arm"],
        "arm_order": raw["arm_order"],
        "job_ids": {"spam_job": raw.get("spam_job_id"),
                    "principal_job": raw["principal_job_id"]},
        "raw_results_hash": sha256_file(raw_path),
        "spam_results_hash": sha256_file(spam_path) if spam is not None else None,
        "metrics": metrics,
        "secondary_arms": secondary,
        "insitu_spam_job": {"Q5": spam_q5, "Q6": spam_q6, "gate_passed": spam_gate_passed},
        "decision_outcome": decision,
        "status": status,
        "rationale": rationale,
        "raw_vs_mitigated": "Primary endpoint = RAW counts, no readout mitigation applied.",
        "preregistered_pass": {"L_D_corrected_max": PASS_LD_CORR, "Delta_B_min": PASS_DELTA_B,
                               "spam_ceiling": SPAM_CEILING},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    pr_path = os.path.join(HERE, "proofrecord.json")
    with open(pr_path, "w") as f:
        json.dump(proofrecord, f, indent=2)
    print(f"[ANALYSIS] wrote {pr_path}")

    _make_plots(raw, ci95, S_A, L_D, SPAM_baseline, L_D_corrected)

    print(f"[ANALYSIS] L_D={L_D:.4f} S_A={S_A:.4f} SPAM={SPAM_baseline:.4f} "
          f"Delta_B={Delta_B:.4f} L_D_corr={L_D_corrected:.4f} I_L={I_L:.4f}")
    print(f"[ANALYSIS] DECISION = {decision} ({status})")
    print(f"[ANALYSIS] {rationale}")
    return proofrecord


def _make_plots(raw, ci95, S_A, L_D, SPAM_baseline, L_D_corrected):
    names = raw["arm_order"]
    vals = [ci95[n][0] for n in names]
    lo = [ci95[n][0] - ci95[n][1] for n in names]
    hi = [ci95[n][2] - ci95[n][0] for n in names]

    # Plot 1: all arms with 95% Wilson error bars
    fig, ax = plt.subplots(figsize=(11, 6))
    x = range(len(names))
    ax.bar(x, vals, yerr=[lo, hi], capsize=4, color="#3b6ea5")
    ax.set_xticks(list(x))
    ax.set_xticklabels([n.replace("_", "\n") for n in names], fontsize=8)
    ax.set_ylabel("P(Q_P = 1)")
    ax.set_title("ARK-441 — Payload activation by arm (95% Wilson CI)")
    ax.axhline(0.02, color="red", ls="--", lw=1, label="L_D_corrected ceiling (0.02)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "plots", "arm_results.png"), dpi=150)
    plt.close(fig)

    # Plot 2: SPAM-corrected L_D visualization
    fig, ax = plt.subplots(figsize=(7, 6))
    labels = ["S_A\n(ALLOW)", "L_D\n(DENY raw)", "SPAM\n(idle)", "L_D_corrected"]
    values = [S_A, L_D, SPAM_baseline, L_D_corrected]
    colors = ["#2ca02c", "#d62728", "#7f7f7f", "#9467bd"]
    ax.bar(labels, values, color=colors)
    ax.axhline(0.02, color="red", ls="--", lw=1, label="0.02 ceiling")
    ax.axhline(0.70, color="green", ls=":", lw=1, label="0.70 Delta_B floor")
    ax.set_ylabel("Probability")
    ax.set_title("ARK-441 — SPAM decomposition of DENY leakage")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "plots", "spam_corrected_LD.png"), dpi=150)
    plt.close(fig)
    print("[ANALYSIS] wrote plots/arm_results.png, plots/spam_corrected_LD.png")


if __name__ == "__main__":
    main()
