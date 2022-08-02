
"""
This module contains shared fixtures, steps, and hooks.
"""
import base64
import logging
from typing import Tuple
import allure
from PIL import Image
from io import BytesIO
import pytest
from allure_commons.types import AttachmentType
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.abstract_event_listener import AbstractEventListener
import settings
from selenium.webdriver.common.action_chains import ActionChains
import wrapt
import wrapt.wrappers

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
        "screenshot_option": request.config.getoption("report_screenshot_option")
    }

    env_resize_info: dict = {
        "resize_percent": settings.IMAGE_PERCENTAGE,
        "resize_width": settings.IMAGE_WIDTH,
        "resize_height": settings.IMAGE_HEIGHT,
        "screenshot_option": settings.SCREENSHOT_OPTION
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
    if cmd_line_resize_info['screenshot_option']:
        screenshot_option = cmd_line_resize_info['screenshot_option']
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
        "screenshot_option": screenshot_option
    }


@pytest.fixture()
def logger():
    # Logger Settings
    logging.basicConfig(
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    yield logger


def pytest_addoption(parser):
    parser.addoption("--report_image_resize_to_percent", action="store", default=0)
    parser.addoption("--report_image_resize_width", action="store", default=0)
    parser.addoption("--report_image_resize_height", action="store", default=0)
    parser.addoption("--report_screenshot_option", action="store", default="all")


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

