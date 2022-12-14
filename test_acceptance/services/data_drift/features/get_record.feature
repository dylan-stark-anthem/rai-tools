Feature: Data Drift service API for getting a record

  Scenario: User gets a record
    Given a user has a well-formed bundle
    When they compile the record
    Then the Data Drift service returns a record in the response
    And the status code is "200"
    And the status description is "Success"
    And the message is "DataDriftRecord was retrieved successfully"

  Scenario: User gets an error instead of a record
    Given a user has an ill-formed bundle
    When they compile the record
    Then the Data Drift service returns an error in the response
    And the status code is "504"
    And the status description is "Failure"
    And the message is "Failed to create DataDriftRecord."
