import logging
import os
import dotenv

from typing import Tuple

from pytest import fixture

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains

import wrapt
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver

from allure_screenshot import WebDriverEventListener
import allure_screenshot

from allure_screenshot import report_screenshot_options
from allure_video_recording import report_video_recording_options, screen_recorder, video_capture_thread

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


@fixture(scope="session", autouse=True)
def screenshotting_driver(report_screenshot_options):
    def _enhanced_driver_getter(driver: WebDriver):
        # Event listener is needed only if the screenshot level is greater than 'error-only'
        if report_screenshot_options['screenshot_level'] != 'all':
            return driver

        # check if the directory to write screenshots exists
        _mkdir(report_screenshot_options["screenshot_dir"])
        return EventFiringWebDriver(driver, WebDriverEventListener(report_screenshot_options))
    return _enhanced_driver_getter


@fixture(scope="session", autouse=True)
def create_wrappers(report_screenshot_options):
    if report_screenshot_options['screenshot_level'] != 'all':
        return

    @wrapt.patch_function_wrapper(ActionChains, 'perform')
    def wrap_action_chains_perform_method(wrapped, instance, args, kwargs):
        # here, wrapped is the original perform method in ActionChains
        # instance is `self` (it is not the case for classmethods though),
        # args and kwargs are a tuple and a dict respectively.

        wrapped(*args, **kwargs)  # note it is already bound to the instance

        allure_screenshot._take_screenshot("After performing selenium action chain", report_screenshot_options, instance._driver)


def pytest_bdd_step_validation_error(request, feature, scenario, step, step_func):
    report_screenshot_options = request.getfixturevalue('report_screenshot_options')

    if report_screenshot_options['screenshot_level'] == 'none':
        return

    driver = request.getfixturevalue('selenium')
    allure_screenshot._take_screenshot("Step failed", driver, report_screenshot_options)


def pytest_bdd_step_error(request, feature, scenario, step, step_func):
    report_screenshot_options = request.getfixturevalue('report_screenshot_options')

    if report_screenshot_options['screenshot_level'] == 'none':
        return

    driver = request.getfixturevalue('selenium')
    allure_screenshot._take_screenshot("Step failed", driver, report_screenshot_options)


def pytest_addoption(parser):
    # a percentage by which the screenshot will be resized. valid values - 75, 60, 50, etc
    parser.addoption("--report_screenshot_resize_percent", action="store", default=0)

    # the expected width of the resized screenshot used in reports.
    # the actual width of the image used in reports could be different depending on the aspect ratio of the image
    parser.addoption("--report_screenshot_width", action="store", default=0)

    # the expected height of the resized screenshot used in reports.
    # the actual height of the image used in reports could be different depending on the aspect ratio of the image
    parser.addoption("--report_screenshot_height", action="store", default=0)

    # valid values for screenshot level are 'none', 'all', 'error-only'
    parser.addoption("--report_screenshot_level", action="store", default=None)

    # valid values for video recording are 'true', 'false'
    parser.addoption("--report_video_recording", action="store", default=0)

    # expected width of video frame to be recorded
    parser.addoption("--report_video_width", action="store", default=0)

    # expected height of video frame to be recorded
    parser.addoption("--report_video_height", action="store", default=0)

    # expected number of frames per second while recording video.
    # this is applicable when there are enough frames present to be recorded in one second
    parser.addoption("--report_video_frame_rate", action="store", default=0)

    # a percentage by which the video frames will be resized. valid values - 75, 60, 50, etc
    parser.addoption("--report_video_resize_percentage", action="store", default=0)

    # path to folder where user wants to preserve screenshots
    parser.addoption("--report_screenshot_dir", action="store", default=0)

    # path to folder where user wants to preserve videos
    parser.addoption("--report_video_dir", action="store", default=0)

    # flag is used to decide whether user wants to preserve screenshots
    parser.addoption("--report_keep_screenshots", action="store", default=0)

    # flag is used to decide whether user wants to preserve videos
    parser.addoption("--report_keep_videos", action="store", default=0)


def pytest_bdd_before_scenario(request, feature, scenario):
    video_recording = request.getfixturevalue('report_video_recording_options')['video_recording']
    if video_recording:
        obj_recorder_thread, obj_recorder = request.getfixturevalue('video_capture_thread')
        obj_recorder_thread.start()
    logging.info("TEST EXECUTION VIDEO RECORDING: " + str(video_recording))


def pytest_bdd_after_scenario(request, feature, scenario):
    video_info = request.getfixturevalue('report_video_recording_options')
    if video_info['video_recording']:
        scenario_info = "video"
        obj_recorder_thread, obj_recorder = request.getfixturevalue('video_capture_thread')
        obj_recorder.stop_recording_and_stitch_video(video_info, obj_recorder_thread, scenario_info, scenario.name)


def _get_env_var(env_var_name, default_value=None):
    return os.getenv(env_var_name, default_value)


def __get_resized_resolution(width, height, resize_factor) -> Tuple[int, int]:
    new_width = int(width * resize_factor)
    new_height = int(height * resize_factor)
    return new_width, new_height


def _mkdir(dir_name):
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)


def _clean_image_repository(img_dir):
    # Now clean the images directory
    if os.path.isdir(img_dir):
        for f in os.listdir(img_dir):
            os.remove(os.path.join(img_dir, f))
        os.rmdir(img_dir)
        logger.info(f"IMAGE REPOSOTORY CLEANED. {img_dir} FOLDER DELETED.")

