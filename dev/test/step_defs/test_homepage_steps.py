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
def user_login(selenium):
    LoginPage(selenium).navigate_to_url()
    LoginPage(selenium).set_username(properties.VALID_USER)
    LoginPage(selenium).set_password(properties.VALID_PASS)
    LoginPage(selenium).click_login()


@when(parsers.parse('The user clicks on tab "{tab}"'))
def click_tab(selenium, tab):
    HomePage(selenium).click_tab(tab)


@then(parsers.parse('The user enters "{username}" into username search'))
def enter_username_search(selenium, username):
    HomePage(selenium).enter_username(username)


@then("User clicks on search button")
def click_search(selenium):
    HomePage(selenium).click_search()


@then(parsers.parse('The value "{row_value}" is present'))
def check_value(selenium, row_value):
    actual_value = selenium.find_element(*ROW_VALUE).text
    assert actual_value == row_value


@when("User clicks on profile button")
def click_profile(selenium):
    HomePage(selenium).click_profile_bar()


@when("User clicks on logout button")
def click_logout(selenium):
    HomePage(selenium).click_logout()


@then('the home page is displayed')
def login_page_display(selenium):
    assert selenium.find_element_by_id('txtUsername').is_displayed()
