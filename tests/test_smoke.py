import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_HTML = ROOT / "meta-regression.html"


def test_app_html_exists_and_names_tool():
    html_path = APP_HTML
    text = html_path.read_text(encoding="utf-8")

    assert html_path.exists()
    assert "Meta-Regression" in text or "Meta Regression" in text
    assert "moderator" in text.lower()


def test_e156_submission_page_exists():
    html_path = ROOT / "e156-submission" / "index.html"
    text = html_path.read_text(encoding="utf-8")

    assert html_path.exists()
    assert "E156" in text or "paper" in text.lower()


# --- Structural integrity of the single-file app (non-browser regressions) ---
# These guard against edits that silently break the standalone HTML: unbalanced
# <div> tags, a stray </script> inside a template literal, unfilled placeholder
# tokens, a UTF-8 BOM, or a hardcoded local path leaking into a shipped file.


def test_app_html_div_balance():
    text = APP_HTML.read_text(encoding="utf-8")
    opens = len(re.findall(r"<div[\s>]", text))
    closes = len(re.findall(r"</div>", text))
    assert opens == closes, f"div imbalance: {opens} open vs {closes} close"


def test_app_html_script_tag_balance():
    # No literal </script> orphaned inside a template literal: every closing tag
    # must pair with an opening <script ...> tag.
    text = APP_HTML.read_text(encoding="utf-8")
    opens = len(re.findall(r"<script", text))
    closes = len(re.findall(r"</script>", text))
    assert opens == closes, f"script tag imbalance: {opens} open vs {closes} close"


def test_app_html_no_unfilled_placeholders():
    text = APP_HTML.read_text(encoding="utf-8")
    for token in ("{{", "REPLACE_ME", "__PLACEHOLDER__"):
        assert token not in text, f"unfilled placeholder token present: {token!r}"


def test_app_html_no_bom():
    raw = APP_HTML.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf"), "shipped HTML must not start with a UTF-8 BOM"


def test_app_html_no_hardcoded_local_paths():
    text = APP_HTML.read_text(encoding="utf-8")
    for pattern in (r"C:\\Users", r"file:///", r"/home/", r"F:\\Models"):
        assert not re.search(pattern, text), f"hardcoded local path present: {pattern}"
