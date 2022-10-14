from selenium.webdriver.support.abstract_event_listener import (
    AbstractEventListener,
)
from selenium.webdriver.remote.webdriver import WebDriver
from screenshot_manager import (
    take_screenshot,
    highlight_element_and_take_a_screenshot,
)
from browser_console_manager import capture_output
import allure
from allure_commons.types import AttachmentType


class WebDriverEventListener(AbstractEventListener):
    def __init__(self, report_options: dict = {}):
        self.report_options = report_options

    def after_navigate_to(self, url, driver: WebDriver):
        take_screenshot(f"Navigation to {url}", self.report_options, driver)
        if self.report_options["capture_browser_console_log"] == "always":
            logs = capture_output(driver)
            allure.attach(
                bytes(logs, "utf-8"), "Browser Outputs", AttachmentType.TEXT
            )

    def before_click(self, element, driver):
        if self.report_options["highlight_element"]:
            highlight_element_and_take_a_screenshot(
                element, "Before click", self.report_options, driver
            )

    def after_click(self, element, driver):
        take_screenshot("After click", self.report_options, driver)
        if self.report_options["capture_browser_console_log"] == "always":
            logs = capture_output(driver)
            allure.attach(
                bytes(logs, "utf-8"), "Browser Outputs", AttachmentType.TEXT
            )

    def before_change_value_of(self, element, driver):
        if self.report_options["highlight_element"]:
            highlight_element_and_take_a_screenshot(
                element,
                "Before keyboard input",
                self.report_options,
                driver,
            )

    def after_change_value_of(self, element, driver):
        take_screenshot("After keyboard input", self.report_options, driver)
        if self.report_options["capture_browser_console_log"] == "always":
            logs = capture_output(driver)
            allure.attach(
                bytes(logs, "utf-8"), "Browser Outputs", AttachmentType.TEXT
            )

    def after_execute_script(self, script, driver):
        take_screenshot("JS execution", self.report_options, driver)
        if self.report_options["capture_browser_console_log"] == "always":
            logs = capture_output(driver)
            allure.attach(
                bytes(logs, "utf-8"), "Browser Outputs", AttachmentType.TEXT
            )

    def after_navigate_back(self, driver):
        if self.report_options["capture_browser_console_log"] == "always":
            logs = capture_output(driver)
            allure.attach(
                bytes(logs, "utf-8"), "Browser Outputs", AttachmentType.TEXT
            )
