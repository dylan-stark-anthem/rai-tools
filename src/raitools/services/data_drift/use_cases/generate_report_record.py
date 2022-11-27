"""Report record (data) generation."""

from collections import defaultdict
from typing import Dict
from raitools.services.data_drift.domain.data_drift_record import (
    DataDriftRecord,
    DriftSummaryFeature,
)
from raitools.services.data_drift.domain.data_drift_report import DataDriftReportRecord


def generate_report_record(record: DataDriftRecord) -> DataDriftReportRecord:
    """Generates a report record from the given data drift record."""
    report_data = compile_report_data(record)
    return report_data


def compile_report_data(record: DataDriftRecord) -> DataDriftReportRecord:
    """Compiles report data from the given record."""
    data_drift_report = DataDriftReportRecord(
        metadata=record.metadata,
        report_name=record.bundle.job_config.report_name,
        dataset_name=record.bundle.job_config.dataset_name,
        dataset_version=record.bundle.job_config.dataset_version,
        model_catalog_id=record.bundle.job_config.model_catalog_id,
        thresholds=_thresholds_map(record.results.features),
        num_total_features=record.results.drift_summary.num_total_features,
        num_features_drifted=record.results.drift_summary.num_features_drifted,
        top_10_features_drifted=record.results.drift_summary.top_10_features_drifted,
        top_20_features_drifted=record.results.drift_summary.top_20_features_drifted,
        fields=record.results.drift_details.fields,
        observations=record.results.drift_details.observations,
        num_rows_baseline_data=record.bundle.data["baseline_data"].num_rows,
        num_columns_baseline_data=record.bundle.data["baseline_data"].num_columns,
        num_rows_test_data=record.bundle.data["test_data"].num_rows,
        num_columns_test_data=record.bundle.data["test_data"].num_columns,
        num_numerical_features=(record.results.data_summary.num_numerical_features),
        num_categorical_features=(record.results.data_summary.num_categorical_features),
    )

    return data_drift_report


def _thresholds_map(
    features: Dict[str, DriftSummaryFeature]
) -> Dict[str, Dict[str, float]]:
    thresholds: Dict[str, Dict[str, float]] = defaultdict(dict)
    for feature in features.values():
        kind = feature.kind
        test_name = feature.statistical_test.name
        threshold = feature.statistical_test.significance_level
        thresholds[kind][test_name] = threshold
    return thresholds
