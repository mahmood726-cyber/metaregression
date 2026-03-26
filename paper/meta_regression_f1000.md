# MetaRegression Workbench: A Browser-Based Mixed-Effects Meta-Regression Engine

Mahmood Ahmad^1 | ^1 Royal Free Hospital, London, UK | mahmood.ahmad2@nhs.net | ORCID: 0009-0003-7781-4478

## Abstract

MetaRegression Workbench is a single-file browser application (2,709 lines) implementing mixed-effects meta-regression entirely client-side. It supports multiple continuous and categorical moderators, weighted least squares estimation with Knapp-Hartung adjustment, bubble plots with regression lines, permutation tests for moderator significance (10,000 permutations), model comparison via AIC/BIC, and residual diagnostics. The tool is the first browser-based meta-regression engine, removing the R/Stata dependency barrier. Available at https://github.com/mahmood726-cyber/meta-regression.

## Introduction

Meta-regression investigates sources of heterogeneity by modelling the relationship between study-level covariates and effect sizes. Current tools require statistical software (metafor in R, metareg in Stata). MetaRegression Workbench democratizes access by running entirely in the browser with no installation.

## Implementation

The engine implements the mixed-effects model: yi = beta0 + beta1*x1i + ... + betap*xpi + ui + ei, where ui ~ N(0, tau2) and ei ~ N(0, vi). Estimation uses iterative weighted least squares with REML for tau2. The Knapp-Hartung adjustment is applied for inference. Permutation tests (10,000 random reassignments) provide robust p-values that do not assume normality. Model comparison uses QM (moderator test), R-squared analog, AIC, and BIC. Bubble plots weight point size by study precision.

## Availability

Single HTML file, MIT license. Source: https://github.com/mahmood726-cyber/meta-regression

## Funding
None.

## References
1. Thompson SG, Higgins JPT. How should meta-regression analyses be undertaken and interpreted? Stat Med. 2002;21:1559-1573.
2. Viechtbauer W. Conducting meta-analyses in R with the metafor package. J Stat Softw. 2010;36(3):1-48.
3. Knapp G, Hartung J. Improved tests for a random effects meta-regression. Stat Med. 2003;22:2693-2710.
