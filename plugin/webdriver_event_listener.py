from selenium.webdriver.support.abstract_event_listener import AbstractEventListener
from selenium.webdriver.remote.webdriver import WebDriver
from allure_screenshot import take_screenshot, highlight_element_and_take_a_screenshot
from browser_console_manager import capture_output


class WebDriverEventListener(AbstractEventListener):
    def __init__(self, screen_shot_plugin_options: dict = {}, other_configs: dict = {}):
        self.screen_shot_plugin_options = screen_shot_plugin_options
        self.other_configs = other_configs

    def after_navigate_to(self, url, driver: WebDriver):
        take_screenshot(f"Navigation to {url}", self.screen_shot_plugin_options, driver)
        if self.other_configs.get('always_capture_log'):
            capture_output(driver)

    def before_click(self, element, driver):
        if self.other_configs.get('highlight_element'):
            highlight_element_and_take_a_screenshot(element, "Before click", self.screen_shot_plugin_options, driver)

    def after_click(self, element, driver):
        take_screenshot("After click", self.screen_shot_plugin_options, driver)
        if self.other_configs.get('always_capture_log'):
            capture_output(driver)

    def before_change_value_of(self, element, driver):
        if self.other_configs.get('highlight_element'):
            highlight_element_and_take_a_screenshot(element, "Before keyboard input",
                                                    self.screen_shot_plugin_options, driver)

    def after_change_value_of(self, element, driver):
        take_screenshot("After keyboard input", self.screen_shot_plugin_options, driver)
        if self.other_configs.get('always_capture_log'):
            capture_output(driver)

    def after_execute_script(self, script, driver):
        take_screenshot("JS execution", self.screen_shot_plugin_options, driver)
        if self.other_configs.get('always_capture_log'):
            capture_output(driver)

    def after_navigate_back(self, driver):
        if self.other_configs.get('always_capture_log'):
            capture_output(driver)
