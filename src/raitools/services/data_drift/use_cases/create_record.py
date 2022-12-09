"""Process data drift bundle."""

from collections import defaultdict
from operator import attrgetter
from typing import Any, Dict, List, Optional


from raitools.services.data_drift.bundles import Bundle
from raitools.services.data_drift.data.data_drift_record import (
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
    StatisticalTestResult,
)
from raitools.services.data_drift.use_cases.get_drift_results import (
    DriftResultsType,
    FeatureType,
    get_drift_results,
)


def create_record_from_bundle(
    bundle: Bundle,
    bundle_filename: str,
    timestamp: Optional[str] = None,
    uuid: Optional[str] = None,
) -> DataDriftRecord:
    """Processes a data drift bundle."""
    feature_mapping = {
        name: FeatureType(name=details.name, kind=details.kind)
        for name, details in bundle.feature_mapping.feature_mapping.items()
    }

    drift_results = get_drift_results(
        baseline_data=bundle.baseline_data,
        test_data=bundle.test_data,
        feature_mapping=feature_mapping,
    )

    record_bundle = _compile_bundle_for_record(bundle, bundle_filename)
    results = _compile_drift_results_for_record(
        drift_results,
        bundle.feature_mapping.feature_mapping,
        bundle.job_config.report_name,
        timestamp,
        uuid,
    )

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
    drift_results: DriftResultsType,
    feature_mapping: Dict,
    report_name: str,
    timestamp: Optional[str] = None,
    uuid: Optional[str] = None,
) -> RecordResults:
    """Creates drift summary for record."""
    features = feature_mapping

    drift_summary_features = _compile_features_for_drift_summary(
        drift_results, feature_mapping
    )

    thresholds = _thresholds_map(drift_summary_features)

    num_numerical_features = _compute_num_feature_kind(features, "numerical")
    num_categorical_features = _compute_num_feature_kind(features, "categorical")

    features_list = list(drift_summary_features.values())
    num_total_features = len(features_list)
    num_features_drifted = len(_drifted_feature_list(features_list))
    top_10_features_drifted = len(_top_10_drifted_features_list(features_list))
    top_20_features_drifted = len(_top_20_drifted_features_list(features_list))

    fields = _fields()
    observations = _observations(features_list)

    results = RecordResults(
        metadata=ResultMetadata(
            report_name=report_name,
            timestamp=timestamp,
            uuid=uuid,
            thresholds=thresholds,
        ),
        data_summary=RecordDataSummary(
            num_numerical_features=num_numerical_features,
            num_categorical_features=num_categorical_features,
        ),
        drift_summary=RecordDriftSummary(
            num_total_features=num_total_features,
            num_features_drifted=num_features_drifted,
            top_10_features_drifted=top_10_features_drifted,
            top_20_features_drifted=top_20_features_drifted,
        ),
        drift_details=RecordDriftDetails(
            fields=fields,
            observations=observations,
        ),
        features=drift_summary_features,
    )

    return results


def _compile_features_for_drift_summary(
    drift_results: DriftResultsType, feature_mapping: Dict
) -> Dict[str, DriftSummaryFeature]:
    """Calculates drift statistics for all features."""
    ranking = {
        x.name: rank
        for x, rank in zip(
            sorted(
                [value for value in feature_mapping.values()],
                key=attrgetter("importance_score"),
                reverse=True,
            ),
            range(1, len(feature_mapping.values()) + 1),
        )
    }

    results: Dict[str, DriftSummaryFeature] = {}
    for feature_name, feature_results in drift_results.items():
        kind = feature_mapping[feature_name].kind
        importance_score = feature_mapping[feature_name].importance_score
        results[feature_name] = DriftSummaryFeature(
            name=feature_name,
            kind=kind,
            rank=ranking[feature_name],
            importance_score=importance_score,
            statistical_test=FeatureStatisticalTest(
                name=feature_results["test_name"],
                result=StatisticalTestResult(
                    test_statistic=feature_results["drift_result"]["statistical_test"][
                        "test_statistic"
                    ],
                    p_value=feature_results["drift_result"]["statistical_test"][
                        "p_value"
                    ],
                ),
                significance_level=feature_results["drift_result"]["statistical_test"][
                    "significance_level"
                ],
                outcome=feature_results["drift_result"]["statistical_test"]["outcome"],
            ),
            drift_status=feature_results["drift_result"]["drift_status"],
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
