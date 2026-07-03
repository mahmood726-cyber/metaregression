"use strict";
/*
 * extract_core.js — pull the pure computational functions out of the shipped
 * single-file app (meta-regression.html) so they can be exercised head-lessly
 * in Node, WITHOUT copying/duplicating the math.
 *
 * The whole app lives inside one `(function(){ ... })()` IIFE in a single
 * <script> block. The statistical core (matrix ops, distribution functions,
 * buildDesignMatrix, dlTau2, fitMetaRegression) consists of plain top-level
 * `function NAME(...) { ... }` declarations that touch no DOM. We locate each
 * by name and brace-match its body, concatenate the sources, and evaluate them
 * in an isolated scope. This means the benchmark tests the exact code that
 * ships to the browser: if someone edits fitMetaRegression in the HTML, the
 * benchmark sees the change.
 *
 * If the app is ever refactored (functions renamed, moved to modules, or made
 * DOM-dependent), extraction throws a clear error rather than silently testing
 * stale code.
 */
const fs = require("fs");
const path = require("path");

const APP_HTML = path.resolve(__dirname, "..", "meta-regression.html");

// Pure functions the benchmark needs. Order does not matter (function
// declarations are hoisted within the assembled scope).
const REQUIRED_FUNCTIONS = [
  "matCreate", "matTranspose", "matMul", "matDiag", "matInverse", "matSolve",
  "normalCDF", "normalQuantile", "chiSqCDF", "chiSqQuantile",
  "tCDF", "tQuantile", "tPDF", "regIncBeta", "betaCF", "lnGamma", "fCDF",
  "buildDesignMatrix", "dlTau2", "fitMetaRegression",
];

// Example datasets embedded in the app, extracted so the benchmark reuses the
// exact shipped values.
const REQUIRED_ARRAYS = ["BCG_DATA", "EXERCISE_DATA"];

function readScriptBody(html) {
  const m = html.match(/<script>([\s\S]*)<\/script>/);
  if (!m) throw new Error("extract_core: no <script> block found in " + APP_HTML);
  return m[1];
}

// Brace-match a `function NAME(...) { ... }` declaration and return its source.
function extractFunction(src, name) {
  const re = new RegExp("function\\s+" + name + "\\s*\\(");
  const start = src.search(re);
  if (start < 0) {
    throw new Error("extract_core: function '" + name + "' not found in app HTML. " +
      "Was the computational core renamed or moved out of meta-regression.html?");
  }
  const open = src.indexOf("{", start);
  if (open < 0) throw new Error("extract_core: no '{' after function " + name);
  let depth = 0;
  for (let i = open; i < src.length; i++) {
    const c = src[i];
    if (c === "{") depth++;
    else if (c === "}") {
      depth--;
      if (depth === 0) return src.slice(start, i + 1);
    }
  }
  throw new Error("extract_core: unbalanced braces while extracting " + name);
}

// Extract `var NAME = [ ... ];` array literal.
function extractArray(src, name) {
  const re = new RegExp("var\\s+" + name + "\\s*=\\s*\\[[\\s\\S]*?\\];");
  const m = src.match(re);
  if (!m) {
    throw new Error("extract_core: array '" + name + "' not found in app HTML.");
  }
  return m[0];
}

function loadCore() {
  const html = fs.readFileSync(APP_HTML, "utf8");
  const body = readScriptBody(html);

  const parts = [];
  for (const fn of REQUIRED_FUNCTIONS) parts.push(extractFunction(body, fn));
  for (const arr of REQUIRED_ARRAYS) parts.push(extractArray(body, arr));

  // Assemble into a factory that returns the internals. Evaluated in strict
  // mode inside its own function scope so nothing leaks into globals.
  const exportNames = REQUIRED_FUNCTIONS.concat(REQUIRED_ARRAYS);
  const source =
    '"use strict";\n' +
    parts.join("\n\n") +
    "\nreturn { " + exportNames.join(", ") + " };\n";

  // eslint-disable-next-line no-new-func
  const factory = new Function(source);
  return factory();
}

module.exports = { loadCore, REQUIRED_FUNCTIONS, REQUIRED_ARRAYS, APP_HTML };

if (require.main === module) {
  const core = loadCore();
  const ok = REQUIRED_FUNCTIONS.every((f) => typeof core[f] === "function");
  process.stdout.write("extract_core: loaded " + REQUIRED_FUNCTIONS.length +
    " functions and " + REQUIRED_ARRAYS.length + " datasets; all callable: " + ok + "\n");
  process.exit(ok ? 0 : 1);
}
