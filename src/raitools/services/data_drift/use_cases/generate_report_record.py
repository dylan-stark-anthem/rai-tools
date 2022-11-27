"""Report record (data) generation."""

from collections import defaultdict
from typing import Any, Dict, List
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
    features_list = list(record.results.features.values())

    data_drift_report = DataDriftReportRecord(
        metadata=record.metadata,
        report_name=record.bundle.job_config.report_name,
        dataset_name=record.bundle.job_config.dataset_name,
        dataset_version=record.bundle.job_config.dataset_version,
        model_catalog_id=record.bundle.job_config.model_catalog_id,
        thresholds=_thresholds_map(record.results.features),
        num_total_features=len(record.results.features),
        num_features_drifted=len(_drifted_feature_list(features_list)),
        top_10_features_drifted=len(_top_10_drifted_features_list(features_list)),
        top_20_features_drifted=len(_top_20_drifted_features_list(features_list)),
        fields=_fields(),
        observations=_observations(features_list),
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


def _drifted_feature_list(
    features: List[DriftSummaryFeature],
) -> List[DriftSummaryFeature]:
    drifted_features = [
        feature for feature in features if feature.drift_status == "drifted"
    ]
    return drifted_features


def _top_10_drifted_features_list(
    features: List[DriftSummaryFeature],
) -> List[DriftSummaryFeature]:
    top_10_drifted_features = [
        feature for feature in _drifted_feature_list(features) if feature.rank <= 10
    ]
    return top_10_drifted_features


def _top_20_drifted_features_list(
    features: List[DriftSummaryFeature],
) -> List[DriftSummaryFeature]:
    top_20_drifted_features = [
        feature for feature in _drifted_feature_list(features) if feature.rank <= 20
    ]
    return top_20_drifted_features


def _fields() -> List[str]:
    fields = [
        "rank",
        "importance_score",
        "name",
        "kind",
        "p_value",
        "drift_status",
    ]
    return fields


def _observations(features: List[DriftSummaryFeature]) -> Dict[str, Any]:
    ranked_features = sorted(features, key=lambda x: x.rank)
    observations: Dict[str, Any] = {
        "rank": [feature.rank for feature in ranked_features],
        "importance_score": [feature.importance_score for feature in ranked_features],
        "name": [feature.name for feature in ranked_features],
        "kind": [feature.kind for feature in ranked_features],
        "p_value": [
            feature.statistical_test.result.p_value for feature in ranked_features
        ],
        "drift_status": [feature.drift_status for feature in ranked_features],
    }
    return observations
