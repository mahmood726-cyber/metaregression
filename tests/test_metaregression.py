"""
Selenium test suite for MetaRegression Workbench v1.0
World-first browser meta-regression tool.

Tests core calculations (via injected harness), UI interactions,
example data loading, regression workflow, report generation, exports.
"""
import sys, io, os, unittest, time, math, json
from pathlib import Path

# Only re-wrap stdout when this file is executed directly (python test_metaregression.py).
# Under pytest, sys.stdout is already a capture fixture and wrapping its buffer
# closes the underlying tempfile, breaking pytest's capture pipeline and
# causing "ValueError: I/O operation on closed file." at session teardown.
if __name__ == '__main__' and os.environ.get('PYTHONIOENCODING') is None and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HTML = (PROJECT_ROOT / 'meta-regression.html').resolve().as_uri()


def _build_driver():
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--window-size=1400,900')
    try:
        return webdriver.Chrome(options=opts)
    except WebDriverException as exc:
        raise unittest.SkipTest(f'Chrome webdriver unavailable: {exc}') from exc

# JavaScript snippet to expose IIFE-internal functions for testing.
# We re-run the pure-math portion on window so execute_script can call them.
INJECT_HARNESS = r"""
(function(){
  // ---- normalCDF ----
  window._test_normalCDF = function(x) {
    if (x < -8) return 0;
    if (x > 8) return 1;
    var sign = x < 0 ? -1 : 1;
    x = Math.abs(x);
    var t = 1 / (1 + 0.2316419 * x);
    var d = 0.3989422804014327;
    var p = d * Math.exp(-x * x / 2);
    var a = ((((1.330274429*t - 1.821255978)*t + 1.781477937)*t - 0.356563782)*t + 0.319381530)*t;
    return sign === 1 ? 1 - p * a : p * a;
  };
  // ---- normalQuantile ----
  window._test_normalQuantile = function(p) {
    if (p <= 0) return -Infinity; if (p >= 1) return Infinity; if (p === 0.5) return 0;
    var a=[-3.969683028665376e+01,2.209460984245205e+02,-2.759285104469687e+02,1.383577518672690e+02,-3.066479806614716e+01,2.506628277459239e+00];
    var b=[-5.447609879822406e+01,1.615858368580409e+02,-1.556989798598866e+02,6.680131188771972e+01,-1.328068155288572e+01];
    var c=[-7.784894002430293e-03,-3.223964580411365e-01,-2.400758277161838e+00,-2.549732539343734e+00,4.374664141464968e+00,2.938163982698783e+00];
    var d=[7.784695709041462e-03,3.224671290700398e-01,2.445134137142996e+00,3.754408661907416e+00];
    var pLow=0.02425, pHigh=1-pLow; var q,r;
    if(p<pLow){q=Math.sqrt(-2*Math.log(p));return(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);}
    else if(p<=pHigh){q=p-0.5;r=q*q;return(((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q/(((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1);}
    else{q=Math.sqrt(-2*Math.log(1-p));return-(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);}
  };
  // ---- lnGamma ----
  window._test_lnGamma = function(x) {
    var g=7;
    var co=[0.99999999999980993,676.5203681218851,-1259.1392167224028,771.32342877765313,-176.61502916214059,12.507343278686905,-0.13857109526572012,9.9843695780195716e-6,1.5056327351493116e-7];
    if(x<0.5){return Math.log(Math.PI/Math.sin(Math.PI*x))-window._test_lnGamma(1-x);}
    x-=1; var aa=co[0]; var t=x+g+0.5;
    for(var i=1;i<g+2;i++) aa+=co[i]/(x+i);
    return 0.5*Math.log(2*Math.PI)+(x+0.5)*Math.log(t)-t+Math.log(aa);
  };
  // ---- matCreate, matMul, matTranspose, matInverse, matDiag ----
  window._test_matCreate=function(rows,cols,fill){fill=fill!=null?fill:0;var m=[];for(var i=0;i<rows;i++){m[i]=[];for(var j=0;j<cols;j++)m[i][j]=fill;}return m;};
  window._test_matTranspose=function(A){var r=A.length,c=A[0].length;var T=window._test_matCreate(c,r);for(var i=0;i<r;i++)for(var j=0;j<c;j++)T[j][i]=A[i][j];return T;};
  window._test_matMul=function(A,B){var rA=A.length,cA=A[0].length,cB=B[0].length;var C=window._test_matCreate(rA,cB);for(var i=0;i<rA;i++)for(var j=0;j<cB;j++){var s=0;for(var k=0;k<cA;k++)s+=A[i][k]*B[k][j];C[i][j]=s;}return C;};
  window._test_matDiag=function(arr){var n=arr.length;var D=window._test_matCreate(n,n);for(var i=0;i<n;i++)D[i][i]=arr[i];return D;};
  window._test_matInverse=function(M){var n=M.length;var aug=window._test_matCreate(n,2*n);for(var i=0;i<n;i++){for(var j=0;j<n;j++)aug[i][j]=M[i][j];aug[i][n+i]=1;}for(var col=0;col<n;col++){var maxRow=col;for(var row=col+1;row<n;row++){if(Math.abs(aug[row][col])>Math.abs(aug[maxRow][col]))maxRow=row;}var tmp=aug[col];aug[col]=aug[maxRow];aug[maxRow]=tmp;if(Math.abs(aug[col][col])<1e-14)return null;var pivot=aug[col][col];for(var j2=0;j2<2*n;j2++)aug[col][j2]/=pivot;for(var row2=0;row2<n;row2++){if(row2!==col){var factor=aug[row2][col];for(var j3=0;j3<2*n;j3++)aug[row2][j3]-=factor*aug[col][j3];}}}var inv=window._test_matCreate(n,n);for(var i2=0;i2<n;i2++)for(var j4=0;j4<n;j4++)inv[i2][j4]=aug[i2][n+j4];return inv;};
  // ---- xoshiro128** ----
  window._test_xoshiro128ss=function(seed){var s=[seed>>>0,(seed*2654435761)>>>0,(seed*2246822519)>>>0,(seed*3266489917)>>>0];if((s[0]|s[1]|s[2]|s[3])===0){s[0]=1;}function rotl(x,k){return((x<<k)|(x>>>(32-k)))>>>0;}return function(){var result=(rotl((s[1]*5)>>>0,7)*9)>>>0;var t=(s[1]<<9)>>>0;s[2]^=s[0];s[3]^=s[1];s[1]^=s[2];s[0]^=s[3];s[2]^=t;s[3]=rotl(s[3],11);return(result>>>0)/4294967296;};};
  window._test_injected = true;
})();
"""


