# This module contains shared fixtures, steps, and hooks.
from tests.util.common_actions import *
import pytest
import logging

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption(
        "--headless", action="store", default="true", help="run test headless"
    )


@pytest.fixture
def chrome_options(chrome_options, request):
    headless = request.config.getoption("--headless")
    if headless == "true":
        chrome_options.add_argument("--headless")
    return chrome_options


@pytest.fixture
def selenium(selenium, screenshotting_driver, request):
    enhanced_driver = None
    try:
        enhanced_driver = screenshotting_driver(selenium)
    except Exception as e:
        logger.error(e)

    yield enhanced_driver if enhanced_driver else selenium

    selenium.quit()
