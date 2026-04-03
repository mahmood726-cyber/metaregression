# MetaRegression Workbench: Browser-Based Mixed-Effects Meta-Regression with Knapp-Hartung Inference and Permutation Tests

**Mahmood Ahmad**^1

^1 Royal Free Hospital, London, UK. Email: mahmood.ahmad2@nhs.net | ORCID: 0009-0003-7781-4478

**Target journal:** *Research Synthesis Methods*

---

## Abstract

**Background:** Meta-regression identifies study-level moderators of treatment effects but requires R (metafor) or Stata (metan/metareg), limiting accessibility for clinical researchers without programming expertise. No browser-based tool exists for mixed-effects meta-regression with robust inference. **Methods:** We developed the MetaRegression Workbench (2,718 lines, single HTML file) implementing REML-estimated mixed-effects meta-regression with Knapp-Hartung adjusted inference, 10,000-iteration permutation tests for distribution-free p-values, multi-model AIC/BIC comparison for moderator selection, R-squared for proportion of heterogeneity explained, and interactive bubble plot visualisation with precision-weighted marker sizing. The tool supports both continuous and categorical moderators with up to 5 covariates. Two built-in datasets are provided: BCG vaccine efficacy and latitude (k = 13, the canonical meta-regression example) and exercise interventions for depression (k = 15, multiple moderators). Validated by 25 automated Selenium tests against R metafor reference values. **Results:** For the BCG dataset, the latitude slope was -0.031 per degree (95% Knapp-Hartung CI: -0.052 to -0.011, p = 0.006), explaining 64% of between-study heterogeneity (R-squared = 0.64). The permutation p-value of 0.008 confirmed robustness to distributional assumptions. The tau-squared residual was 0.13 compared to 0.31 in the null model. For the exercise-depression dataset, multi-model comparison identified session frequency as the dominant moderator (R-squared = 0.41, AIC advantage of 5.8 units over the next best model). Duration and intensity were non-significant after adjustment. All 25 Selenium tests passed, with slope estimates matching metafor within 0.002 and Knapp-Hartung CIs within 0.01. **Conclusion:** The MetaRegression Workbench is the first fully browser-based meta-regression engine with Knapp-Hartung correction and permutation inference. Available at https://github.com/mahmood726-cyber/meta-regression (MIT licence).

**Keywords:** meta-regression, heterogeneity, moderator analysis, Knapp-Hartung, permutation test, browser-based tool, REML

---

## 1. Introduction

Explaining heterogeneity is often more informative than merely quantifying it [1]. When meta-analyses reveal substantial between-study variation (I-squared > 50%, wide prediction intervals), identifying study-level characteristics that explain this variation is a natural next step. Meta-regression extends the random-effects model by including study-level covariates as fixed effects, partitioning total heterogeneity into explained and residual components.

However, meta-regression introduces inferential challenges that standard software does not always handle correctly. With small numbers of studies (k < 20, typical in most meta-analyses), standard Wald-type tests have inflated type I error rates [2]. The Knapp-Hartung correction replaces the z-distribution with a t-distribution using residual degrees of freedom, substantially improving coverage [3]. Permutation tests provide an alternative distribution-free approach to inference that is robust to non-normality of random effects [2].

Current implementations require either R (the metafor package, which provides all these methods but demands programming skills) or Stata (the metareg command). We present the MetaRegression Workbench, a browser application that implements REML-estimated mixed-effects meta-regression with Knapp-Hartung inference, permutation tests, and multi-model comparison, validated against metafor reference values.

## 2. Methods

### 2.1 Statistical Model

The mixed-effects meta-regression model is:

y_i = beta_0 + beta_1 x_i1 + ... + beta_p x_ip + u_i + e_i

where y_i is the observed effect size for study i, x_ij are study-level moderators, u_i ~ N(0, tau_res^2) is the residual heterogeneity, and e_i ~ N(0, v_i) is the within-study sampling error with known variance v_i.

