from os import getcwd, path, walk
from subprocess import Popen
import pytest
import logging
from tests.util import util
from glob import glob


logger = logging.getLogger(__name__)

TIMEOUT = 120  # 120 seconds timeout for running normal tests

RUN_NORMAL_TESTS = "pytest -vv --disable-warnings \
--headless=True \
--alluredir='{0}' \
--report_screenshot_capture='each_ui_operation' \
--report_video_recording=True \
--report_keep_screenshots='{1}' \
--report_keep_videos='{2}' \
--report_screenshot_dir='{0}/screenshot' \
--report_video_dir='{0}/video' \
normal_tests"


@pytest.mark.parametrize(
    "keep_screenshots, keep_videos",
    [(True, True), (True, False), (False, True), (False, False)],
)
def test_keep_files(keep_screenshots, keep_videos):
    report_dir = f"keep_files_{keep_screenshots}_{keep_videos}"
    logger.info("Clean up folder")
    util.clean_up_report_directories(report_dir)

    logger.info(
        f"Start running NORMAL tests: keep_screenshots={keep_screenshots}, keep_videos={keep_videos}..."
    )
    test_process = Popen(
        RUN_NORMAL_TESTS.format(report_dir, keep_screenshots, keep_videos),
        shell=True,
    )
    test_process.wait(TIMEOUT)

    logger.info(
        f"Start running PLUGIN tests: keep_screenshots={keep_screenshots}, keep_videos={keep_videos}..."
    )
    scenarios = ["Run Test for browser's outputs", "Failed test only"]
    verify_keep_files_screenshots(keep_screenshots, scenarios, report_dir)
    verify_keep_files_videos(keep_videos, scenarios, report_dir)


def verify_keep_files_screenshots(
    keep_screenshots, scenarios, report_dir="keep_files"
):
    curr_dir = getcwd()
    observe_files = len(
        [
            y
            for x in walk(path.join(curr_dir, report_dir))
            for y in glob(path.join(x[0], "*.png"))
        ]
    )

    # collect all png files in report dir
    files_in_json = 0
    for scenario in scenarios:
        files_in_json += len(
            util.collect_files_in_report_json(
                curr_dir, report_dir, scenario, "Screenshot"
            )
        )

    if keep_screenshots:
        assert (
            files_in_json < observe_files
        ), f"Total screenshot files in report json {files_in_json} are LESS than in report dir {observe_files} while keep_screenshots set to True"
    else:
        assert (
            observe_files == files_in_json
        ), f"Total screenshot files in report json {files_in_json} are NOT EQUAL with files in report directory {observe_files} while keep_screenshot set to False"


def verify_keep_files_videos(keep_videos, scenarios, report_dir="keep_files"):
    curr_dir = getcwd()
    observe_files = len(
        [
            y
            for x in walk(path.join(curr_dir, report_dir))
            for y in glob(path.join(x[0], "*.webm"))
        ]
    )
    files_in_json = 0
    for scenario in scenarios:
        files_in_json += len(
            util.collect_files_in_report_json(
                curr_dir, report_dir, scenario, "Video"
            )
        )
    assert (
        files_in_json > 0
    ), f"Video feature is not working while keep_videos set to {keep_videos}"

    assert (
        observe_files == files_in_json
    ), f"Total video files in report json {files_in_json} are NOT EQUAL in report dir {observe_files} while keep_video = {keep_videos}"
