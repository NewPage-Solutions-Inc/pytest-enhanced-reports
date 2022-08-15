import logging
import os
import dotenv
import threading

from typing import Tuple

import pytest
from pytest import fixture

import allure
from allure_commons.types import AttachmentType

import base64
from PIL import Image
from io import BytesIO

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.abstract_event_listener import AbstractEventListener
from selenium.webdriver.common.action_chains import ActionChains

import wrapt
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver


import cv2

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


@fixture(scope="session", autouse=True)
def screenshotting_driver(report_screenshot_options):
    def _enhanced_driver_getter(driver: WebDriver):
        # Event listener is needed only if the screenshot level is greater than 'error-only'
        if report_screenshot_options['screenshot_level'] != 'all':
            return driver

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

        _take_screenshot("After performing selenium action chain", report_screenshot_options, instance._driver)


@pytest.fixture
def screen_recorder():
    obj = ScreenRecorder()
    yield obj


@pytest.fixture
def video_capture_thread(screen_recorder, selenium):
    recorder_thread = threading.Thread(target=screen_recorder.start_capturing, name='Recorder', args=[selenium])
    yield recorder_thread, screen_recorder


class WebDriverEventListener(AbstractEventListener):

    def __init__(self, plugin_options: dict):
        self.plugin_options = plugin_options

    def after_navigate_to(self, url, driver: WebDriver):
        _take_screenshot(f"Navigation to {url}", self.plugin_options, driver)

    def after_click(self, element, driver):
        _take_screenshot("Click", self.plugin_options, driver)

    def after_change_value_of(self, element, driver):
        _take_screenshot("Keyboard input", self.plugin_options, driver)

    def after_execute_script(self, script, driver):
        _take_screenshot("JS execution", self.plugin_options, driver)


class ScreenRecorder:

    def __init__(self):
        self.video = None
        self.stop = False
        self.directory = "video/"

    def start_capturing(self, driver_):
        """This method will start caotyring images and saving them on disk under /video folder
            These images will later be used to stich together into a video"""
        try:
            count = 0
            while True:
                if not os.path.isdir(self.directory):
                    os.mkdir(self.directory)
                    logging.info("Creating new directory: " + self.directory)
                driver_.save_screenshot(self.directory+str(count)+".png")
                count += 1
                if self.stop:
                    logging.info("Stopping Screen Capture")
                    break
            logger.info("SCREENSHOTS CAPTURED AND WRITTEN ON DISK: " + str(count))
        except Exception as error:
            logger.error("An Exception occurred while taking screenshot. " + str(error))

    def create_video_from_images(self, video_size: tuple, frame_rate: int):
        """This method will sticth the images under /video directory into a video"""
        try:
            fourcc = cv2.VideoWriter_fourcc(*'vp09')
            video = cv2.VideoWriter("video.webm", fourcc, int(frame_rate), video_size)
            images_path = os.listdir(self.directory)
            images_path = sorted(images_path, key=lambda x: int(os.path.splitext(x)[0]))
            for img in images_path:
                if img.__contains__('png'):
                    video.write(cv2.resize(cv2.imread(self.directory + img), video_size))
            video.release()
            logger.info("TEST EXECUTION VIDEO RECORDING VIDEO STOPPED [Video Size: " + str(video_size) + " - Frame Rate: " + str(frame_rate) + "]")
        except Exception as error:
            logger.error("An Exception occurred while stitching video. " + str(error))
        finally:
            # Now clean the images directory
            _clean_image_repository(self.directory)


def pytest_bdd_step_validation_error(request, feature, scenario, step, step_func):
    report_screenshot_options = request.getfixturevalue('report_screenshot_options')

    if report_screenshot_options['screenshot_level'] == 'none':
        return

    driver = request.getfixturevalue('selenium')
    _take_screenshot("Step failed", driver, report_screenshot_options)


def pytest_bdd_step_error(request, feature, scenario, step, step_func):
    report_screenshot_options = request.getfixturevalue('report_screenshot_options')

    if report_screenshot_options['screenshot_level'] == 'none':
        return

    driver = request.getfixturevalue('selenium')
    _take_screenshot("Step failed", driver, report_screenshot_options)


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


