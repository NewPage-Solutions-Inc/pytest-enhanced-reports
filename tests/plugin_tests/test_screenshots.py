import cv2
import numpy as np
from pytest_bdd import scenario
import json
import pytest
from os import getcwd

from tests.step_defs.shared_steps import *  # noqa
from tests.util import util


@scenario("../features/test_site.feature", "Run Test for browser's outputs")
def test_run_ss(driver):
    pass


@pytest.mark.order(after="test_run_ss")
def test_verify_ss():
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
