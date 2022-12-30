import pytest
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# try:
#     from enhanced_reports import core
#     local_run = False
# except Exception:
#     local_run = True
# if not local_run:
#     pytest_plugins = [
#         "enhanced_reports.core"
#     ]
# from enhanced_reports.core import (
#     pytest_addoption,
#     _report_options,
#     _global_config,
#     _reports,
#     _reports_function_scope,
#     _scenario_name,
#     _local_driver,
#     enhance_driver,
#     _video_capture,
#     _create_wrappers
# )

logging.basicConfig(
    filename="reports/tests.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption(
        "--headless", action="store", default="true", help="run test headless"
    )


@pytest.fixture
def old_driver(request):
    chrome_options = webdriver.ChromeOptions()
    headless = (
        True if request.config.getoption("--headless") == "True" else False
    )
    if headless:
        chrome_options.add_argument("--headless")

    caps = {"goog:loggingPrefs": {"browser": "ALL"}}

    import os

    driver_path = os.getenv("CHROMEWEBDRIVER")
    service = (
        ChromeService(executable_path=driver_path)
        if driver_path
        else ChromeService(ChromeDriverManager().install())
    )

    return webdriver.Chrome(
        desired_capabilities=caps, options=chrome_options, service=service
    )


@pytest.fixture
def driver(old_driver, enhance_driver):
    enhanced_driver = None
    try:
        enhanced_driver = enhance_driver(old_driver)
    except Exception as e:
        logger.error(e)

    yield enhanced_driver if enhanced_driver else old_driver

    old_driver.quit()
