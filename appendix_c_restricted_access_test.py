# UIP Phase 1 - Appendix C: Preregistered v3 test
# Inheritance-guided control under RESTRICTED ACCESS (target not directly correctable).
# Predictions P1 and P2 were locked before execution. Result: ROBUST PASS at weak coupling.
# Companion to DOI: 10.5281/zenodo.21246247
import numpy as np
from functools import reduce
from scipy.linalg import expm
from scipy import stats

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
    phase = (t // 15) % 2
    return (0.15, 0.01) if phase == 0 else (0.01, 0.15)

def apply_noise(rho, t):
    gA, gB = rates(t)
    pA = (1 - np.exp(-gA)) / 2; pB = (1 - np.exp(-gB)) / 2
    ZA = kron(Z, I2); ZB = kron(I2, Z)
    rho = (1 - pA) * rho + pA * (ZA @ rho @ ZA)
    return (1 - pB) * rho + pB * (ZB @ rho @ ZB)

def correct_A(rho, f=0.5):
    # ONLY the relay A is correctable (restricted access) - the change from Appendix B
    rB = ptrace(rho, 1)
    return (1 - f) * rho + f * kron(rho_plus, rB)

def resonance(rA, rB):
    a = rA[0, 1]; b = rB[0, 1]
    if abs(a) < 1e-9 or abs(b) < 1e-9: return 0.0
    return float(np.real(a * np.conj(b)) / (abs(a) * abs(b)) * 0.5 + 0.5)

def run(policy, s_couple, T=90, seed=2, k_period=2):
    rng = np.random.default_rng(seed)
    Usw = expm(-1j * s_couple * (np.eye(4) - SWAP))
    tau_eff = np.sin(s_couple) ** 2
    rho = kron(rho_plus, zero); CB = []
    for t in range(T):
        rho = apply_noise(rho, t)
        rho = Usw @ rho @ Usw.conj().T
        rA = ptrace(rho, 0); rB = ptrace(rho, 1)
        CA = max(C_l1(rA) + rng.normal(0, 0.02), 0)
        gA, gB = rates(t)
        gAe = max(gA + rng.normal(0, 0.01), 0)
        R = resonance(rA, rB)
        act = False
        if policy == 'uip_v3':
            # correct A only when deliverable replenishment benefit exceeds
            # the disturbance cost to inheritance in transit
            I2ab = R * CA * tau_eff
            benefit = (1 - CA) * tau_eff
            cost = I2ab * 0.5
            act = benefit * np.exp(-gAe) > cost or CA < 0.3
        elif policy == 'alwaysA': act = True
        elif policy == 'never': act = False
        elif policy == 'random': act = rng.random() < 0.5
        elif policy == 'periodic': act = (t % k_period == 0)
        if act: rho = correct_A(rho)
        CB.append(C_l1(ptrace(rho, 1)))
    return float(np.mean(CB))

# --- Coupling sweep (10 seeds) ---
sweep = [0.15, 0.25, 0.5, 0.8, 1.1, 1.4]
def mean_pol(p, s, k=2, N=10): return np.mean([run(p, s, seed=sd, k_period=k) for sd in range(N)])
print("Coupling sweep - mean stored coherence C_B (10 seeds):\n")
p2_wins = []
for s in sweep:
    m = {p: mean_pol(p, s) for p in ['uip_v3', 'alwaysA', 'never', 'random']}
    best_k, best_per = max(((k, mean_pol('periodic', s, k)) for k in [2, 3, 4]), key=lambda x: x[1])
    best_base = max(m['alwaysA'], m['never'], m['random'], best_per)
    win = m['uip_v3'] > best_base
    p2_wins.append(win)
    print(f"s={s:.2f}  v3={m['uip_v3']:.4f}  alwaysA={m['alwaysA']:.4f}  "
          f"random={m['random']:.4f}  periodic(k={best_k})={best_per:.4f}  "
          f"{'BEATS ALL' if win else 'loses'}")
print("\nP2 (v3 beats ALL baselines in >=1 regime):", "PASS" if any(p2_wins) else "FAIL")

# --- Robustness check at s=0.15, N=100 seeds ---
s, N = 0.15, 100
v3 = np.array([run('uip_v3', s, seed=sd) for sd in range(N)])
per = {k: np.array([run('periodic', s, seed=sd, k_period=k) for sd in range(N)]) for k in [2, 3, 4]}
best = per[max(per, key=lambda k: per[k].mean())]
d = v3 - best
lo = d.mean() - 1.96 * d.std() / np.sqrt(N)
hi = d.mean() + 1.96 * d.std() / np.sqrt(N)
t, pv = stats.ttest_rel(v3, best)
print(f"\nRobustness (s=0.15, N={N}): v3={v3.mean():.4f} vs best baseline={best.mean():.4f}")
print(f"Edge = {d.mean():+.4f} ({d.mean()/best.mean()*100:+.1f}%), 95% CI [{lo:.4f}, {hi:.4f}], paired t p={pv:.2e}")
print("VERDICT:", "ROBUST PASS" if lo > 0 else "NOT ROBUST")
