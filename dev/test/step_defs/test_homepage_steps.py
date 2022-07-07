import allure
from allure_commons.types import AttachmentType

from dev import properties
from pytest_bdd import scenarios, given, when, then, parsers
from dev.pages.login_page import LoginPage
from dev.pages.home_page import HomePage
from selenium.webdriver.common.by import By


# Scenarios
scenarios('../features/homepage.feature')

# Locators
ROW_VALUE = By.XPATH, '//a[@href="saveSystemUser?userId=1"]'


@given('The user logs in to OpenHRM')
def user_login(browser):
    LoginPage(browser).navigate_to_url()
    LoginPage(browser).set_username(properties.VALID_USER)
    LoginPage(browser).set_password(properties.VALID_PASS)
    LoginPage(browser).click_login()
    allure.attach(browser.get_screenshot_as_png(), name="HomePageScreenAfterLogin",
                  attachment_type=AttachmentType.PNG)


@when(parsers.parse('The user clicks on tab "{tab}"'))
def click_tab(browser, tab):
    allure.attach(browser.get_screenshot_as_png(), name="clickingTab",
                  attachment_type=AttachmentType.PNG)
    HomePage(browser).click_tab(tab)


@then(parsers.parse('The user enters "{username}" into username search'))
def enter_username_search(browser, username):
    HomePage(browser).enter_username(username)
    allure.attach(browser.get_screenshot_as_png(), name="searchUserName",
                  attachment_type=AttachmentType.PNG)


@then("User clicks on search button")
def click_search(browser):
    HomePage(browser).click_search()
    allure.attach(browser.get_screenshot_as_png(), name="ClickSearch",
                  attachment_type=AttachmentType.PNG)


@then(parsers.parse('The value "{row_value}" is present'))
def check_value(browser, row_value):
    actual_value = browser.find_element(*ROW_VALUE).text
    allure.attach(browser.get_screenshot_as_png(), name="ValueVerification",
                  attachment_type=AttachmentType.PNG)

    assert actual_value == row_value


@when("User clicks on profile button")
def click_profile(browser):
    HomePage(browser).click_profile_bar()
    allure.attach(browser.get_screenshot_as_png(), name="ClickingProfile",
                  attachment_type=AttachmentType.PNG)


@when("User clicks on logout button")
def click_logout(browser):
    HomePage(browser).click_logout()
    allure.attach(browser.get_screenshot_as_png(), name="Logout",
                  attachment_type=AttachmentType.PNG)


@then('the home page is displayed')
def login_page_display(browser):
    allure.attach(browser.get_screenshot_as_png(), name="HomePageScreen",
                  attachment_type=AttachmentType.PNG)
    assert browser.find_element_by_id('txtUsername').is_displayed()
