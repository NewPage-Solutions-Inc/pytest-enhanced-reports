import pytest
import subprocess
import os
import shutil

# clean up folders and recreate them
report_folders = ["reports"]
print(os.path.exists(os.path.join(os.curdir, "reports")))
for item in report_folders:
    if os.path.exists(os.path.join(os.curdir, item)):
        shutil.rmtree(os.path.join(os.curdir, item))
    os.makedirs(os.path.join(os.curdir, item), exist_ok=True)


RUN_ARGS = [
    "-vv",
    "--disable-warnings",
    "--headless=False",
    "--report_browser_console_log_capture=always",
    "--alluredir='reports'",
]

FREQUENCY = ["always", "never"]

# run tests in normal_tests folder
pytest.main(RUN_ARGS.append("normal_tests/"))
