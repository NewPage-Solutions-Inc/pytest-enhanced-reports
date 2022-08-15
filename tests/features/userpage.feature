Feature: OpenHRM User Page
Background:
  Given The user logs in to OpenHRM

  @user_add
  Scenario: User Page Displayed
    When User clicks User menu
    Then Search field is present

    Scenario:  Admin user is able to see user management page
    When the user selects user management under admin option in portal
    Then the user is able to see system users
