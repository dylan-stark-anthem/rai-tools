"""Data Drift results."""

from typing import Callable, Dict, List, TypedDict

import pyarrow as pa

from raitools.services.data_drift.domain.statistical_test_result import (
    StatisticalTestResult,
)
from raitools.services.data_drift.stats import statistical_tests


class Result(TypedDict):
    """Statistical test result."""

    test_name: str
    drift_result: StatisticalTestResult


def get_drift_result(
    test_fn: Callable, baseline_data: List, test_data: List
) -> StatisticalTestResult:
    """Computes drift result."""
    return test_fn(baseline_data, test_data)


def get_drift_results(
    baseline_data: pa.Table,
    test_data: pa.Table,
    feature_mapping: Dict,
) -> Dict:
    """Computes drift results."""
    drift_results: Dict[str, Result] = {}
    for feature_name, feature_details in feature_mapping.items():
        kind = feature_details.kind
        for test_name, test_details in statistical_tests[kind].items():
            drift_result = get_drift_result(
                test_details["method"],
                baseline_data.column(feature_name).to_pylist(),
                test_data.column(feature_name).to_pylist(),
            )
            drift_results[feature_name] = dict(
                test_name=test_name, drift_result=drift_result
            )

    OUTCOME_DESC = {
        True: "reject null hypothesis",
        False: "fail to reject null hypothesis",
    }
    STATUS_DESC = {
        "reject null hypothesis": "drifted",
        "fail to reject null hypothesis": "not drifted",
    }

    significance_level = 0.05

    results = {}
    for feature_name, drift_result_ in drift_results.items():
        outcome = OUTCOME_DESC[
            drift_result_["drift_result"].p_value <= significance_level
        ]
        drift_status = STATUS_DESC[outcome]
        results[feature_name] = dict(
            name=feature_name,
            statistical_test=dict(
                name=drift_result_["test_name"],
                result=drift_result_["drift_result"],
                significance_level=significance_level,
                outcome=outcome,
            ),
            drift_status=drift_status,
        )
    return results
