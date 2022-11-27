"""Process data drift bundle."""

from operator import attrgetter
from pathlib import Path
from typing import Dict, List

import pyarrow as pa

import raitools
from raitools.services.data_drift.domain.bundle import (
    DataDriftBundle,
    create_bundle_from_zip,
)
from raitools.services.data_drift.domain.data_drift_record import (
    BundleData,
    BundleManifest,
    DataDriftRecord,
    DriftSummaryFeature,
    FeatureStatisticalTest,
    RecordBundle,
    RecordDataSummary,
    RecordDriftSummary,
    RecordMetadata,
    RecordResults,
)
from raitools.services.data_drift.domain.stats import statistical_tests
from raitools.services.data_drift.exceptions import BadPathToBundleError


def process_bundle(bundle_path: Path) -> DataDriftRecord:
    """Processes a data drift bundle."""
    _validate_is_pathlib_path(bundle_path)

    bundle = create_bundle_from_zip(bundle_path)

    metadata = _compile_metadata_for_record()
    record_bundle = _compile_bundle_for_record(bundle, bundle_path.name)
    results = _compile_drift_results_for_record(bundle)

    record = DataDriftRecord(
        metadata=metadata,
        bundle=record_bundle,
        results=results,
    )

    return record


def _compile_metadata_for_record() -> RecordMetadata:
    """Creates record metadata."""
    metadata = RecordMetadata(raitools_version=raitools.__version__)
    return metadata


def _compile_bundle_for_record(
    bundle: DataDriftBundle, bundle_filename: str
) -> RecordBundle:
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


def _compile_drift_results_for_record(bundle: DataDriftBundle) -> RecordResults:
    """Creates drift summary for record."""
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


def _validate_is_pathlib_path(bundle_path: Path) -> None:
    if not isinstance(bundle_path, Path):
        raise BadPathToBundleError(
            f"Path to bundle is not a valid `pathlib.Path`, it's a(n) `{type(bundle_path)}`."
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
