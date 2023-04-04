import pytest
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.ie.options import Options as IEOptions

logging.basicConfig(
    filename="reports/tests.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption(
        "--headless", action="store", default="True", help="run test headless"
    )


@pytest.fixture
def old_driver(request):
    browser = request.config.getoption("--driver")
    caps = {"goog:loggingPrefs": {"browser": "ALL"}}
    window_size = "1024,768"
    headless = request.config.getoption("--headless") == "True"
    logger.error(browser)
    if not browser or browser.lower() in ["chrome", "gc", "googlechrome"]:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f"--window-size={window_size}")

        if headless:
            chrome_options.add_argument("--headless")

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
    elif browser.lower() in ["firefox", "ff"]:
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument(f"--window-size={window_size}")

        return webdriver.Firefox(desired_capabilities=caps, options=options)
    elif browser.lower() in ["edge", "microsoftedge"]:
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument(f"--window-size={window_size}")

        return webdriver.Edge(capabilities=caps, options=options)
    elif browser.lower() in ["safari"]:
        options = SafariOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument(f"--window-size={window_size}")

        return webdriver.Safari(desired_capabilities=caps, options=options)
    elif browser.lower() in ["ie", "internetexplorer"]:
        options = IEOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument(f"--window-size={window_size}")

        return webdriver.Ie(desired_capabilities=caps, options=options)

    assert False, f"browser {browser} isn't supported yet."


@pytest.fixture
def driver(old_driver, enhance_driver):
    enhanced_driver = None
    try:
        enhanced_driver = enhance_driver(old_driver)
    except Exception as e:
        logger.error(e)

    yield enhanced_driver if enhanced_driver else old_driver

    old_driver.quit()
