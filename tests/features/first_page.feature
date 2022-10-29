Feature: Test First Page
  Background:
    Given Start Website

  @existing_user
  Scenario: Existing user submit
    When User enters first name Existing
    And User enters last name User
    And User enters email test@test.com
    And User enters phone 1234567890
    And User clicks on submit button
    Then User can see welcome message for existing user

  @new_user
  Scenario: New user submit
    When User enters first name New
    And User enters last name User
    And User enters email new_user@test.com
    And User enters phone 1234567891
    And User clicks on submit button
    Then User can see welcome message for new user

  @multiple_focus
  Scenario: Focus many times on text fields + submit
    When User enters first name Test
    And User enters last name ABC
    And User enters email test@test.com
    And User enters phone 1234567890
    And User clicks on submit button
    And User enters first name ABC
    And User enters last name User
    And User enters email sample@test.com
    And User enters phone 1234567890
    And User clicks on submit button
    Then User can see welcome message for new user

    @navigate_to_page2
    Scenario: Navigate to page 2 and navigate back
      When User clicks on go to page 2 button
      Then User can see page 2
      When User clicks on go to page 1 button
      Then User can see page 1