def pytest_bdd_before_scenario(request, feature, scenario):
    video_recording = request.getfixturevalue('report_video_recording_options')['video_recording']
    if video_recording:
        obj_recorder_thread, obj_recorder = request.getfixturevalue('video_capture_thread')
        obj_recorder_thread.start()
    logging.info("TEST EXECUTION VIDEO RECORDING: " + str(video_recording))


def pytest_bdd_after_scenario(request, feature, scenario):
    video_info = request.getfixturevalue('report_video_recording_options')
    if video_info['video_recording']:
        obj_recorder_thread, obj_recorder = request.getfixturevalue('video_capture_thread')
        obj_recorder.stop = True
        obj_recorder_thread.join()
        video_resize_info = _get_video_resize_resolution(video_info)
        obj_recorder.create_video_from_images(video_resize_info, video_info['video_frame_rate'])
        allure.attach.file("video.webm", name=scenario.name, attachment_type=AttachmentType.WEBM)


@fixture(scope="session")
def report_screenshot_options(request) -> dict:
    cmd_line_plugin_options: dict = {
        "screenshot_level": request.config.getoption("report_screenshot_level"),
        "resize_percent": request.config.getoption("report_screenshot_resize_percent"),
        "resize_width": request.config.getoption("report_screenshot_width"),
        "resize_height": request.config.getoption("report_screenshot_height")
    }

    env_plugin_options: dict = {
        "screenshot_level": _get_env_var("REPORT_SCREENSHOT_LEVEL", default_value="all"),
        "resize_percent": _get_env_var("REPORT_SCREENSHOT_RESIZE_PERCENT"),
        "resize_width": _get_env_var("REPORT_SCREENSHOT_WIDTH"),
        "resize_height": _get_env_var("REPORT_SCREENSHOT_HEIGHT")
    }

    resize_percent = None
    resize_width = None
    resize_height = None

    screenshot_level = None

    if cmd_line_plugin_options['screenshot_level']:
        screenshot_level = cmd_line_plugin_options['screenshot_level']
    else:
        screenshot_level = env_plugin_options['screenshot_level']

    """
    Order of precedence for resize config:
    1. Specific resolution
        1.1 - From command line options
        1.2 - From environment variables
    2. Resize percentage
        2.1 - From command line option
        2.2 - From environment variable
    3. Default value (defined in the resize method)
    """
    if cmd_line_plugin_options['resize_width'] and cmd_line_plugin_options['resize_height']:
        resize_width = cmd_line_plugin_options['resize_width']
        resize_height = cmd_line_plugin_options['resize_height']
    elif env_plugin_options['resize_width'] and env_plugin_options['resize_height']:
        resize_width = env_plugin_options['resize_width']
        resize_height = env_plugin_options['resize_height']
    else:
        if cmd_line_plugin_options['resize_percent']:
            resize_percent = cmd_line_plugin_options['resize_percent']
        elif env_plugin_options['resize_percent']:
            resize_percent = env_plugin_options['resize_percent']

    return {
        "screenshot_level": screenshot_level,
        "resize_percent": resize_percent,
        "resize_width": resize_width,
        "resize_height": resize_height
    }


