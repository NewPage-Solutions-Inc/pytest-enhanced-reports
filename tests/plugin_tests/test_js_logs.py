import json
from os import getcwd
from subprocess import Popen
import pytest
import logging
from tests.step_defs.shared_steps import *  # noqa
from tests.util import util

logger = logging.getLogger(__name__)

JS_LOG_FREQUENCY = [
    "always",
    "each_ui_operation",
    "end_of_each_test",
    "failed_test_only",
    "never",
]

TIMEOUT = 120  # 120 seconds timeout for running normal tests

RUN_NORMAL_TESTS = "pytest -vv --disable-warnings \
--headless=True \
--alluredir='{0}' \
--report_browser_console_log_capture='{1}' \
normal_tests"

RUN_PLUGIN_TESTS = "pytest -vv --disable-warnings \
--headless=True \
--report_browser_console_log_capture='{0}' \
plugin_tests"


@pytest.mark.parametrize("frequency", JS_LOG_FREQUENCY)
def test_js_logs(frequency):
    logger.info("Clean up folder ")
    util.clean_up_report_directories(frequency)

    logger.info(f"Start running NORMAL tests: js_log_frequency={frequency}...")
    test_process = Popen(
        RUN_NORMAL_TESTS.format(frequency, frequency), shell=True
    )
    test_process.wait(TIMEOUT)

    logger.info(f"Start running PLUGIN tests: js_log_frequency={frequency}...")
    verify_js_logs(frequency)


def verify_js_logs(js_log_frequency):
    actual_report_dir = js_log_frequency
    curr_dir = getcwd()
    if js_log_frequency == "never":
        actual_txt_files = util.count_file_match(".txt", actual_report_dir)
        assert (
            actual_txt_files == 0
        ), "there are some txt files inside the report folder while js log frequency = never"
    elif js_log_frequency in ["always", "end_of_each_test"]:
        verify_js_logs_with_params(
            curr_dir, actual_report_dir, "Run Test for browser's outputs"
        )
    elif js_log_frequency in ["failed_test_only", "each_ui_operation"]:
        verify_js_logs_with_params(
            curr_dir, actual_report_dir, "Failed test only"
        )


def verify_js_logs_with_params(current_dir, frequency, scenario):
    actual_file = util.find_newest_report(scenario, frequency)

    # for a_file in list_of_files:
    with open(actual_file) as f:
        output = json.load(f)

    if not output:
        assert False, "Test was not run successfully or file not found!"

    actual_files = []
    # collect js_logs in steps
    for step in output["steps"]:
        if step.get("attachments"):
            for attachment in step.get("attachments"):
                if "Logs from browser console" in attachment.get("name"):
                    actual_files.append(
                        f"{current_dir}/{frequency}/" + attachment.get("source")
                    )

    expected_files = []
    data_path_prefix = f"{current_dir}/data/js_logs/{frequency}"
    if frequency == "always":
        expected_files.append(f"{data_path_prefix}/first_attachment.txt")
        expected_files.append(f"{data_path_prefix}/second_attachment.txt")
    elif frequency in ["failed_test_only", "end_of_each_test"]:
        expected_files.append(f"{data_path_prefix}/attachment.txt")

        # collect js_logs in attachment
        if frequency in ["failed_test_only", "end_of_each_test"]:
            for attachment in output["attachments"]:
                if "Logs from browser console" in attachment.get("name"):
                    actual_files.append(
                        f"{current_dir}/{frequency}/" + attachment.get("source")
                    )
    else:
        # each_ui_operation
        for i in range(1, 7):
            expected_files.append(f"{data_path_prefix}/{i}-attachment.txt")

    assert len(actual_files) == len(
        expected_files
    ), "number of js output files are different"
    for i in range(len(expected_files)):
        with open(actual_files[i]) as act:
            actual_file_content = "".join(act.readlines())
        with open(expected_files[i]) as exp:
            expected_file_content = exp.readlines()
        for item in expected_file_content:
            assert (
                item.rstrip("\n") in actual_file_content
            ), "console logs are not matching."
