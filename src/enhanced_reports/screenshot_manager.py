import logging
from typing import Dict, Any, Tuple

from datetime import datetime
import base64
from PIL import Image
from io import BytesIO

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions

from . import common_utils
from .config import Parameter

logger = logging.getLogger(__name__)


__desired_resolution: Tuple[int, int] = None
__resize_factor: float = None


@common_utils.fail_silently
def get_screenshot(screenshot_name: str, scenario_name: str, plugin_options, driver: WebDriver) -> str:
    # selenium can't take screenshots if a browser alert/prompt is open. trying to do so would break the current test.
    # so, skipping screenshots in such a case
    if expected_conditions.alert_is_present()(driver):
        return ""
    return _get_resized_image(driver.get_screenshot_as_base64(), plugin_options, scenario_name, screenshot_name)


def _get_resized_image(
    image_bytes, report_options: Dict[Parameter, Any], scenario_name, screenshot_name="screenshot.png"
):
    global __desired_resolution, __resize_factor
    __desired_resolution = __desired_resolution if __desired_resolution \
                               else (report_options[Parameter.SS_WIDTH], report_options[Parameter.SS_HEIGHT])
    __resize_factor = __resize_factor if __resize_factor else report_options[Parameter.SS_RESIZE_PERCENT] / 100

    screenshot_file_name: str = common_utils.clean_filename(f"{screenshot_name} {str(datetime.now())}.png")

    # open the image directly thru an in-memory buffer
    img = Image.open(BytesIO(base64.b64decode(image_bytes)))

    # Check if user wants to keep the screenshots, if yes then create directory and save original images
    if report_options[Parameter.SS_KEEP_FILES]:
        common_utils.mkdir(
            f"{report_options[Parameter.SS_DIR]}/{scenario_name}"
        )
        path: str = f"{report_options[Parameter.SS_DIR]}/{scenario_name}/{screenshot_file_name}"
        img.save(path)

    # if the user has not passed a specific resolution, create it from the resize factor
    desired_resolution = common_utils.get_resized_resolution(img.width, img.height, __resize_factor) \
        if __desired_resolution == (0, 0) else __desired_resolution

    # resize image to the desired resolution. if more customizability is needed, consider the resize or reduce methods
    img.thumbnail(desired_resolution)
    # in tobytes() need to return the array before the join operation happens
    # return img.tobytes()

    path: str = f"{report_options[Parameter.SS_DIR]}/{scenario_name}.png"
    img.save(path)
    return path


@common_utils.fail_silently
def get_highlighted_screenshot(element: WebElement, action_name: str, scenario_name: str, report_options,
                               driver: WebDriver, color: str = "red", border_width: int = 5) -> str:
    def apply_style(s):
        driver.execute_script(
            "arguments[0].setAttribute('style', arguments[1]);", element, s
        )

    original_style = element.get_attribute("style")
    apply_style(
        "border: {0}px solid {1}; padding:{2}px".format(border_width, color, 5)
    )

    path: str = get_screenshot(action_name, scenario_name, report_options, driver)

    apply_style(original_style)

    return path