@fixture(scope="session")
def report_video_recording_options(request) -> dict:
    cmd_line_plugin_options: dict = {
        "video_recording": request.config.getoption("report_video_recording"),
        "video_width": request.config.getoption("report_video_width"),
        "video_height": request.config.getoption("report_video_height"),
        "video_frame_rate": request.config.getoption("report_video_frame_rate"),
        "video_resize_percentage": request.config.getoption("report_video_resize_percentage")
    }

    env_plugin_options: dict = {
        "video_recording": _get_env_var("VIDEO_RECORDING", default_value=False),
        "video_width": _get_env_var("VIDEO_WIDTH"),
        "video_height": _get_env_var("VIDEO_HEIGHT"),
        "video_frame_rate": _get_env_var("VIDEO_FRAME_RATE", default_value=5),
        "video_resize_percentage": _get_env_var("VIDEO_RESIZE_PERCENTAGE", default_value=30)
    }

    video_recording = None
    video_height = None
    video_width = None
    video_frame_rate = None
    video_resize_percentage = None

    if cmd_line_plugin_options['video_recording']:
        video_recording = str(cmd_line_plugin_options['video_recording']).lower() == 'true'
    elif env_plugin_options['video_recording']:
        video_recording = str(env_plugin_options['video_recording']).lower() == 'true'

    if cmd_line_plugin_options['video_frame_rate']:
        video_frame_rate = cmd_line_plugin_options['video_frame_rate']
    elif env_plugin_options['video_frame_rate']:
        video_frame_rate = env_plugin_options['video_frame_rate']

    if cmd_line_plugin_options['video_width'] and cmd_line_plugin_options['video_height']:
        video_width = cmd_line_plugin_options['video_width']
        video_height = cmd_line_plugin_options['video_height']
    elif env_plugin_options['video_width'] and env_plugin_options['video_height']:
        video_width = env_plugin_options['video_width']
        video_height = env_plugin_options['video_height']
    else:
        if cmd_line_plugin_options['video_resize_percentage']:
            video_resize_percentage = cmd_line_plugin_options['video_resize_percentage']
        elif env_plugin_options['video_resize_percentage']:
            video_resize_percentage = env_plugin_options['video_resize_percentage']

    return {
        "video_recording": video_recording,
        "video_height": video_height,
        "video_width": video_width,
        "video_frame_rate": video_frame_rate,
        "video_resize_percentage": video_resize_percentage
    }


def fail_silently(func):
    """Makes sure that any errors/exceptions do not get outside the plugin"""
    def wrapped_func(*args, **kws):
        try:
            return func(*args, **kws)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")

    return wrapped_func


def _get_env_var(env_var_name, default_value=None):
    return os.getenv(env_var_name, default_value)


@fail_silently
def _take_screenshot(screenshot_name: str, plugin_options, driver: WebDriver):
    path_to_resized_image = _get_resized_image(driver.get_screenshot_as_base64(), plugin_options)
    allure.attach.file(path_to_resized_image, name=screenshot_name, attachment_type=AttachmentType.PNG)


def _get_resized_image(image_bytes, options: dict):
    desired_resolution = None
    # default resize factor if no values are passed from cmd line args or env vars
    resize_factor: float = 0.3
    if options:
        if options['resize_width'] and options['resize_height']:
            # if a resolution is provided, use that
            desired_resolution = (int(options['resize_width']), int(options['resize_height']))
        elif options['resize_percent']:
            # if a percentage is provided instead, some calculations are required
            resize_factor = int(options['resize_percent']) / 100

    # open the image directly thru an in-memory buffer
    img = Image.open(BytesIO(base64.b64decode(image_bytes)))

    # if the user has not passed a specific resolution, create it from the resize factor
    if not desired_resolution:
        desired_resolution = __get_resized_resolution(img.width, img.height, resize_factor)

    # resize image to the desired resolution. if more customizability is needed, consider the resize or reduce methods
    img.thumbnail(desired_resolution)
    # in tobytes() need to return the array before the join operation happens
    # return img.tobytes()
    path: str = "../screenshot.png"
    img.save(path)
    return path


def __get_resized_resolution(width, height, resize_factor) -> Tuple[int, int]:
    new_width = int(width * resize_factor)
    new_height = int(height * resize_factor)
    return new_width, new_height


def _get_video_resize_resolution(info):
    desired_resolution = None
    obj_screen_recorder = ScreenRecorder()
    if info:
        if info['video_width'] and info['video_height']:
            # if a resolution is provided, use that
            desired_resolution = (int(info['video_width']), int(info['video_height']))
        elif info['video_resize_percentage']:
            # if a percentage is provided, set the resize factor from default to user provided value
            resize_factor = int(info['video_resize_percentage']) / 100
            img = Image.open(os.path.join(obj_screen_recorder.directory, os.listdir(obj_screen_recorder.directory)[0]))
            desired_resolution = __get_resized_resolution(img.width, img.height, resize_factor)

    return desired_resolution


def _clean_image_repository(img_dir):
    # Now clean the images directory
    for f in os.listdir(img_dir):
        os.remove(os.path.join(img_dir, f))
    os.rmdir(img_dir)
    lo
