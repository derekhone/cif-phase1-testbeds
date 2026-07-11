"""
H1: Hardware fixed-point test (IBM Quantum)
Preregistered: prereg_h1_ibm_fixed_point.md
Part A prints the analytic prediction (FREE - calibration data only).
It then asks for confirmation before Part B (the QPU job, ~2-3 min).
"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

# ---------------- Config (matches preregistration) ----------------
GAIN_F   = 0.5      # re-preparation fraction f
N_CYCLES = 8        # cycles 0..8 -> 9 circuits
DELAY_US = 40.0     # idle delay per cycle, microseconds
SHOTS    = 4096

# ---------------- Connect ----------------
service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False)
print(f"Backend: {backend.name}")

# Pick the qubit with the best T2
props = backend.properties()
t2s = []
for q in range(backend.num_qubits):
    try:
        t2 = props.qubit_property(q, "T2")[0]  # seconds
        if t2 and t2 > 0:
            t2s.append((t2, q))
    except Exception:
        pass
t2, QUBIT = max(t2s)
t2_us = t2 * 1e6
print(f"Qubit {QUBIT}: T2 = {t2_us:.1f} us (from calibration, no QPU cost)")

# ---------------- Part A: analytic prediction ----------------
gamma = DELAY_US / t2_us
decay = np.exp(-gamma)
C_star = GAIN_F / (1.0 - (1.0 - GAIN_F) * decay)
D_star = (1.0 - C_star) / 2.0
print("\n--- PART A (prediction, on record) ---")
print(f"gamma per cycle = {gamma:.4f}   per-cycle decay = {decay:.4f}")
print(f"PREDICTED  C* = {C_star:.4f}   D* = {D_star:.4f}")
print(f"PASS window (preregistered +/-10%): D* in [{0.9*D_star:.4f}, {1.1*D_star:.4f}]")

if input("\nRun Part B on hardware (~2-3 min QPU)? [y/N]: ").strip().lower() != "y":
    print("Stopped before hardware. Prediction recorded above.")
    raise SystemExit

# ---------------- Part B: hardware circuits ----------------
def coherence_from_counts(counts):
    tot = sum(counts.values())
    p0 = counts.get("0", 0) / tot
    return abs(2 * p0 - 1)  # |<X>| when measured in X basis

circuits, meta = [], []
for n in range(N_CYCLES + 1):
    fams = [(n, (1 - GAIN_F) ** n)]
    for k in range(1, n + 1):
        fams.append((n - k, GAIN_F * (1 - GAIN_F) ** (n - k)))
    for m, w in fams:
        qc = QuantumCircuit(1, 1)
        qc.h(0)                                   # prepare |+>
        if m > 0:
            qc.delay(int(DELAY_US * 1000) * m, 0, unit="ns")
        qc.h(0)                                   # X-basis measurement
        qc.measure(0, 0)
        circuits.append(qc)
        meta.append((n, w))

tc = transpile(circuits, backend, initial_layout=[QUBIT], scheduling_method="asap")
sampler = SamplerV2(mode=backend)
job = sampler.run(tc, shots=SHOTS)
print(f"Job submitted: {job.job_id()}  (waiting... this can take a while in queue)")
res = job.result()

# ---------------- Analysis ----------------
C_meas = np.zeros(N_CYCLES + 1)
for (n, w), r in zip(meta, res):
    data = r.data
    counts = data.c.get_counts() if hasattr(data, "c") else data.meas.get_counts()
    C_meas[n] += w * coherence_from_counts(counts)

print("\n--- PART B (hardware) ---")
for n in range(N_CYCLES + 1):
    print(f"cycle {n}: C = {C_meas[n]:.4f}   D = {(1-C_meas[n])/2:.4f}")
C_ss = C_meas[-3:].mean()
D_ss = (1 - C_ss) / 2
rel = abs(D_ss - D_star) / D_star
print(f"\nMEASURED steady-state D* = {D_ss:.4f}   PREDICTED = {D_star:.4f}")
print(f"Relative deviation = {100*rel:.1f}%  ->  {'PASS' if rel <= 0.10 else 'FAIL'} (preregistered +/-10%)")