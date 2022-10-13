"""Setup for simple non-drifted test scenario."""

from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Union

import pyarrow as pa
import pytest

from raitools.services.data_drift.domain.data_drift_record import DataDriftRecord
from raitools.services.data_drift.domain.data_drift_report import DataDriftReportData
from raitools.services.data_drift.domain.html_report_builder import (
    HtmlReportBuilder,
    basic_data_summary_maker,
    basic_drift_magnitude_maker,
    basic_drift_summary_maker,
)

from tests.services.data_drift.use_cases.fixtures.common import create_bundle


@pytest.fixture
def simple_undrifted_record(simple_spec: Dict) -> DataDriftRecord:
    """The expected record for the simple scenario."""
    expected_record_dict = {
        "apiVersion": "raitools/v1",
        "kind": "DataDriftRecord",
        "metadata": {
            "raitools_version": simple_spec["raitools_version"],
        },
        "drift_summary": {
            "features": {
                "numerical_feature_0": {
                    "name": "numerical_feature_0",
                    "kind": "numerical",
                    "rank": 1,
                    "statistical_test": {
                        "name": "kolmogorov-smirnov",
                        "result": {"test_statistic": 0.0, "p_value": 1.0},
                        "significance_level": 0.05,
                        "adjusted_significance_level": simple_spec[
                            "adjusted_significance_level"
                        ],
                        "outcome": "fail to reject null hypothesis",
                    },
                    "drift_status": "not drifted",
                },
                "numerical_feature_1": {
                    "name": "numerical_feature_1",
                    "kind": "numerical",
                    "rank": 2,
                    "statistical_test": {
                        "name": "kolmogorov-smirnov",
                        "result": {"test_statistic": 0.0, "p_value": 1.0},
                        "significance_level": 0.05,
                        "adjusted_significance_level": simple_spec[
                            "adjusted_significance_level"
                        ],
                        "outcome": "fail to reject null hypothesis",
                    },
                    "drift_status": "not drifted",
                },
                "categorical_feature_0": {
                    "name": "categorical_feature_0",
                    "kind": "categorical",
                    "rank": 3,
                    "statistical_test": {
                        "name": "chi-squared",
                        "result": {
                            "test_statistic": 0.0,
                            "p_value": 1.0,
                        },
                        "significance_level": 0.05,
                        "adjusted_significance_level": simple_spec[
                            "adjusted_significance_level"
                        ],
                        "outcome": "fail to reject null hypothesis",
                    },
                    "drift_status": "not drifted",
                },
                "categorical_feature_1": {
                    "name": "categorical_feature_1",
                    "kind": "categorical",
                    "rank": 4,
                    "statistical_test": {
                        "name": "chi-squared",
                        "result": {
                            "test_statistic": 0.0,
                            "p_value": 1.0,
                        },
                        "significance_level": 0.05,
                        "adjusted_significance_level": simple_spec[
                            "adjusted_significance_level"
                        ],
                        "outcome": "fail to reject null hypothesis",
                    },
                    "drift_status": "not drifted",
                },
                "categorical_feature_2": {
                    "name": "categorical_feature_2",
                    "kind": "categorical",
                    "rank": 5,
                    "statistical_test": {
                        "name": "chi-squared",
                        "result": {
                            "test_statistic": 0.0,
                            "p_value": 1.0,
                        },
                        "significance_level": 0.05,
                        "adjusted_significance_level": simple_spec[
                            "adjusted_significance_level"
                        ],
                        "outcome": "fail to reject null hypothesis",
                    },
                    "drift_status": "not drifted",
                },
            },
            "metadata": {
                "num_numerical_features": simple_spec["num_numerical_features"],
                "num_categorical_features": simple_spec["num_categorical_features"],
            },
        },
        "bundle": {
            "job_config": simple_spec["job_config"],
            "data": {
                "baseline_data": {
                    "filename": simple_spec["job_config"]["baseline_data_filename"],
                    "num_rows": simple_spec["num_baseline_observations"],
                    "num_columns": simple_spec["num_features"],
                },
                "test_data": {
                    "filename": simple_spec["job_config"]["test_data_filename"],
                    "num_rows": simple_spec["num_test_observations"],
                    "num_columns": simple_spec["num_features"],
                },
            },
            "manifest": {
                "bundle_path": simple_spec["bundle_path"],
                "job_config_filename": simple_spec["job_config_filename"],
                "baseline_data_filename": simple_spec["job_config"][
                    "baseline_data_filename"
                ],
                "test_data_filename": simple_spec["job_config"]["test_data_filename"],
            },
        },
    }

    expected_record = DataDriftRecord(**expected_record_dict)
    return expected_record


