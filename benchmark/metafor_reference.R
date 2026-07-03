# metafor_reference.R
# ---------------------------------------------------------------------------
# Regenerate the reference values that benchmark.js checks the shipped
# JavaScript meta-regression engine against.
#
# Requires: R (>= 4.0) with the `metafor` package (Viechtbauer 2010).
#   install.packages("metafor")
# Run:  Rscript benchmark/metafor_reference.R
#
# WHAT IS VALIDATED
# -----------------
# The app estimates residual heterogeneity (tau^2_res) with an ITERATED
# method-of-moments update, which is a legitimate MoM variant but is NOT
# bit-identical to metafor's single-step method="DL" for meta-regression.
# What IS exactly metafor-equivalent, and what the benchmark locks down, is:
#   (1) the DerSimonian-Laird tau^2 with no moderators (tau^2_base), and
#   (2) the generalised-least-squares fit (coefficients, standard errors,
#       and the QM omnibus statistic) CONDITIONAL on a given tau^2.
# So we feed the app's converged tau^2_res into metafor as a FIXED variance
# component (by adding it to vi and fitting a fixed-effect model) and confirm
# the app reproduces metafor's GLS output to 1e-6.
#
# The printed values below are transcribed into benchmark.js as fixtures.
# ---------------------------------------------------------------------------

suppressMessages(library(metafor))

fmt <- function(x) sprintf("%.12f", x)

cat("## metafor", as.character(packageVersion("metafor")),
    "| R", as.character(getRversion()), "\n\n")

## ---- Case 1: BCG vaccine, latitude (continuous moderator, tau^2 > 0) ------
yi <- c(-0.8893,-1.5854,-1.3481,-1.4415,-0.0173,-0.4717,-0.0193,
        0.0115,-0.4674,-1.6209,-0.3394,-0.0169,0.4467)
se <- c(0.4073,0.5715,0.3421,0.2154,0.1098,0.5414,0.2272,
        0.0635,0.2229,0.7061,0.2278,0.2297,0.2902)
lat <- c(44,55,42,52,13,27,19,13,27,42,18,33,33)
vi <- se^2

cat("### BCG latitude\n")
m0 <- rma(yi = yi, vi = vi, method = "DL")
cat("tau2_base (DL, no mods):", fmt(m0$tau2), "\n")

# App's converged iterated-MoM tau^2_res for this dataset:
tau2res_bcg <- 0.04840370552001843
mg <- rma(yi = yi, vi = vi + tau2res_bcg, mods = ~lat, method = "FE", test = "z")
cat("b_intercept:", fmt(mg$b[1]), " se:", fmt(mg$se[1]), "\n")
cat("b_latitude :", fmt(mg$b[2]), " se:", fmt(mg$se[2]), "\n")
cat("QM         :", fmt(mg$QM), "\n\n")

## ---- Case 2: Exercise/Depression, dose (continuous, tau^2 = 0) ------------
yi2 <- c(-0.56,-0.32,-0.24,-0.80,-0.48,-0.15,-0.71,-0.42,
         -0.90,-0.38,-0.52,-0.63,-0.29,-0.19,-0.67)
se2 <- c(0.22,0.18,0.25,0.30,0.20,0.28,0.26,0.21,
         0.34,0.19,0.23,0.27,0.16,0.24,0.15)
dose <- c(135,180,120,240,135,90,180,150,150,120,150,210,240,135,180)
delivery <- c('group','individual','group','individual','group','group',
              'group','individual','group','group','individual',
              'individual','individual','group','group')
vi2 <- se2^2

cat("### Exercise dose (tau^2 = 0)\n")
m0e <- rma(yi = yi2, vi = vi2, method = "DL")
cat("tau2_base (DL):", fmt(m0e$tau2), "\n")
md <- rma(yi = yi2, vi = vi2, mods = ~dose, method = "FE", test = "z")
cat("b_intercept:", fmt(md$b[1]), " se:", fmt(md$se[1]), "\n")
cat("b_dose     :", fmt(md$b[2]), " se:", fmt(md$se[2]), "\n")
cat("QM         :", fmt(md$QM), "\n\n")

## ---- Case 3: Exercise/Depression, delivery (categorical dummy coding) -----
cat("### Exercise delivery (categorical; reference = 'group')\n")
mc <- rma(yi = yi2, vi = vi2, mods = ~factor(delivery), method = "FE", test = "z")
cat("b_intercept       :", fmt(mc$b[1]), " se:", fmt(mc$se[1]), "\n")
cat("b_delivery:individual:", fmt(mc$b[2]), " se:", fmt(mc$se[2]), "\n")
cat("QM                :", fmt(mc$QM), "\n")
