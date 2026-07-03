"""Run the metafor cross-validation benchmark as part of the test suite.

The benchmark (benchmark/benchmark.js) extracts the shipped meta-regression
engine straight out of meta-regression.html and checks its output against
reference values from R's metafor package (see benchmark/metafor_reference.R).
It needs Node.js; if Node is unavailable the test skips rather than failing so
the pure-Python smoke suite still runs on a bare box.
"""
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BENCH_DIR = ROOT / "benchmark"
BENCH_JS = BENCH_DIR / "benchmark.js"
EXTRACT_JS = BENCH_DIR / "extract_core.js"


def _node():
    return shutil.which("node")


def test_benchmark_files_present():
    assert BENCH_JS.exists(), "benchmark/benchmark.js missing"
    assert EXTRACT_JS.exists(), "benchmark/extract_core.js missing"
    assert (BENCH_DIR / "metafor_reference.R").exists(), "R reference script missing"


@pytest.mark.skipif(_node() is None, reason="node not available")
def test_core_extraction_loads():
    """The math core must still be extractable from the shipped HTML."""
    proc = subprocess.run(
        [_node(), str(EXTRACT_JS)],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "all callable: true" in proc.stdout


@pytest.mark.skipif(_node() is None, reason="node not available")
def test_metafor_benchmark_passes():
    """Shipped JS engine must match metafor references within tolerance."""
    proc = subprocess.run(
        [_node(), str(BENCH_JS)],
        capture_output=True, text=True, timeout=120,
    )
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, out
    assert "All checks passed." in proc.stdout
    # Guard against a silently empty run.
    assert "18/18 checks within tol" in proc.stdout, out
