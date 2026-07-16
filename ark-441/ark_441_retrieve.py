"""
ARK-441 — Principal job result retrieval
Remnant Fieldworks Inc. — Derek Hone

Retrieves raw counts for the principal 8-arm job and writes raw_results.json.
Job id is read from principal_job_meta.json (recorded at submission time), so
results are only ever read AFTER the job id has been committed.

Raw counts are the PRIMARY endpoint. No readout mitigation is applied.
"""

import json
import os
import sys
from datetime import datetime, timezone

from qiskit_ibm_runtime import QiskitRuntimeService

HERE = os.path.dirname(os.path.abspath(__file__))
SECRETS = "/home/ubuntu/.config/abacusai_auth_secrets.json"
CHANNEL = "ibm_quantum_platform"
INSTANCE = "open-instance"


def load_token():
    with open(SECRETS) as f:
        d = json.load(f)
    return d["ibm quantum"]["secrets"]["api_token"]["value"]


def main():
    meta_path = os.path.join(HERE, "principal_job_meta.json")
    if not os.path.exists(meta_path):
        print("[RETRIEVE] ABORT: principal_job_meta.json not found. Submit first.")
        sys.exit(2)
    with open(meta_path) as f:
        meta = json.load(f)
    job_id = meta["principal_job_id"]
    arm_order = meta["arm_order"]

    token = load_token()
    service = QiskitRuntimeService(channel=CHANNEL, token=token, instance=INSTANCE)
    job = service.job(job_id)
    status = str(job.status())
    print(f"[RETRIEVE] job {job_id} status = {status}")
    result = job.result()  # blocks until done

    arms = {}
    for i, name in enumerate(arm_order):
        counts = result[i].data.cp.get_counts()   # payload register 'cp'
        total = sum(counts.values())
        p1 = counts.get("1", 0) / total
        arms[name] = {"counts": counts, "total": total, "P_Q_P_1": p1}
        print(f"[RETRIEVE] {name}: P(Q_P=1)={p1:.4f} counts={counts}")

    out = {
        "experiment_id": "ARK-441",
        "principal_job_id": job_id,
        "backend": meta["backend"],
        "instance": meta["instance"],
        "initial_layout": meta["initial_layout"],
        "shots_per_arm": meta["shots_per_arm"],
        "arm_order": arm_order,
        "spam_job_id": meta.get("spam_job_id"),
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "final_status": status,
        "arms": arms,
        "primary_endpoint": "raw counts, no readout mitigation",
    }
    out_path = os.path.join(HERE, "raw_results.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[RETRIEVE] wrote {out_path}")


if __name__ == "__main__":
    main()
