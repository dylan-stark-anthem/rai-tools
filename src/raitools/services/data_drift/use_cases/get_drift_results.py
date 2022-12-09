"""Data Drift results."""

from typing import Dict, List, TypedDict

import pyarrow as pa

from raitools.services.data_drift.data.bundle import Feature
from raitools.services.data_drift.stats import statistical_tests
from raitools.services.data_drift.stats.common import StatisticalTestType

OUTCOME_DESC = {
    True: "reject null hypothesis",
    False: "fail to reject null hypothesis",
}
STATUS_DESC = {
    "reject null hypothesis": "drifted",
    "fail to reject null hypothesis": "not drifted",
}

SIGNIFICANCE_LEVEL = 0.05


class TestResultType(TypedDict):
    """Statistical test result."""

    name: str
    significance_level: float
    test_statistic: float
    p_value: float
    outcome: str


class DriftResultType(TypedDict):
    """Drift result type."""

    name: str
    statistical_test: TestResultType
    drift_status: str


class ResultType(TypedDict):
    """Statistical test result."""

    test_name: str
    drift_result: DriftResultType


def get_result_for_test(
    baseline_data: List, test_data: List, test: StatisticalTestType
) -> TestResultType:
    """Computes result for this test applied to feature data."""
    result = test["method"](baseline_data, test_data)
    is_significant = result["p_value"] <= SIGNIFICANCE_LEVEL
    outcome = OUTCOME_DESC[is_significant]

    return TestResultType(
        name=test["name"],
        significance_level=SIGNIFICANCE_LEVEL,
        test_statistic=result["test_statistic"],
        p_value=result["p_value"],
        outcome=outcome,
    )


def get_drift_result_for_test(
    baseline_data: List,
    test_data: List,
    feature_name: str,
    test_details: StatisticalTestType,
) -> DriftResultType:
    """Gets drift result for this feature and test."""
    result = get_result_for_test(baseline_data, test_data, test_details)
    status = STATUS_DESC[result["outcome"]]

    return DriftResultType(
        name=feature_name, statistical_test=result, drift_status=status
    )


def get_drift_results_for_feature(
    baseline_data: List, test_data: List, feature_name: str, feature_kind: str
) -> ResultType:
    """Gets drift result for all associated tests."""
    test_name = statistical_tests[feature_kind]["name"]
    test_details = statistical_tests[feature_kind]
    result = get_drift_result_for_test(
        baseline_data, test_data, feature_name, test_details
    )

    return ResultType(test_name=test_name, drift_result=result)


DriftResultsType = Dict[str, ResultType]


def get_drift_results(
    baseline_data: pa.Table,
    test_data: pa.Table,
    feature_mapping: Dict[str, Feature],
) -> DriftResultsType:
    """Gets drift results for all features."""
    results = {
        feature_name: get_drift_results_for_feature(
            baseline_data.column(feature_name).to_pylist(),
            test_data.column(feature_name).to_pylist(),
            feature_details.name,
            feature_details.kind,
        )
        for feature_name, feature_details in feature_mapping.items()
    }
    return results
