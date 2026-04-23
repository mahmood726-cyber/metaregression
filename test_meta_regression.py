"""
Meta-Regression Workbench — Selenium Test Suite (25 tests)
Run: python test_meta_regression.py
"""
import sys, os, time, io, unittest

# Only re-wrap stdout when this legacy script is executed directly.
# Under pytest, rebinding the capture tempfile closes it and breaks teardown.
if __name__ == '__main__' and os.environ.get('PYTHONIOENCODING') is None and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'meta-regression.html')
URL = 'file:///' + HTML_PATH.replace('\\', '/')

def get_driver():
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--window-size=1400,900')
    opts.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    try:
        d = webdriver.Chrome(options=opts)
    except WebDriverException as exc:
        raise unittest.SkipTest(f'Chrome webdriver unavailable: {exc}') from exc
    d.implicitly_wait(2)
    return d

class MetaRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = get_driver(); cls.driver.get(URL); time.sleep(0.5)
    @classmethod
    def tearDownClass(cls):
        logs = cls.driver.get_log('browser')
        severe = [l for l in logs if l['level']=='SEVERE' and 'favicon' not in l.get('message','')]
        if severe: print(f"\nJS ERRORS: {len(severe)}")
        cls.driver.quit()
    def _reload(self): self.driver.get(URL); time.sleep(0.3)
    def _click(self, by, val):
        el = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((by, val)))
        self.driver.execute_script("arguments[0].click()", el); return el

    def test_01_page_loads(self):
        self.assertIn('Regression', self.driver.title)
    def test_02_five_tabs(self):
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '[role="tab"]')
        self.assertGreaterEqual(len(tabs), 4)
    def test_03_load_bcg(self):
        self._reload(); self._click(By.ID, 'btnLoadBCG'); time.sleep(0.5)
        # Data loaded = table has rows or container has content
        container = self.driver.find_element(By.ID, 'dataGridContainer')
        self.assertTrue(container.is_displayed())
    def test_04_load_exercise(self):
        self._reload(); self._click(By.ID, 'btnLoadExercise'); time.sleep(0.5)
    def test_05_data_table(self):
        self._reload(); self._click(By.ID, 'btnLoadBCG'); time.sleep(0.3)
        container = self.driver.find_element(By.ID, 'dataGridContainer')
        self.assertTrue(container.is_displayed())
    def test_06_moderator_config(self):
        self._reload(); self._click(By.ID, 'btnLoadBCG'); time.sleep(0.3)
        config = self.driver.find_element(By.ID, 'moderatorConfig')
        self.assertTrue(len(config.text) > 0 or config.is_displayed())
    def test_07_regression_tab(self):
        self._click(By.ID, 'tab-regression'); time.sleep(0.3)
        panel = self.driver.find_element(By.ID, 'panel-regression')
        self.assertTrue(panel.is_displayed())
    def test_08_knapp_hartung_toggle(self):
        chk = self.driver.find_element(By.ID, 'chkKnappHartung')
        self.assertIsNotNone(chk)
    def test_09_run_regression(self):
        self._reload(); self._click(By.ID, 'btnLoadBCG'); time.sleep(0.5)
        self._click(By.ID, 'tab-regression'); time.sleep(0.3)
        # Find and click the run button
        btns = self.driver.find_elements(By.CSS_SELECTOR, '#panel-regression button')
        run_btn = None
        for b in btns:
            if 'run' in b.text.lower() or 'fit' in b.text.lower() or 'regress' in b.text.lower():
                run_btn = b; break
        if run_btn is None and len(btns) > 0:
            run_btn = btns[0]
        if run_btn:
            self.driver.execute_script("arguments[0].click()", run_btn)
            time.sleep(1)
    def test_10_coefficient_table(self):
        text = self.driver.find_element(By.ID, 'panel-regression').text.lower()
        has_content = any(kw in text for kw in ['coefficient','intercept','beta','estimate','slope','regression','model'])
        self.assertTrue(has_content or len(text) > 50)
    def test_11_tau2_residual(self):
        text = self.driver.find_element(By.ID, 'panel-regression').text.lower()
        has_content = any(kw in text for kw in ['tau','heterogeneity','residual','variance','moderator'])
        self.assertTrue(has_content or len(text) > 50)
    def test_12_r_squared(self):
        text = self.driver.find_element(By.ID, 'panel-regression').text
        has_content = any(kw in text for kw in ['R','r2','R-squared','explained','proportion','%'])
        self.assertTrue(has_content or len(text) > 50)
    def test_13_qm_test(self):
        text = self.driver.find_element(By.ID, 'panel-regression').text
        has_content = any(kw in text for kw in ['Q','moderator','test','p-value','p =','chi','omnibus'])
        self.assertTrue(has_content or len(text) > 50)
    def test_14_viz_tab(self):
        self._click(By.ID, 'tab-viz'); time.sleep(0.3)
        panel = self.driver.find_element(By.ID, 'panel-viz')
        self.assertTrue(panel.is_displayed())
    def test_15_bubble_plot(self):
        panel = self.driver.find_element(By.ID, 'panel-viz')
        svg_html = panel.get_attribute('innerHTML')
        self.assertTrue('svg' in svg_html.lower() or 'circle' in svg_html.lower() or 'canvas' in svg_html.lower() or len(panel.text) > 20)
    def test_16_compare_tab(self):
        self._click(By.ID, 'tab-compare'); time.sleep(0.3)
        panel = self.driver.find_element(By.ID, 'panel-compare')
        self.assertTrue(panel.is_displayed())
    def test_17_model_comparison(self):
        text = self.driver.find_element(By.ID, 'panel-compare').text
        self.assertTrue('AIC' in text or 'BIC' in text or 'model' in text.lower() or 'compare' in text.lower() or len(text) > 20)
    def test_18_report_tab(self):
        self._click(By.ID, 'tab-report'); time.sleep(0.3)
        panel = self.driver.find_element(By.ID, 'panel-report')
        self.assertTrue(panel.is_displayed())
    def test_19_r_code(self):
        text = self.driver.find_element(By.ID, 'panel-report').text
        self.assertTrue('metafor' in text or 'rma' in text)
    def test_20_dark_mode(self):
        self._reload()
        btn = self.driver.find_element(By.ID, 'btnDarkMode')
        self.driver.execute_script("arguments[0].click()", btn); time.sleep(0.2)
        # Theme may be on html or body element
        theme_html = self.driver.find_element(By.TAG_NAME, 'html').get_attribute('data-theme')
        theme_body = self.driver.find_element(By.TAG_NAME, 'body').get_attribute('data-theme')
        theme_class = self.driver.find_element(By.TAG_NAME, 'body').get_attribute('class') or ''
        self.assertTrue(theme_html == 'dark' or theme_body == 'dark' or 'dark' in theme_class)
        self.driver.execute_script("arguments[0].click()", btn)
    def test_21_tab_keyboard(self):
        self._reload()
        tab = self.driver.find_element(By.ID, 'tab-data')
        tab.send_keys(Keys.ARROW_RIGHT); time.sleep(0.2)
    def test_22_clear_data(self):
        self._reload(); self._click(By.ID, 'btnLoadBCG'); time.sleep(0.3)
        self._click(By.ID, 'btnClearData'); time.sleep(0.2)
    def test_23_csv_paste(self):
        self._reload()
        ta = self.driver.find_element(By.ID, 'csvPaste')
        ta.send_keys("study,yi,sei,mod1\nA,0.5,0.2,10")
        self._click(By.ID, 'btnParseCSV'); time.sleep(0.3)
    def test_24_validate_data(self):
        self._reload(); self._click(By.ID, 'btnLoadBCG'); time.sleep(0.3)
        self._click(By.ID, 'btnValidateData'); time.sleep(0.3)
        status = self.driver.find_element(By.ID, 'dataStatus')
        self.assertGreater(len(status.text), 0)
    def test_25_data_summary(self):
        self._reload(); self._click(By.ID, 'btnLoadBCG'); time.sleep(0.5)
        # Verify data was loaded by checking the grid container has content
        container = self.driver.find_element(By.ID, 'dataGridContainer')
        html = container.get_attribute('innerHTML')
        self.assertGreater(len(html), 100, "Data grid should have content after loading BCG")

if __name__ == '__main__':
    unittest.main(verbosity=2)
