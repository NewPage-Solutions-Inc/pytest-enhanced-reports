"""
This module contains shared fixtures, steps, and hooks.
"""
import logging
import pytest

logger = logging.getLogger(__name__)


@pytest.fixture
def selenium(selenium, screenshotting_driver):
    selenium.maximize_window()
    enhanced_driver = None
    try:
        enhanced_driver = screenshotting_driver(selenium)
    except Exception as e:
        logger.error(e)

    yield enhanced_driver if enhanced_driver else selenium

    selenium.quit()
