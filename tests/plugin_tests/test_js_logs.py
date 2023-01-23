import json
from os import getcwd, path, curdir, makedirs, listdir
from shutil import rmtree
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
    clean_up_report_directories(frequency)

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

    # read report file (to get all js log files in ordered)
    with open(actual_file) as f:
        output = json.load(f)

    if not output:
        assert False, "Test was not run successfully or file not found!"

    actual_files = []
    actual_report_dir = f"{current_dir}/{frequency}/"
    # collect js_logs in steps (output > steps > attachments)
    for step in output["steps"]:
        actual_files.extend(collect_js_logs(step, actual_report_dir))
    # collect js_logs in attachment (output > attachments)
    actual_files.extend(collect_js_logs(output, actual_report_dir))

    data_path_prefix = f"{current_dir}/data/js_logs/{frequency}"
    expected_files = [
        path.join(data_path_prefix, f)
        for f in listdir(data_path_prefix)
        if path.isfile(path.join(data_path_prefix, f))
    ]
    expected_files = sorted(expected_files, key=lambda x: path.basename(x))

    # compare number of js files
    assert len(actual_files) == len(
        expected_files
    ), "number of js output files are different"

    # compare file content
    for i in range(len(expected_files)):
        logger.error(actual_files[i])
        logger.error(expected_files[i])
        with open(actual_files[i]) as act:
            actual_file_content = "".join(act.readlines())
        with open(expected_files[i]) as exp:
            expected_file_content = exp.readlines()
        for item in expected_file_content:
            assert (
                item.rstrip("\n") in actual_file_content
            ), "console logs are not matching."


def clean_up_report_directories(report_dir):
    if path.exists(path.join(curdir, report_dir)):
        rmtree(path.join(curdir, report_dir))
    makedirs(path.join(curdir, report_dir), exist_ok=True)


def collect_js_logs(source, path_prefix):
    output = []
    if source.get("attachments"):
        for attachment in source["attachments"]:
            if "Logs from browser console" in attachment.get("name"):
                output.append(f"{path_prefix}/" + attachment.get("source"))
    return output
