import pytest
from subprocess import Popen
import os
import shutil

TIMEOUT = 120  # 120 seconds timeout for running normal tests


def clean_up_report_directories(report_dir):
    if os.path.exists(os.path.join(os.curdir, report_dir)):
        shutil.rmtree(os.path.join(os.curdir, report_dir))
    os.makedirs(os.path.join(os.curdir, report_dir), exist_ok=True)


RUN_NORMAL_TESTS = "pytest -vv --disable-warnings \
--headless=True \
--alluredir='{0}' \
--report_browser_console_log_capture='{1}' \
normal_tests"

RUN_PLUGIN_TESTS = "pytest -vv --disable-warnings \
--headless=True \
--report_browser_console_log_capture='{0}' \
plugin_tests"

JS_LOG_FREQUENCY = [
    # "always",
    # "each_ui_operation",
    # "end_of_each_test",
    # "failed_test_only",
    "never",
]

# run normal tests with different frequency
normal_tests_processes = []
for a_frequency in JS_LOG_FREQUENCY:
    print(f"Start running NORMAL tests: js_log_frequency={a_frequency}...")
    clean_up_report_directories(a_frequency)
    normal_tests_processes.append(
        Popen(RUN_NORMAL_TESTS.format(a_frequency, a_frequency), shell=True)
    )


# check if processes is finished
for a_process in normal_tests_processes:
    a_process.wait(TIMEOUT)


plugin_tests_processes = []
# run plugin tests
for a_frequency in JS_LOG_FREQUENCY:
    print(f"Start running PLUGIN tests: js_log_frequency={a_frequency}...")
    plugin_tests_processes.append(
        Popen(RUN_PLUGIN_TESTS.format(a_frequency), shell=True)
    )


[a_process.wait(TIMEOUT) for a_process in plugin_tests_processes]
