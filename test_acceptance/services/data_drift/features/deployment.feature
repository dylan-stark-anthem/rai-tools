Feature: Data Drift service

  @wip
  Scenario: Successful run creates a record
    Given a user has a well-formed bundle
    When they compile the record
    Then the Data Drift service returns success
