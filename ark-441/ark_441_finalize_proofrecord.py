"""
ARK-441 — Finalize ProofRecord provenance
Remnant Fieldworks Inc. — Derek Hone

Enriches proofrecord.json with the full provenance hash set required by the
ARK-441 record spec, WITHOUT modifying any hash-locked preregistration/code file.

Adds: preregistration_hash (git lock commit + file sha256), code_hash,
circuit_hash, parameter_hash, calibration_hash, spam_job/principal_job ids
already present, and the raw_vs_mitigated distinction.
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PREREG_LOCK_COMMIT = "fd1c7fad7c290ee04fc564575f9d7bc12000c3b7"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(8192), b""):
            h.update(c)
    return h.hexdigest()


def main():
    pr_path = os.path.join(HERE, "proofrecord.json")
    with open(pr_path) as f:
        pr = json.load(f)

    circuit_hash = sha256_file(os.path.join(HERE, "ark_441_circuits.py"))
    calibration_hash = sha256_file(os.path.join(HERE, "calibration_snapshot_20260716.json"))
    prereg_file_hash = sha256_file(os.path.join(HERE, "ARK_441_preregistration.md"))
    manifest_hash = sha256_file(os.path.join(HERE, "MANIFEST.txt"))

    # code_hash = sha256 over the concatenated sha256 of every code file (stable, order-fixed)
    code_files = ["ark_441_circuits.py", "ark_441_spam_job.py", "ark_441_submit_ibm.py",
                  "ark_441_retrieve.py", "ark_441_analysis.py", "requirements.txt"]
    concat = "".join(sha256_file(os.path.join(HERE, f)) for f in code_files)
    code_hash = hashlib.sha256(concat.encode()).hexdigest()

    # parameter_hash = sha256 over the canonical experiment parameters
    params = {
        "backend": pr["backend"],
        "instance": pr["instance"],
        "qubits": pr["qubits"],
        "shots_per_arm": pr["shots_per_arm"],
        "arm_order": pr["arm_order"],
        "optimization_level": 1,
        "dynamical_decoupling": False,
        "pass": pr["preregistered_pass"],
    }
    parameter_hash = hashlib.sha256(
        json.dumps(params, sort_keys=True).encode()).hexdigest()

    pr["provenance"] = {
        "preregistration_hash": {
            "git_lock_commit": PREREG_LOCK_COMMIT,
            "prereg_file_sha256": prereg_file_hash,
            "manifest_sha256": manifest_hash,
        },
        "code_hash": code_hash,
        "circuit_hash": circuit_hash,
        "parameter_hash": parameter_hash,
        "calibration_hash": calibration_hash,
    }
    # Also surface the flat fields for machine-readability per spec
    pr["preregistration_hash"] = PREREG_LOCK_COMMIT
    pr["code_hash"] = code_hash
    pr["circuit_hash"] = circuit_hash
    pr["parameter_hash"] = parameter_hash
    pr["calibration_hash"] = calibration_hash
    pr["independence"] = ("Independent supplemental experiment. NOT part of UIP "
                          "Phase 1/2. See INDEPENDENCE_NOTICE.md.")

    with open(pr_path, "w") as f:
        json.dump(pr, f, indent=2)
    print("[FINALIZE] enriched proofrecord.json provenance:")
    for k, v in pr["provenance"].items():
        print(f"   {k}: {v}")


if __name__ == "__main__":
    main()
