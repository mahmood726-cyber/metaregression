# Reproducible benchmark

Cross-validation of the MetaRegression Workbench engine against R's
[`metafor`](https://www.metafor-project.org/) package.

## Files

| File | Purpose |
|------|---------|
| `extract_core.js` | Pulls the pure statistical functions out of `../meta-regression.html` by name + brace matching, so the benchmark tests the exact shipped code (not a copy). Throws a clear error if the core is renamed or moved. |
| `benchmark.js` | Runs three worked examples through the extracted engine and compares tau^2, coefficients, standard errors, and the QM omnibus statistic to metafor reference values. Exits non-zero on any mismatch beyond `1e-6`. |
| `metafor_reference.R` | Regenerates the reference values in R. |

## Run

```bash
# JS benchmark (Node.js only, no npm install):
node benchmark/benchmark.js

# Regenerate reference values (needs R + the metafor package):
Rscript benchmark/metafor_reference.R
```

The benchmark also runs from the Python test suite via
`tests/test_benchmark.py` (skips if Node is absent).

## What is validated, and why conditionally

The app estimates residual heterogeneity `tau^2_res` with an **iterated
method-of-moments** update. That is a legitimate MoM variant, but it is *not*
bit-identical to metafor's single-step `method="DL"` for meta-regression, nor to
metafor's `DLIT`/`SJIT` iterated estimators (which differ in how the residual
weights enter the moment equation). Validating the app's `tau^2_res` against any
single `metafor` `method=` option would therefore be comparing two different
estimators — not a correctness check.

What *is* exactly metafor-equivalent, and what this benchmark locks down:

1. **`tau^2_base`** — the DerSimonian-Laird tau^2 with no moderators. Matches
   `rma(yi, vi, method="DL")` to ~1e-13.
2. **The generalised-least-squares fit** — coefficients, standard errors, and
   the QM Wald omnibus statistic, *conditional on a given `tau^2`*. We take the
   app's converged `tau^2_res`, feed it to metafor as a fixed variance component
   (`rma(yi, vi + tau2, mods=~x, method="FE")`), and confirm the app reproduces
   metafor's GLS output to ~1e-13.

Together these confirm the two independently-correct pieces of the engine (the
DL moment estimator and the weighted-least-squares machinery). The iterated MoM
step that combines them is additionally pinned as a golden regression value, so
any future edit that changes it is caught by the benchmark.

## Reference environment

- metafor 5.0.1
- R 4.6.0

Reference values are transcribed into `benchmark.js`. Re-run
`metafor_reference.R` after any change to the example datasets.
