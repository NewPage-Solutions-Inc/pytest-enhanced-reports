"""
This module contains shared fixtures, steps, and hooks.
"""
import logging

import allure
import pytest
from pytest_bdd import when, parsers, then, given
from selenium.webdriver.common.by import By
from selenium import webdriver

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption(
        "--headless", action="store", default="false", help="run test headless"
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


# helper methods (selenium)
BASE_URL = (
    "https://newpage-solutions-inc.github.io/allure-screenshots/test-site"
)
FIRST_PAGE_URL = f"{BASE_URL}/index.html"
SECOND_PAGE_URL = f"{BASE_URL}/page2.html"

# Locators
FIRST_NAME = By.ID, "firstName"
LAST_NAME = By.ID, "lastName"
EMAIL = By.ID, "email"
PHONE = By.ID, "phone"
SUBMIT = By.ID, "submit"
MESSAGE = By.ID, "message"
LINK_TO_PAGE_2 = By.ID, "link_to_page_2"
LINK_TO_PAGE_1 = By.ID, "back_to_page1"


@given("I open first page")
def open_first_page(selenium):
    selenium.get(FIRST_PAGE_URL)
    check_first_page_displayed(selenium)


@when("I open second page")
def open_second_page(selenium):
    selenium.get(SECOND_PAGE_URL)
    check_second_page_displayed(selenium)


def enter_first_name(selenium, first_name):
    first_name_field = selenium.find_element(*FIRST_NAME)
    first_name_field.send_keys(first_name)
    logger.info("first_name is entered")


@when(parsers.parse("User enters last name {last_name}"))
def enter_last_name(selenium, last_name):
    last_name_field = selenium.find_element(*LAST_NAME)
    last_name_field.send_keys(last_name)
    logger.info("last_name is entered")


@when(parsers.parse("User enters email {email}"))
def enter_email(selenium, email):
    email_field = selenium.find_element(*EMAIL)
    email_field.send_keys(email)
    logger.info("email is entered")


@when(parsers.parse("User enters phone {phone}"))
def enter_phone(selenium, phone):
    phone_field = selenium.find_element(*PHONE)
    phone_field.send_keys(phone)
    logger.info("last_name is entered")


@when("User clicks on submit button")
def click_login(selenium):
    with allure.step("Submit Click"):
        selenium.find_element(*SUBMIT).click()


@allure.severity(allure.severity_level.MINOR)
@then("User can see welcome message for new user")
def verify_message_new_user(selenium):
    check_message_content(selenium, "Welcome new user!")


@allure.severity(allure.severity_level.MINOR)
@then("User can see welcome message for existing user")
def verify_message_existing_user(selenium):
    check_message_content(selenium, "Welcome back!")


@when("I click go to page 2")
def click_go_to_page2(selenium):
    with allure.step("Go To Page 2 Click"):
        selenium.find_element(*LINK_TO_PAGE_2).click()
        check_second_page_displayed(selenium)


@then("I verify page 2 is displayed")
def verify_page_2(selenium):
    check_second_page_displayed(selenium)


@when("User clicks on go to page 1 button")
def click_go_to_page1(selenium):
    selenium.find_element(*LINK_TO_PAGE_1).click()


@then("User can see page 1")
def verify_page_1(selenium):
    check_first_page_displayed(selenium)


def check_first_page_displayed(driver):
    assert len(driver.find_elements(*FIRST_NAME)) == 1


def check_second_page_displayed(driver):
    assert len(driver.find_elements(*LINK_TO_PAGE_1)) == 1


def check_message_content(driver, content):
    message = driver.find_element(*MESSAGE)
    assert message.text == content, "message are different"
