import logging

import allure
from pytest_bdd import scenarios, given, when, then, parsers
from tests.pages.first_page import FirstPage
from tests.pages.second_page import SecondPage

logger = logging.getLogger(__name__)
scenarios("../features/first_page.feature")


@given("Start Website")
def open_url(selenium):
    FirstPage(selenium).navigate_to_url()
    FirstPage(selenium).check_first_page_display()


@when(parsers.parse("User enters first name {first_name}"))
def enter_first_name(selenium, first_name):
    FirstPage(selenium).set_first_name(first_name)
    logger.info("first_name is entered")


@when(parsers.parse("User enters last name {last_name}"))
def enter_last_name(selenium, last_name):
    FirstPage(selenium).set_last_name(last_name)
    logger.info("last_name is entered")


@when(parsers.parse("User enters email {email}"))
def enter_email(selenium, email):
    FirstPage(selenium).set_email(email)
    logger.info("email is entered")


@when(parsers.parse("User enters phone {phone}"))
def enter_phone(selenium, phone):
    FirstPage(selenium).set_phone(phone)
    logger.info("last_name is entered")


@when("User clicks on submit button")
def click_login(selenium):
    with allure.step("Submit Click"):
        FirstPage(selenium).click_submit()


@allure.severity(allure.severity_level.MINOR)
@then("User can see welcome message for new user")
def verify_message_new_user(selenium):
    FirstPage(selenium).check_message_content("Welcome new user!")


@allure.severity(allure.severity_level.MINOR)
@then("User can see welcome message for existing user")
def verify_message_existing_user(selenium):
    FirstPage(selenium).check_message_content("Welcome back!")


@when("User clicks on go to page 2 button")
def click_go_to_page2(selenium):
    with allure.step("Go To Page 2 Click"):
        FirstPage(selenium).click_link_to_page_2()


@then("User can see page 2")
def verify_page_2(selenium):
    SecondPage(selenium).check_current_page()


@when("User clicks on go to page 1 button")
def click_go_to_page1(selenium):
    SecondPage(selenium).click_link_to_page_1()


@then("User can see page 1")
def verify_page_1(selenium):
    FirstPage(selenium).check_first_page_display()
