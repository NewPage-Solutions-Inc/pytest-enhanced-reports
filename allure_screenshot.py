
"""
This module contains shared fixtures, steps, and hooks.
"""
import base64
import logging
from typing import Tuple
import allure
from io import BytesIO
import pytest
from allure_commons.types import AttachmentType
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.abstract_event_listener import AbstractEventListener
import settings
from selenium.webdriver.common.action_chains import ActionChains
import wrapt.wrappers
from PIL import Image
import cv2
import os
import threading


@wrapt.patch_function_wrapper(ActionChains, 'perform')
def perform(wrapped, instance, args, kwargs):
    # here, wrapped is the original perform,
    # instance is `self` instance (it is not true for classmethods though),
    # args and kwargs are tuple and dict respectively.
    if pytest.image_info['screenshot_option'] == 'all':
        path_to_resized_image = _get_resized_image(instance._driver.get_screenshot_as_base64(), pytest.image_info)
        allure.attach.file(path_to_resized_image, name="Before ActionChain Perform", attachment_type=AttachmentType.PNG)
        wrapped(*args, **kwargs)  # note it is already bound to the instance
        path_to_resized_image = _get_resized_image(instance._driver.get_screenshot_as_base64(), pytest.image_info)
        allure.attach.file(path_to_resized_image, name="Before ActionChain Perform", attachment_type=AttachmentType.PNG)
    else:
        wrapped(*args, **kwargs)


@pytest.fixture(scope="session")
def resize_info(request) -> dict:
    cmd_line_resize_info: dict = {
        "resize_percent": request.config.getoption("report_image_resize_to_percent"),
        "resize_width": request.config.getoption("report_image_resize_width"),
        "resize_height": request.config.getoption("report_image_resize_height"),
        "screenshot_option": request.config.getoption("report_screenshot_option"),
        "video_recording": request.config.getoption("video_recording"),
        "video_width": request.config.getoption("video_width"),
        "video_height": request.config.getoption("video_height"),
        "video_frame_rate": request.config.getoption("video_frame_rate"),
        "video_resize_percentage": request.config.getoption("video_resize_percentage")
    }

    env_resize_info: dict = {
        "resize_percent": settings.IMAGE_PERCENTAGE,
        "resize_width": settings.IMAGE_WIDTH,
        "resize_height": settings.IMAGE_HEIGHT,
        "screenshot_option": settings.SCREENSHOT_OPTION,
        "video_recording": settings.VIDEO_RECORDING,
        "video_width": settings.VIDEO_WIDTH,
        "video_height": settings.VIDEO_HEIGHT,
        "video_frame_rate": settings.VIDEO_FRAME_RATE,
        "video_resize_percentage": settings.VIDEO_RESIZE_PERCENTAGE
    }

    """
    Order of precedence:
    1. Specific resolution
        1.1 - From command line options
        1.2 - From environment variables
    2. Resize percentage
        1.1 - From command line option
        1.2 - From environment variable
    3. Default value (defined in the resize method)
    """
    resize_percent = None
    resize_width = None
    resize_height = None
    screenshot_option = None
    video_recording = None
    video_height = None
    video_width = None
    video_frame_rate = None
    video_resize_percentage = None

    if cmd_line_resize_info['screenshot_option']:
        screenshot_option = cmd_line_resize_info['screenshot_option']
    elif env_resize_info['screenshot_option']:
        screenshot_option = env_resize_info['screenshot_option']

    if cmd_line_resize_info['video_recording']:
        video_recording = str(cmd_line_resize_info['video_recording']).lower() == 'true'
    elif env_resize_info['video_recording']:
        video_recording = str(env_resize_info['video_recording']).lower() == 'true'
    else:
        # If command line and env arguments are not given then set default video recording to False
        video_recording = False

    if cmd_line_resize_info['video_frame_rate']:
        video_frame_rate = cmd_line_resize_info['video_frame_rate']
    elif env_resize_info['video_frame_rate']:
        video_frame_rate = env_resize_info['video_frame_rate']
    else:
        # If command line and env arguments are not given then set default video frame rate to '5'
        video_frame_rate = 5

    if cmd_line_resize_info['resize_width'] and cmd_line_resize_info['resize_height']:
        resize_width = cmd_line_resize_info['resize_width']
        resize_height = cmd_line_resize_info['resize_height']
    elif env_resize_info['resize_width'] and env_resize_info['resize_height']:
        resize_width = env_resize_info['resize_width']
        resize_height = env_resize_info['resize_height']
    else:
        if cmd_line_resize_info['resize_percent']:
            resize_percent = cmd_line_resize_info['resize_percent']
        elif env_resize_info['resize_percent']:
            resize_percent = env_resize_info['resize_percent']

    if cmd_line_resize_info['video_width'] and cmd_line_resize_info['video_height']:
        video_width = cmd_line_resize_info['video_width']
        video_height = cmd_line_resize_info['video_height']
    elif env_resize_info['video_width'] and env_resize_info['video_height']:
        video_width = env_resize_info['video_width']
        video_height = env_resize_info['video_height']
    else:
        if cmd_line_resize_info['video_resize_percentage']:
            video_resize_percentage = cmd_line_resize_info['video_resize_percentage']
        elif env_resize_info['video_resize_percentage']:
            video_resize_percentage = env_resize_info['video_resize_percentage']
        else:
            # If command line and env arguments are not given then set video Resize Factor to '30'
            video_resize_percentage = 30

    pytest.image_info = {
        "resize_percent": resize_percent,
        "resize_width": resize_width,
        "resize_height": resize_height,
        "screenshot_option": screenshot_option
    }
    return {
        "resize_percent": resize_percent,
        "resize_width": resize_width,
        "resize_height": resize_height,
        "screenshot_option": screenshot_option,
        "video_recording": video_recording,
        "video_height": video_height,
        "video_width": video_width,
        "video_frame_rate": video_frame_rate,
        "video_resize_percentage": video_resize_percentage
    }


