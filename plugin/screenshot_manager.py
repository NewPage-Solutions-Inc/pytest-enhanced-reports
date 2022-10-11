import logging
import dotenv
from datetime import datetime
import allure
from allure_commons.types import AttachmentType
import base64
from PIL import Image
from io import BytesIO
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
import common_utils

dotenv.load_dotenv()
logger = logging.getLogger(__name__)


@common_utils.fail_silently
def take_screenshot(screenshot_name: str, plugin_options, driver: WebDriver):
    # selenium can't take screenshots if a browser alert/prompt is open. trying to do so would break the current test.
    # so, skipping screenshots in such a case
    if expected_conditions.alert_is_present()(driver):
        return
    path_to_resized_image = _get_resized_image(
        driver.get_screenshot_as_base64(), plugin_options, screenshot_name
    )
    allure.attach.file(
        path_to_resized_image, name=screenshot_name, attachment_type=AttachmentType.PNG
    )


def _get_resized_image(image_bytes, options: dict, screenshot_name="screenshot.png"):
    desired_resolution = None
    screenshot_file_name = f"{screenshot_name} {str(datetime.now())}.png"
    screenshot_file_name = common_utils.clean_filename(screenshot_file_name)

    # default resize factor if no values are passed from cmd line args or env vars
    resize_factor: float = 0.3
    if options:
        if options["resize_width"] and options["resize_height"]:
            # if a resolution is provided, use that
            desired_resolution = (
                int(options["resize_width"]),
                int(options["resize_height"]),
            )
        elif options["resize_percent"]:
            # if a percentage is provided instead, some calculations are required
            resize_factor = int(options["resize_percent"]) / 100

    # open the image directly thru an in-memory buffer
    img = Image.open(BytesIO(base64.b64decode(image_bytes)))

    # Check if user wants to keep the screenshots, if yes then create directory and save original images
    if options["keep_screenshots"]:
        common_utils.mkdir(f"{options['screenshot_dir']}/{options['scenario_name']}")
        path: str = f"{options['screenshot_dir']}/{options['scenario_name']}/{screenshot_file_name}"
        img.save(path)

    # if the user has not passed a specific resolution, create it from the resize factor
    if not desired_resolution:
        desired_resolution = common_utils.get_resized_resolution(
            img.width, img.height, resize_factor
        )

    # resize image to the desired resolution. if more customizability is needed, consider the resize or reduce methods
    img.thumbnail(desired_resolution)
    # in tobytes() need to return the array before the join operation happens
    # return img.tobytes()

    path: str = f"{options['screenshot_dir']}/{options['scenario_name']}.png"
    img.save(path)
    return path


@common_utils.fail_silently
def highlight_element_and_take_a_screenshot(
    element,
    action_name,
    screen_shot_plugin_options,
    driver: WebDriver,
    color="red",
    border_width=5,
):
    def apply_style(s):
        driver.execute_script(
            "arguments[0].setAttribute('style', arguments[1]);", element, s
        )

    original_style = element.get_attribute("style")
    apply_style("border: {0}px solid {1}; padding:{2}px".format(border_width, color, 5))
    take_screenshot(action_name, screen_shot_plugin_options, driver)
    apply_style(original_style)
