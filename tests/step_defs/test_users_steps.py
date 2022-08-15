import logging

import pytest

from tests import properties
from pytest_bdd import scenarios, given, when, then, parsers
from tests.pages.login_page import LoginPage
from tests.pages.users_page import UserPage
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)

scenarios('../features/userpage.feature')

# Locators
USER_MANAGEMENT_TAB = By.ID, 'menu_admin_UserManagement'
USERS_MENU = By.ID, 'menu_admin_viewSystemUsers'
SEARCH_BUTTON = By.ID, "searchBtn"


@given('The user logs in to OpenHRM')
def user_login(selenium):
    LoginPage(selenium).navigate_to_url()
    LoginPage(selenium).set_username(properties.VALID_USER)
    LoginPage(selenium).set_password(properties.VALID_PASS)
    LoginPage(selenium).click_login()


@when('User clicks User menu')
def click_user_menu(selenium):
    UserPage(selenium).hover_and_click_tab()
    logger.info("User menu selected")


@then('Search field is present')
def verify_search_button(selenium):
    assert selenium.find_element(*SEARCH_BUTTON).is_displayed()
    logger.info("Search field is present")


@when('the user selects user management under admin option in portal')
def click_user_management(selenium):
    pytest.skip("this is skipped")
    logger.info("User management option selected")


@then('the user is able to see system users')
def verify_search_button(selenium):
    pytest.skip('skipped for testing purposes')
    logger.info("the user is able to see system users")
