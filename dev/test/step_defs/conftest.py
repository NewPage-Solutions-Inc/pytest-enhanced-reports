"""
This module contains shared fixtures, steps, and hooks.
"""
import logging

import allure
import pytest
from allure_commons.types import AttachmentType
from pytest_selenium.drivers.chrome import chrome_options
from selenium import webdriver
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

from dev.utilities.event_capture import MyListener


def pytest_bdd_after_step(request, feature, scenario, step, step_func):
    browser = request.getfixturevalue('selenium')
    allure.attach(browser.get_screenshot_as_png(), name="screenshot", attachment_type=AttachmentType.PNG)


def pytest_bdd_step_error(request, feature, scenario, step, step_func):
    browser = request.getfixturevalue('selenium')
    allure.attach(browser.get_screenshot_as_png(), name="screenshot", attachment_type=AttachmentType.PNG)


'''
@pytest.fixture
def browser():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    b = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    b.implicitly_wait(30)
    yield b
    b.quit()
'''


@pytest.fixture
def selenium(selenium):
    selenium.implicitly_wait(10)
    selenium.maximize_window()
    edriver = EventFiringWebDriver(selenium, MyListener())
    yield edriver
    edriver.quit()


@pytest.fixture
def exp_wait():
    wait = WebDriverWait(selenium, 30)
    yield wait


@pytest.fixture()
def logger():
    # Logger Settings
    logging.basicConfig(
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    yield logger
