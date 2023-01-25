import json
from os import getcwd, path, listdir, walk
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
    "keep_screenshot, keep_video",
    [(True, True), (True, False), (False, True), (False, False)],
)
def test_keep_files(keep_screenshot, keep_video):
    report_dir = "keep_files"
    logger.info("Clean up folder")
    util.clean_up_report_directories(report_dir)

    logger.info(
        f"Start running NORMAL tests: keep_screenshot={keep_screenshot}, keep_video={keep_video}..."
    )
    test_process = Popen(
        RUN_NORMAL_TESTS.format(report_dir, keep_screenshot, keep_video),
        shell=True,
    )
    test_process.wait(TIMEOUT)

    logger.info(
        f"Start running PLUGIN tests: keep_screenshot={keep_screenshot}, keep_video={keep_video}..."
    )
    verify_keep_files(keep_screenshot, keep_video, report_dir)


def verify_keep_files(keep_screenshot, keep_video, report_dir="keep_files"):
    curr_dir = getcwd()
    scenarios = ["Run Test for browser's outputs", "Failed test only"]
    actual_screenshot_files = util.count_file_match(".png", report_dir)
    actual_video_files = util.count_file_match(".png", report_dir)
    # screenshot
    if keep_screenshot:
        # collect all png files in report dir
        observe_files = len(
            [
                y
                for x in walk(path.join(curr_dir, report_dir))
                for y in glob(path.join(x[0], "*.png"))
            ]
        )
        files_in_json = 0
        for scenario in scenarios:
            files_in_json += collect_files_in_report_json(
                curr_dir, report_dir, scenario, "Screenshot"
            )
        assert (
            files_in_json == observe_files
        ), f"Total screenshot files in report json {files_in_json} are different than in report dir {observe_files}"
    else:
        assert (
            actual_screenshot_files == 0
        ), f"There are {actual_screenshot_files} screenshots in the report folder while keep_screenshot set to False"
    # video
    if keep_video:
        observe_files = len(
            [
                y
                for x in walk(path.join(curr_dir, report_dir))
                for y in glob(path.join(x[0], "*.webm"))
            ]
        )
        files_in_json = 0
        for scenario in scenarios:
            files_in_json += collect_files_in_report_json(
                curr_dir, report_dir, scenario, "Video"
            )
        assert (
            files_in_json == observe_files
        ), f"Total video files in report json {files_in_json} are different than in report dir {observe_files}"
    else:
        assert (
            actual_video_files == 0
        ), f"There are {actual_video_files} videos in the report folder while keep_video set to False"


def collect_files_in_report_json(current_dir, report_dir, scenario, file_type):
    """Collect files in the report json file
    file_tpe: Screenshot/Video
    """
    report_file = util.find_newest_report(scenario, report_dir)

    # read report file
    with open(report_file) as f:
        output = json.load(f)

    if not output:
        assert False, "Test was not run successfully or file not found!"

    # collect files in the report json
    actual_files = []
    actual_report_dir = f"{current_dir}/{report_dir}/"
    # collect files in steps (output > steps > attachments)
    for step in output["steps"]:
        actual_files.extend(
            util.collect_files_from_report(step, file_type, actual_report_dir)
        )
    # collect files in attachment (output > attachments)
    actual_files.extend(
        util.collect_files_from_report(output, file_type, actual_report_dir)
    )
    return len(actual_files)
