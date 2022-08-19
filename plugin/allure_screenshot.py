import logging
import dotenv
from datetime import datetime

import allure
from allure_commons.types import AttachmentType

import base64
from PIL import Image
from io import BytesIO

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.abstract_event_listener import AbstractEventListener

import common_utils

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


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
    path_to_resized_image = _get_resized_image(driver.get_screenshot_as_base64(), plugin_options, screenshot_name)
    allure.attach.file(path_to_resized_image, name=screenshot_name, attachment_type=AttachmentType.PNG)


def _get_resized_image(image_bytes, options: dict, screenshot_name="screenshot.png"):
    desired_resolution = None
    screenshot_file_name = f"{screenshot_name} {str(datetime.now())}.png"
    screenshot_file_name = clean_filename(screenshot_file_name)

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

    # Check if user wants to keep the screenshots, if yes then create directory and save original images
    if options['keep_screenshots']:
        common_utils._mkdir(f"{options['screenshot_dir']}/{options['scenario_name']}")
        path: str = f"{options['screenshot_dir']}/{options['scenario_name']}/{screenshot_file_name}"
        img.save(path)

    # if the user has not passed a specific resolution, create it from the resize factor
    if not desired_resolution:
        desired_resolution = common_utils._get_resized_resolution(img.width, img.height, resize_factor)

    # resize image to the desired resolution. if more customizability is needed, consider the resize or reduce methods
    img.thumbnail(desired_resolution)
    # in tobytes() need to return the array before the join operation happens
    # return img.tobytes()

    path: str = f"{options['screenshot_dir']}/{options['scenario_name']}.png"
    img.save(path)
    return path


def clean_filename(sourcestring,  removestring ="%:/,\\[]<>*?"):
    #remove the undesireable characters
    return ''.join([c for c in sourcestring if c not in removestring])
