from selenium.webdriver.support.abstract_event_listener import AbstractEventListener
from selenium.webdriver.remote.webdriver import WebDriver
from allure_screenshot import _take_screenshot
from browser_output_manager import capture_output_and_attach_to_allure


class WebDriverEventListener(AbstractEventListener):
    def __init__(self, screen_shot_plugin_options: dict = {}, browser_output_plugin_options: dict = {}):
        self.screen_shot_plugin_options = screen_shot_plugin_options
        self.browser_output_plugin_options = browser_output_plugin_options

    def after_navigate_to(self, url, driver: WebDriver):
        _take_screenshot(f"Navigation to {url}", self.screen_shot_plugin_options, driver)
        if self.browser_output_plugin_options:
            capture_output_and_attach_to_allure(driver)

    def after_click(self, element, driver):
        _take_screenshot("Click", self.screen_shot_plugin_options, driver)
        if self.browser_output_plugin_options:
            capture_output_and_attach_to_allure(driver)

    def after_change_value_of(self, element, driver):
        _take_screenshot("Keyboard input", self.screen_shot_plugin_options, driver)
        if self.browser_output_plugin_options:
            capture_output_and_attach_to_allure(driver)

    def after_execute_script(self, script, driver):
        _take_screenshot("JS execution", self.screen_shot_plugin_options, driver)
        if self.browser_output_plugin_options:
            capture_output_and_attach_to_allure(driver)

    def after_navigate_back(self, driver):
        if self.browser_output_plugin_options:
            capture_output_and_attach_to_allure(driver)
