import json
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
--alluredir='{}' \
--report_screenshot_capture='each_ui_operation' \
--report_video_recording=True \
--report_keep_screenshots='{}' \
--report_keep_videos='{}' \
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

    if keep_screenshots:
        # collect all png files in report dir
        files_in_json = 0
        for scenario in scenarios:
            files_in_json += len(
                util.collect_files_in_report_json(
                    curr_dir, report_dir, scenario, "Screenshot"
                )
            )
        assert (
            files_in_json == observe_files
        ), f"Total screenshot files in report json {files_in_json} are different than in report dir {observe_files}"
        assert (
            files_in_json > 0
        ), "There is no screenshot files in the report dir while screenshot flag is on"
    else:
        assert (
            observe_files == 0
        ), f"There are {observe_files} screenshots in the report folder while keep_screenshot set to False"


def verify_keep_files_videos(keep_videos, scenarios, report_dir="keep_files"):
    curr_dir = getcwd()
    observe_files = len(
        [
            y
            for x in walk(path.join(curr_dir, report_dir))
            for y in glob(path.join(x[0], "*.webm"))
        ]
    )

    if keep_videos:
        files_in_json = 0
        for scenario in scenarios:
            files_in_json += len(
                util.collect_files_in_report_json(
                    curr_dir, report_dir, scenario, "Video"
                )
            )
        assert (
            files_in_json == observe_files
        ), f"Total video files in report json {files_in_json} are different than in report dir {observe_files}"
        assert (
            files_in_json > 0
        ), "There is no video files in the report dir while video flag is on"
    else:
        assert (
            observe_files == 0
        ), f"There are {observe_files} videos in the report folder while keep_video set to False"
