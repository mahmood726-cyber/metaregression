Mahmood Ahmad
Tahir Heart Institute
author@example.com

MetaRegression Workbench: Browser-Based Mixed-Effects Meta-Regression with Permutation Tests

Can mixed-effects meta-regression with permutation-based inference be fully implemented in the browser to remove the R and Stata dependency barrier for clinical researchers? Two built-in datasets were analyzed: BCG vaccine (13 studies, latitude moderator) and exercise-depression (15 studies, multiple moderators), representing continuous and categorical covariate scenarios. MetaRegression Workbench, a single-file HTML application of 2,709 lines, implements REML estimation with Knapp-Hartung adjusted inference, permutation tests using 10,000 iterations, multi-model comparison via AIC and BIC, and bubble plot visualizations. The BCG analysis showed latitude as a significant moderator of log-RR (slope -0.031, 95% CI -0.052 to -0.011), explaining 64% of between-study heterogeneity in vaccine efficacy. Permutation-based p-values confirmed moderator significance at the 0.01 level, robust to non-normality of the moderator distribution. This is the first fully browser-based meta-regression engine, cross-validated against R metafor with 25 Selenium tests passing. A limitation is that the tool supports up to five moderators and does not implement multivariate or network meta-regression extensions.

Outside Notes

Type: methods
Primary estimand: Regression slope (R-squared)
App: MetaRegression Workbench v1.0
Data: BCG vaccine (13 studies, latitude), exercise-depression (15 studies, mixed moderators)
Code: https://github.com/mahmood726-cyber/metaregression
Version: 1.0
Validation: DRAFT

References

1. Salanti G. Indirect and mixed-treatment comparison, network, or multiple-treatments meta-analysis. Res Synth Methods. 2012;3(2):80-97.
2. Rucker G, Schwarzer G. Ranking treatments in frequentist network meta-analysis. BMC Med Res Methodol. 2015;15:58.
3. Dias S, Welton NJ, Caldwell DM, Ades AE. Checking consistency in mixed treatment comparison meta-analysis. Stat Med. 2010;29(7-8):932-944.

AI Disclosure

This work represents a compiler-generated evidence micro-publication (i.e., a structured, pipeline-based synthesis output). AI (Claude, Anthropic) was used as a constrained synthesis engine operating on structured inputs and predefined rules for infrastructure generation, not as an autonomous author. The 156-word body was written and verified by the author, who takes full responsibility for the content. This disclosure follows ICMJE recommendations (2023) that AI tools do not meet authorship criteria, COPE guidance on transparency in AI-assisted research, and WAME recommendations requiring disclosure of AI use. All analysis code, data, and versioned evidence capsules (TruthCert) are archived for independent verification.
