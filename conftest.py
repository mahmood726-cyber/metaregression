import os


if not os.environ.get("RUN_BROWSER_TESTS"):
    collect_ignore_glob = [
        "tests/test_metaregression.py",
    ]