class TestMetaRegression(unittest.TestCase):
    """Comprehensive Selenium tests for MetaRegression Workbench."""

    @classmethod
    def setUpClass(cls):
        cls.drv = _build_driver()
        cls.drv.get(HTML)
        time.sleep(1.5)
        cls.drv.execute_script(INJECT_HARNESS)

    @classmethod
    def tearDownClass(cls):
        cls.drv.quit()

    def js(self, script, *args):
        # Forward *args so callers can pass values into JS via the standard
        # Selenium `arguments[0..n]` pattern (e.g. pasting CSV text).
        return self.drv.execute_script(script, *args)

    def reload_app(self):
        self.drv.get(HTML)
        time.sleep(1)
        self.drv.execute_script(INJECT_HARNESS)

    # Full UI workflow helper
    def _load_bcg_and_validate(self):
        self.reload_app()
        self.drv.find_element(By.ID, 'btnLoadBCG').click()
        time.sleep(0.5)
        self.drv.find_element(By.ID, 'btnValidateData').click()
        time.sleep(0.5)

    def _load_bcg_validate_and_regress(self):
        self._load_bcg_and_validate()
        self.drv.find_element(By.ID, 'tab-regression').click()
        time.sleep(0.3)
        self.drv.find_element(By.ID, 'btnRunRegression').click()
        time.sleep(1.5)

    # =================================================================
    # 1. PURE MATH: normalCDF
    # =================================================================

    def test_01_normalCDF_known_values(self):
        """normalCDF(0) = 0.5, normalCDF(1.96) ~ 0.975"""
        cdf0 = self.js("return window._test_normalCDF(0);")
        self.assertAlmostEqual(cdf0, 0.5, places=6)
        cdf196 = self.js("return window._test_normalCDF(1.96);")
        self.assertAlmostEqual(cdf196, 0.975, delta=0.002)
        cdfNeg = self.js("return window._test_normalCDF(-1.96);")
        self.assertAlmostEqual(cdfNeg, 0.025, delta=0.002)

    def test_02_normalCDF_extreme(self):
        """normalCDF handles extreme inputs"""
        self.assertAlmostEqual(self.js("return window._test_normalCDF(-10);"), 0.0, places=5)
        self.assertAlmostEqual(self.js("return window._test_normalCDF(10);"), 1.0, places=5)

    # =================================================================
    # 2. PURE MATH: normalQuantile
    # =================================================================

    def test_03_normalQuantile_inverse(self):
        """normalQuantile(0.975) ~ 1.96"""
        q = self.js("return window._test_normalQuantile(0.975);")
        self.assertAlmostEqual(q, 1.96, delta=0.01)
        q50 = self.js("return window._test_normalQuantile(0.5);")
        self.assertAlmostEqual(q50, 0.0, places=5)

    def test_04_normalQuantile_roundtrip(self):
        """CDF(Quantile(p)) = p"""
        for p in [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]:
            result = self.js(f"var q = window._test_normalQuantile({p}); return window._test_normalCDF(q);")
            self.assertAlmostEqual(result, p, delta=0.002, msg=f"Roundtrip failed for p={p}")

    # =================================================================
    # 3. PURE MATH: lnGamma
    # =================================================================

    def test_05_lnGamma_known(self):
        """lnGamma(1) = 0, lnGamma(5) = ln(24)"""
        lg1 = self.js("return window._test_lnGamma(1);")
        self.assertAlmostEqual(lg1, 0.0, places=5)
        lg5 = self.js("return window._test_lnGamma(5);")
        self.assertAlmostEqual(lg5, math.log(24), delta=0.001)

    # =================================================================
    # 4. MATRIX OPERATIONS
    # =================================================================

    def test_06_matMul_identity(self):
        """A * I = A"""
        result = self.js("""
            var A = [[1,2],[3,4]];
            var I = [[1,0],[0,1]];
            return window._test_matMul(A, I);
        """)
        self.assertEqual(result, [[1, 2], [3, 4]])

    def test_07_matInverse_2x2(self):
        """Inverse of 2x2 matrix: A * A^{-1} = I"""
        result = self.js("""
            var A = [[4,7],[2,6]];
            var Ainv = window._test_matInverse(A);
            var I = window._test_matMul(A, Ainv);
            return [Math.abs(I[0][0]-1)<1e-10, Math.abs(I[0][1])<1e-10,
                    Math.abs(I[1][0])<1e-10, Math.abs(I[1][1]-1)<1e-10];
        """)
        self.assertTrue(all(result), "A * A^{-1} should be identity")

    def test_08_matTranspose_shape(self):
        """Transpose of 2x3 matrix is 3x2"""
        result = self.js("""
            var A = [[1,2,3],[4,5,6]];
            var T = window._test_matTranspose(A);
            return [T.length, T[0].length, T[0][0], T[2][1]];
        """)
        self.assertEqual(result, [3, 2, 1, 6])

    def test_09_matDiag(self):
        """matDiag creates correct diagonal matrix"""
        result = self.js("""
            var D = window._test_matDiag([2, 5, 9]);
            return [D[0][0], D[1][1], D[2][2], D[0][1], D[1][2]];
        """)
        self.assertEqual(result, [2, 5, 9, 0, 0])

    def test_10_matInverse_singular(self):
        """Singular matrix returns null"""
        result = self.js("return window._test_matInverse([[1,2],[2,4]]);")
        self.assertIsNone(result)

    # =================================================================
    # 5. PRNG (xoshiro128**)
    # =================================================================

    def test_11_xoshiro_deterministic(self):
        """Same seed produces identical sequence"""
        result = self.js("""
            var rng1 = window._test_xoshiro128ss(42);
            var rng2 = window._test_xoshiro128ss(42);
            var match = true;
            for (var i = 0; i < 100; i++) {
                if (rng1() !== rng2()) { match = false; break; }
            }
            return match;
        """)
        self.assertTrue(result)

    def test_12_xoshiro_range(self):
        """All values in [0, 1)"""
        result = self.js("""
            var rng = window._test_xoshiro128ss(123);
            var ok = true;
            for (var i = 0; i < 1000; i++) {
                var v = rng();
                if (v < 0 || v >= 1) { ok = false; break; }
            }
            return ok;
        """)
        self.assertTrue(result)

    # =================================================================
    # 6. EXAMPLE DATA LOADING
    # =================================================================

    def test_13_load_BCG_example(self):
        """Load BCG dataset: 13 studies, 1 moderator (latitude)"""
        self.reload_app()
        self.drv.find_element(By.ID, 'btnLoadBCG').click()
        time.sleep(0.5)
        count = self.js("return STATE.studies.length;")
        self.assertEqual(count, 13)
        mod_name = self.js("return STATE.moderators[0].name;")
        self.assertEqual(mod_name, 'latitude')

    def test_14_load_exercise_example(self):
        """Load Exercise/Depression: 15 studies, 3 moderators (dose, delivery, duration)"""
        self.reload_app()
        self.drv.find_element(By.ID, 'btnLoadExercise').click()
        time.sleep(0.5)
        count = self.js("return STATE.studies.length;")
        self.assertEqual(count, 15)
        mod_count = self.js("return STATE.moderators.length;")
        self.assertEqual(mod_count, 3)
        mod_names = self.js("return STATE.moderators.map(function(m){return m.name;});")
        self.assertIn('dose', mod_names)
        self.assertIn('delivery', mod_names)
        self.assertIn('duration', mod_names)

    # =================================================================
    # 7. DATA VALIDATION
    # =================================================================

    def test_15_validate_BCG(self):
        """Validate BCG data succeeds (13 studies)"""
        self._load_bcg_and_validate()
        validated = self.js("return STATE.validated;")
        self.assertTrue(validated)
        status = self.drv.find_element(By.ID, 'dataStatus').text
        self.assertIn('13', status)

    def test_16_validate_empty_fails(self):
        """Validation fails with fewer than 3 studies"""
        self.reload_app()
        # STATE starts with no data (or empty)
        self.drv.find_element(By.ID, 'btnClearData').click()
        time.sleep(0.3)
        self.drv.find_element(By.ID, 'btnValidateData').click()
        time.sleep(0.3)
        validated = self.js("return STATE.validated;")
        self.assertFalse(validated)

    # =================================================================
    # 8. DATA SUMMARY
    # =================================================================

    def test_17_data_summary_shown(self):
        """After validation, summary card appears with study count"""
        self._load_bcg_and_validate()
        card = self.drv.find_element(By.ID, 'dataSummaryCard')
        display = card.value_of_css_property('display')
        self.assertNotEqual(display, 'none')
        summary_text = self.drv.find_element(By.ID, 'dataSummary').text
        self.assertIn('13', summary_text)

    # =================================================================
    # 9. RUN REGRESSION VIA UI
    # =================================================================

    def test_18_run_regression_BCG(self):
        """Full workflow: load BCG, validate, run regression, check model stored"""
        self._load_bcg_validate_and_regress()
        has_model = self.js("return STATE.lastModel !== null;")
        self.assertTrue(has_model, "Model should be stored in STATE.lastModel")

    def test_19_regression_coefficients_visible(self):
        """Coefficient table card is displayed after regression"""
        self._load_bcg_validate_and_regress()
        card = self.drv.find_element(By.ID, 'coeffTableCard')
        self.assertEqual(card.value_of_css_property('display'), 'block')

    def test_20_regression_fit_stats_visible(self):
        """Fit statistics card is displayed after regression"""
        self._load_bcg_validate_and_regress()
        card = self.drv.find_element(By.ID, 'fitStatsCard')
        self.assertEqual(card.value_of_css_property('display'), 'block')
        text = self.drv.find_element(By.ID, 'fitStats').text
        self.assertIn('QM', text)
        self.assertIn('QE', text)
        self.assertIn('tau', text.lower())

    def test_21_regression_results_numeric(self):
        """Regression produces finite numeric results"""
        self._load_bcg_validate_and_regress()
        result = self.js("""
            var m = STATE.lastModel;
            return {
                n: m.n,
                p: m.p,
                tau2res: m.tau2res,
                R2: m.R2,
                QM: m.QM,
                coeffsLen: m.coeffs.length,
                interceptEst: m.coeffs[0].estimate,
                slopeEst: m.coeffs[1].estimate,
                slopeP: m.coeffs[1].pval,
                AIC: m.AIC,
                BIC: m.BIC
            };
        """)
        self.assertEqual(result['n'], 13)
        self.assertEqual(result['p'], 2)
        self.assertEqual(result['coeffsLen'], 2)
        self.assertTrue(math.isfinite(result['tau2res']))
        self.assertTrue(math.isfinite(result['R2']))
        self.assertTrue(math.isfinite(result['AIC']))
        self.assertTrue(math.isfinite(result['BIC']))
        # Latitude slope should be negative (higher latitude => more vaccine protection)
        self.assertLess(result['slopeEst'], 0, "Latitude slope should be negative")

    # =================================================================
    # 10. TAB NAVIGATION
    # =================================================================

    def test_22_tab_switching(self):
        """Clicking each tab activates the corresponding panel"""
        self.reload_app()
        tab_ids = ['tab-data', 'tab-regression', 'tab-viz', 'tab-compare', 'tab-report']
        panel_ids = ['panel-data', 'panel-regression', 'panel-viz', 'panel-compare', 'panel-report']
        for tab_id, panel_id in zip(tab_ids, panel_ids):
            self.drv.find_element(By.ID, tab_id).click()
            time.sleep(0.2)
            is_active = self.js(f"return document.getElementById('{panel_id}').classList.contains('active');")
            self.assertTrue(is_active, f"Panel {panel_id} should be active after clicking {tab_id}")

    # =================================================================
    # 11. DARK MODE
    # =================================================================

    def test_23_dark_mode_toggle(self):
        """Dark mode toggle adds/removes dark-mode class on body"""
        self.reload_app()
        initial = self.js("return document.body.classList.contains('dark-mode');")
        self.drv.find_element(By.ID, 'btnDarkMode').click()
        time.sleep(0.3)
        toggled = self.js("return document.body.classList.contains('dark-mode');")
        self.assertNotEqual(initial, toggled)
        self.drv.find_element(By.ID, 'btnDarkMode').click()
        time.sleep(0.3)
        restored = self.js("return document.body.classList.contains('dark-mode');")
        self.assertEqual(initial, restored)

    # =================================================================
    # 12. REPORT GENERATION
    # =================================================================

    def test_24_report_methods_text(self):
        """Report tab shows methods text with meta-regression mention"""
        self._load_bcg_validate_and_regress()
        self.drv.find_element(By.ID, 'tab-report').click()
        time.sleep(0.3)
        methods_text = self.drv.find_element(By.ID, 'methodsText').text
        self.assertIn('meta-regression', methods_text.lower())
        self.assertIn('tau', methods_text.lower())

    def test_25_report_R_code(self):
        """Report tab shows R code with library(metafor) and rma()"""
        self._load_bcg_validate_and_regress()
        self.drv.find_element(By.ID, 'tab-report').click()
        time.sleep(0.3)
        r_code = self.drv.find_element(By.ID, 'rCode').text
        self.assertIn('library(metafor)', r_code)
        self.assertIn('rma(', r_code)
        self.assertIn('latitude', r_code)

    # =================================================================
    # 13. CSV PARSING
    # =================================================================

    def test_26_csv_paste_parsing(self):
        """Paste CSV text, parse into STATE with auto-detected moderators"""
        self.reload_app()
        csv_text = "study,yi,se,dose\nStudy1,-0.5,0.2,100\nStudy2,-0.3,0.15,200\nStudy3,-0.7,0.25,150\nStudy4,-0.1,0.1,120"
        self.js("document.getElementById('csvPaste').value = arguments[0];", csv_text)
        self.drv.find_element(By.ID, 'btnParseCSV').click()
        time.sleep(0.5)
        count = self.js("return STATE.studies.length;")
        self.assertEqual(count, 4)
        mod_count = self.js("return STATE.moderators.length;")
        self.assertEqual(mod_count, 1)

    # =================================================================
    # 14. CLEAR DATA
    # =================================================================

    def test_27_clear_data(self):
        """Clear button empties studies array"""
        self.reload_app()
        self.drv.find_element(By.ID, 'btnLoadBCG').click()
        time.sleep(0.3)
        self.assertEqual(self.js("return STATE.studies.length;"), 13)
        self.drv.find_element(By.ID, 'btnClearData').click()
        time.sleep(0.3)
        self.assertEqual(self.js("return STATE.studies.length;"), 0)

    # =================================================================
    # 15. MODEL COMPARISON TAB
    # =================================================================

    def test_28_model_comparison_exercise(self):
        """Run all model comparisons on Exercise data, results container filled"""
        self.reload_app()
        self.drv.find_element(By.ID, 'btnLoadExercise').click()
        time.sleep(0.5)
        self.drv.find_element(By.ID, 'btnValidateData').click()
        time.sleep(0.5)
        self.drv.find_element(By.ID, 'tab-compare').click()
        time.sleep(0.3)
        self.drv.find_element(By.ID, 'btnRunComparison').click()
        time.sleep(3)
        content = self.drv.find_element(By.ID, 'comparisonTable').text
        self.assertTrue(len(content) > 0, "Comparison results should have content")

    # =================================================================
    # 16. REGRESSION DIAGNOSTICS
    # =================================================================

    def test_29_regression_diagnostics_present(self):
        """Model has fitted values, residuals, Cook's D, hat values"""
        self._load_bcg_validate_and_regress()
        result = self.js("""
            var m = STATE.lastModel;
            return {
                nFitted: m.fitted.length,
                nResid: m.residuals.length,
                nStudResid: m.studResiduals.length,
                nHat: m.hatValues.length,
                nCooksD: m.cooksD.length
            };
        """)
        self.assertEqual(result['nFitted'], 13)
        self.assertEqual(result['nResid'], 13)
        self.assertEqual(result['nStudResid'], 13)
        self.assertEqual(result['nHat'], 13)
        self.assertEqual(result['nCooksD'], 13)

    # =================================================================
    # 17. VISUALIZATION TAB
    # =================================================================

    def test_30_generate_bubble_plot(self):
        """Bubble plot generated for continuous moderator"""
        self._load_bcg_validate_and_regress()
        self.drv.find_element(By.ID, 'tab-viz').click()
        time.sleep(0.3)
        self.drv.find_element(By.ID, 'btnGenerateViz').click()
        time.sleep(1)
        container = self.drv.find_element(By.ID, 'bubblePlotContainer')
        display = container.value_of_css_property('display')
        self.assertNotEqual(display, 'none', "Bubble plot container should be visible")
        svg = container.get_attribute('innerHTML')
        self.assertIn('<svg', svg.lower(), "Should contain SVG element")

    # =================================================================
    # 18. R-SQUARED BOUNDS
    # =================================================================

    def test_31_R2_in_range(self):
        """R-squared is between 0 and 1"""
        self._load_bcg_validate_and_regress()
        r2 = self.js("return STATE.lastModel.R2;")
        self.assertGreaterEqual(r2, 0)
        self.assertLessEqual(r2, 1)

    # =================================================================
    # 19. KNAPP-HARTUNG CHECKBOX
    # =================================================================

    def test_32_knapp_hartung_checkbox(self):
        """KH checkbox toggles the adjustment in the model"""
        self._load_bcg_and_validate()
        self.drv.find_element(By.ID, 'tab-regression').click()
        time.sleep(0.3)
        kh_checkbox = self.drv.find_element(By.ID, 'chkKnappHartung')
        if not kh_checkbox.is_selected():
            kh_checkbox.click()
        self.drv.find_element(By.ID, 'btnRunRegression').click()
        time.sleep(1.5)
        kh_flag = self.js("return STATE.lastModel.knappHartung;")
        self.assertTrue(kh_flag)

    # =================================================================
    # 20. INITIAL RENDER
    # =================================================================

    def test_33_initial_page_loads(self):
        """Page title and header present"""
        self.reload_app()
        title = self.drv.title
        self.assertIn('MetaRegression', title)
        header = self.drv.find_element(By.CSS_SELECTOR, '.app-header h1')
        self.assertIn('MetaRegression', header.text)

    # =================================================================
    # 21. MODERATOR CONFIGURATION
    # =================================================================

    def test_34_moderator_config_change(self):
        """Changing moderator count updates the config grid"""
        self.reload_app()
        num_el = self.drv.find_element(By.ID, 'numModerators')
        num_el.clear()
        num_el.send_keys('3')
        self.drv.find_element(By.ID, 'btnSetModerators').click()
        time.sleep(0.3)
        mod_count = self.js("return STATE.moderators.length;")
        self.assertEqual(mod_count, 3)

    # =================================================================
    # 22. STATE PERSISTENCE CHECK
    # =================================================================

    def test_35_state_after_example_load(self):
        """STATE.validated is false after loading example (needs explicit validation)"""
        self.reload_app()
        self.drv.find_element(By.ID, 'btnLoadBCG').click()
        time.sleep(0.3)
        validated = self.js("return STATE.validated;")
        self.assertFalse(validated)

    # =================================================================
    # 23. EXERCISE DATA REGRESSION (MULTI-MODERATOR)
    # =================================================================

    def test_36_exercise_multi_moderator_regression(self):
        """Exercise data with 3 moderators (mixed types) runs without error"""
        self.reload_app()
        self.drv.find_element(By.ID, 'btnLoadExercise').click()
        time.sleep(0.5)
        self.drv.find_element(By.ID, 'btnValidateData').click()
        time.sleep(0.5)
        self.drv.find_element(By.ID, 'tab-regression').click()
        time.sleep(0.3)
        self.drv.find_element(By.ID, 'btnRunRegression').click()
        time.sleep(2)
        has_model = self.js("return STATE.lastModel !== null && !STATE.lastModel.error;")
        self.assertTrue(has_model, "Multi-moderator regression should succeed")
        n_coeffs = self.js("return STATE.lastModel.coeffs.length;")
        # intercept + dose + delivery:individual + duration = 4 coefficients
        self.assertGreaterEqual(n_coeffs, 4)

    # =================================================================
    # 24. MATRIX 3x3 INVERSE
    # =================================================================

    def test_37_matInverse_3x3(self):
        """3x3 matrix inverse roundtrip"""
        result = self.js("""
            var A = [[1,2,3],[0,1,4],[5,6,0]];
            var Ainv = window._test_matInverse(A);
            if (!Ainv) return false;
            var I = window._test_matMul(A, Ainv);
            var ok = true;
            for (var i = 0; i < 3; i++)
              for (var j = 0; j < 3; j++) {
                var expected = (i===j) ? 1 : 0;
                if (Math.abs(I[i][j] - expected) > 1e-8) ok = false;
              }
            return ok;
        """)
        self.assertTrue(result)

    # =================================================================
    # 25. ADD ROW
    # =================================================================

    def test_38_add_row_functionality(self):
        """Adding a row via button increases data grid rows"""
        self.reload_app()
        initial = self.js("return document.querySelectorAll('.dg-study').length;")
        self.js("document.getElementById('btnAddRow').click();")
        time.sleep(0.3)
        after = self.js("return document.querySelectorAll('.dg-study').length;")
        self.assertEqual(after, initial + 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
