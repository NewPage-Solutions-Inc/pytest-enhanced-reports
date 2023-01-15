import json
from os import getcwd

import pytest

from tests.step_defs.shared_steps import *  # noqa
from tests.util import util


def test_verify_js_logs(js_log_frequency):
    curr_dir = getcwd()

    # get current js log frequency
    frequency = js_log_frequency
    actual_file_dir = frequency
    actual_file = util.find_newest_report(
        "Run Test for browser's outputs", actual_file_dir
    )
    if frequency == "never":
        actual_txt_files = util.count_file_match(".txt", frequency)
        assert (
            actual_txt_files == 0
        ), "there are some txt files inside the report folder while js log frequency = never"
    else:
        # for a_file in list_of_files:
        with open(actual_file) as f:
            output = json.load(f)

        if not output:
            assert False, "Test was not run successfully or file not found!"

        actual_files = []
        for step in output["steps"]:
            if step.get("attachments"):
                for attachment in step.get("attachments"):
                    if "Logs from browser console" in attachment.get("name"):
                        actual_files.append(
                            f"{curr_dir}/{actual_file_dir}/"
                            + attachment.get("source")
                        )
        expected_files = [
            f"{curr_dir}/data/first_attachment.txt",
            f"{curr_dir}/data/second_attachment.txt",
        ]
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


@pytest.fixture
def js_log_frequency(request):
    return request.config.getoption("--report_browser_console_log_capture")