@pytest.fixture()
def logger():
    # Logger Settings
    logging.basicConfig(
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    yield logger


@pytest.fixture
def screen_recorder():
    obj = ScreenRecorder()
    yield obj


@pytest.fixture
def video_capture_thread(screen_recorder, selenium):
    recorder_thread = threading.Thread(target=screen_recorder.start_capturing, name='Recorder', args=[selenium])
    yield recorder_thread, screen_recorder


def pytest_addoption(parser):
    parser.addoption("--report_image_resize_to_percent", action="store", default=0)
    parser.addoption("--report_image_resize_width", action="store", default=0)
    parser.addoption("--report_image_resize_height", action="store", default=0)
    parser.addoption("--report_screenshot_option", action="store", default="all")
    parser.addoption("--video_recording", action="store", default=0)
    parser.addoption("--video_width", action="store", default=0)
    parser.addoption("--video_height", action="store", default=0)
    parser.addoption("--video_frame_rate", action="store", default=0)
    parser.addoption("--video_resize_percentage", action="store", default=0)


def pytest_bdd_before_scenario(request, feature, scenario):
    video_recording = request.getfixturevalue('resize_info')['video_recording']
    if video_recording:
        obj_recorder_thread, obj_recorder = request.getfixturevalue('video_capture_thread')
        obj_recorder_thread.start()
    logging.info("TEST EXECUTION VIDEO RECORDING: " + str(video_recording))


def pytest_bdd_step_validation_error(request, feature, scenario, step, step_func):
    driver = request.getfixturevalue('selenium')
    level_value = request.getfixturevalue('resize_info')
    if level_value['screenshot_option'] == 'fail' or level_value['screenshot_option'] == 'all':
        path_to_resized_image = _get_resized_image(driver.get_screenshot_as_base64(), level_value)
        allure.attach.file(path_to_resized_image, name="Step failed", attachment_type=AttachmentType.PNG)


def pytest_bdd_step_error(request, feature, scenario, step, step_func):
    driver = request.getfixturevalue('selenium')
    level_value = request.getfixturevalue('resize_info')
    if level_value['screenshot_option'] == 'fail' or level_value['screenshot_option'] == 'all':
        path_to_resized_image = _get_resized_image(driver.get_screenshot_as_base64(), level_value)
        allure.attach.file(path_to_resized_image, name="Step failed", attachment_type=AttachmentType.PNG)


def pytest_bdd_after_scenario(request, feature, scenario):
    video_info = request.getfixturevalue('resize_info')
    if video_info['video_recording']:
        obj_recorder_thread, obj_recorder = request.getfixturevalue('video_capture_thread')
        obj_recorder.stop = True
        obj_recorder_thread.join()
        video_resize_info = _get_video_resize_resolution(video_info)
        obj_recorder.create_video_from_images(video_resize_info, video_info['video_frame_rate'])
        allure.attach.file("video.webm", name=scenario.name, attachment_type=AttachmentType.WEBM)
        logging.info("TEST EXECUTION VIDEO RECORDING VIDEO STOPPED [Video Size: " + str(video_resize_info) + " - Frame Rate: " + str(video_info['video_frame_rate']) + "]")


class WebDriverEventListener(AbstractEventListener):

    def __init__(self, resize_info: dict):
        self.resize_info = resize_info

    def after_navigate_to(self, url, driver: WebDriver):
        if self.resize_info['screenshot_option'] == 'all':
            path_to_resized_image = _get_resized_image(driver.get_screenshot_as_base64(), self.resize_info)
            allure.attach.file(path_to_resized_image, name="Navigation", attachment_type=AttachmentType.PNG)

    def after_click(self, element, driver):
        if self.resize_info['screenshot_option'] == 'all':
            path_to_resized_image = _get_resized_image(driver.get_screenshot_as_base64(), self.resize_info)
            allure.attach.file(path_to_resized_image, name="Click", attachment_type=AttachmentType.PNG)

    def after_change_value_of(self, element, driver):
        if self.resize_info['screenshot_option'] == 'all':
            path_to_resized_image = _get_resized_image(driver.get_screenshot_as_base64(), self.resize_info)
            allure.attach.file(path_to_resized_image, name="Keyboard input", attachment_type=AttachmentType.PNG)


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
                driver_.save_screenshot("video/"+str(count)+".png")
                count += 1
                if self.stop:
                    logging.info("Stopping Screen Capture")
                    break
            logging.error("SCREENSHOTS CAPTURED AND WRITTEN ON DISK: " + str(count))
            print("SCREENSHOTS CAPTURED AND WRITTEN ON DISK: " + str(count))
        except Exception as error:
            logging.error("An Exception occurred while taking screenshot. " + str(error))

    def create_video_from_images(self, video_size: tuple, frame_rate: int):
        """This method will sticth the images under /video directory into a video"""
        try:
            fourcc = cv2.VideoWriter_fourcc(*'vp09')
            video = cv2.VideoWriter("video.webm", fourcc, int(frame_rate), video_size)
            img_dir = "video"
            images_path = os.listdir(img_dir)
            images_path = sorted(images_path, key=lambda x: int(os.path.splitext(x)[0]))
            for img in images_path:
                if img.__contains__('png'):
                    video.write(cv2.resize(cv2.imread(img_dir + "/" + img), video_size))
            video.release()
            # Now clean the images directory
            for f in images_path:
                os.remove(os.path.join(img_dir, f))

        except Exception as error:
            logging.error("An Exception occurred while stitching video. " + str(error))


def __get_resized_resolution(width, height, resize_factor) -> Tuple[int, int]:
    new_width = int(width * resize_factor)
    new_height = int(height * resize_factor)
    return new_width, new_height


def _get_resized_image(image_bytes, info):
    desired_resolution = None
    # default resize factor if no values are passed from cmd line args or env vars
    resize_factor: float = 0.3
    if info:
        if info['resize_width'] and info['resize_height']:
            # if a resolution is provided, use that
            desired_resolution = (int(info['resize_width']), int(info['resize_height']))
        elif info['resize_percent']:
            # if a percentage is provided instead, some calculations are required
            resize_factor = int(info['resize_percent']) / 100

    # open the image directly thru an in-memory buffer
    img = Image.open(BytesIO(base64.b64decode(image_bytes)))

    # if the user has not passed a specific resolution, create it from the resize factor
    if not desired_resolution:
        desired_resolution = __get_resized_resolution(img.width, img.height, resize_factor)

    # resize image to the desired resolution. if more customizability is needed, consider the resize or reduce methods
    img.thumbnail(desired_resolution)
    # in tobytes() need to return the array before the join operation happens
    # return img.tobytes()
    path: str = "screenshot.png"
    img.save(path)
    return path


def _get_video_resize_resolution(info):
    desired_resolution = None
    obj_screen_recorder = ScreenRecorder()
    resize_factor = None
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

