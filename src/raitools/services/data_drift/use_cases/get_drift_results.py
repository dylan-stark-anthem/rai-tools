"""Data Drift results."""

from typing import Dict
import pyarrow as pa

from raitools.services.data_drift.domain.stats import statistical_tests


def get_drift_results(
    baseline_data: pa.Table,
    test_data: pa.Table,
    feature_mapping: Dict,
) -> Dict:
    """Computes drift results."""
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
    for feature_name, feature_details in feature_mapping.items():
        kind = feature_details.kind
        tests = statistical_tests[kind]
        for test_name, test_details in tests.items():
            result = test_details["method"](
                baseline_data.column(feature_name).to_pylist(),
                test_data.column(feature_name).to_pylist(),
            )
            outcome = OUTCOME_DESC[result.p_value <= significance_level]
            drift_status = STATUS_DESC[outcome]
            results[feature_name] = dict(
                name=feature_name,
                statistical_test=dict(
                    name=test_name,
                    result=result,
                    significance_level=significance_level,
                    outcome=outcome,
                ),
                drift_status=drift_status,
            )
    return results
