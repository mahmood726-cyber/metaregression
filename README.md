# Meta-Regression Workbench

Browser-based mixed-effects meta-regression with bubble plots, permutation tests, and multi-model comparison.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Overview

MetaRegression Workbench is the first fully browser-based meta-regression tool, implementing mixed-effects (random-effects) meta-regression models with support for up to 5 moderator variables (continuous or categorical). It includes Knapp-Hartung adjusted inference, permutation tests for moderator significance, bubble plots and subgroup forest plots, and an automated model comparison framework using AIC, BIC, and R-squared. All computations run client-side with no server dependencies.

## Features

- Mixed-effects meta-regression with REML estimation of residual heterogeneity
- Support for up to 5 moderators (continuous and/or categorical)
- Knapp-Hartung adjustment for confidence intervals and hypothesis tests
- Permutation test (1000 iterations) for robust moderator significance assessment
- Bubble plot visualization for continuous moderators (bubble size proportional to study weight)
- Subgroup forest plot for categorical moderators
- Multi-model comparison: all single-moderator models and full model ranked by AIC, BIC, and R-squared
- Multi-model inference with Akaike weights across candidate models
- Omnibus test of moderators (QM statistic)
- Residual heterogeneity statistics (tau-squared, I-squared, QE)
- Regression coefficient table with SE, z/t-values, p-values, and 95% CIs
- User-configurable permutation seed for reproducibility
- Auto-generated methods text for manuscripts
- Equivalent R code generation (metafor rma() syntax)
- CSV data import with header-row parsing
- MAIF (Meta-Analysis Interchange Format) import/export for cross-tool data flow
- Dark mode toggle
- Print-optimized layout

## Quick Start

1. Download `meta-regression.html`
2. Open in any modern browser
3. No installation, no dependencies, works offline

## Built-in Examples

- **BCG Vaccine**: 13 studies with latitude as a continuous moderator (classic demonstration of geographic latitude as an effect modifier)
- **Exercise and Depression**: 15 studies with continuous and categorical moderators

## Methods

- Mixed-effects model: y_i = X_i * beta + u_i + e_i, where u_i ~ N(0, tau-squared) and e_i ~ N(0, sigma_i-squared)
- REML estimation of residual tau-squared via iterative Fisher scoring
- Knapp-Hartung adjustment: t-distribution with k - p degrees of freedom and adjusted SE
- Permutation test: randomly permutes moderator values 1000 times to build null distribution of QM
- Model comparison: AIC = -2*logLik + 2p; BIC = -2*logLik + p*log(k); R-squared = 1 - tau-squared_model / tau-squared_null
- Based on: Viechtbauer W. Conducting meta-analyses in R with the metafor package. JSS. 2010;36(3).

## Screenshots

> Screenshots can be added by opening the tool and using browser screenshot.

## Validation

- 25/25 Selenium tests pass
- Cross-validated against the R metafor package rma() function (Viechtbauer 2010)

## Export

- CSV (study data, regression results)
- JSON (full analysis output)
- R code (metafor rma() equivalent)
- Methods text (clipboard, manuscript-ready)
- MAIF (Meta-Analysis Interchange Format) for cross-tool data flow

## Citation

If you use this tool, please cite:

> Ahmad M. MetaRegression Workbench: A browser-based mixed-effects meta-regression tool with permutation tests and model comparison. 2026. Available at: https://github.com/mahmood726-cyber/meta-regression

## Author

**Mahmood Ahmad**
Royal Free Hospital, London, United Kingdom
ORCID: [0009-0003-7781-4478](https://orcid.org/0009-0003-7781-4478)

## License

MIT
