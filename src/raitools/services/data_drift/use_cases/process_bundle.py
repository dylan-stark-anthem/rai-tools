"""Process data drift bundle."""

from pathlib import Path
from typing import Dict

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
    DriftSummaryMetadata,
    FeatureStatisticalTest,
    RecordBundle,
    RecordDriftSummary,
    RecordMetadata,
)
from raitools.services.data_drift.domain.job_config import JobConfigFeature
from raitools.services.data_drift.domain.stats import statistical_tests
from raitools.stats.bonferroni_correction import (
    bonferroni_correction,
)


def process_bundle(bundle_path: Path) -> DataDriftRecord:
    """Processes a data drift bundle."""
    bundle = create_bundle_from_zip(bundle_path)

    metadata = _compile_metadata_for_record()
    record_bundle = _compile_bundle_for_record(bundle, bundle_path.name)
    drift_summary = _compile_drift_summary_for_record(bundle)

    record = DataDriftRecord(
        metadata=metadata,
        bundle=record_bundle,
        drift_summary=drift_summary,
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
            baseline_data_filename=bundle.baseline_data_filename,
            test_data_filename=bundle.test_data_filename,
        ),
    )
    return record_bundle


def _compile_drift_summary_for_record(bundle: DataDriftBundle) -> RecordDriftSummary:
    """Creates drift summary for record."""
    features = bundle.job_config.feature_mapping
    num_numerical_features = _compute_num_feature_kind(features, "numerical")
    num_categorical_features = _compute_num_feature_kind(features, "categorical")

    drift_summary_features = _compile_features_for_drift_summary(
        bundle.baseline_data,
        bundle.test_data,
        features,
    )

    drift_summary = RecordDriftSummary(
        features=drift_summary_features,
        metadata=DriftSummaryMetadata(
            features=features,
            num_numerical_features=num_numerical_features,
            num_categorical_features=num_categorical_features,
        ),
    )

    return drift_summary


def _compile_features_for_drift_summary(
    baseline_data: pa.Table,
    test_data: pa.Table,
    feature: Dict[str, JobConfigFeature],
) -> Dict[str, DriftSummaryFeature]:
    """Calculates drift statistics for all features."""
    significance_level = 0.05
    adjusted_significance_level = round(
        bonferroni_correction(baseline_data.num_columns, alpha=significance_level),
        ndigits=6,
    )

    results: Dict[str, DriftSummaryFeature] = {}
    for feature_name, feature_details in feature.items():
        kind = feature_details.kind
        tests = statistical_tests[kind]
        for test_name, test_details in tests.items():
            result = test_details["method"](
                baseline_data.column(feature_name).to_pylist(),
                test_data.column(feature_name).to_pylist(),
            )
            if result.p_value <= adjusted_significance_level:
                outcome = "reject null hypothesis"
            else:
                outcome = "fail to reject null hypothesis"
            statistical_test = FeatureStatisticalTest(
                name=test_name,
                result=result,
                significance_level=significance_level,
                adjusted_significance_level=adjusted_significance_level,
                outcome=outcome,
            )
            if outcome == "reject null hypothesis":
                drift_status = "drifted"
            else:
                drift_status = "not drifted"
            results[feature_name] = DriftSummaryFeature(
                name=feature_name,
                kind=kind,
                rank=feature_details.rank,
                statistical_test=statistical_test,
                drift_status=drift_status,
            )

    return results


def _compute_num_feature_kind(
    feature_mapping: Dict[str, JobConfigFeature], kind: str
) -> int:
    """Counts number of features of a specific kind."""
    return len(
        [feature for feature in feature_mapping.values() if feature.kind == kind]
    )
