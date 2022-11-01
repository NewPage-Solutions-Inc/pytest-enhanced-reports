import logging
from pytest_bdd import scenarios, given, when, then, parsers
import json

logger = logging.getLogger(__name__)

scenarios("../features/plugin_functionalities.feature")


@then("Test Browser output functionality")
def check_browser_output():
    actual_file_dir = "reports/"
    with open(f"{actual_file_dir}allure-output.json", "r") as f:
        output = json.load(f)

    if not output:
        assert False, "Test was not run successfully or file not found!"

    actual_files = []

    for step in output["steps"]:
        if step.get("attachments"):
            actual_files.append(
                actual_file_dir + step.get("attachments")[0].get("source")
            )

    expected_files = [
        "tests/data/first_attachment.txt",
        "tests/data/second_attachment.txt",
    ]
    assert len(actual_files) == len(
        expected_files
    ), "number of js output files are different"
    for i in range(len(expected_files)):
        with open(actual_files[i], "r") as act:
            actual_file_content = "".join(act.readlines())
        with open(expected_files[i], "r") as exp:
            expected_file_content = exp.readlines()
        for item in expected_file_content:
            assert (
                item.rstrip("\n") in actual_file_content
            ), "console logs are not matching."
