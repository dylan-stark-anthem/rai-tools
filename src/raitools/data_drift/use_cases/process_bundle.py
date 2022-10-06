"""Process data drift bundle."""

from pathlib import Path
from typing import Dict

import pyarrow as pa
from pydantic import BaseModel

import raitools
from raitools.data_drift.domain.bundle import create_bundle_from_zip
from raitools.data_drift.domain.data_drift_record import (
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
from raitools.data_drift.domain.job_config import JobConfigFeature
from raitools.data_drift.domain.stats import statistical_tests


class ProcessBundleRequest(BaseModel):
    """A process bundle request."""

    bundle_path: Path


def process_bundle(request: ProcessBundleRequest) -> DataDriftRecord:
    """Processes a data drift bundle."""
    bundle = create_bundle_from_zip(request.bundle_path)
    features = {
        name: JobConfigFeature(**feature.dict())
        for name, feature in bundle.job_config.feature_mapping.items()
    }
    num_numerical_features = compute_num_feature_kind(
        bundle.job_config.feature_mapping, "numerical"
    )
    num_categorical_features = compute_num_feature_kind(
        bundle.job_config.feature_mapping, "categorical"
    )

    bundle_data = {
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
    }

    adjusted_significance_level = round(
        bonferroni_correction(len(features), alpha=0.05), ndigits=6
    )

    drift_summary = create_drift_summary(
        bundle.baseline_data,
        bundle.test_data,
        features,
        adjusted_significance_level,
    )

    record = DataDriftRecord(
        metadata=RecordMetadata(
            raitools_version=raitools.__version__,
        ),
        bundle=RecordBundle(
            job_config=bundle.job_config,
            data=bundle_data,
            manifest=BundleManifest(
                bundle_path=request.bundle_path,
                job_config_filename=bundle.job_config_filename,
                baseline_data_filename=bundle.baseline_data_filename,
                test_data_filename=bundle.test_data_filename,
            ),
        ),
        drift_summary=RecordDriftSummary(
            features=drift_summary,
            metadata=DriftSummaryMetadata(
                features=features,
                num_numerical_features=num_numerical_features,
                num_categorical_features=num_categorical_features,
            ),
        ),
    )

    return record


def compute_num_feature_kind(
    feature_mapping: Dict[str, JobConfigFeature], kind: str
) -> int:
    """Counts number of features of a specific kind."""
    return len(
        [feature for feature in feature_mapping.values() if feature.kind == kind]
    )


def bonferroni_correction(num_features: int, alpha: float) -> float:
    """Calculates Bonferroni correction for given number of features."""
    return alpha / num_features


def create_drift_summary(
    baseline_data: pa.Table,
    test_data: pa.Table,
    feature: Dict[str, JobConfigFeature],
    adjusted_significance_level: float,
) -> Dict[str, DriftSummaryFeature]:
    """Calculates drift statistics for all features."""
    significance_level = 0.05

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
