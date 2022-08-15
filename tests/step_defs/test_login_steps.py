import logging

import allure
from tests import properties
from pytest_bdd import scenarios, given, when, then, parsers
from tests.pages.login_page import LoginPage
from selenium.webdriver.common.by import By


logger = logging.getLogger(__name__)

scenarios('../features/login.feature')

# Locators

ADMIN_TAB = By.ID, "menu_admin_viewAdminModule"
LOGIN_MESSAGE = By.ID, "spanMessage"


# Given Steps
@given('the OpenHRM home page is displayed')
def open_url(selenium):
    LoginPage(selenium).navigate_to_url()
    assert selenium.find_element_by_id('txtUsername').is_displayed()


@when(parsers.parse('the user enters username "{username}"'))
def enter_username(selenium, username):
    LoginPage(selenium).set_username(username)
    logger.info('Username set')


@when(parsers.parse('the user enters password "{password}"'))
def enter_password(selenium, password):
    LoginPage(selenium).set_password(password)
    logger.info('Password set')


@when('the user clicks on login button')
def click_login(selenium):
    with allure.step("Login Click"):
        LoginPage(selenium).click_login()


@allure.severity(allure.severity_level.MINOR)
@then('Home page is displayed')
def home_page(selenium):
    assert selenium.find_element(*ADMIN_TAB).is_displayed()
    logger.info('Login Test Passed')


@allure.severity(allure.severity_level.MINOR)
@then('Credentials error is displayed')
def home_page(selenium):
    actual_message = selenium.find_element(*LOGIN_MESSAGE).text
    assert actual_message == properties.INVALID_CRED_MESSAGE
    logger.info('Credentials Test Passed')


@allure.severity(allure.severity_level.MINOR)
@then('Credentials error for empty field is displayed')
def home_page(selenium):
    actual_message = selenium.find_element(*LOGIN_MESSAGE).text
    assert actual_message == properties.EMPTY_CRED_MESSAGE
    logger.info('Empty Credentials Test Passed')


@allure.severity(allure.severity_level.MINOR)
@when('the user clicks on the forgot password link')
def forgot_password_page(selenium):
    LoginPage(selenium).click_forgot_password()
    logger.info('Forgot password link')


@allure.severity(allure.severity_level.MINOR)
@then('the "Forgot Your Password?" text is shown on the home page')
def forgot_password_page(selenium):
    assert "Forgot" == "forgot"
    logger.info('Forgot password link Test Passed')
