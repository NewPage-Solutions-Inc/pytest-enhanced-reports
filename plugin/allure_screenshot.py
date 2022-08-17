import logging
import dotenv

from pytest import fixture

import allure
from allure_commons.types import AttachmentType

import base64
from PIL import Image
from io import BytesIO

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.abstract_event_listener import AbstractEventListener

import enhanced_allure

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


@fixture(scope="session")
def report_screenshot_options(request) -> dict:
    cmd_line_plugin_options: dict = {
        "screenshot_level": request.config.getoption("report_screenshot_level"),
        "resize_percent": request.config.getoption("report_screenshot_resize_percent"),
        "resize_width": request.config.getoption("report_screenshot_width"),
        "resize_height": request.config.getoption("report_screenshot_height"),
        "screenshot_dir": request.config.getoption("report_screenshot_dir"),
        "keep_screenshots": request.config.getoption("report_keep_screenshots")
    }

    env_plugin_options: dict = {
        "screenshot_level": enhanced_allure._get_env_var("REPORT_SCREENSHOT_LEVEL", default_value="all"),
        "resize_percent": enhanced_allure._get_env_var("REPORT_SCREENSHOT_RESIZE_PERCENT"),
        "resize_width": enhanced_allure._get_env_var("REPORT_SCREENSHOT_WIDTH"),
        "resize_height": enhanced_allure._get_env_var("REPORT_SCREENSHOT_HEIGHT"),
        "screenshot_dir": enhanced_allure._get_env_var("REPORT_SCREENSHOT_DIR", default_value="screenshots/"),
        "keep_screenshots": enhanced_allure._get_env_var("REPORT_KEEP_SCREENSHOTS", default_value=False)
    }

    resize_percent = None
    resize_width = None
    resize_height = None

    screenshot_level = None
    screenshot_dir = None
    keep_screenshots = None

    if cmd_line_plugin_options['screenshot_level']:
        screenshot_level = cmd_line_plugin_options['screenshot_level']
    else:
        screenshot_level = env_plugin_options['screenshot_level']

    if cmd_line_plugin_options['screenshot_dir']:
        screenshot_dir = cmd_line_plugin_options['screenshot_dir']
    else:
        screenshot_dir = env_plugin_options['screenshot_dir']

    if cmd_line_plugin_options['keep_screenshots']:
        keep_screenshots = str(cmd_line_plugin_options['keep_screenshots']).lower() == 'true'
    else:
        keep_screenshots = str(env_plugin_options['keep_screenshots']).lower() == 'true'

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
        "screenshot_dir": screenshot_dir,
        "resize_percent": resize_percent,
        "resize_width": resize_width,
        "resize_height": resize_height,
        "keep_screenshots": keep_screenshots
    }


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


def fail_silently(func):
    """Makes sure that any errors/exceptions do not get outside the plugin"""
    def wrapped_func(*args, **kws):
        try:
            return func(*args, **kws)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")

    return wrapped_func


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
        desired_resolution = enhanced_allure.__get_resized_resolution(img.width, img.height, resize_factor)

    # resize image to the desired resolution. if more customizability is needed, consider the resize or reduce methods
    img.thumbnail(desired_resolution)
    # in tobytes() need to return the array before the join operation happens
    # return img.tobytes()

    path: str = options["screenshot_dir"]+"/screenshotO.png"
    img.save(path)
    return path
