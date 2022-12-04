Feature: Data Drift service API

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

  Scenario: User gets an error instead of a record
    Given a user has an ill-formed bundle
    When they compile the record
    Then the Data Drift service returns an error in the response
    And the status code is "504"
    And the status description is "Failure"
    And the message is "Failed to create DataDriftRecord."

  Scenario: User gets an error instead of a report
    Given a user has an corrupt record
    When they compile the report
    Then the Data Drift service returns an error in the response
    And the status code is "506"
    And the status description is "Failure"
    And the message is "Failed to create DataDriftReport."
