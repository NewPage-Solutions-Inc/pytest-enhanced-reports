Feature: Test First Page
  Background:
    Given I open first page

  @existing_user
  Scenario: Existing user submit
    When User enters first name Existing
    And User enters last name User
    And User enters email test@test.com
    And User enters phone 1234567890
    And User clicks on submit button
    Then User can see welcome message for existing user

  Scenario: Run Test for clean up file
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

  Scenario: Run Test for browser's outputs
    When I click go to page 2
