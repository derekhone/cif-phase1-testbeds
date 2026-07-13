# ARK-DM-1 Sample Plan

## Purpose

This file defines the planned data-selection approach for ARK-DM-1 before running the experiment.

The purpose is to avoid cherry-picking galaxies after seeing results.

## Dataset

Primary dataset:

SPARC galaxy rotation-curve database.

The test will use public galaxy rotation-curve data and available baryonic component information.

## Initial Sample Rule

ARK-DM-1 will begin with a small reproducible sample of galaxies from SPARC.

The first implementation may use a limited sample for code validation, but the preregistered result should be based on a clearly defined sample selected before outcome analysis.

## Planned Sample Selection

Preferred sample size:

25 galaxies.

Selection rule:

Use the first 25 galaxies available in the SPARC rotation-curve data after applying basic quality filters.

Quality filters may include:

- rotation-curve data available,
- observed velocity values available,
- baryonic component values available or computable,
- no missing critical columns needed for the baseline calculation,
- sufficient radial points to compute a meaningful prediction error.

## No Post-Hoc Exclusion Rule

Galaxies may not be removed after results are viewed merely because they make the Ark-inspired term perform worse.

A galaxy may only be excluded if:

- required data is missing,
- the row format cannot be parsed,
- units cannot be interpreted,
- or the galaxy fails the quality filters stated above.

Any exclusion must be listed in the final results file.

## Models Compared

ARK-DM-1 will compare:

1. Visible-matter-only baseline.
2. Standard halo-style baseline where feasible.
3. Ark-inspired hidden-inheritance correction term.

## Primary Metric

Primary metric:

Median prediction error across the selected galaxy sample.

The exact error calculation will be documented in the code and final results.

## Preregistered Threshold

The Ark-inspired hidden-inheritance term must reduce median prediction error by at least 10% compared with the visible-matter-only baseline.

If it does not, the Ark-inspired term FAILS.

## Novelty Rule

If the Ark-inspired term improves over visible-matter-only but performs worse than, or only comparably to, a standard dark-matter halo baseline after considering model complexity, it will not be treated as novel.

## Result Categories

PASS:

The Ark-inspired term improves median prediction error by at least 10% over visible-matter-only and the result is reproducible under the stated rules.

FAIL:

The Ark-inspired term does not meet the 10% improvement threshold.

LIMITED / NON-NOVEL:

The Ark-inspired term improves over visible-matter-only but does not outperform or meaningfully distinguish itself from standard halo-style modeling.

HOLD:

The data cannot be parsed, the baseline cannot be computed, or the sample selection cannot be completed without changing the rules.

## Rule

No code execution before sample-selection logic is documented.

No cherry-picking after seeing outcomes.

Publish pass, fail, limited, or hold.
