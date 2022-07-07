import allure
import pytest
from allure_commons.types import AttachmentType

from dev import properties
from pytest_bdd import scenarios, given, when, then, parsers
from dev.pages.login_page import LoginPage
from selenium.webdriver.common.by import By


# Scenarios
scenarios('../features/login.feature')

# Locators

ADMIN_TAB = By.ID, "menu_admin_viewAdminModule"
LOGIN_MESSAGE = By.ID, "spanMessage"


# Given Steps

@given('the OpenHRM home page is displayed')
def open_url(browser):
    LoginPage(browser).navigate_to_url()
    allure.attach(browser.get_screenshot_as_png(), name="HomePageScreen",
                  attachment_type=AttachmentType.PNG)
    assert browser.find_element_by_id('txtUsername').is_displayed()


@when(parsers.parse('the user enters username "{username}"'))
def enter_username(browser, logger, username):
    LoginPage(browser).set_username(username)
    allure.attach(browser.get_screenshot_as_png(), name="EnteringUserName",
                  attachment_type=AttachmentType.PNG)
    logger.info('Username set')


@when(parsers.parse('the user enters password "{password}"'))
def enter_password(browser, logger, password):
    LoginPage(browser).set_password(password)
    allure.attach(browser.get_screenshot_as_png(), name="EnteringPassword",
                  attachment_type=AttachmentType.PNG)
    logger.info('Password set')


@when('the user clicks on login button')
def click_login(browser):
    with allure.step("Login Click"):
        LoginPage(browser).click_login()
    allure.attach(browser.get_screenshot_as_png(), name="ClickingLoginButton",
                  attachment_type=AttachmentType.PNG)


@allure.severity(allure.severity_level.MINOR)
@then('Home page is displayed')
def home_page(browser, logger):
    allure.attach(browser.get_screenshot_as_png(), name="VerifyingHomePage",
                  attachment_type=AttachmentType.PNG)
    assert browser.find_element(*ADMIN_TAB).is_displayed()
    logger.info('Login Test Passed')


@allure.severity(allure.severity_level.MINOR)
@then('Credentials error is displayed')
def home_page(browser, logger):
    actual_message = browser.find_element(*LOGIN_MESSAGE).text
    allure.attach(browser.get_screenshot_as_png(), name="CredentialsErrorVerification",
                  attachment_type=AttachmentType.PNG)
    assert actual_message == properties.INVALID_CRED_MESSAGE
    logger.info('Credentials Test Passed')


@allure.severity(allure.severity_level.MINOR)
@then('Credentials error for empty field is displayed')
def home_page(browser, logger):
    actual_message = browser.find_element(*LOGIN_MESSAGE).text
    allure.attach(browser.get_screenshot_as_png(), name="CredentialsErrorForEmptyField",
                  attachment_type=AttachmentType.PNG)
    assert actual_message == properties.EMPTY_CRED_MESSAGE
    logger.info('Empty Credentials Test Passed')


@allure.severity(allure.severity_level.MINOR)
@when('the user clicks on the forgot password link')
def forgot_password_page(browser, logger):
    allure.attach(browser.get_screenshot_as_png(), name="ClickForgotPasswordLink",
                  attachment_type=AttachmentType.PNG)
    LoginPage(browser).click_forgot_password()
    logger.info('Forgot password link')


@allure.severity(allure.severity_level.MINOR)
@then('the "Forgot Your Password?" text is shown on the home page')
def forgot_password_page(browser, logger):
    allure.attach(browser.get_screenshot_as_png(), name="ForgotPasswordPage",
                  attachment_type=AttachmentType.PNG)
    assert "Forgot" == "forgot"
    logger.info('Forgot password link Test Passed')
