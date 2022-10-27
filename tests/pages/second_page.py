from selenium.webdriver.common.by import By
from os import getenv

PROJECT_DIR = getenv("PROJECT_DIR", "/tmp")
SITE_URL = f"file://{PROJECT_DIR}/local-app/page2.html"

# Locators
LINK_TO_PAGE_1 = By.ID, "back_to_page1"


class SecondPage:
    def __init__(self, driver):
        self.driver = driver

    def navigate_to_url(self):
        self.driver.get(SITE_URL)

    def click_link_to_page_1(self):
        self.driver.find_element(*LINK_TO_PAGE_1).click()

    def check_current_page(self):
        assert len(self.driver.find_elements(*LINK_TO_PAGE_1)) == 1
