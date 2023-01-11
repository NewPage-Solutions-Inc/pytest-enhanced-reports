import cv2
import numpy as np
from pytest_bdd import scenario
import json
import pytest
from os import getcwd

from .shared_steps import *  # noqa
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
    attachments = [
        attachment
        for step in output["steps"]
        if step.get("attachments")
        for attachment in step.get("attachments")
        if "Screenshot" in attachment.get("name")
    ]
    for attachment in attachments:
        if "Screenshot Navigation" in attachment.get("name"):
            actual_files["screenshot_navigation"] = file_path + attachment.get(
                "source"
            )
        else:
            key_name = attachment.get("name").replace(" ", "_")
            actual_files[key_name] = file_path + attachment.get("source")
    for key, path in actual_files.items():
        actual_image = cv2.imread(path)
        h, w, e = actual_image.shape
        expected_image = cv2.imread(
            f"{curr_dir}/data/screenshots/{key}" + ".png"
        )
        if actual_image.shape == expected_image.shape:
            difference = cv2.subtract(actual_image, expected_image)
            err = np.sum(difference**2)
            mse = err / (h * w)
            assert mse == 0.0 or mse <= 0.1
