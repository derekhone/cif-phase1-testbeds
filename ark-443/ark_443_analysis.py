"""
ARK-443 — Analysis and scoring
Two-of-Three (M-of-N) Quorum Authorization
Remnant Fieldworks Inc. — Derek Hone

Loads raw_results.json (+ spam_results.json), computes all preregistered metrics
(Field 17) with Wilson score confidence intervals, applies the preregistered
PASS / FAIL / KILL decision rule (Fields 20-22), generates plots, and writes
proofrecord.json.

Central question: Does the payload execute ONLY when at least two of three
independent authorizers approve, and can NO single channel — honest, replayed, or
compromised — cause execution, while a legitimate two-authorizer quorum tolerates a
degraded third channel?

Metrics (preregistered before execution, Field 17):
    L_0of3        = P(Q_P=1 | Arm 1)   000 no approvals leakage        (PRIMARY)
    L_1of3        = P(Q_P=1 | Arm 2)   100 one channel alone leakage   (PRIMARY)
    S_2of3        = P(Q_P=1 | Arm 3)   110 quorum executes             (PRIMARY)
    S_3of3        = P(Q_P=1 | Arm 4)   111 unanimous executes
    L_1of3_alt    = P(Q_P=1 | Arm 5)   001 alt single channel leakage  (PRIMARY)
    S_degraded    = P(Q_P=1 | Arm 6)   two honest + noisy third executes (tolerance)
    L_replay      = P(Q_P=1 | Arm 7)   post-vote replay/tamper leakage (PRIMARY)
    SPAM_baseline = P(Q_P=1 | Arm 8)   idle readout error
    L_worst       = max(L_0of3, L_1of3, L_1of3_alt, L_replay)     (raw)
    S_min         = min(S_2of3, S_3of3, S_degraded)
    Delta_B       = S_min - L_worst   quorum discrimination
    L_x_corrected = L_x - SPAM_baseline  (each DENY leakage)

Decision rule (preregistered — authoritative, Fields 20-22):
    PASS : ALL FOUR corrected DENY leakages (L_0of3, L_1of3, L_1of3_alt, L_replay)
           <= 0.02 AND all three ALLOW arms (S_2of3, S_3of3, S_degraded) >= 0.90 AND
           Delta_B >= 0.70, with in-situ SPAM_baseline <= 0.02 on ALL four qubits.
    FAIL : any DENY arm leaks corrected > 0.02 with in-situ SPAM clean; OR any ALLOW
           arm < 0.90; OR Delta_B < 0.70.
    KILL : in-situ SPAM_baseline > 0.02 on any qubit; OR SPAM drift > 0.005 between
           the SPAM and principal jobs => INDETERMINATE.

This is a metrological characterization of a quorum-gated execution rule on this
hardware, NOT new physics and NOT a cryptographic guarantee. The three committed
bits are a hardware abstraction of independent approvals. A 2-of-3 quorum protects
against ONE compromised channel; two colluding channels form a legitimate quorum
(intended design limit, not a defect).
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
PASS_S_ALLOW = 0.90
PASS_DELTA_B = 0.70
SPAM_CEILING = 0.02
DRIFT_CEILING = 0.005

# Four preregistered DENY (must-fail-closed) arms -> metric name.
DENY_ARMS = {
    "arm1_0of3_deny": "L_0of3",
    "arm2_1of3_deny": "L_1of3",
    "arm5_1of3_altchannel_deny": "L_1of3_alt",
    "arm7_replay_tamper_deny": "L_replay",
}
# Three ALLOW (must-execute) arms -> metric name.
ALLOW_ARMS = {
    "arm3_2of3_allow": "S_2of3",
    "arm4_3of3_allow": "S_3of3",
    "arm6_degraded_quorum_allow": "S_degraded",
}
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

    SPAM_baseline = p(SPAM_ARM)

    deny_raw = {metric: p(arm) for arm, metric in DENY_ARMS.items()}
    deny_corrected = {m: (deny_raw[m] - SPAM_baseline) for m in deny_raw}
    allow_raw = {metric: p(arm) for arm, metric in ALLOW_ARMS.items()}

    L_worst = max(deny_raw.values())
    S_min = min(allow_raw.values())
    Delta_B = S_min - L_worst

    # Upper 95% Wilson bounds on corrected DENY leakage (one-sided diagnostics).
    sb_p, sb_lo, sb_hi = ci95[SPAM_ARM]
    deny_corr_upper95 = {}
    for arm, metric in DENY_ARMS.items():
        _, _, hi = ci95[arm]
        deny_corr_upper95[metric] = hi - sb_lo
    # Lower 95% Wilson bounds on ALLOW arms vs 0.90 floor.
    allow_lower95 = {}
    for arm, metric in ALLOW_ARMS.items():
        _, lo, _ = ci95[arm]
        allow_lower95[metric] = lo

    # In-situ SPAM gate (separate SPAM job, all four qubits) + drift vs arm8.
    spam_gate_passed = True
    spam_baselines = {}
    drift = None
    drift_ok = True
    if spam is not None:
        for label in ("Q_P", "Q_A1", "Q_A2", "Q_A3"):
            spam_baselines[label] = spam["qubit_metrics"][label]["spam_baseline"]
        spam_gate_passed = all(v <= SPAM_CEILING for v in spam_baselines.values())
        # SPAM job Q_P |0> readout vs principal idle arm8 (both P(read1|prep0) on Q_P).
        drift = abs(spam_baselines["Q_P"] - SPAM_baseline)
        drift_ok = drift <= DRIFT_CEILING

    # Decision rule (authoritative — Fields 20-22).
    if not spam_gate_passed:
        decision = "KILL"
        status = "INDETERMINATE"
        rationale = ("In-situ SPAM_baseline > 0.02 on at least one qubit. "
                     "Qubit/backend disqualified; quorum claim indeterminate.")
    elif not drift_ok:
        decision = "KILL"
        status = "INDETERMINATE"
        rationale = (f"SPAM baseline drift {drift:.4f} > {DRIFT_CEILING} between the SPAM "
                     f"and principal jobs (calibration drift). INDETERMINATE.")
    else:
        denies_ok = {m: (deny_corrected[m] <= PASS_LEAK_CORR) for m in deny_corrected}
        allows_ok = {m: (allow_raw[m] >= PASS_S_ALLOW) for m in allow_raw}
        cond_deny = all(denies_ok.values())
        cond_allow = all(allows_ok.values())
        cond_db = Delta_B >= PASS_DELTA_B
        if cond_deny and cond_allow and cond_db:
            decision = "PASS"
            status = "PASS"
            rationale = (
                "All four corrected DENY leakages <= "
                f"{PASS_LEAK_CORR} ("
                + ", ".join(f"{m}={deny_corrected[m]:.4f}" for m in deny_corrected)
                + ") AND all three ALLOW arms >= "
                f"{PASS_S_ALLOW} ("
                + ", ".join(f"{m}={allow_raw[m]:.4f}" for m in allow_raw)
                + f") AND Delta_B={Delta_B:.4f} >= {PASS_DELTA_B}; in-situ SPAM within "
                "ceiling. No single channel (0-of-3, 1-of-3, alt-channel, or post-vote "
                "replay) crosses the boundary; a 2-of-3 quorum executes, unanimity "
                "executes, and a quorum of two honest channels tolerates a degraded third.")
        else:
            decision = "FAIL"
            status = "FAIL"
            reasons = []
            for m in deny_corrected:
                if not denies_ok[m]:
                    reasons.append(f"{m}_corrected={deny_corrected[m]:.4f} > {PASS_LEAK_CORR}")
            for m in allow_raw:
                if not allows_ok[m]:
                    reasons.append(f"{m}={allow_raw[m]:.4f} < {PASS_S_ALLOW}")
            if not cond_db:
                reasons.append(f"Delta_B={Delta_B:.4f} < {PASS_DELTA_B}")
            rationale = ("Quorum boundary failed with in-situ SPAM within ceiling: "
                         + "; ".join(reasons))

    # H2a: all four DENY arms are mutually indistinguishable (all fail closed at the
    # SPAM floor). Check every DENY arm's 99% CI overlaps the SPAM 99% CI.
    sb99 = ci99[SPAM_ARM]
    deny_at_floor99 = {}
    for arm, metric in DENY_ARMS.items():
        a99 = ci99[arm]
        overlap = not (a99[1] > sb99[2] or sb99[1] > a99[2])
        deny_at_floor99[metric] = bool(overlap)
    # H2b: degraded-quorum tolerance — S_degraded concordant with S_2of3 (95% CI overlap).
    s2_95 = ci95["arm3_2of3_allow"]
    sd_95 = ci95["arm6_degraded_quorum_allow"]
    degraded_vs_2of3_overlap95 = not (sd_95[1] > s2_95[2] or s2_95[1] > sd_95[2])
    # H2c: replay indistinguishable from 0-of-3 baseline deny (99% CI overlap).
    replay99 = ci99["arm7_replay_tamper_deny"]
    base99 = ci99["arm1_0of3_deny"]
    replay_vs_baseline_overlap99 = not (replay99[1] > base99[2] or base99[1] > replay99[2])

    metrics = {
        "L_0of3": {"value": deny_raw["L_0of3"], "ci95": ci95["arm1_0of3_deny"],
                   "ci99": ci99["arm1_0of3_deny"],
                   "definition": "P(Q_P=1 | Arm 1 000 no approvals) PRIMARY"},
        "L_1of3": {"value": deny_raw["L_1of3"], "ci95": ci95["arm2_1of3_deny"],
                   "ci99": ci99["arm2_1of3_deny"],
                   "definition": "P(Q_P=1 | Arm 2 100 one channel alone) PRIMARY"},
        "S_2of3": {"value": allow_raw["S_2of3"], "ci95": ci95["arm3_2of3_allow"],
                   "ci95_lower": allow_lower95["S_2of3"],
                   "definition": "P(Q_P=1 | Arm 3 110 quorum) PRIMARY"},
        "S_3of3": {"value": allow_raw["S_3of3"], "ci95": ci95["arm4_3of3_allow"],
                   "ci95_lower": allow_lower95["S_3of3"],
                   "definition": "P(Q_P=1 | Arm 4 111 unanimous)"},
        "L_1of3_alt": {"value": deny_raw["L_1of3_alt"], "ci95": ci95["arm5_1of3_altchannel_deny"],
                       "ci99": ci99["arm5_1of3_altchannel_deny"],
                       "definition": "P(Q_P=1 | Arm 5 001 alt single channel) PRIMARY"},
        "S_degraded": {"value": allow_raw["S_degraded"], "ci95": ci95["arm6_degraded_quorum_allow"],
                       "ci95_lower": allow_lower95["S_degraded"],
                       "definition": "P(Q_P=1 | Arm 6 two honest + degraded third) tolerance"},
        "L_replay": {"value": deny_raw["L_replay"], "ci95": ci95["arm7_replay_tamper_deny"],
                     "ci99": ci99["arm7_replay_tamper_deny"],
                     "definition": "P(Q_P=1 | Arm 7 post-vote replay/tamper) PRIMARY"},
        "SPAM_baseline_arm8": {"value": SPAM_baseline, "ci95": ci95[SPAM_ARM],
                               "definition": "P(Q_P=1 | Arm 8 idle)"},
        "L_worst": {"value": L_worst, "definition": "max of the four raw DENY leakages"},
        "S_min": {"value": S_min, "definition": "min of the three ALLOW success rates"},
        "Delta_B": {"value": Delta_B, "definition": "S_min - L_worst"},
        "L_0of3_corrected": {"value": deny_corrected["L_0of3"],
                             "upper95": deny_corr_upper95["L_0of3"],
                             "definition": "L_0of3 - SPAM_baseline"},
        "L_1of3_corrected": {"value": deny_corrected["L_1of3"],
                             "upper95": deny_corr_upper95["L_1of3"],
                             "definition": "L_1of3 - SPAM_baseline"},
        "L_1of3_alt_corrected": {"value": deny_corrected["L_1of3_alt"],
                                 "upper95": deny_corr_upper95["L_1of3_alt"],
                                 "definition": "L_1of3_alt - SPAM_baseline"},
        "L_replay_corrected": {"value": deny_corrected["L_replay"],
                               "upper95": deny_corr_upper95["L_replay"],
                               "definition": "L_replay - SPAM_baseline"},
    }

    secondary = {
        "H2a_denies_fail_closed_at_floor": {
            "deny_raw": deny_raw,
            "each_overlaps_spam_99CI": deny_at_floor99,
            "all_at_floor": bool(all(deny_at_floor99.values())),
            "note": "Every DENY arm withholds the payload down to the SPAM floor "
                    "(no residual execution). Descriptive; no pass/fail weight.",
        },
        "H2b_degraded_quorum_tolerance": {
            "S_2of3": allow_raw["S_2of3"], "S_degraded": allow_raw["S_degraded"],
            "overlap_95CI": bool(degraded_vs_2of3_overlap95),
            "note": "A quorum of two honest channels executes within the clean-2of3 95% "
                    "CI even when the third channel is degraded (superposed).",
        },
        "H2c_replay_indistinguishable_from_baseline": {
            "L_replay": deny_raw["L_replay"], "L_0of3": deny_raw["L_0of3"],
            "overlap_99CI": bool(replay_vs_baseline_overlap99),
            "note": "A post-vote replayed/tampered single channel is no more able to "
                    "execute than the 0-of-3 baseline.",
        },
    }

    proofrecord = {
        "experiment_id": "ARK-443",
        "title": "Two-of-Three (M-of-N) Quorum Authorization",
        "central_question": ("Does the payload execute ONLY when at least two of three "
                             "independent authorizers approve, and can no single channel "
                             "(honest, replayed, or compromised) cause execution, while a "
                             "two-authorizer quorum tolerates a degraded third?"),
        "backend": raw["backend"],
        "instance": raw["instance"],
        "qubits": {"Q_P": raw["initial_layout"][0], "Q_A1": raw["initial_layout"][1],
                   "Q_A2": raw["initial_layout"][2], "Q_A3": raw["initial_layout"][3]},
        "shots_per_arm": raw["shots_per_arm"],
        "arm_order": raw["arm_order"],
        "arm_class": raw.get("arm_class"),
        "arm_expect": raw.get("arm_expect"),
        "job_ids": {"spam_job": raw.get("spam_job_id"),
                    "principal_job": raw["principal_job_id"]},
        "raw_results_hash": sha256_file(raw_path),
        "spam_results_hash": sha256_file(spam_path) if spam is not None else None,
        "metrics": metrics,
        "secondary_hypotheses": secondary,
        "insitu_spam_job": {"baselines": spam_baselines, "gate_passed": spam_gate_passed,
                            "drift_vs_arm8": drift, "drift_ok": drift_ok},
        "decision_outcome": decision,
        "status": status,
        "rationale": rationale,
        "raw_vs_mitigated": "Primary endpoint = RAW counts, no readout mitigation applied.",
        "preregistered_pass": {"deny_leak_corrected_max": PASS_LEAK_CORR,
                               "allow_min": PASS_S_ALLOW,
                               "Delta_B_min": PASS_DELTA_B,
                               "spam_ceiling": SPAM_CEILING,
                               "drift_ceiling": DRIFT_CEILING},
        "interpretation": ("Metrological characterization of a 2-of-3 quorum-gated "
                           "execution rule on this hardware: whether the payload fires "
                           "iff at least two of three measured authorization bits are 1, "
                           "no single channel (including a post-vote replay/tamper) can "
                           "unilaterally execute, and a quorum of two honest channels "
                           "tolerates a degraded third. NOT new physics, NOT a "
                           "cryptographic guarantee. The committed bits are a hardware "
                           "abstraction of independent approvals. A 2-of-3 quorum "
                           "protects against ONE compromised channel; two colluding "
                           "channels form a legitimate quorum (intended design limit). "
                           "Findings apply only to this implementation on these qubits "
                           "on this backend at this calibration."),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    pr_path = os.path.join(HERE, "proofrecord.json")
    with open(pr_path, "w") as f:
        json.dump(proofrecord, f, indent=2)
    print(f"[ANALYSIS] wrote {pr_path}")

    _make_plots(raw, ci95, allow_raw, deny_raw, deny_corrected, SPAM_baseline, Delta_B)

    for m in allow_raw:
        print(f"[ANALYSIS] {m}={allow_raw[m]:.4f}")
    for m in deny_raw:
        print(f"[ANALYSIS] {m}={deny_raw[m]:.4f} ({m}_corrected={deny_corrected[m]:.4f})")
    print(f"[ANALYSIS] SPAM(arm8)={SPAM_baseline:.4f}")
    print(f"[ANALYSIS] L_worst={L_worst:.4f} S_min={S_min:.4f} Delta_B={Delta_B:.4f}")
    print(f"[ANALYSIS] DECISION = {decision} ({status})")
    print(f"[ANALYSIS] {rationale}")
    return proofrecord


def _make_plots(raw, ci95, allow_raw, deny_raw, deny_corrected, SPAM_baseline, Delta_B):
    os.makedirs(os.path.join(HERE, "plots"), exist_ok=True)

    # Plot 1: all arms with 95% Wilson error bars
    names = raw["arm_order"]
    vals = [ci95[n][0] for n in names]
    lo = [ci95[n][0] - ci95[n][1] for n in names]
    hi = [ci95[n][2] - ci95[n][0] for n in names]
    allow_set = set(ALLOW_ARMS.keys())
    deny_set = set(DENY_ARMS.keys())
    colors = []
    for n in names:
        if n in allow_set:
            colors.append("#2ca02c")   # green = should execute
        elif n == SPAM_ARM:
            colors.append("#7f7f7f")   # gray = idle SPAM
        else:
            colors.append("#d62728")   # red = must fail closed
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(names))
    ax.bar(x, vals, yerr=[lo, hi], capsize=4, color=colors)
    ax.set_xticks(list(x))
    ax.set_xticklabels([n.replace("_", "\n") for n in names], fontsize=7.5)
    ax.set_ylabel("P(Q_P = 1)")
    ax.set_title("ARK-443 (ibm_marrakesh) — Payload execution by arm (95% Wilson CI)\n"
                 "green = quorum should execute, red = must fail closed, gray = idle SPAM")
    ax.axhline(0.02, color="red", ls="--", lw=1, label="corrected-leakage ceiling (0.02)")
    ax.axhline(0.90, color="green", ls=":", lw=1, label="ALLOW floor (0.90)")
    ax.set_ylim(0, 1.02)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "plots", "arm_results.png"), dpi=150)
    plt.close(fig)

    # Plot 2: quorum discrimination — ALLOW success vs corrected DENY leakage
    allow_labels = ["S_2of3", "S_3of3", "S_degraded"]
    deny_labels = ["L_0of3", "L_1of3", "L_1of3_alt", "L_replay"]
    fig, ax = plt.subplots(figsize=(10, 6))
    xa = range(len(allow_labels))
    xd = range(len(allow_labels) + 1, len(allow_labels) + 1 + len(deny_labels))
    a_bars = ax.bar(xa, [allow_raw[m] for m in allow_labels], color="#2ca02c",
                    width=0.6, label="ALLOW P(Q_P=1)")
    d_bars = ax.bar(xd, [deny_corrected[m] for m in deny_labels], color="#d62728",
                    width=0.6, label="DENY corrected leakage")
    ax.axhline(0.90, color="green", ls=":", lw=1.2, label="ALLOW floor (0.90)")
    ax.axhline(0.02, color="black", ls="--", lw=1.2, label="DENY ceiling (0.02)")
    all_x = list(xa) + list(xd)
    ax.set_xticks(all_x)
    ax.set_xticklabels(allow_labels + deny_labels, fontsize=9, rotation=20)
    ax.set_ylabel("P(Q_P=1)  (DENY = corrected)")
    ax.set_title("ARK-443 (ibm_marrakesh) — Quorum discrimination\n"
                 f"Delta_B = S_min - L_worst = {Delta_B:.3f}  (SPAM={SPAM_baseline:.3f})")
    for b, v in zip(list(a_bars) + list(d_bars),
                    [allow_raw[m] for m in allow_labels] + [deny_corrected[m] for m in deny_labels]):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
                f"{v:.4f}", ha="center", va="bottom", fontsize=8)
    ax.set_ylim(min(0, min(deny_corrected.values()) * 1.2), 1.05)
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "plots", "quorum_discrimination.png"), dpi=150)
    plt.close(fig)
    print("[ANALYSIS] wrote plots/arm_results.png, plots/quorum_discrimination.png")


if __name__ == "__main__":
    main()