@pytest.fixture
def simple_undrifted_test_data(
    simple_num_observations: int,
    simple_numerical_features: Dict,
    simple_categorical_features: Dict,
    simple_data_schema: pa.Schema,
) -> pa.Table:
    """Test data for simple undrifted scenario."""
    data: Dict[str, List[Union[int, str]]] = {}
    for feature in simple_numerical_features:
        data[feature] = [index for index in range(simple_num_observations)]
    for feature in simple_categorical_features:
        data[feature] = [
            f"category_{index}" for index in range(simple_num_observations)
        ]
    table = pa.Table.from_pydict(data, schema=simple_data_schema)
    return table


@pytest.fixture
def simple_undrifted_bundle_path(
    simple_feature_mapping: Dict,
    simple_baseline_data: pa.Table,
    simple_undrifted_test_data: pa.Table,
    tmp_path: Path,
) -> Path:
    """Path to a simple bundle."""
    job_config_filename = "some_job_config.json"

    bundle_path = create_bundle(
        job_config_filename,
        simple_feature_mapping,
        simple_baseline_data,
        simple_undrifted_test_data,
        tmp_path,
    )

    return bundle_path


def simple_undrifted_report_builder_impl(report_data: DataDriftReportData) -> str:
    """Creates a report builder for the simple test case."""
    report_builder = HtmlReportBuilder()
    report_builder.data_summary_maker = basic_data_summary_maker
    report_builder.drift_summary_maker = basic_drift_summary_maker
    report_builder.drift_magnitude_maker = basic_drift_magnitude_maker
    report_builder.report_data = report_data
    report_builder.compile()
    return report_builder.get()


@pytest.fixture
def simple_undrifted_report_builder() -> Callable[[DataDriftReportData], str]:
    """Returms simple report builder method."""
    return simple_undrifted_report_builder_impl


@pytest.fixture
def simple_undrifted_report_html(
    simple_undrifted_record: DataDriftRecord,
    simple_undrifted_report_builder: Callable[[DataDriftReportData], str],
) -> str:
    """Creates expected report html for simple test case."""
    job_config = simple_undrifted_record.bundle.job_config
    data = simple_undrifted_record.bundle.data

    thresholds: Dict[str, Dict[str, float]] = defaultdict(dict)
    for feature in simple_undrifted_record.drift_summary.features.values():
        kind = feature.kind
        test_name = feature.statistical_test.name
        threshold = feature.statistical_test.adjusted_significance_level
        thresholds[kind][test_name] = threshold

    features = simple_undrifted_record.drift_summary.features.values()
    num_total_features = len(features)

    drifted_features = [
        feature for feature in features if feature.drift_status == "drifted"
    ]
    num_features_drifted = len(drifted_features)

    top_10_drifted_features = [
        feature for feature in drifted_features if feature.rank <= 10
    ]
    num_top_10_features_drifted = len(top_10_drifted_features)

    top_20_drifted_features = [
        feature for feature in drifted_features if feature.rank <= 20
    ]
    num_top_20_features_drifted = len(top_20_drifted_features)

    fields = [
        "rank",
        "name",
        "kind",
        "p_value",
        "drift_status",
    ]
    ranked_features = sorted(features, key=lambda x: x.rank)
    observations: Dict[str, Any] = {
        "rank": [feature.rank for feature in ranked_features],
        "name": [feature.name for feature in ranked_features],
        "kind": [feature.kind for feature in ranked_features],
        "p_value": [
            feature.statistical_test.result.p_value for feature in ranked_features
        ],
        "drift_status": [feature.drift_status for feature in ranked_features],
    }

    report_data = DataDriftReportData(
        report_name=job_config.report_name,
        dataset_name=job_config.dataset_name,
        dataset_version=job_config.dataset_version,
        model_catalog_id=job_config.model_catalog_id,
        thresholds=thresholds,
        num_total_features=num_total_features,
        num_features_drifted=num_features_drifted,
        top_10_features_drifted=num_top_10_features_drifted,
        top_20_features_drifted=num_top_20_features_drifted,
        fields=fields,
        observations=observations,
        num_rows_baseline_data=data["baseline_data"].num_rows,
        num_columns_baseline_data=data["baseline_data"].num_columns,
        num_rows_test_data=data["test_data"].num_rows,
        num_columns_test_data=data["test_data"].num_columns,
        num_numerical_features=(
            simple_undrifted_record.drift_summary.metadata.num_numerical_features
        ),
        num_categorical_features=(
            simple_undrifted_record.drift_summary.metadata.num_categorical_features
        ),
    )

    simple_undrifted_report_html = simple_undrifted_report_builder(report_data)

    return simple_undrifted_report_html
