"""
This module contains shared fixtures, steps, and hooks.
"""
import logging

import allure
import pytest
from allure_commons.types import AttachmentType
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait


def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    print("-------This is after step method-------")
    print(f'Step Name: {step}')
    return step
    #allure.attach(browser.get_screenshot_as_png(), name=request.function.__name__, attachment_type=AttachmentType.PNG)


def take_screenshot(browser, name):
    allure.attach(browser.get_screenshot_as_png(), name=name, attachment_type=AttachmentType.PNG)


@pytest.fixture
def browser():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    b = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    b.implicitly_wait(30)
    yield b
    b.quit()


@pytest.fixture
def exp_wait():
    wait = WebDriverWait(browser, 30)
    yield wait


@pytest.fixture()
def logger():
    # Logger Settings
    logging.basicConfig(
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    yield logger
