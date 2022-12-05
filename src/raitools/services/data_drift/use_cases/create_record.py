"""Process data drift bundle."""

from collections import defaultdict
from datetime import datetime, timezone
from operator import attrgetter
from typing import Any, Dict, List, Optional
import uuid

import pyarrow as pa

from raitools.services.data_drift.domain.bundle import Bundle
from raitools.services.data_drift.domain.data_drift_record import (
    BundleData,
    BundleManifest,
    DataDriftRecord,
    DriftSummaryFeature,
    FeatureStatisticalTest,
    RecordBundle,
    RecordDataSummary,
    RecordDriftDetails,
    RecordDriftSummary,
    RecordResults,
    ResultMetadata,
)
from raitools.services.data_drift.domain.stats import statistical_tests


def create_record_from_bundle(
    bundle: Bundle,
    bundle_filename: str,
    timestamp: Optional[str] = None,
    uuid: Optional[str] = None,
) -> DataDriftRecord:
    """Processes a data drift bundle."""
    record_bundle = _compile_bundle_for_record(bundle, bundle_filename)
    results = _compile_drift_results_for_record(bundle, timestamp, uuid)

    record = DataDriftRecord(
        bundle=record_bundle,
        results=results,
    )

    return record


def _compile_bundle_for_record(bundle: Bundle, bundle_filename: str) -> RecordBundle:
    """Creates record bundle."""
    record_bundle = RecordBundle(
        job_config=bundle.job_config,
        data={
            "baseline_data": BundleData(
                filename=bundle.job_config.baseline_data_filename,
                num_rows=bundle.baseline_data.num_rows,
                num_columns=bundle.baseline_data.num_columns,
            ),
            "test_data": BundleData(
                filename=bundle.job_config.test_data_filename,
                num_rows=bundle.test_data.num_rows,
                num_columns=bundle.test_data.num_columns,
            ),
        },
        manifest=BundleManifest(
            bundle_filename=bundle_filename,
            job_config_filename=bundle.job_config_filename,
            feature_mapping_filename=bundle.feature_mapping_filename,
            baseline_data_filename=bundle.baseline_data_filename,
            test_data_filename=bundle.test_data_filename,
        ),
    )
    return record_bundle


def _compile_drift_results_for_record(
    bundle: Bundle, timestamp: Optional[str] = None, uuid: Optional[str] = None
) -> RecordResults:
    """Creates drift summary for record."""
    if not timestamp:
        timestamp = _timestamp()
    if not uuid:
        uuid = _uuid()

    features = bundle.feature_mapping.feature_mapping
    num_numerical_features = _compute_num_feature_kind(features, "numerical")
    num_categorical_features = _compute_num_feature_kind(features, "categorical")

    drift_summary_features = _compile_features_for_drift_summary(
        bundle.baseline_data,
        bundle.test_data,
        features,
    )

    features_list = list(drift_summary_features.values())

    results = RecordResults(
        metadata=ResultMetadata(
            report_name=bundle.job_config.report_name,
            timestamp=timestamp,
            uuid=uuid,
            thresholds=_thresholds_map(drift_summary_features),
        ),
        data_summary=RecordDataSummary(
            num_numerical_features=num_numerical_features,
            num_categorical_features=num_categorical_features,
        ),
        drift_summary=RecordDriftSummary(
            num_total_features=len(features_list),
            num_features_drifted=len(_drifted_feature_list(features_list)),
            top_10_features_drifted=len(_top_10_drifted_features_list(features_list)),
            top_20_features_drifted=len(_top_20_drifted_features_list(features_list)),
        ),
        drift_details=RecordDriftDetails(
            fields=_fields(),
            observations=_observations(features_list),
        ),
        features=drift_summary_features,
    )

    return results


def _compile_features_for_drift_summary(
    baseline_data: pa.Table,
    test_data: pa.Table,
    feature: Dict,
) -> Dict[str, DriftSummaryFeature]:
    """Calculates drift statistics for all features."""
    significance_level = 0.05

    ranking = {
        x.name: rank
        for x, rank in zip(
            sorted(
                [value for value in feature.values()],
                key=attrgetter("importance_score"),
                reverse=True,
            ),
            range(1, len(feature.values()) + 1),
        )
    }

    results: Dict[str, DriftSummaryFeature] = {}
    for feature_name, feature_details in feature.items():
        kind = feature_details.kind
        tests = statistical_tests[kind]
        for test_name, test_details in tests.items():
            result = test_details["method"](
                baseline_data.column(feature_name).to_pylist(),
                test_data.column(feature_name).to_pylist(),
            )
            if result.p_value <= significance_level:
                outcome = "reject null hypothesis"
            else:
                outcome = "fail to reject null hypothesis"
            statistical_test = FeatureStatisticalTest(
                name=test_name,
                result=result,
                significance_level=significance_level,
                outcome=outcome,
            )
            if outcome == "reject null hypothesis":
                drift_status = "drifted"
            else:
                drift_status = "not drifted"
            results[feature_name] = DriftSummaryFeature(
                name=feature_name,
                kind=kind,
                rank=ranking[feature_name],
                importance_score=feature_details.importance_score,
                statistical_test=statistical_test,
                drift_status=drift_status,
            )

    return results


def _compute_num_feature_kind(feature_mapping: Dict, kind: str) -> int:
    """Counts number of features of a specific kind."""
    return len(
        [feature for feature in feature_mapping.values() if feature.kind == kind]
    )


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


def _timestamp() -> str:
    timestamp = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
    return timestamp


def _uuid() -> str:
    uuid_ = uuid.uuid4().hex
    return uuid_