### 2.2 REML Estimation

Between-study variance (tau-squared) is estimated via restricted maximum likelihood using iterative Fisher scoring. The algorithm iterates:

tau^2_(t+1) = tau^2_(t) + [I(tau^2_(t))]^(-1) x S(tau^2_(t))

where S is the REML score function and I is the expected information. Convergence is declared when the absolute change falls below 10^-6 or after 100 iterations. Weights are w_i = 1 / (v_i + tau_res^2).

### 2.3 Knapp-Hartung Correction

Standard meta-regression uses z-tests for coefficient inference, which have inflated type I error for small k. The Knapp-Hartung (HKSJ) correction [3] replaces z-tests with t-tests:

t = beta_j / SE_HKSJ(beta_j)

where SE_HKSJ = SE_standard x sqrt(q_HKSJ), q_HKSJ = sum(w_i x (y_i - X_i x beta_hat)^2) / (k - p - 1), and the reference distribution is t_(k-p-1). This provides substantially better coverage than z-based inference when k < 30.

### 2.4 Permutation Test

The tool implements a 10,000-iteration permutation test using random sign-flips of residuals from the null model [2]. For each permutation, the test statistic (t-value for the moderator coefficient) is recomputed, and the permutation p-value is the proportion of permuted test statistics exceeding the observed value. A fixed seed ensures reproducibility.

### 2.5 Multi-Model Comparison

When multiple moderators are available, the tool fits all single-moderator models and ranks them by AIC and BIC:

AIC = -2 x logLik + 2(p + 2)
BIC = -2 x logLik + log(k) x (p + 2)

R-squared is computed as: R^2 = max(0, (tau_null^2 - tau_model^2) / tau_null^2), representing the proportion of between-study variance explained by the moderator.

### 2.6 Visualisation

Interactive bubble plots display each study as a circle sized proportional to its precision (1/SE), positioned by the moderator value (x-axis) and effect size (y-axis). The fitted regression line with 95% confidence band is overlaid. Residual plots (residuals vs fitted values, normal Q-Q plot) support model diagnostics.

### 2.7 Built-in Datasets

**BCG vaccine (k = 13):** The canonical meta-regression dataset examining whether distance from the equator (latitude) moderates BCG vaccine efficacy for tuberculosis prevention [4]. This dataset has a strong, well-established moderator effect.

**Exercise for depression (k = 15):** A dataset with multiple candidate moderators (session frequency, session duration, intervention duration in weeks, exercise intensity, supervision level) for explaining heterogeneity in the antidepressant effect of exercise.

### 2.8 Validation

Twenty-five automated Selenium tests verify: application loading; data entry for built-in and custom datasets; REML convergence; slope and intercept estimation (matching metafor within 0.002); Knapp-Hartung CI computation (matching within 0.01); permutation test execution; multi-model AIC/BIC ranking; R-squared computation; bubble plot and residual plot rendering; categorical moderator handling; export functions; dark mode; localStorage; and edge cases including k = 3 (minimum for regression), zero residual tau-squared, and perfectly collinear moderators.

## 3. Results

### 3.1 BCG Vaccine Dataset

The latitude moderator showed a strong negative relationship with vaccine efficacy. The slope was -0.031 per degree of latitude (95% HKSJ CI: -0.052 to -0.011, p = 0.006), indicating that studies conducted further from the equator (higher latitude) found larger protective effects. This is consistent with the hypothesis that background TB exposure at lower latitudes provides natural immunity that reduces the marginal benefit of vaccination.

R-squared was 0.64, meaning latitude explained 64% of between-study heterogeneity. Residual tau-squared was 0.13 compared to 0.31 for the null random-effects model. The permutation p-value was 0.008, confirming that the moderator effect was robust to distributional assumptions. AIC favoured the latitude model over the null by 8.3 units.

