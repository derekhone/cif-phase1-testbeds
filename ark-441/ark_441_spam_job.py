"""
ARK-441 — In-situ SPAM estimation job (RUNS FIRST)
Remnant Fieldworks Inc. — Derek Hone

Directly characterizes state-preparation-and-measurement (SPAM) readout error
on the preregistered physical qubits Q5 and Q6 of ibm_kingston, BEFORE the
principal 8-arm job is submitted.

Four circuits, 2048 shots each:
    Q5 |0>  -> measure   (p01_q5 = P(read 1 | prepared 0))
    Q5 |1>  -> measure   (p10_q5 = P(read 0 | prepared 1))
    Q6 |0>  -> measure   (p01_q6)
    Q6 |1>  -> measure   (p10_q6)

Kill gate (preregistered): SPAM_baseline := p01 (false-1 rate when prepared |0>)
must be <= 0.02 on BOTH Q5 and Q6. This directly addresses the VBE-1 failure,
where an idle baseline of ~13.5% was indistinguishable from DENY-leakage.

Output: spam_results.json  (raw counts + derived per-qubit SPAM metrics)

This script must run and complete, and its results must be committed, BEFORE
ark_441_submit_ibm.py submits the principal job.
"""

import json
import os
import sys
from datetime import datetime, timezone

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

HERE = os.path.dirname(os.path.abspath(__file__))
SECRETS = "/home/ubuntu/.config/abacusai_auth_secrets.json"

BACKEND_NAME = "ibm_kingston"
CHANNEL = "ibm_quantum_platform"
INSTANCE = "open-instance"
SHOTS = 2048
PHYSICAL_QUBITS = {"Q5": 5, "Q6": 6}
SPAM_CEILING = 0.02


def load_token():
    with open(SECRETS) as f:
        d = json.load(f)
    return d["ibm quantum"]["secrets"]["api_token"]["value"]


def spam_circuit(prep_one: bool):
    """One-qubit direct readout characterization circuit."""
    q = QuantumRegister(1, "q")
    c = ClassicalRegister(1, "c")
    qc = QuantumCircuit(q, c)
    if prep_one:
        qc.x(q[0])
    qc.measure(q[0], c[0])
    return qc


def main():
    token = load_token()
    service = QiskitRuntimeService(channel=CHANNEL, token=token, instance=INSTANCE)
    backend = service.backend(BACKEND_NAME)

    # Build 4 circuits: (qubit label, prep) pinned to its physical qubit
    specs = [
        ("Q5", 5, "0", False),
        ("Q5", 5, "1", True),
        ("Q6", 6, "0", False),
        ("Q6", 6, "1", True),
    ]
    circuits = []
    meta = []
    for label, phys, prep_label, prep_one in specs:
        qc = spam_circuit(prep_one)
        tqc = transpile(qc, backend=backend, optimization_level=1,
                        initial_layout=[phys])
        circuits.append(tqc)
        meta.append({"qubit": label, "physical": phys, "prepared": prep_label})

    sampler = SamplerV2(mode=backend)
    submitted = datetime.now(timezone.utc).isoformat()
    print(f"[SPAM] submitting 4 circuits x {SHOTS} shots to {BACKEND_NAME} ...")
    job = sampler.run(circuits, shots=SHOTS)
    job_id = job.job_id()
    print(f"[SPAM] job_id = {job_id}")
    result = job.result()
    completed = datetime.now(timezone.utc).isoformat()

    per_circuit = []
    for i, m in enumerate(meta):
        counts = result[i].data.c.get_counts()
        total = sum(counts.values())
        p1 = counts.get("1", 0) / total
        p0 = counts.get("0", 0) / total
        rec = dict(m)
        rec.update({"counts": counts, "total": total,
                    "P_read_1": p1, "P_read_0": p0})
        per_circuit.append(rec)
        print(f"[SPAM] {m['qubit']} prep|{m['prepared']}>: "
              f"P(1)={p1:.4f} P(0)={p0:.4f} counts={counts}")

    # Per-qubit SPAM metrics
    qubit_metrics = {}
    for label in ("Q5", "Q6"):
        p01 = next(r["P_read_1"] for r in per_circuit
                   if r["qubit"] == label and r["prepared"] == "0")
        p10 = next(r["P_read_0"] for r in per_circuit
                   if r["qubit"] == label and r["prepared"] == "1")
        qubit_metrics[label] = {
            "p01_false_one_when_zero": p01,   # SPAM_baseline for kill gate
            "p10_false_zero_when_one": p10,
            "spam_baseline": p01,
            "passes_ceiling": bool(p01 <= SPAM_CEILING),
        }

    spam_ok = all(v["passes_ceiling"] for v in qubit_metrics.values())

    out = {
        "experiment_id": "ARK-441",
        "job_type": "in_situ_spam",
        "backend": BACKEND_NAME,
        "instance": INSTANCE,
        "physical_qubits": PHYSICAL_QUBITS,
        "shots_per_circuit": SHOTS,
        "spam_ceiling": SPAM_CEILING,
        "spam_job_id": job_id,
        "submitted_utc": submitted,
        "completed_utc": completed,
        "per_circuit": per_circuit,
        "qubit_metrics": qubit_metrics,
        "spam_gate_passed": bool(spam_ok),
        "kill_condition": "SPAM_baseline (p01) > 0.02 on either qubit => INDETERMINATE",
    }
    out_path = os.path.join(HERE, "spam_results.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[SPAM] wrote {out_path}")
    print(f"[SPAM] Q5 baseline={qubit_metrics['Q5']['spam_baseline']:.4f} "
          f"Q6 baseline={qubit_metrics['Q6']['spam_baseline']:.4f} "
          f"gate_passed={spam_ok}")

    if not spam_ok:
        print("[SPAM] KILL: SPAM baseline exceeds 0.02 on at least one qubit. "
              "Principal job MUST NOT be submitted. Result is INDETERMINATE.")
        sys.exit(2)
    print("[SPAM] PASS: baselines within ceiling. Principal job may proceed.")


if __name__ == "__main__":
    main()
