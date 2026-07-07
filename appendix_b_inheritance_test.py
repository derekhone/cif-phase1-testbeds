# UIP Phase 1 - Appendix B: Two-qubit inheritance-guided control test
# Preregistered NEGATIVE RESULT (v1 and v2 both failed). Reported in full.
# Companion to DOI: 10.5281/zenodo.21246247
import numpy as np
from functools import reduce
from scipy.linalg import expm

I2 = np.eye(2, dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
rho_plus = np.outer(plus, plus.conj())
zero = np.array([[1, 0], [0, 0]], dtype=complex)

def kron(*o): return reduce(np.kron, o)
def ptrace(rho, keep):
    r = rho.reshape(2, 2, 2, 2)
    return np.trace(r, axis1=1, axis2=3) if keep == 0 else np.trace(r, axis1=0, axis2=2)
def C_l1(r): return 2 * abs(r[0, 1])

SWAP = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex)

def rates(t):
    # time-varying environment: noise attack alternates between A and B every 15 cycles
    phase = (t // 15) % 2
    return (0.15, 0.01) if phase == 0 else (0.01, 0.15)

def apply_noise(rho, t):
    gA, gB = rates(t)
    pA = (1 - np.exp(-gA)) / 2
    pB = (1 - np.exp(-gB)) / 2
    ZA = kron(Z, I2); ZB = kron(I2, Z)
    rho = (1 - pA) * rho + pA * (ZA @ rho @ ZA)
    return (1 - pB) * rho + pB * (ZB @ rho @ ZB)

def correct(rho, which, f=0.5):
    # recirculation: partial re-preparation of the chosen qubit toward |+>
    rA = ptrace(rho, 0); rB = ptrace(rho, 1)
    repl = kron(rho_plus, rB) if which == 'A' else kron(rA, rho_plus)
    return (1 - f) * rho + f * repl

def resonance(rA, rB):
    a = rA[0, 1]; b = rB[0, 1]
    if abs(a) < 1e-9 or abs(b) < 1e-9: return 0.0
    return float(np.real(a * np.conj(b)) / (abs(a) * abs(b)) * 0.5 + 0.5)

def run(policy, s_couple, T=90, seed=2):
    rng = np.random.default_rng(seed)
    Usw = expm(-1j * s_couple * (np.eye(4) - SWAP))   # partial SWAP inheritance channel
    tau_eff = np.sin(s_couple) ** 2                    # effective transfer fraction
    rho = kron(rho_plus, zero)                         # A coherent source, B empty memory
    CB = []; alt = 0
    for t in range(T):
        rho = apply_noise(rho, t)
        rho = Usw @ rho @ Usw.conj().T
        rA = ptrace(rho, 0); rB = ptrace(rho, 1)
        # noisy sensing of coherences and rates
        CA = max(C_l1(rA) + rng.normal(0, 0.02), 0)
        CBe = max(C_l1(rB) + rng.normal(0, 0.02), 0)
        gA, gB = rates(t)
        gAe = max(gA + rng.normal(0, 0.01), 0)
        gBe = max(gB + rng.normal(0, 0.01), 0)
        R = resonance(rA, rB)
        if policy == 'uip_v2':                         # deliverable inheritance
            I2ab = R * CA * tau_eff
            risk_A = I2ab * (1 - np.exp(-gAe))
            risk_B = CBe * (1 - np.exp(-gBe))
            which = 'A' if risk_A > risk_B else 'B'
        elif policy == 'uip_v1':                       # inheritance potential (v1)
            I1 = R * CA
            which = 'A' if I1 * (1 - np.exp(-gAe)) > CBe * (1 - np.exp(-gBe)) else 'B'
        elif policy == 'alwaysB': which = 'B'
        elif policy == 'alwaysA': which = 'A'
        elif policy == 'alternate': which = 'A' if alt % 2 == 0 else 'B'; alt += 1
        else: which = 'A' if rng.random() < 0.5 else 'B'
        rho = correct(rho, which)
        CB.append(C_l1(ptrace(rho, 1)))
    return np.array(CB)

policies = ['uip_v2', 'uip_v1', 'alwaysB', 'alwaysA', 'alternate', 'random']
print("Coupling sweep - mean stored coherence C_B (10 seeds each):\n")
print(f"{'s':>5}" + "".join(f"{p:>11}" for p in policies) + f"{'v2 verdict':>12}")
wins = []
for s in [0.15, 0.25, 0.5, 0.8, 1.1, 1.4]:
    means = {p: np.mean([run(p, s, seed=sd) for sd in range(10)]) for p in policies}
    best_base = max(v for k, v in means.items() if k != 'uip_v2')
    verdict = "BEATS ALL" if means['uip_v2'] > best_base else (
        "ties" if means['uip_v2'] > best_base - 0.005 else "loses")
    wins.append(means['uip_v2'] > best_base)
    print(f"{s:>5.2f}" + "".join(f"{means[p]:>11.4f}" for p in policies) + f"{verdict:>12}")

print("\n--- Preregistered falsification tests ---")
print("P1 (weak coupling: v2 ~ always-B, fixing v1's error): see s=0.15, 0.25 rows")
print("P2 (exists coupling regime where v2 beats ALL baselines):",
      "PASS" if any(wins) else "FAIL")
print("\nResult as published: P2 FAIL. Inheritance-guided allocation loses to")
print("direct target protection whenever the target is directly correctable.")
print("Open v3 hypothesis (untested): restricted-access systems only.")
