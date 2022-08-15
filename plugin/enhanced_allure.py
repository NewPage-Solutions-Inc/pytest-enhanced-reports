import logging
import os
import dotenv

from typing import Tuple

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
    path: str = "screenshot.png"
    img.save(path)
    return path


def __get_resized_resolution(width, height, resize_factor) -> Tuple[int, int]:
    new_width = int(width * resize_factor)
    new_height = int(height * resize_factor)
    return new_width, new_height
