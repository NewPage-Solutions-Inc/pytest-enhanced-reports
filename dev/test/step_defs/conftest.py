"""
This module contains shared fixtures, steps, and hooks.
"""
import logging
import pytest
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver
from selenium.webdriver.support.ui import WebDriverWait
from allure_screenshot import WebDriverEventListener


@pytest.fixture
def selenium(selenium, resize_info):
    selenium.maximize_window()
    driver = EventFiringWebDriver(selenium, WebDriverEventListener(resize_info))
    yield driver
    driver.quit()


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
