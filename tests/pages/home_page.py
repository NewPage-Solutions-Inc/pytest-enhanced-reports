from selenium.webdriver.common.by import By

# Locators

USERNAME_SEARCH = By.ID, "searchSystemUser_userName"
SEARCH_BUTTON = By.ID, "searchBtn"
PROFILE_BAR = By.ID, "welcome"
LOGOUT_BUTTON = By.XPATH, '//a[@href="/index.php/auth/logout"]'


class HomePage:
    def __init__(self, driver):
        self.driver = driver

    def click_tab(self, tab):
        self.driver.find_element(By.LINK_TEXT, tab).click()

    def enter_username(self, username):
        self.driver.find_element(*USERNAME_SEARCH).send_keys(username)

    def click_search(self):
        self.driver.find_element(*SEARCH_BUTTON).click()

    def click_profile_bar(self):
        self.driver.find_element(*PROFILE_BAR).click()

    def click_logout(self):
        self.driver.find_element(*LOGOUT_BUTTON).click()
