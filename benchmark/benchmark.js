"use strict";
/*
 * benchmark.js — reproducible cross-validation of the shipped meta-regression
 * engine (meta-regression.html) against R's `metafor` package.
 *
 *   Run:   node benchmark/benchmark.js
 *   Exit:  0 = all checks within tolerance, 1 = at least one mismatch.
 *
 * The math functions are pulled directly from the app HTML by extract_core.js,
 * so this benchmark validates the exact code that ships to the browser.
 *
 * Reference values come from benchmark/metafor_reference.R (metafor 5.0.1,
 * R 4.6.0). See that file for the validation design: the app's iterated
 * method-of-moments tau^2_res is a legitimate MoM variant that is not
 * bit-identical to metafor's single-step DL for meta-regression, so we validate
 * (a) the DL tau^2 with no moderators, and (b) the GLS coefficients / SEs / QM
 * conditional on the app's converged tau^2 (fed to metafor as a fixed variance
 * component). Both agree with metafor to well under 1e-6.
 */
const { loadCore } = require("./extract_core.js");

// Deterministic estimator tolerance (per project R-validation convention).
const TOL = 1e-6;

const core = loadCore();

// ---------------------------------------------------------------------------
// Reference fixtures (transcribed from benchmark/metafor_reference.R output).
// ---------------------------------------------------------------------------
const CASES = [
  {
    label: "BCG vaccine — latitude (continuous, tau^2 > 0)",
    data: core.BCG_DATA,
    mods: [{ name: "latitude", type: "continuous" }],
    ref: {
      tau2base: 0.210802240069,
      coeffs: {
        intercept: { estimate: 0.521236882712, se: 0.207984049457 },
        latitude: { estimate: -0.033279220836, se: 0.006925293827 },
      },
      QM: 23.092443535000,
    },
  },
  {
    label: "Exercise/Depression — dose (continuous, tau^2 = 0)",
    data: core.EXERCISE_DATA,
    mods: [{ name: "dose", type: "continuous" }],
    ref: {
      tau2base: 0.0,
      coeffs: {
        intercept: { estimate: -0.289792545307, se: 0.228342964569 },
        dose: { estimate: -0.001035887558, se: 0.001338151099 },
      },
      QM: 0.599259494039,
    },
  },
  {
    label: "Exercise/Depression — delivery (categorical dummy coding)",
    data: core.EXERCISE_DATA,
    mods: [{ name: "delivery", type: "categorical" }],
    ref: {
      // tau^2_base is shared with the dose case (same outcomes) = 0.
      tau2base: 0.0,
      coeffs: {
        intercept: { estimate: -0.486825851157, se: 0.073055771773 },
        "delivery:individual": { estimate: 0.060747457804, se: 0.112570170134 },
      },
      QM: 0.291212203924,
    },
  },
];

function approx(a, b, tol) {
  return Math.abs(a - b) <= tol;
}

function pad(s, n) {
  s = String(s);
  return s.length >= n ? s : s + " ".repeat(n - s.length);
}

const results = [];
let failures = 0;

for (const c of CASES) {
  // useKH = false to match the normal-theory metafor GLS reference.
  const r = core.fitMetaRegression(c.data, c.mods, false);
  if (r.error) {
    console.error("FAIL [" + c.label + "]: fit error: " + r.error);
    failures++;
    continue;
  }

  const checks = [];
  checks.push(["tau2base", r.tau2base, c.ref.tau2base]);
  checks.push(["QM", r.QM, c.ref.QM]);
  for (const co of r.coeffs) {
    const ref = c.ref.coeffs[co.name];
    if (!ref) continue;
    checks.push([co.name + ".estimate", co.estimate, ref.estimate]);
    checks.push([co.name + ".se", co.se, ref.se]);
  }

  console.log("\n" + c.label);
  console.log("  " + pad("quantity", 26) + pad("app (JS)", 22) +
              pad("metafor", 22) + "abs.diff   ok");
  for (const [name, got, want] of checks) {
    const diff = Math.abs(got - want);
    const ok = approx(got, want, TOL);
    if (!ok) failures++;
    console.log("  " + pad(name, 26) +
      pad(got.toPrecision(10), 22) +
      pad(want.toPrecision(10), 22) +
      pad(diff.toExponential(2), 11) + (ok ? "PASS" : "FAIL"));
    results.push({ case: c.label, quantity: name, app: got, metafor: want, diff, ok });
  }
}

console.log("\n" + "=".repeat(60));
console.log("metafor cross-validation: " + (results.length - failures) + "/" +
  results.length + " checks within tol=" + TOL);
console.log("=".repeat(60));

if (failures > 0) {
  console.error("BENCHMARK FAILED: " + failures + " check(s) exceeded tolerance.");
  process.exit(1);
}
console.log("All checks passed.");
process.exit(0);
