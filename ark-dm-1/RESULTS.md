# ARK-DM-1 — RESULTS

**Experiment:** ARK-DM-1 (preregistered open-data test)
**Run date (UTC):** 2026-07-14
**Data:** SPARC (Lelli, McGaugh & Schombert 2016) — Table 1 + Rotmod_LTG
**Status:** COMPLETE — single locked run, no post-hoc tuning

## Verdict: ❌ FAIL

## Headline numbers

| Model | Median fractional velocity error |
|---|---|
| Visible-matter-only baseline | 0.4145 |
| Ark term (global α* = 2.13) | **0.3826** |
| Pseudo-isothermal halo (per-galaxy, 2 params) | 0.0305 |

- Improvement vs. visible-only: **7.69%** (threshold: ≥10%) → **FAIL**
- Galaxies individually improved by Ark term: 17 / 25
- Exclusions (documented quality filters): D512-2 (insufficient radial points)

## Per-galaxy results (full sample)

| # | Galaxy | N pts | R_disk (kpc) | Err (visible) | Err (Ark) | Improved | Halo V₀ (km/s) | Halo r_c (kpc) | Err (halo) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | CamB | 9 | 0.47 | 0.5335 | 0.7578 | ✗ | 5 | 20.00 | 0.5336 |
| 2 | D564-8 | 6 | 0.61 | 0.4663 | 0.4336 | ✓ | 35 | 1.60 | 0.0154 |
| 3 | D631-7 | 16 | 0.70 | 0.5009 | 0.4996 | ✓ | 120 | 6.20 | 0.0305 |
| 4 | DDO064 | 14 | 0.69 | 0.4072 | 0.3745 | ✓ | 45 | 0.60 | 0.0435 |
| 5 | DDO154 | 12 | 0.37 | 0.5600 | 0.5599 | ✓ | 60 | 1.80 | 0.0153 |
| 6 | DDO161 | 31 | 1.22 | 0.3508 | 0.3956 | ✗ | 80 | 5.10 | 0.0202 |
| 7 | DDO168 | 10 | 1.02 | 0.4130 | 0.3941 | ✓ | 95 | 3.10 | 0.0377 |
| 8 | DDO170 | 8 | 1.95 | 0.4436 | 0.4231 | ✓ | 55 | 1.30 | 0.0137 |
| 9 | ESO079-G014 | 15 | 5.08 | 0.1964 | 0.1799 | ✓ | 165 | 6.80 | 0.0136 |
| 10 | ESO116-G012 | 15 | 1.51 | 0.3140 | 0.3568 | ✗ | 125 | 3.10 | 0.0142 |
| 11 | ESO444-G084 | 7 | 0.46 | 0.5563 | 0.5472 | ✓ | 75 | 1.00 | 0.0254 |
| 12 | ESO563-G021 | 30 | 5.45 | 0.1547 | 0.1858 | ✗ | 350 | 19.70 | 0.0285 |
| 13 | F561-1 | 6 | 2.79 | 0.0829 | 0.1661 | ✗ | 15 | 0.80 | 0.0780 |
| 14 | F563-1 | 17 | 3.52 | 0.6181 | 0.5690 | ✓ | 125 | 3.60 | 0.0265 |
| 15 | F563-V1 | 6 | 3.79 | 0.0493 | 0.2651 | ✗ | 5 | 0.70 | 0.0494 |
| 16 | F563-V2 | 10 | 2.43 | 0.5354 | 0.4694 | ✓ | 125 | 2.00 | 0.0189 |
| 17 | F565-V2 | 7 | 2.17 | 0.5907 | 0.5737 | ✓ | 100 | 3.10 | 0.0118 |
| 18 | F567-2 | 5 | 3.08 | 0.2245 | 0.1817 | ✓ | 40 | 2.80 | 0.0087 |
| 19 | F568-1 | 12 | 5.18 | 0.5363 | 0.4533 | ✓ | 130 | 1.40 | 0.0132 |
| 20 | F568-3 | 18 | 4.99 | 0.3911 | 0.2766 | ✓ | 100 | 2.50 | 0.0403 |
| 21 | F568-V1 | 15 | 2.85 | 0.5525 | 0.5210 | ✓ | 105 | 0.40 | 0.0241 |
| 22 | F571-8 | 13 | 3.56 | 0.4861 | 0.5728 | ✗ | 230 | 9.40 | 0.0642 |
| 23 | F571-V1 | 7 | 2.47 | 0.4612 | 0.4372 | ✓ | 90 | 3.10 | 0.0055 |
| 24 | F574-1 | 14 | 4.46 | 0.4365 | 0.3453 | ✓ | 90 | 1.40 | 0.0092 |
| 25 | F574-2 | 5 | 3.76 | 0.1605 | 0.4643 | ✗ | 5 | 20.00 | 0.1610 |

## Interpretation

The locked Ark term, V² = V_bar² · (1 + α·exp(−r/R_disk)), adds velocity
support only at small radii and decays within a few disk scale lengths.
The observed velocity deficit lives at large radii (flat outer rotation
curves). A decaying-exponential multiplier cannot supply outer-curve
support at any α. The per-galaxy halo baseline confirms the data favors
a term that persists or grows with radius.

## Transparency notes

- One infrastructure fix mid-run, permitted by the preregistered HOLD
  rules: Table 1 parsed as whitespace-delimited tokens rather than at
  MRT byte positions (byte-position parsing returned zero rows). Fixed
  before any model output was seen. No model, metric, threshold, or
  sample rule changed.
- Per the No Rescue Rule, no alternate equation was substituted after
  the result. A radially-persistent variant would be a new
  preregistration (ARK-DM-2).

## Files

- `ark_dm1_run.py` — analysis script (exact locked protocol)
- `results/ark_dm1_results.json` — full machine-readable output
- `MODEL_LOCK.md` — preregistered model, metric, threshold, sample rules

## Data credit

Lelli F., McGaugh S.S., Schombert J.M. (2016), AJ 152, 157.
SPARC database: http://astroweb.cwru.edu/SPARC/