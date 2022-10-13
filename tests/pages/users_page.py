from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

ADMIN_TAB = By.ID, "menu_admin_viewAdminModule"
USER_MANAGEMENT_TAB = By.ID, "menu_admin_UserManagement"
USERS_MENU = By.ID, "menu_admin_viewSystemUsers"
SEARCH_FIELD = By.ID, "searchSystemUser_userName"


class UserPage:
    def __init__(self, driver):
        self.driver = driver

    def hover_and_click_tab(self):
        action = ActionChains(self.driver)
        admin_tab = self.driver.find_element(*ADMIN_TAB)
        user_management_tab = self.driver.find_element(*USER_MANAGEMENT_TAB)
        user_button = self.driver.find_element(*USERS_MENU)
        action.move_to_element(admin_tab).move_to_element(user_management_tab).click(
            user_button
        ).perform()
