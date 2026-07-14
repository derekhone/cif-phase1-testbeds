# ARK-DM-1 Model Lock

## Purpose

This file locks the exact mathematical model, parameter rules, error metric, and comparison baseline for ARK-DM-1 before code execution or outcome analysis.

This file supersedes any loose language in MODEL_SPEC.md.

If this file conflicts with MODEL_SPEC.md, this file controls.

## Locked Dataset Rule

The test will use the sample-selection rules stated in SAMPLE_PLAN.md.

No galaxy may be added, removed, or substituted after outcome analysis except for documented parsing failure, missing required columns, or failure of the preregistered quality filters.

## Observables Used

The Ark-inspired term will use only:

- baryonic rotation contribution,
- radial distance,
- galaxy disk scale length where available,
- observed rotation velocity for error measurement only.

No additional hidden variables may be introduced after seeing results.

## Visible-Matter Baseline

The visible-matter-only baseline is:

V_bar(r)^2 = V_gas(r)^2 + V_disk(r)^2 + V_bulge(r)^2

If a bulge component is unavailable or marked absent, V_bulge(r) = 0.

The predicted baseline velocity is:

V_visible(r) = sqrt(max(V_bar(r)^2, 0))

## Locked Ark-Inspired Hidden-Inheritance Term

The Ark-inspired correction term is defined as a single global radial inheritance support term:

V_ark(r)^2 = V_bar(r)^2 * [1 + alpha * exp(-r / R_d)]

Where:

- r = radial distance for the measurement point,
- R_d = disk scale length for the galaxy,
- alpha = one global fitted parameter shared across all galaxies in the selected sample.

The final predicted velocity is:

V_ark(r) = sqrt(max(V_ark(r)^2, 0))

## Parameter Rule

The Ark-inspired model has exactly one free parameter:

alpha

Alpha must be fitted globally across the selected sample.

Alpha may not be fitted separately per galaxy.

Alpha may not be changed after seeing individual-galaxy results.

No additional parameters may be added.

## Alpha Search Rule

Alpha will be selected by grid search over the fixed range:

alpha in [0.00, 5.00]

Grid step:

0.01

The alpha value that minimizes the primary error metric across the full selected training/sample set will be used.

No post-hoc expansion of the alpha range is permitted.

## Standard Halo Baseline

The standard halo-style baseline for ARK-DM-1 will be the pseudo-isothermal halo model.

The halo velocity term is:

V_halo(r)^2 = 4 * pi * G * rho_0 * r_c^2 * [1 - (r_c / r) * arctan(r / r_c)]

The full halo prediction is:

V_iso(r)^2 = V_bar(r)^2 + V_halo(r)^2

Free parameters:

- rho_0
- r_c

These parameters may be fitted per galaxy because standard halo modeling is normally galaxy-specific.

This makes the halo baseline more flexible than the Ark-inspired one. Therefore, if the halo baseline wins, the Ark-inspired term will not be treated as novel.

## Primary Error Metric

The primary error metric is median fractional absolute velocity error across all valid radial points in the selected sample:

error = median( abs(V_pred(r) - V_obs(r)) / max(V_obs(r), epsilon) )

Where:

epsilon = 1e-6

The same error metric must be used for:

- visible-matter-only baseline,
- Ark-inspired hidden-inheritance term,
- pseudo-isothermal halo baseline.

## Primary Kill-Condition

The Ark-inspired model FAILS if:

error_ark > 0.90 * error_visible

In plain language:

The Ark-inspired model must reduce median fractional absolute velocity error by at least 10% compared with visible matter only.

If it improves by less than 10%, it FAILS.

## Novelty Condition

Even if the Ark-inspired model beats visible matter only by at least 10%, the result is LIMITED / NON-NOVEL if:

- the pseudo-isothermal halo baseline performs better, or
- the Ark-inspired term performs only comparably to the halo baseline while using less physical justification, or
- the improvement appears concentrated in a small number of galaxies rather than broadly across the sample.

## Result Categories

PASS:

The Ark-inspired model reduces median fractional absolute velocity error by at least 10% compared with visible matter only, using one global alpha, without post-hoc tuning.

FAIL:

The Ark-inspired model does not reduce median fractional absolute velocity error by at least 10% compared with visible matter only.

LIMITED / NON-NOVEL:

The Ark-inspired model beats visible matter only by at least 10% but does not meaningfully outperform the pseudo-isothermal halo baseline.

HOLD:

The data cannot be parsed, disk scale length values are unavailable for the selected sample, required baryonic components cannot be interpreted, or the test cannot be completed under the locked rules without changing the model.

## Interpretation Limits

A PASS does not prove dark matter.

A PASS does not prove new physics.

A PASS does not prove Ark, UIP, or the hidden-inheritance framework.

A PASS only means this exact locked one-parameter radial correction survived this specific preregistered open-data test.

A FAIL means this locked Ark-inspired term did not survive the test.

## No Rescue Rule

If the locked equation fails, the result is published as FAIL.

No alternate Ark term may be substituted inside ARK-DM-1.

Any future alternate equation must be preregistered as a separate experiment, such as ARK-DM-2.

## Rule

One locked equation.

One global Ark parameter.

One primary error metric.

One standard halo baseline.

Publish pass, fail, limited, or hold.
