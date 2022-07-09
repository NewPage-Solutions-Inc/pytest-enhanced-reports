import allure
import pytest

from dev import properties
from pytest_bdd import scenarios, given, when, then, parsers
from dev.pages.login_page import LoginPage
from dev.pages.users_page import UserPage
from selenium.webdriver.common.by import By


# Scenarios
scenarios('../features/userpage.feature')

# Locators
USER_MANAGEMENT_TAB = By.ID, 'menu_admin_UserManagement'
USERS_MENU = By.ID, 'menu_admin_viewSystemUsers'
SEARCH_BUTTON = By.ID, "searchBtn"


@given('The user logs in to OpenHRM')
def user_login(browser):
    LoginPage(browser).navigate_to_url()
    LoginPage(browser).set_username(properties.VALID_USER)
    LoginPage(browser).set_password(properties.VALID_PASS)
    LoginPage(browser).click_login()


@when('User clicks User menu')
def click_user_menu(browser, logger):
    UserPage(browser).hover_and_click_tab()
    logger.info("User menu selected")


@then('Search field is present')
def verify_search_button(browser, logger):
    assert browser.find_element(*SEARCH_BUTTON).is_displayed()
    logger.info("Search field is present")


@when('the user selects user management under admin option in portal')
def click_user_management(browser, logger):
    pytest.skip("this is skipped")
    logger.info("User management option selected")


@then('the user is able to see system users')
def verify_search_button(browser, logger):
    pytest.skip('skipped for testing purposes')
    logger.info("the user is able to see system users")
