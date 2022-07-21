"""
This module contains shared fixtures, steps, and hooks.
"""
import logging
import base64
import allure
from PIL import Image
from io import BytesIO
import pytest
from allure_commons.types import AttachmentType
from selenium.webdriver.support.abstract_event_listener import AbstractEventListener
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver
from selenium.webdriver.support.ui import WebDriverWait
from dev import settings
from dev.test.step_defs.test_strings import test_valid_size, test_get_image_details


@pytest.fixture
def selenium(selenium, request):
    selenium.implicitly_wait(10)
    selenium.maximize_window()
    edriver = EventFiringWebDriver(selenium, MyListener())
    yield edriver
    data = edriver.get_log('browser')
    print('----browser console data----')
    print(data)
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

@pytest.fixture
def get_image_details(request):
    ima = request.getfixturevalue('image_size')
    driver = request.getfixturevalue('selenium')
    print('The get_image_details value:')
    p = ima / 100
    print(p)
    img = Image.open(BytesIO(base64.b64decode(driver.get_screenshot_as_base64())))
    print('--get_image_details type of image_size')
    print(type(image_size))
    actual_size = img.size
    print('---get_image_details size of image is')
    print(actual_size)
    w, h = img.size
    print('---get_image_details Height---')
    print(h)
    print('---get_image_details Width---')
    print(w)
    print('--get_image_details after percentage_change--')
    print('get_image_details new width')
    nw = float(w) * p
    print(nw)
    print('get_image_details new height')
    nh = float(h) * p
    print(nh)
    return nw, nh


def pytest_addoption(parser):
    parser.addoption("--imagereduction", action="store", default=0)


@pytest.fixture
def image_size(pytestconfig):
    yield int(pytestconfig.getoption("imagereduction"))


# Below hooks can be used to take screenshots if needed
def pytest_bdd_after_step(request, feature, scenario, step, step_func):
    browser = request.getfixturevalue('selenium')
    ima = request.getfixturevalue('image_size')
    b = test_calculate_resolution(browser, ima)
    allure.attach(b, name="screenshot", attachment_type=AttachmentType.PNG)

'''
def pytest_bdd_step_error(request, feature, scenario, step, step_func):
    browser = request.getfixturevalue('selenium')
    allure.attach(browser.get_screenshot_as_png(), name="screenshot", attachment_type=AttachmentType.PNG)
'''
# below fixture can be used for chrome using webdriver manager
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


class MyListener(AbstractEventListener):

    def before_navigate_to(self, url, driver):
        print("Before navigating to ", url)

    def after_navigate_to(self, url, driver):
        print("after_navigate_to ", driver.current_url)
        image = takes_screenshot_for_allure(driver)
        allure.attach(image, name="Navigate", attachment_type=AttachmentType.PNG)

    def before_navigate_back(self, driver):
        print("before navigating back ", driver.current_url)

    def after_navigate_back(self, driver):
        print("After navigating back ", driver.current_url)

    def before_navigate_forward(self, driver):
        print("before navigating forward ", driver.current_url)

    def after_navigate_forward(self, driver):
        print("After navigating forward ", driver.current_url)

    def before_find(self, by, value, driver):
        print("before find")

    def after_find(self, by, value, driver):
        print("after_find")

    def before_click(self, element, driver):
        print("before_click")

    def after_click(self, element, driver):
        image = takes_screenshot_for_allure(driver)
        allure.attach(image, name="After_Click", attachment_type=AttachmentType.PNG)
        print('--------screenshot saved in allure------')

    def before_change_value_of(self, element, driver):
        print("before_change_value_of")

    def after_change_value_of(self, element, driver):
        image = takes_screenshot_for_allure(driver)
        allure.attach(image, name="After_Sending_Keys", attachment_type=AttachmentType.PNG)

    def before_execute_script(self, script, driver):
        print("before_execute_script")

    def after_execute_script(self, script, driver):
        print("after_execute_script")

    def before_close(self, driver):
        print("before_close")

    def after_close(self, driver):
        print("after_close")

    def before_quit(self, driver):
        print("before_quit")

    def after_quit(self, driver):
        print("after_quit")

    def on_exception(self, exception, driver):
        print("on_exception")


def takes_screenshot_for_allure(driver):
    if image_size == 0:
        print('in the default value section')
        # open the image in memory
        img = Image.open(BytesIO(base64.b64decode(driver.get_screenshot_as_base64())))
        img.thumbnail((int(settings.IMAGE_HEIGHT), int(settings.IMAGE_WIDTH)))
        img.save("reports/screenshot.png")
        with open("reports/screenshot.png", 'rb') as image:
            file = image.read()
            byte_array = bytearray(file)
        return byte_array
    else:
        print('The user sent input value:')
        p = image_size() / 100
        print(p)
        img = Image.open(BytesIO(base64.b64decode(driver.get_screenshot_as_base64())))
        print('--type of image_size')
        print(type(image_size))
        actual_size = img.size
        print('---size of image is')
        print(actual_size)
        w, h = img.size
        print('---Height---')
        print(h)
        print('---Width---')
        print(w)
        print('--after percentage_change--')
        print('new width')
        nw = float(w) * p
        print(nw)
        print('new height')
        nh = float(h) * p
        print(nh)
        img.thumbnail((int(nw), int(nh)))
        img.save("reports/screenshot.png")
        with open("reports/screenshot.png", 'rb') as image:
            file = image.read()
            byte_array = bytearray(file)
        return byte_array


def test_calculate_resolution(driver, ima):
    print('The user sent input value:')
    p = ima / 100
    print(p)
    img = Image.open(BytesIO(base64.b64decode(driver.get_screenshot_as_base64())))
    print('--type of image_size')
    print(type(image_size))
    actual_size = img.size
    print('---size of image is')
    print(actual_size)
    w, h = img.size
    print('---Height---')
    print(h)
    print('---Width---')
    print(w)
    print('--after percentage_change--')
    print('new width')
    nw = float(w) * p
    print(nw)
    print('new height')
    nh = float(h) * p
    print(nh)
    img.thumbnail((int(nw), int(nh)))
    img.save("reports/screenshot.png")
    with open("reports/screenshot.png", 'rb') as image:
        file = image.read()
        byte_array = bytearray(file)
    return byte_array


def takes_screenshot_for_allure_new(driver):
    if image_size == 0:
        print('in the default value section')
        # open the image in memory
        img = Image.open(BytesIO(base64.b64decode(driver.get_screenshot_as_base64())))
        img.thumbnail((int(settings.IMAGE_HEIGHT), int(settings.IMAGE_WIDTH)))
        img.save("reports/screenshot.png")
        with open("reports/screenshot.png", 'rb') as image:
            file = image.read()
            byte_array = bytearray(file)
        return byte_array
    else:
        print('The user sent input value:')
        a, b = test_get_image_details
        img = Image.open(BytesIO(base64.b64decode(driver.get_screenshot_as_base64())))
        img.thumbnail((int(a), int(b)))
        img.save("reports/screenshot.png")
        with open("reports/screenshot.png", 'rb') as image:
            file = image.read()
            byte_array = bytearray(file)
        return byte_array
