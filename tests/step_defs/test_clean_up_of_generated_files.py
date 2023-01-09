from pytest_bdd import scenario
import pytest
from .shared_steps import *  # noqa
from tests.util import util


@scenario("../features/test_site.feature", "Run Test for clean up file")
def test_run_test_for_clean_up_files(driver):
    pass


@pytest.mark.order(after="test_run_test_for_clean_up_files")
def test_clean_up_files(keep_files_mode):
    keep_screenshots, keep_videos = keep_files_mode

    if keep_screenshots:
        assert (
            util.check_file_exist_with_extension()
        ), "no screenshots found in the reports directory!"
    else:
        assert (
            not util.check_file_exist_with_extension()
        ), "screenshots found in the reports directory"

    video_extension = ".webm"
    if keep_videos:
        assert util.check_file_exist_with_extension(
            video_extension
        ), "no videos found in the reports directory!"
    else:
        assert util.check_file_exist_with_extension(
            video_extension
        ), "videos found in the reports directory!"


@pytest.fixture
def keep_files_mode(request):
    """return 2 vars:
    keep screenshots: True/False
    keep videos: True/False
    """
    prefix = "report_"
    screenshot_enable = (
        request.config.getoption(f"--{prefix}screenshot_capture") != "never"
    )
    video_enable = (
        request.config.getoption(f"--{prefix}video_recording") == "True"
    )
    keep_screenshots = (
        request.config.getoption(f"--{prefix}keep_screenshots") == "True"
    )
    keep_videos = request.config.getoption(f"--{prefix}keep_videos") == "True"
    return screenshot_enable and keep_screenshots, video_enable and keep_videos
