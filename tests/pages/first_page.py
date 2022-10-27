from selenium.webdriver.common.by import By
from os import getenv

PROJECT_DIR = getenv("PROJECT_DIR", "/tmp")
SITE_URL = f"file://{PROJECT_DIR}/local-app/index.html"

# Locators
FIRST_NAME = By.ID, "firstName"
LAST_NAME = By.ID, "lastName"
EMAIL = By.ID, "email"
PHONE = By.ID, "phone"
SUBMIT = By.ID, "submit"

MESSAGE = By.ID, "message"

LINK_TO_PAGE_2 = By.ID, "link_to_page_2"


class FirstPage:
    def __init__(self, driver):
        self.driver = driver

    def navigate_to_url(self):
        self.driver.get(SITE_URL)

    def set_first_name(self, first_name):
        username_field = self.driver.find_element(*FIRST_NAME)
        username_field.send_keys(first_name)

    def set_last_name(self, last_name):
        username_field = self.driver.find_element(*LAST_NAME)
        username_field.send_keys(last_name)

    def set_email(self, email):
        username_field = self.driver.find_element(*EMAIL)
        username_field.send_keys(email)

    def set_phone(self, phone):
        username_field = self.driver.find_element(*PHONE)
        username_field.send_keys(phone)

    def click_submit(self):
        self.driver.find_element(*SUBMIT).click()

    def click_link_to_page_2(self):
        self.driver.find_element(*LINK_TO_PAGE_2).click()

    def check_message_content(self, message):
        curr_message = self.driver.find_element(*MESSAGE).text
        return curr_message == message

    def check_first_page_display(self):
        assert len(self.driver.find_elements(*FIRST_NAME)) == 1
