Feature: Data Drift service API

  @wip
  Scenario: User gets a record
    Given a user has a well-formed bundle
    When they compile the record
    Then the Data Drift service returns a record in the response
    And the status code is "200"
    And the status description is "Success"
    And the message is "DataDriftRecord was retrieved successfully"

  Scenario: User gets a report
    Given a user has a record
    When they compile the report
    Then the Data Drift service returns a report in the response
    And the status code is "200"
    And the status description is "Success"
    And the message is "DataDriftReport was retrieved successfully"
