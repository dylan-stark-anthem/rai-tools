Feature: Data Drift service API for getting a report

  Scenario: User gets a report
    Given a user has a record
    When they compile the report
    Then the Data Drift service returns a report in the response
    And the status code is "200"
    And the status description is "Success"
    And the message is "DataDriftReport was retrieved successfully"

  Scenario: User gets an error instead of a report
    Given a user has an corrupt record
    When they compile the report
    Then the Data Drift service returns an error in the response
    And the status code is "506"
    And the status description is "Failure"
    And the message is "Failed to create DataDriftReport."
