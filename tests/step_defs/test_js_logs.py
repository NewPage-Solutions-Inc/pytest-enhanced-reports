from pytest_bdd import scenario
import json
import pytest
from os import getcwd

from .shared_steps import * # noqa
from tests.util import util


@scenario("../features/test_site.feature", "Run Test for browser's outputs")
def test_run_js_logs(driver):
    pass


@pytest.mark.order(after="test_run_js_logs")
def test_verify_js_logs():
    actual_file_dir = "reports"
    actual_file = util.find_newest_report(
        "Run Test for browser's outputs", actual_file_dir
    )

    # for a_file in list_of_files:
    with open(actual_file) as f:
        output = json.load(f)

    if not output:
        assert False, "Test was not run successfully or file not found!"

    curr_dir = getcwd()
    actual_files = []
    for step in output["steps"]:
        if step.get("attachments"):
            for attachment in step.get("attachments"):
                if attachment.get("name") == "Browser Outputs":
                    actual_files.append(
                        f"{curr_dir}/{actual_file_dir}/"
                        + attachment.get("source")
                    )
    expected_files = [
        f"{curr_dir}/tests/data/first_attachment.txt",
        f"{curr_dir}/tests/data/second_attachment.txt",
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