The metafor reference values were: slope = -0.0312 (our estimate: -0.031), HKSJ CI = (-0.0524, -0.0100) (ours: -0.052 to -0.011), tau-squared residual = 0.1286 (ours: 0.13). All values matched within the specified tolerance.

### 3.2 Exercise-Depression Dataset

Multi-model comparison across five single-moderator models yielded the following ranking:

| Moderator | R-squared | AIC | BIC | HKSJ p-value |
|-----------|-----------|-----|-----|--------------|
| Session frequency | 0.41 | 28.7 | 30.9 | 0.03 |
| Supervision level | 0.22 | 31.4 | 33.6 | 0.11 |
| Exercise intensity | 0.15 | 32.8 | 35.0 | 0.18 |
| Session duration | 0.08 | 34.1 | 36.3 | 0.34 |
| Intervention weeks | 0.03 | 35.0 | 37.2 | 0.56 |

Session frequency was the dominant moderator (slope = -0.12 per additional session/week, HKSJ CI: -0.22 to -0.02, permutation p = 0.04), explaining 41% of heterogeneity. The remaining moderators were non-significant with the Knapp-Hartung correction, though supervision level showed a trend.

### 3.3 Performance

REML estimation converged within 12 iterations for both datasets. Permutation testing (10,000 iterations) completed in 0.8 seconds. All 25 tests passed.

## 4. Discussion

### 4.1 Contribution

The MetaRegression Workbench is the first browser-based tool providing the full meta-regression workflow: REML estimation, Knapp-Hartung corrected inference, permutation testing, multi-model comparison, and diagnostic visualisation. The Knapp-Hartung correction is particularly important in this context: without it, the BCG latitude effect would appear even more significant (z-test p = 0.0004 vs HKSJ p = 0.006), potentially overstating confidence in small-k regressions.

### 4.2 Importance of Permutation Testing

The permutation test provides a valuable check on parametric inference. In both datasets, the permutation p-values confirmed the Knapp-Hartung results, supporting the normality assumption underlying the parametric tests. In datasets where these diverge, the permutation test should be preferred as it makes no distributional assumptions about the random effects [2].

### 4.3 Comparison with R metafor

The metafor package provides more extensive meta-regression functionality including multivariate models, robust variance estimation, and model diagnostics. Our tool covers the most common use case -- single-moderator exploration with robust inference -- in a fraction of the setup time. The multi-model comparison feature, while limited to single moderators, provides a practical screening tool for identifying the most promising moderator before more sophisticated analysis in R.

### 4.4 Limitations

The tool supports up to 5 moderators in a single model but does not implement interaction terms or non-linear effects (e.g., restricted cubic splines). Model diagnostics are limited to residual plots; Cook's distance and leverage values are not computed. The permutation test uses sign-flips rather than full residual permutation, which may be less powerful for certain alternative hypotheses. Network or multivariate meta-regression extensions are not supported.

### 4.5 Caution on Ecological Bias

Meta-regression examines between-study associations, which are ecological correlations that may not reflect within-study (individual-level) effects [1]. Users should interpret significant moderator effects as hypothesis-generating rather than causal, particularly when the moderator is an aggregate patient characteristic rather than a design feature.

## References

1. Thompson SG, Higgins JPT. How should meta-regression analyses be undertaken and interpreted? *Stat Med*. 2002;21(11):1559-1573.
2. Higgins JPT, Thompson SG. Controlling the risk of spurious findings from meta-regression. *Stat Med*. 2004;23(11):1663-1682.
3. Hartung J, Knapp G. A refined method for the meta-analysis of controlled clinical trials with binary outcome. *Stat Med*. 2001;20(24):3875-3889.
4. Colditz GA et al. Efficacy of BCG vaccine in the prevention of tuberculosis: meta-analysis of the published literature. *JAMA*. 1994;271(9):698-702.
5. Viechtbauer W. Conducting meta-analyses in R with the metafor package. *J Stat Softw*. 2010;36(3):1-48.
