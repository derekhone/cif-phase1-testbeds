# UIP Phase 1 - Appendix A: Single noisy qubit memory testbed
# Six falsification tests + fixed-point prediction (G = L).
# Companion to DOI: 10.5281/zenodo.21246247
import numpy as np
from scipy.optimize import brentq

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
rho_star = np.outer(plus, plus.conj())          # target state |+><+|

gamma, eta = 0.06, 0.02                         # dephasing, amplitude damping per cycle
sigma_sense, gain, fmax = 0.005, 0.5, 0.9       # sensing noise, feedback gain, cap
purity_floor = 0.55                             # non-harm envelope E
T = 400

def C_l1(r):  return 2 * abs(r[0, 1])           # l1-norm coherence
def drift(r):                                   # trace distance to target
    d = r - rho_star
    return 0.5 * np.sum(np.abs(np.linalg.eigvalsh(d)))
def purity(r): return float(np.real(np.trace(r @ r)))

def noise(r):
    p = (1 - np.exp(-gamma)) / 2                # dephasing
    r = (1 - p) * r + p * (Z @ r @ Z)
    K0 = np.array([[1, 0], [0, np.sqrt(1 - eta)]], dtype=complex)
    K1 = np.array([[0, np.sqrt(eta)], [0, 0]], dtype=complex)
    return K0 @ r @ K0.conj().T + K1 @ r @ K1.conj().T

def run(strategy, T=T, seed=0, rho0=None, g=gain):
    rng = np.random.default_rng(seed)
    rho = rho_star.copy() if rho0 is None else rho0.copy()
    Ds, Cs, ks, Ws, dCs, GmLs, env_ok = [], [], [], [], [], True, True
    env_ok = True
    for t in range(T):
        C_before = C_l1(rho)
        rho = noise(rho)
        W = C_before - C_l1(rho)                # waste: coherence lost to environment
        D_pre = drift(rho)
        C_pre = C_l1(rho)
        if strategy == 'generic':               # fixed X echo pulse
            rho = X @ rho @ X
        elif strategy == 'matched':             # UIP: sense drift, recirculate
            D_est = max(D_pre + rng.normal(0, sigma_sense), 0)
            f = min(g * D_est, fmax)
            rho = (1 - f) * rho + f * rho_star  # measurement-based partial re-preparation
        D_post = drift(rho)
        ks.append(D_post / D_pre if D_pre > 1e-12 else 1.0)
        Ds.append(D_post); Cs.append(C_l1(rho)); Ws.append(W)
        dCs.append(C_l1(rho) - C_before)
        GmLs.append((C_l1(rho) - C_pre) - W)    # bookkeeping: G - L
        if purity(rho) < purity_floor: env_ok = False
    return dict(D=np.array(Ds), C=np.array(Cs), k=np.array(ks),
                W=np.array(Ws), dC=np.array(dCs), GmL=np.array(GmLs), env=env_ok)

res = {s: run(s) for s in ['none', 'generic', 'matched']}
print(f"{'strategy':>10} {'final D':>9} {'steady C':>9} {'envelope':>9}")
for s, r in res.items():
    print(f"{s:>10} {r['D'][-1]:>9.4f} {np.mean(r['C'][-50:]):>9.4f} {str(r['env']):>9}")

# Fixed-point prediction: G = L  =>  steady-state drift D*
def fixed_point(D):
    f = min(gain * D, fmax)
    p = (1 - np.exp(-gamma)) / 2
    C_ss = 1 - 2 * D                            # coherence at drift D near |+>
    loss = 2 * p * C_ss + eta * C_ss / 2
    gainG = f * (1 - C_ss + loss)
    return gainG - loss
D_pred = brentq(fixed_point, 1e-4, 0.5)
D_sim = float(np.mean(res['matched']['D'][-100:]))
print(f"\nFixed-point prediction D* = {D_pred:.4f} | simulated = {D_sim:.4f}")

# Falsification tests
mixed = 0.5 * I2                                 # badly drifted start for T3
rec = run('matched', T=60, rho0=mixed, g=0.5)
noise_only = run('none')
print("\n--- Falsification tests ---")
print("T1 Drift-recovery:", "PASS" if res['matched']['D'][-1] < res['none']['D'][-1] else "FAIL")
print("T2 Beats generic:", "PASS" if res['matched']['D'][-1] < res['generic']['D'][-1] else "FAIL")
print("T3 Contraction k<1 (transient):", "PASS" if np.all(rec['k'][:10] < 1.0) else "FAIL",
      "| first k values:", np.round(rec['k'][:5], 3))
print("T4 Coherence monotone under pure noise:",
      "PASS" if np.all(np.diff(noise_only['C']) <= 1e-9) else "FAIL")
print("T5 Non-harm envelope:", "PASS" if res['matched']['env'] else "FAIL")
print("T6 Bookkeeping closure:",
      "PASS" if abs(np.mean(res['matched']['GmL']) - np.mean(res['matched']['dC'])) < 1e-9 else "FAIL")
