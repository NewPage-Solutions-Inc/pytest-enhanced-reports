import cv2
import numpy as np
import json
import pytest
from os import getcwd
from subprocess import Popen
from tests.step_defs.shared_steps import *  # noqa
from tests.util import util
import logging

logger = logging.getLogger(__name__)

SCREENSHOT_FREQUENCY = [
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


@pytest.mark.parametrize("frequency", SCREENSHOT_FREQUENCY)
def test_js_logs(frequency):
    logger.info("Clean up folder ")
    util.clean_up_report_directories(frequency)

    logger.info(
        f"Start running NORMAL tests: screenshot_frequency={frequency}..."
    )
    test_process = Popen(
        RUN_NORMAL_TESTS.format(frequency, frequency), shell=True
    )
    test_process.wait(TIMEOUT)

    logger.info(
        f"Start running PLUGIN tests: screenshot_frequency={frequency}..."
    )
    verify_screenshot(frequency)


def verify_screenshot(frequency):
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
    actual_files = {}
    file_path = f"{curr_dir}/{actual_file_dir}/"
    # Get screenshot attachments from the report attachment
    attachments = [
        attachment
        for step in output["steps"]
        if step.get("attachments")
        for attachment in step.get("attachments")
        if "Screenshot" in attachment.get("name")
    ]
    # Replace space with underscores of a source name for the comparison
    for attachment in attachments:
        if "Screenshot Navigation" in attachment.get("name"):
            actual_files["screenshot_navigation"] = file_path + attachment.get(
                "source"
            )
        else:
            key_name = attachment.get("name").replace(" ", "_")
            actual_files[key_name] = file_path + attachment.get("source")

    # Iterate and compare the reports image with expected image
    for image_name, image_path in actual_files.items():
        actual_image = cv2.imread(image_path)

        expected_image = cv2.imread(
            f"{curr_dir}/data/screenshots/{image_name}" + ".png"
        )
        height, width, e = actual_image.shape
        if actual_image.shape == expected_image.shape:
            # Get the difference between the two images and returns an arrays with 0,1 and 2
            # Mean Square Error (MSE) of the pixel values of the two images.
            # Similar images will have less mean square error value.
            # Using this method, we can compare two images having the same height, width and number of channels.
            difference = cv2.subtract(actual_image, expected_image)
            err = np.sum(difference**2)
            mse = err / (height * width)
            assert mse == 0.0 or mse <= 0.1
