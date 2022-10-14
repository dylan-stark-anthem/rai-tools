"""Setup for simple non-drifted test scenario."""

from collections import defaultdict
from typing import Any, Callable, Dict

import pytest

from raitools.services.data_drift.domain.data_drift_report import DataDriftReportRecord
from raitools.services.data_drift.domain.html_report_builder import (
    HtmlReportBuilder,
    basic_data_summary_maker,
    basic_drift_magnitude_maker,
    basic_drift_summary_maker,
)

from tests.services.data_drift.use_cases.fixtures.common import prepare_record


def simple_undrifted_report_builder_impl(report_data: DataDriftReportRecord) -> str:
    """Creates a report builder for the simple test case."""
    report_builder = HtmlReportBuilder()
    report_builder.timestamp = "1970-01-01 00:00:00"
    report_builder.data_summary_maker = basic_data_summary_maker
    report_builder.drift_summary_maker = basic_drift_summary_maker
    report_builder.drift_magnitude_maker = basic_drift_magnitude_maker
    report_builder.report_data = report_data
    report_builder.compile()
    return report_builder.get()


@pytest.fixture
def simple_undrifted_report_builder() -> Callable[[DataDriftReportRecord], str]:
    """Returms simple report builder method."""
    return simple_undrifted_report_builder_impl


@pytest.fixture
def simple_undrifted_report_html(
    simple_undrifted_report_builder: Callable[[DataDriftReportRecord], str],
) -> str:
    """Creates expected report html for simple test case."""
    simple_undrifted_record = prepare_record("simple_undrifted_record.json")

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

    report_record = DataDriftReportRecord(
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

    simple_undrifted_report_html = simple_undrifted_report_builder(report_record)

    return simple_undrifted_report_html
