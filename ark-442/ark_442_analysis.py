"""
ARK-442 — Analysis and scoring
Authorization Boundary Degradation Under Verification-to-Execution Delay
Remnant Fieldworks Inc. — Derek Hone

Loads raw_results.json (+ spam_results.json), computes all preregistered metrics
(Field 17) with Wilson score confidence intervals, applies the preregistered
PASS / FAIL / KILL decision rule (Fields 20-22), generates plots (including the
S_A(delay) decay curve, H2a), and writes proofrecord.json.

Metrics (preregistered before execution, Field 17):
    S_A_0          = P(Q_P=1 | Arm 1)   ALLOW reference (0 us)
    S_A_short      = P(Q_P=1 | Arm 2)   ALLOW, ~0.5 us
    S_A_medium     = P(Q_P=1 | Arm 3)   ALLOW, ~1.0 us
    S_A_long       = P(Q_P=1 | Arm 4)   ALLOW, ~2.0 us
    L_expired      = P(Q_P=1 | Arm 5)   expired-auth leakage (PRIMARY)
    L_replayed     = P(Q_P=1 | Arm 6)   replayed-auth leakage (PRIMARY)
    S_reverified   = P(Q_P=1 | Arm 7)   reverified ALLOW fidelity
    SPAM_baseline  = P(Q_P=1 | Arm 8)   idle readout error
    Delta_B        = S_A_0 - L_expired  boundary discrimination (Arm 1 vs Arm 5)
    L_expired_corrected  = L_expired  - SPAM_baseline
    L_replayed_corrected = L_replayed - SPAM_baseline

Decision rule (preregistered — authoritative, Fields 20-22):
    PASS : L_expired_corrected <= 0.02 AND L_replayed_corrected <= 0.02
           AND S_reverified >= 0.90 AND Delta_B >= 0.70,
           with in-situ SPAM_baseline <= 0.02 on BOTH qubits.
    FAIL : any DENY arm (5 expired, 6 replayed) leaks corrected > 0.02 with
           in-situ SPAM clean; OR S_reverified < 0.90; OR Delta_B < 0.70.
    KILL : in-situ SPAM_baseline > 0.02 on either qubit; OR SPAM drift > 0.005
           between the SPAM and principal jobs => INDETERMINATE.

The delay-decay arms (2, 3, 4) are DESCRIPTIVE (H2a) and do not gate the verdict.
This is a metrological characterization of decoherence-driven boundary erosion,
NOT new physics and NOT a cryptographic claim.
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
PASS_S_REVERIFIED = 0.90
PASS_DELTA_B = 0.70
SPAM_CEILING = 0.02
DRIFT_CEILING = 0.005

ARM_DELAY_US = {
    "arm1_allow_immediate": 0.0,
    "arm2_allow_short_delay": 0.5,
    "arm3_allow_medium_delay": 1.0,
    "arm4_allow_long_delay": 2.0,
}


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

    S_A_0 = p("arm1_allow_immediate")
    S_A_short = p("arm2_allow_short_delay")
    S_A_medium = p("arm3_allow_medium_delay")
    S_A_long = p("arm4_allow_long_delay")
    L_expired = p("arm5_expired_auth_deny")
    L_replayed = p("arm6_replayed_after_expiry")
    S_reverified = p("arm7_reverified_after_expiry")
    SPAM_baseline = p("arm8_idle_spam")

    Delta_B = S_A_0 - L_expired
    L_expired_corrected = L_expired - SPAM_baseline
    L_replayed_corrected = L_replayed - SPAM_baseline

    # Upper 95% Wilson bounds on corrected leakage (one-sided ceiling diagnostics).
    le_p, le_lo, le_hi = ci95["arm5_expired_auth_deny"]
    lr_p, lr_lo, lr_hi = ci95["arm6_replayed_after_expiry"]
    sb_p, sb_lo, sb_hi = ci95["arm8_idle_spam"]
    L_expired_corrected_upper95 = le_hi - sb_lo
    L_replayed_corrected_upper95 = lr_hi - sb_lo
    # Lower 95% Wilson bound on S_reverified vs 0.90 floor.
    sr_p, sr_lo, sr_hi = ci95["arm7_reverified_after_expiry"]

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
                     "Qubit/backend disqualified; boundary claim indeterminate.")
    elif not drift_ok:
        decision = "KILL"
        status = "INDETERMINATE"
        rationale = (f"SPAM baseline drift {drift:.4f} > {DRIFT_CEILING} between the SPAM "
                     f"and principal jobs (calibration drift). INDETERMINATE.")
    else:
        cond_le = L_expired_corrected <= PASS_LD_CORR
        cond_lr = L_replayed_corrected <= PASS_LD_CORR
        cond_sr = S_reverified >= PASS_S_REVERIFIED
        cond_db = Delta_B >= PASS_DELTA_B
        if cond_le and cond_lr and cond_sr and cond_db:
            decision = "PASS"
            status = "PASS"
            rationale = (
                f"L_expired_corrected={L_expired_corrected:.4f} <= {PASS_LD_CORR} AND "
                f"L_replayed_corrected={L_replayed_corrected:.4f} <= {PASS_LD_CORR} AND "
                f"S_reverified={S_reverified:.4f} >= {PASS_S_REVERIFIED} AND "
                f"Delta_B={Delta_B:.4f} >= {PASS_DELTA_B}; in-situ SPAM within ceiling. "
                f"Expired and replayed authorizations do not execute the payload; fresh "
                f"reverification restores ALLOW.")
        else:
            decision = "FAIL"
            status = "FAIL"
            reasons = []
            if not cond_le:
                reasons.append(f"L_expired_corrected={L_expired_corrected:.4f} > {PASS_LD_CORR}")
            if not cond_lr:
                reasons.append(f"L_replayed_corrected={L_replayed_corrected:.4f} > {PASS_LD_CORR}")
            if not cond_sr:
                reasons.append(f"S_reverified={S_reverified:.4f} < {PASS_S_REVERIFIED}")
            if not cond_db:
                reasons.append(f"Delta_B={Delta_B:.4f} < {PASS_DELTA_B}")
            rationale = ("Boundary failed with in-situ SPAM within ceiling: "
                         + "; ".join(reasons))

    # H2b: replay vs expiry distinguishability (99% Wilson overlap).
    le99 = ci99["arm5_expired_auth_deny"]
    lr99 = ci99["arm6_replayed_after_expiry"]
    replay_vs_expiry_overlap99 = not (lr99[1] > le99[2] or le99[1] > lr99[2])
    # H2c: reverification vs immediate ALLOW concordance (95% Wilson overlap).
    a1_95 = ci95["arm1_allow_immediate"]
    a7_95 = ci95["arm7_reverified_after_expiry"]
    reverify_vs_allow_overlap95 = not (a7_95[1] > a1_95[2] or a1_95[1] > a7_95[2])

    metrics = {
        "S_A_0": {"value": S_A_0, "ci95": ci95["arm1_allow_immediate"],
                  "definition": "P(Q_P=1 | Arm 1 ALLOW immediate, 0 us)"},
        "S_A_short": {"value": S_A_short, "ci95": ci95["arm2_allow_short_delay"],
                      "definition": "P(Q_P=1 | Arm 2 ALLOW ~0.5 us)"},
        "S_A_medium": {"value": S_A_medium, "ci95": ci95["arm3_allow_medium_delay"],
                       "definition": "P(Q_P=1 | Arm 3 ALLOW ~1.0 us)"},
        "S_A_long": {"value": S_A_long, "ci95": ci95["arm4_allow_long_delay"],
                     "definition": "P(Q_P=1 | Arm 4 ALLOW ~2.0 us)"},
        "L_expired": {"value": L_expired, "ci95": ci95["arm5_expired_auth_deny"],
                      "ci99": ci99["arm5_expired_auth_deny"],
                      "definition": "P(Q_P=1 | Arm 5 expired-auth) PRIMARY"},
        "L_replayed": {"value": L_replayed, "ci95": ci95["arm6_replayed_after_expiry"],
                       "ci99": ci99["arm6_replayed_after_expiry"],
                       "definition": "P(Q_P=1 | Arm 6 replayed-auth) PRIMARY"},
        "S_reverified": {"value": S_reverified, "ci95": ci95["arm7_reverified_after_expiry"],
                         "ci95_lower": sr_lo,
                         "definition": "P(Q_P=1 | Arm 7 reverified ALLOW)"},
        "SPAM_baseline_arm8": {"value": SPAM_baseline, "ci95": ci95["arm8_idle_spam"],
                               "definition": "P(Q_P=1 | Arm 8 idle)"},
        "Delta_B": {"value": Delta_B, "definition": "S_A_0 - L_expired"},
        "L_expired_corrected": {"value": L_expired_corrected,
                                "upper95": L_expired_corrected_upper95,
                                "definition": "L_expired - SPAM_baseline"},
        "L_replayed_corrected": {"value": L_replayed_corrected,
                                 "upper95": L_replayed_corrected_upper95,
                                 "definition": "L_replayed - SPAM_baseline"},
    }

    delay_decay = [
        {"arm": name, "delay_us": ARM_DELAY_US[name], "S_A": p(name), "ci95": ci95[name]}
        for name in ["arm1_allow_immediate", "arm2_allow_short_delay",
                     "arm3_allow_medium_delay", "arm4_allow_long_delay"]
    ]

    secondary = {
        "H2a_delay_decay_monotone": {
            "S_A_by_delay_us": {str(d["delay_us"]): d["S_A"] for d in delay_decay},
            "monotone_non_increasing": bool(
                S_A_0 >= S_A_short >= S_A_medium >= S_A_long),
            "note": "Descriptive decay curve (T1/T2 of the payload during the delay). "
                    "No pass/fail weight.",
        },
        "H2b_replay_indistinguishable_from_expiry": {
            "L_expired": L_expired, "L_replayed": L_replayed,
            "overlap_99CI": bool(replay_vs_expiry_overlap99),
            "note": "A replayed stale bit is no better than an expired one.",
        },
        "H2c_reverification_concordance": {
            "S_A_0": S_A_0, "S_reverified": S_reverified,
            "overlap_95CI": bool(reverify_vs_allow_overlap95),
            "note": "Reverification restores ALLOW within the immediate ALLOW 95% CI.",
        },
    }

    proofrecord = {
        "experiment_id": "ARK-442",
        "title": "Authorization Boundary Degradation Under Verification-to-Execution Delay",
        "backend": raw["backend"],
        "instance": raw["instance"],
        "qubits": {"Q_A": raw["initial_layout"][0], "Q_P": raw["initial_layout"][1]},
        "shots_per_arm": raw["shots_per_arm"],
        "arm_order": raw["arm_order"],
        "arm_delay_ns": raw.get("arm_delay_ns"),
        "job_ids": {"spam_job": raw.get("spam_job_id"),
                    "principal_job": raw["principal_job_id"]},
        "raw_results_hash": sha256_file(raw_path),
        "spam_results_hash": sha256_file(spam_path) if spam is not None else None,
        "metrics": metrics,
        "delay_decay_curve": delay_decay,
        "secondary_hypotheses": secondary,
        "insitu_spam_job": {"Q_A": spam_qa, "Q_P": spam_qp, "gate_passed": spam_gate_passed,
                            "drift_vs_arm8": drift, "drift_ok": drift_ok},
        "decision_outcome": decision,
        "status": status,
        "rationale": rationale,
        "raw_vs_mitigated": "Primary endpoint = RAW counts, no readout mitigation applied.",
        "preregistered_pass": {"L_D_corrected_max": PASS_LD_CORR,
                               "S_reverified_min": PASS_S_REVERIFIED,
                               "Delta_B_min": PASS_DELTA_B,
                               "spam_ceiling": SPAM_CEILING,
                               "drift_ceiling": DRIFT_CEILING},
        "interpretation": ("Metrological characterization of decoherence-driven erosion "
                           "of the verify-then-execute authorization boundary under "
                           "verification-to-execution delay. NOT new physics, NOT a "
                           "cryptographic claim. Findings apply only to this boundary "
                           "implementation on this qubit pair on this backend at this "
                           "calibration."),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    pr_path = os.path.join(HERE, "proofrecord.json")
    with open(pr_path, "w") as f:
        json.dump(proofrecord, f, indent=2)
    print(f"[ANALYSIS] wrote {pr_path}")

    _make_plots(raw, ci95, delay_decay, S_A_0, L_expired, L_replayed,
                S_reverified, SPAM_baseline, L_expired_corrected, L_replayed_corrected)

    print(f"[ANALYSIS] S_A_0={S_A_0:.4f} S_A_short={S_A_short:.4f} "
          f"S_A_medium={S_A_medium:.4f} S_A_long={S_A_long:.4f}")
    print(f"[ANALYSIS] L_expired={L_expired:.4f} L_replayed={L_replayed:.4f} "
          f"S_reverified={S_reverified:.4f} SPAM(arm8)={SPAM_baseline:.4f}")
    print(f"[ANALYSIS] Delta_B={Delta_B:.4f} L_expired_corr={L_expired_corrected:.4f} "
          f"L_replayed_corr={L_replayed_corrected:.4f}")
    print(f"[ANALYSIS] DECISION = {decision} ({status})")
    print(f"[ANALYSIS] {rationale}")
    return proofrecord


def _make_plots(raw, ci95, delay_decay, S_A_0, L_expired, L_replayed,
                S_reverified, SPAM_baseline, L_expired_corrected, L_replayed_corrected):
    os.makedirs(os.path.join(HERE, "plots"), exist_ok=True)

    # Plot 1: all arms with 95% Wilson error bars
    names = raw["arm_order"]
    vals = [ci95[n][0] for n in names]
    lo = [ci95[n][0] - ci95[n][1] for n in names]
    hi = [ci95[n][2] - ci95[n][0] for n in names]
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(names))
    ax.bar(x, vals, yerr=[lo, hi], capsize=4, color="#3b6ea5")
    ax.set_xticks(list(x))
    ax.set_xticklabels([n.replace("_", "\n") for n in names], fontsize=7.5)
    ax.set_ylabel("P(Q_P = 1)")
    ax.set_title("ARK-442 (ibm_marrakesh) — Payload activation by arm (95% Wilson CI)")
    ax.axhline(0.02, color="red", ls="--", lw=1, label="corrected-leakage ceiling (0.02)")
    ax.axhline(0.90, color="green", ls=":", lw=1, label="S_reverified floor (0.90)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "plots", "arm_results.png"), dpi=150)
    plt.close(fig)

    # Plot 2: S_A(delay) decay curve (H2a, descriptive)
    ds = [d["delay_us"] for d in delay_decay]
    sa = [d["S_A"] for d in delay_decay]
    err_lo = [d["S_A"] - d["ci95"][1] for d in delay_decay]
    err_hi = [d["ci95"][2] - d["S_A"] for d in delay_decay]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.errorbar(ds, sa, yerr=[err_lo, err_hi], fmt="o-", capsize=4, color="#2ca02c",
                lw=2, label="S_A(delay) ALLOW survival")
    ax.set_xlabel("Verification-to-execution delay (µs)")
    ax.set_ylabel("S_A = P(Q_P = 1)")
    ax.set_title("ARK-442 (ibm_marrakesh) — ALLOW survival vs delay (H2a, descriptive)\n"
                 "Decoherence-driven decay of the authorization boundary")
    ax.set_ylim(0, 1.02)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "plots", "delay_decay.png"), dpi=150)
    plt.close(fig)
    print("[ANALYSIS] wrote plots/arm_results.png, plots/delay_decay.png")


if __name__ == "__main__":
    main()
