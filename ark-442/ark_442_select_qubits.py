"""
ARK-442 — Preregistered qubit selection on ibm_marrakesh (Heron r2)
Remnant Fieldworks Inc. — Derek Hone

Selection rule (preregistered, Field 10 — identical to ARK-441/446):
  - Both qubits must have readout_error < 0.020 from today's calibration snapshot.
  - Must be directly connected in the coupling map.
  - Among qualifying connected pairs, select the minimum SUM of readout errors.

Outputs:
  - calibration_snapshot_marrakesh_20260716.json  (per-qubit readout errors + coupling map)
  - selected_qubits.json                           (the frozen pair, RE values, sum)
"""

import json
import os
from datetime import datetime, timezone

from qiskit_ibm_runtime import QiskitRuntimeService

HERE = os.path.dirname(os.path.abspath(__file__))
SECRETS = "/home/ubuntu/.config/abacusai_auth_secrets.json"

BACKEND_NAME = "ibm_marrakesh"
CHANNEL = "ibm_quantum_platform"
INSTANCE = "open-instance"
RE_CEILING = 0.020


def load_token():
    with open(SECRETS) as f:
        return json.load(f)["ibm quantum"]["secrets"]["api_token"]["value"]


def main():
    token = load_token()
    service = QiskitRuntimeService(channel=CHANNEL, token=token, instance=INSTANCE)
    backend = service.backend(BACKEND_NAME)
    props = backend.properties()
    n = backend.num_qubits

    # Per-qubit readout error from calibration
    readout_error = {}
    for q in range(n):
        try:
            readout_error[q] = float(props.readout_error(q))
        except Exception:
            readout_error[q] = None

    # Coupling map -> set of undirected connected pairs
    cmap = backend.coupling_map
    undirected = set()
    for edge in cmap:
        a, b = int(edge[0]), int(edge[1])
        undirected.add((min(a, b), max(a, b)))

    # Qualifying connected pairs: both RE < ceiling
    qualifying = []
    for (a, b) in sorted(undirected):
        ra, rb = readout_error.get(a), readout_error.get(b)
        if ra is None or rb is None:
            continue
        if ra < RE_CEILING and rb < RE_CEILING:
            qualifying.append({"pair": [a, b], "re_a": ra, "re_b": rb, "sum": ra + rb})

    qualifying.sort(key=lambda d: d["sum"])
    if not qualifying:
        raise SystemExit("[SELECT] No connected pair with both RE < 0.020. Cannot proceed.")

    best = qualifying[0]
    # Assign Q_A / Q_P: lower physical index -> Q_A (deterministic, arbitrary but fixed)
    pa, pb = best["pair"]
    q_a, q_p = (pa, pb)
    re_qa = readout_error[q_a]
    re_qp = readout_error[q_p]

    snapshot = {
        "experiment_id": "ARK-442",
        "backend": BACKEND_NAME,
        "instance": INSTANCE,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "num_qubits": n,
        "re_ceiling": RE_CEILING,
        "readout_error": {str(k): v for k, v in readout_error.items()},
        "connected_pairs_count": len(undirected),
        "backend_version": getattr(backend, "version", None),
        "processor_type": str(getattr(backend, "processor_type", None)),
    }
    snap_path = os.path.join(HERE, "calibration_snapshot_marrakesh_20260716.json")
    with open(snap_path, "w") as f:
        json.dump(snapshot, f, indent=2)

    selection = {
        "experiment_id": "ARK-442",
        "backend": BACKEND_NAME,
        "selection_rule": "RE < 0.020 on both, directly connected, min sum of readout errors",
        "Q_A": q_a,
        "Q_P": q_p,
        "readout_error_Q_A": re_qa,
        "readout_error_Q_P": re_qp,
        "sum_readout_error": re_qa + re_qp,
        "initial_layout": [q_a, q_p],
        "num_qualifying_pairs": len(qualifying),
        "top5_qualifying": qualifying[:5],
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
    }
    sel_path = os.path.join(HERE, "selected_qubits.json")
    with open(sel_path, "w") as f:
        json.dump(selection, f, indent=2)

    print(f"[SELECT] backend={BACKEND_NAME} qubits={n} qualifying_pairs={len(qualifying)}")
    print(f"[SELECT] SELECTED Q_A={q_a} (RE={re_qa:.4%}) Q_P={q_p} (RE={re_qp:.4%}) "
          f"sum={re_qa+re_qp:.4%}")
    print(f"[SELECT] top5 qualifying (by sum): "
          + "; ".join(f"{d['pair']}={d['sum']:.4%}" for d in qualifying[:5]))
    print(f"[SELECT] wrote {snap_path}")
    print(f"[SELECT] wrote {sel_path}")


if __name__ == "__main__":
    main()
