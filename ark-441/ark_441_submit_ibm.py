"""
ARK-441 — Principal 8-arm job submission
Remnant Fieldworks Inc. — Derek Hone

ORDERING CONSTRAINT (enforced in code):
  1. spam_results.json MUST exist and its SPAM gate MUST have passed
     (SPAM_baseline <= 0.02 on BOTH Q5 and Q6). Otherwise this script
     ABORTS without submitting anything.
  2. On pass, transpiles the 8 arms (optimization_level=1, NO dynamical
     decoupling), pins them to physical qubits [5, 6], submits ONE job of
     8 circuits x 8192 shots via SamplerV2.
  3. Immediately records job_id + submission_timestamp to RUN_LOG.md.

Raw counts are the PRIMARY endpoint; no readout mitigation is applied here.
Results are retrieved and saved separately by the retrieval step.
"""

import json
import os
import sys
from datetime import datetime, timezone

from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

from ark_441_circuits import build_all_arms, INITIAL_LAYOUT, ARM_NAMES

HERE = os.path.dirname(os.path.abspath(__file__))
SECRETS = "/home/ubuntu/.config/abacusai_auth_secrets.json"

BACKEND_NAME = "ibm_kingston"
CHANNEL = "ibm_quantum_platform"
INSTANCE = "open-instance"
SHOTS = 8192
OPT_LEVEL = 1
SPAM_CEILING = 0.02


def load_token():
    with open(SECRETS) as f:
        d = json.load(f)
    return d["ibm quantum"]["secrets"]["api_token"]["value"]


def check_spam_gate():
    spam_path = os.path.join(HERE, "spam_results.json")
    if not os.path.exists(spam_path):
        print("[SUBMIT] ABORT: spam_results.json not found. Run ark_441_spam_job.py first.")
        sys.exit(2)
    with open(spam_path) as f:
        spam = json.load(f)
    metrics = spam.get("qubit_metrics", {})
    print("[SUBMIT] SPAM gate check:")
    ok = True
    for label, v in metrics.items():
        b = v["spam_baseline"]
        passed = b <= SPAM_CEILING
        ok = ok and passed
        print(f"   {label}: SPAM_baseline={b:.4f} <= {SPAM_CEILING} ? {passed}")
    if not ok:
        print("[SUBMIT] ABORT: SPAM baseline exceeds ceiling. INDETERMINATE. "
              "Principal job will NOT be submitted.")
        sys.exit(2)
    print("[SUBMIT] SPAM gate PASSED. Proceeding to principal job submission.")
    return spam


def record_run_log(job_id, submitted, spam, tqc_depths):
    log_path = os.path.join(HERE, "RUN_LOG.md")
    lines = []
    lines.append("# ARK-441 — RUN LOG\n")
    lines.append("Remnant Fieldworks Inc. — Derek Hone\n")
    lines.append(f"\n## Principal 8-arm job\n")
    lines.append(f"- **Backend:** {BACKEND_NAME}\n")
    lines.append(f"- **Instance:** {INSTANCE}\n")
    lines.append(f"- **Physical qubits (Q_A, Q_P):** {INITIAL_LAYOUT}\n")
    lines.append(f"- **Shots per arm:** {SHOTS}\n")
    lines.append(f"- **Arms:** {len(ARM_NAMES)} ({', '.join(ARM_NAMES)})\n")
    lines.append(f"- **Optimization level:** {OPT_LEVEL} (no dynamical decoupling)\n")
    lines.append(f"- **JOB ID:** `{job_id}`\n")
    lines.append(f"- **Submission timestamp (UTC):** {submitted}\n")
    lines.append(f"- **SPAM job id:** `{spam.get('spam_job_id')}`\n")
    lines.append(f"- **SPAM baselines:** "
                 f"Q5={spam['qubit_metrics']['Q5']['spam_baseline']:.4f}, "
                 f"Q6={spam['qubit_metrics']['Q6']['spam_baseline']:.4f}\n")
    lines.append(f"- **Transpiled depths:** {tqc_depths}\n")
    with open(log_path, "w") as f:
        f.writelines(lines)
    print(f"[SUBMIT] wrote {log_path}")


def main():
    spam = check_spam_gate()

    token = load_token()
    service = QiskitRuntimeService(channel=CHANNEL, token=token, instance=INSTANCE)
    backend = service.backend(BACKEND_NAME)

    arms = build_all_arms()
    ordered = [arms[name] for name in ARM_NAMES]
    tqcs = transpile(ordered, backend=backend, optimization_level=OPT_LEVEL,
                     initial_layout=INITIAL_LAYOUT)
    depths = {name: tqc.depth() for name, tqc in zip(ARM_NAMES, tqcs)}
    print(f"[SUBMIT] transpiled depths: {depths}")

    sampler = SamplerV2(mode=backend)
    submitted = datetime.now(timezone.utc).isoformat()
    print(f"[SUBMIT] submitting {len(tqcs)} arms x {SHOTS} shots to {BACKEND_NAME} ...")
    job = sampler.run(tqcs, shots=SHOTS)
    job_id = job.job_id()
    print(f"[SUBMIT] PRINCIPAL JOB ID = {job_id}")

    # Record job id IMMEDIATELY, before any result retrieval.
    record_run_log(job_id, submitted, spam, depths)

    # Persist a small pointer for the retrieval step.
    with open(os.path.join(HERE, "principal_job_id.txt"), "w") as f:
        f.write(job_id + "\n")

    meta = {
        "experiment_id": "ARK-441",
        "principal_job_id": job_id,
        "backend": BACKEND_NAME,
        "instance": INSTANCE,
        "initial_layout": INITIAL_LAYOUT,
        "shots_per_arm": SHOTS,
        "arm_order": ARM_NAMES,
        "optimization_level": OPT_LEVEL,
        "dynamical_decoupling": False,
        "submitted_utc": submitted,
        "spam_job_id": spam.get("spam_job_id"),
    }
    with open(os.path.join(HERE, "principal_job_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print("[SUBMIT] job submitted and recorded. Use ark_441_retrieve.py to fetch results.")


if __name__ == "__main__":
    main()
