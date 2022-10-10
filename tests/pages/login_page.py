from selenium.webdriver.common.by import By

SITE_URL = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"

# Locators

USERNAME = By.NAME, "username"
PASSWORD = By.NAME, "password"
LOGIN_BTN = By.XPATH, "//button[@type='submit']"
FORGOT_PWD_LINK = By.XPATH, "//p[text()='Forgot your password? ']"


class LoginPage:
    def __init__(self, driver):
        self.driver = driver

    def navigate_to_url(self):
        self.driver.get(SITE_URL)

    def set_username(self, username):
        username_field = self.driver.find_element(*USERNAME)
        username_field.send_keys(username)

    def set_password(self, password):
        password_field = self.driver.find_element(*PASSWORD)
        password_field.send_keys(password)

    def click_login(self):
        self.driver.find_element(*LOGIN_BTN).click()

    def click_forgot_password(self):
        self.driver.find_element(*FORGOT_PWD_LINK).click()
