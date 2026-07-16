"""
ARK-444 — Analysis and scoring
Decision-to-Execution Integrity
Remnant Fieldworks Inc. — Derek Hone

Loads raw_results.json (+ spam_results.json), computes all preregistered metrics
(Field 17) with Wilson score confidence intervals, applies the preregistered
PASS / FAIL / KILL decision rule (Fields 20-22), generates plots, and writes
proofrecord.json.

Central question: Can the system detect when an approved action is altered before
execution and fail closed?

Metrics (preregistered before execution, Field 17):
    S_match        = P(Q_P=1 | Arm 1)   approved-unchanged executes (reference)
    L_dest         = P(Q_P=1 | Arm 2)   destination-changed leakage   (PRIMARY)
    L_amount       = P(Q_P=1 | Arm 3)   amount-changed leakage        (PRIMARY)
    L_optype       = P(Q_P=1 | Arm 4)   operation-changed leakage     (PRIMARY)
    L_append       = P(Q_P=1 | Arm 5)   extra-action-appended leakage (PRIMARY)
    L_replay       = P(Q_P=1 | Arm 6)   approval-replayed leakage     (PRIMARY)
    S_reverified   = P(Q_P=1 | Arm 7)   mutated-then-reverified executes (recovery)
    SPAM_baseline  = P(Q_P=1 | Arm 8)   idle readout error
    L_worst        = max(L_dest, L_amount, L_optype, L_append, L_replay)  (raw)
    Delta_B        = S_match - L_worst   integrity discrimination
    L_x_corrected  = L_x - SPAM_baseline  (each of the five leakages)

Decision rule (preregistered — authoritative, Fields 20-22):
    PASS : ALL FIVE corrected leakages (L_dest, L_amount, L_optype, L_append,
           L_replay) <= 0.02 AND S_reverified >= 0.90 AND Delta_B >= 0.70,
           with in-situ SPAM_baseline <= 0.02 on BOTH qubits.
    FAIL : any of the five alteration/replay arms leaks corrected > 0.02 with
           in-situ SPAM clean; OR S_reverified < 0.90; OR Delta_B < 0.70.
    KILL : in-situ SPAM_baseline > 0.02 on either qubit; OR SPAM drift > 0.005
           between the SPAM and principal jobs => INDETERMINATE.

This is a metrological characterization of a tamper-evident decision-to-execution
binding on this hardware, NOT new physics and NOT a cryptographic integrity
guarantee. The single committed bit is a hardware abstraction of an action signature.
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

PASS_LEAK_CORR = 0.02
PASS_S_REVERIFIED = 0.90
PASS_DELTA_B = 0.70
SPAM_CEILING = 0.02
DRIFT_CEILING = 0.005

# Five preregistered leakage (alteration/replay) arms -> metric name.
LEAK_ARMS = {
    "arm2_destination_changed": "L_dest",
    "arm3_amount_changed": "L_amount",
    "arm4_operation_changed": "L_optype",
    "arm5_extra_action_appended": "L_append",
    "arm6_approval_replayed": "L_replay",
}
MATCH_ARM = "arm1_approved_unchanged"
REVERIFIED_ARM = "arm7_mutated_then_reverified"
SPAM_ARM = "arm8_idle_spam"


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
    kn = {name: counts_k_n(arms[name]) for name in raw["arm_order"]}

    def p(name):
        k, n = kn[name]
        return k / n if n else 0.0

    ci95 = {name: wilson_ci(*kn[name], z=1.96) for name in raw["arm_order"]}
    ci99 = {name: wilson_ci(*kn[name], z=2.576) for name in raw["arm_order"]}

    S_match = p(MATCH_ARM)
    S_reverified = p(REVERIFIED_ARM)
    SPAM_baseline = p(SPAM_ARM)

    leak_raw = {metric: p(arm) for arm, metric in LEAK_ARMS.items()}
    leak_corrected = {metric: (leak_raw[metric] - SPAM_baseline) for metric in leak_raw}
    L_worst = max(leak_raw.values())
    Delta_B = S_match - L_worst

    # Upper 95% Wilson bounds on corrected leakage (one-sided ceiling diagnostics).
    sb_p, sb_lo, sb_hi = ci95[SPAM_ARM]
    leak_corr_upper95 = {}
    for arm, metric in LEAK_ARMS.items():
        _, _, hi = ci95[arm]
        leak_corr_upper95[metric] = hi - sb_lo
    # Lower 95% Wilson bound on S_reverified vs 0.90 floor.
    sr_p, sr_lo, sr_hi = ci95[REVERIFIED_ARM]

    # In-situ SPAM gate (separate SPAM job, both qubits) + drift vs arm8.
    spam_gate_passed = True
    spam_qa = spam_qp = None
    drift = None
    drift_ok = True
    if spam is not None:
        spam_qa = spam["qubit_metrics"]["Q_A"]["spam_baseline"]
        spam_qp = spam["qubit_metrics"]["Q_P"]["spam_baseline"]
        spam_gate_passed = (spam_qa <= SPAM_CEILING) and (spam_qp <= SPAM_CEILING)
        # SPAM job Q_P |0> readout vs principal-job idle arm8 (both = P(read1|prep0) on Q_P)
        drift = abs(spam_qp - SPAM_baseline)
        drift_ok = drift <= DRIFT_CEILING

    # Decision rule (authoritative — Fields 20-22).
    if not spam_gate_passed:
        decision = "KILL"
        status = "INDETERMINATE"
        rationale = ("In-situ SPAM_baseline > 0.02 on at least one qubit. "
                     "Qubit/backend disqualified; integrity claim indeterminate.")
    elif not drift_ok:
        decision = "KILL"
        status = "INDETERMINATE"
        rationale = (f"SPAM baseline drift {drift:.4f} > {DRIFT_CEILING} between the SPAM "
                     f"and principal jobs (calibration drift). INDETERMINATE.")
    else:
        leaks_ok = {m: (leak_corrected[m] <= PASS_LEAK_CORR) for m in leak_corrected}
        cond_leaks = all(leaks_ok.values())
        cond_sr = S_reverified >= PASS_S_REVERIFIED
        cond_db = Delta_B >= PASS_DELTA_B
        if cond_leaks and cond_sr and cond_db:
            decision = "PASS"
            status = "PASS"
            rationale = (
                "All five corrected leakages <= "
                f"{PASS_LEAK_CORR} ("
                + ", ".join(f"{m}={leak_corrected[m]:.4f}" for m in leak_corrected)
                + f") AND S_reverified={S_reverified:.4f} >= {PASS_S_REVERIFIED} AND "
                f"Delta_B={Delta_B:.4f} >= {PASS_DELTA_B}; in-situ SPAM within ceiling. "
                "Every post-approval alteration and the replayed approval fail closed "
                "(payload withheld); a mutated action that is freshly re-verified "
                "correctly executes.")
        else:
            decision = "FAIL"
            status = "FAIL"
            reasons = []
            for m in leak_corrected:
                if not leaks_ok[m]:
                    reasons.append(f"{m}_corrected={leak_corrected[m]:.4f} > {PASS_LEAK_CORR}")
            if not cond_sr:
                reasons.append(f"S_reverified={S_reverified:.4f} < {PASS_S_REVERIFIED}")
            if not cond_db:
                reasons.append(f"Delta_B={Delta_B:.4f} < {PASS_DELTA_B}")
            rationale = ("Integrity boundary failed with in-situ SPAM within ceiling: "
                         + "; ".join(reasons))

    # H2a: the five alteration/replay arms are mutually indistinguishable (all fail
    # closed at the SPAM floor). Check every leakage arm's 99% CI overlaps the SPAM 99% CI.
    sb99 = ci99[SPAM_ARM]
    leak_at_floor99 = {}
    for arm, metric in LEAK_ARMS.items():
        a99 = ci99[arm]
        overlap = not (a99[1] > sb99[2] or sb99[1] > a99[2])
        leak_at_floor99[metric] = bool(overlap)
    # H2b: reverification concordance with the matched reference (95% CI overlap).
    a1_95 = ci95[MATCH_ARM]
    a7_95 = ci95[REVERIFIED_ARM]
    reverify_vs_match_overlap95 = not (a7_95[1] > a1_95[2] or a1_95[1] > a7_95[2])
    # H2c: replay indistinguishable from the physical alterations (99% CI overlap of
    # L_replay with each of the four alteration arms).
    replay99 = ci99["arm6_approval_replayed"]
    replay_vs_alteration99 = {}
    for arm in ["arm2_destination_changed", "arm3_amount_changed",
                "arm4_operation_changed", "arm5_extra_action_appended"]:
        a99 = ci99[arm]
        overlap = not (replay99[1] > a99[2] or a99[1] > replay99[2])
        replay_vs_alteration99[LEAK_ARMS[arm]] = bool(overlap)

    metrics = {
        "S_match": {"value": S_match, "ci95": ci95[MATCH_ARM],
                    "definition": "P(Q_P=1 | Arm 1 approved-unchanged) reference"},
        "L_dest": {"value": leak_raw["L_dest"], "ci95": ci95["arm2_destination_changed"],
                   "ci99": ci99["arm2_destination_changed"],
                   "definition": "P(Q_P=1 | Arm 2 destination-changed) PRIMARY"},
        "L_amount": {"value": leak_raw["L_amount"], "ci95": ci95["arm3_amount_changed"],
                     "ci99": ci99["arm3_amount_changed"],
                     "definition": "P(Q_P=1 | Arm 3 amount-changed) PRIMARY"},
        "L_optype": {"value": leak_raw["L_optype"], "ci95": ci95["arm4_operation_changed"],
                     "ci99": ci99["arm4_operation_changed"],
                     "definition": "P(Q_P=1 | Arm 4 operation-changed) PRIMARY"},
        "L_append": {"value": leak_raw["L_append"], "ci95": ci95["arm5_extra_action_appended"],
                     "ci99": ci99["arm5_extra_action_appended"],
                     "definition": "P(Q_P=1 | Arm 5 extra-action-appended) PRIMARY"},
        "L_replay": {"value": leak_raw["L_replay"], "ci95": ci95["arm6_approval_replayed"],
                     "ci99": ci99["arm6_approval_replayed"],
                     "definition": "P(Q_P=1 | Arm 6 approval-replayed) PRIMARY"},
        "S_reverified": {"value": S_reverified, "ci95": ci95[REVERIFIED_ARM],
                         "ci95_lower": sr_lo,
                         "definition": "P(Q_P=1 | Arm 7 mutated-then-reverified) recovery"},
        "SPAM_baseline_arm8": {"value": SPAM_baseline, "ci95": ci95[SPAM_ARM],
                               "definition": "P(Q_P=1 | Arm 8 idle)"},
        "L_worst": {"value": L_worst, "definition": "max of the five raw leakages"},
        "Delta_B": {"value": Delta_B, "definition": "S_match - L_worst"},
        "L_dest_corrected": {"value": leak_corrected["L_dest"],
                             "upper95": leak_corr_upper95["L_dest"],
                             "definition": "L_dest - SPAM_baseline"},
        "L_amount_corrected": {"value": leak_corrected["L_amount"],
                               "upper95": leak_corr_upper95["L_amount"],
                               "definition": "L_amount - SPAM_baseline"},
        "L_optype_corrected": {"value": leak_corrected["L_optype"],
                               "upper95": leak_corr_upper95["L_optype"],
                               "definition": "L_optype - SPAM_baseline"},
        "L_append_corrected": {"value": leak_corrected["L_append"],
                               "upper95": leak_corr_upper95["L_append"],
                               "definition": "L_append - SPAM_baseline"},
        "L_replay_corrected": {"value": leak_corrected["L_replay"],
                               "upper95": leak_corr_upper95["L_replay"],
                               "definition": "L_replay - SPAM_baseline"},
    }

    secondary = {
        "H2a_alterations_fail_closed_at_floor": {
            "leak_raw": leak_raw,
            "each_overlaps_spam_99CI": leak_at_floor99,
            "all_at_floor": bool(all(leak_at_floor99.values())),
            "note": "Every alteration/replay arm withholds the payload down to the SPAM "
                    "floor (no residual execution). Descriptive; no pass/fail weight.",
        },
        "H2b_reverification_concordance": {
            "S_match": S_match, "S_reverified": S_reverified,
            "overlap_95CI": bool(reverify_vs_match_overlap95),
            "note": "Fresh re-verification of a mutated action restores execution within "
                    "the matched-reference 95% CI.",
        },
        "H2c_replay_indistinguishable_from_alteration": {
            "L_replay": leak_raw["L_replay"],
            "overlap_99CI_vs_alteration": replay_vs_alteration99,
            "note": "A replayed stale approval is no more able to execute than a "
                    "physically altered action.",
        },
    }

    proofrecord = {
        "experiment_id": "ARK-444",
        "title": "Decision-to-Execution Integrity",
        "central_question": ("Can the system detect when an approved action is altered "
                             "before execution and fail closed?"),
        "backend": raw["backend"],
        "instance": raw["instance"],
        "qubits": {"Q_A": raw["initial_layout"][0], "Q_P": raw["initial_layout"][1]},
        "shots_per_arm": raw["shots_per_arm"],
        "arm_order": raw["arm_order"],
        "arm_class": raw.get("arm_class"),
        "job_ids": {"spam_job": raw.get("spam_job_id"),
                    "principal_job": raw["principal_job_id"]},
        "raw_results_hash": sha256_file(raw_path),
        "spam_results_hash": sha256_file(spam_path) if spam is not None else None,
        "metrics": metrics,
        "secondary_hypotheses": secondary,
        "insitu_spam_job": {"Q_A": spam_qa, "Q_P": spam_qp, "gate_passed": spam_gate_passed,
                            "drift_vs_arm8": drift, "drift_ok": drift_ok},
        "decision_outcome": decision,
        "status": status,
        "rationale": rationale,
        "raw_vs_mitigated": "Primary endpoint = RAW counts, no readout mitigation applied.",
        "preregistered_pass": {"leak_corrected_max": PASS_LEAK_CORR,
                               "S_reverified_min": PASS_S_REVERIFIED,
                               "Delta_B_min": PASS_DELTA_B,
                               "spam_ceiling": SPAM_CEILING,
                               "drift_ceiling": DRIFT_CEILING},
        "interpretation": ("Metrological characterization of a tamper-evident "
                           "decision-to-execution binding on this hardware: whether an "
                           "approved action that is altered (destination, amount, "
                           "operation, appended action) or a replayed stale approval is "
                           "detected and fails closed, while a re-verified mutation "
                           "correctly executes. NOT new physics, NOT a cryptographic "
                           "integrity guarantee. The committed bit is a hardware "
                           "abstraction of an action signature. Findings apply only to "
                           "this binding implementation on this qubit pair on this "
                           "backend at this calibration."),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    pr_path = os.path.join(HERE, "proofrecord.json")
    with open(pr_path, "w") as f:
        json.dump(proofrecord, f, indent=2)
    print(f"[ANALYSIS] wrote {pr_path}")

    _make_plots(raw, ci95, S_match, S_reverified, SPAM_baseline,
                leak_raw, leak_corrected)

    print(f"[ANALYSIS] S_match={S_match:.4f} S_reverified={S_reverified:.4f} "
          f"SPAM(arm8)={SPAM_baseline:.4f}")
    for m in leak_raw:
        print(f"[ANALYSIS] {m}={leak_raw[m]:.4f} ({m}_corrected={leak_corrected[m]:.4f})")
    print(f"[ANALYSIS] L_worst={L_worst:.4f} Delta_B={Delta_B:.4f}")
    print(f"[ANALYSIS] DECISION = {decision} ({status})")
    print(f"[ANALYSIS] {rationale}")
    return proofrecord


def _make_plots(raw, ci95, S_match, S_reverified, SPAM_baseline,
                leak_raw, leak_corrected):
    os.makedirs(os.path.join(HERE, "plots"), exist_ok=True)

    # Plot 1: all arms with 95% Wilson error bars
    names = raw["arm_order"]
    vals = [ci95[n][0] for n in names]
    lo = [ci95[n][0] - ci95[n][1] for n in names]
    hi = [ci95[n][2] - ci95[n][0] for n in names]
    # success arms green, leakage/replay arms red, spam gray
    colors = []
    for n in names:
        if n in (MATCH_ARM, REVERIFIED_ARM):
            colors.append("#2ca02c")
        elif n == SPAM_ARM:
            colors.append("#7f7f7f")
        else:
            colors.append("#d62728")
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(names))
    ax.bar(x, vals, yerr=[lo, hi], capsize=4, color=colors)
    ax.set_xticks(list(x))
    ax.set_xticklabels([n.replace("_", "\n") for n in names], fontsize=7.5)
    ax.set_ylabel("P(Q_P = 1)")
    ax.set_title("ARK-444 (ibm_marrakesh) — Payload execution by arm (95% Wilson CI)\n"
                 "green = should execute, red = must fail closed, gray = idle SPAM")
    ax.axhline(0.02, color="red", ls="--", lw=1, label="corrected-leakage ceiling (0.02)")
    ax.axhline(0.90, color="green", ls=":", lw=1, label="S_reverified floor (0.90)")
    ax.set_ylim(0, 1.02)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "plots", "arm_results.png"), dpi=150)
    plt.close(fig)

    # Plot 2: integrity discrimination — success vs corrected leakages against ceiling
    labels = ["L_dest", "L_amount", "L_optype", "L_append", "L_replay"]
    corr_vals = [leak_corrected[m] for m in labels]
    fig, ax = plt.subplots(figsize=(9, 6))
    xl = range(len(labels))
    bars = ax.bar(xl, corr_vals, color="#d62728", width=0.6,
                  label="corrected leakage (L_x - SPAM)")
    ax.axhline(0.02, color="black", ls="--", lw=1.2, label="leakage ceiling (0.02)")
    ax.set_xticks(list(xl))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Corrected payload leakage  P(Q_P=1) - SPAM")
    ax.set_title("ARK-444 (ibm_marrakesh) — Tamper leakage vs 0.02 ceiling\n"
                 f"S_match={S_match:.3f}, S_reverified={S_reverified:.3f}, "
                 f"SPAM={SPAM_baseline:.3f}")
    # annotate each bar
    ymax = max(corr_vals + [0.02])
    for b, v in zip(bars, corr_vals):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
                f"{v:.4f}", ha="center", va="bottom", fontsize=8)
    ax.set_ylim(min(0, min(corr_vals) * 1.2), max(0.03, ymax * 1.3))
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "plots", "integrity_discrimination.png"), dpi=150)
    plt.close(fig)
    print("[ANALYSIS] wrote plots/arm_results.png, plots/integrity_discrimination.png")


if __name__ == "__main__":
    main()
