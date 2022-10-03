from selenium.webdriver.support.abstract_event_listener import (
    AbstractEventListener,
)
from selenium.webdriver.remote.webdriver import WebDriver
from allure_screenshot import (
    _take_screenshot,
    highlight_element_and_take_a_screenshot,
)
from browser_console_manager import capture_output
import allure
from allure_commons.types import AttachmentType


class WebDriverEventListener(AbstractEventListener):
    def __init__(
        self, screen_shot_plugin_options: dict = {}, other_configs: dict = {}
    ):
        self.screen_shot_plugin_options = screen_shot_plugin_options
        self.other_configs = other_configs

    def after_navigate_to(self, url, driver: WebDriver):
        _take_screenshot(
            f"Navigation to {url}", self.screen_shot_plugin_options, driver
        )
        if self.other_configs.get("always_capture_log"):
            logs = capture_output(driver)
            allure.attach(
                bytes(logs, "utf-8"), "Browser Outputs", AttachmentType.TEXT
            )

    def before_click(self, element, driver):
        if self.other_configs.get("highlight_element"):
            highlight_element_and_take_a_screenshot(
                element,
                "Before click",
                self.screen_shot_plugin_options,
                driver,
            )

    def after_click(self, element, driver):
        _take_screenshot(
            "After click", self.screen_shot_plugin_options, driver
        )
        if self.other_configs.get("always_capture_log"):
            logs = capture_output(driver)
            allure.attach(
                bytes(logs, "utf-8"), "Browser Outputs", AttachmentType.TEXT
            )

    def before_change_value_of(self, element, driver):
        if self.other_configs.get("highlight_element"):
            highlight_element_and_take_a_screenshot(
                element,
                "Before keyboard input",
                self.screen_shot_plugin_options,
                driver,
            )

    def after_change_value_of(self, element, driver):
        _take_screenshot(
            "After keyboard input", self.screen_shot_plugin_options, driver
        )
        if self.other_configs.get("always_capture_log"):
            logs = capture_output(driver)
            allure.attach(
                bytes(logs, "utf-8"), "Browser Outputs", AttachmentType.TEXT
            )

    def after_execute_script(self, script, driver):
        _take_screenshot(
            "JS execution", self.screen_shot_plugin_options, driver
        )
        if self.other_configs.get("always_capture_log"):
            logs = capture_output(driver)
            allure.attach(
                bytes(logs, "utf-8"), "Browser Outputs", AttachmentType.TEXT
            )

    def after_navigate_back(self, driver):
        if self.other_configs.get("always_capture_log"):
            logs = capture_output(driver)
            allure.attach(
                bytes(logs, "utf-8"), "Browser Outputs", AttachmentType.TEXT
            )
