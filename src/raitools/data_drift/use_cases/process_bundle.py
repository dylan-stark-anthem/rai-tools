"""Process data drift bundle."""

from pathlib import Path
from typing import Dict

import pyarrow as pa
from pydantic import BaseModel

from raitools.data_drift.domain.bundle import create_bundle_from_zip
from raitools.data_drift.domain.data_drift_record import (
    BundleManifest,
    BundleManifestMetadata,
    DataDriftRecord,
)
from raitools.data_drift.domain.data_drift_summary import DataDriftDataSummary
from raitools.data_drift.domain.data_summary import DataSummary
from raitools.data_drift.domain.drift_summary import DriftSummary, FeatureSummary
from raitools.data_drift.domain.job_config import Feature
from raitools.data_drift.domain.stats import statistical_tests
from raitools.data_drift.domain.statistical_test import StatisticalTest


class Request(BaseModel):
    """A process bundle request."""

    bundle_path: Path


def create_data_summary(data: pa.Table) -> DataSummary:
    """Creates summary statistics for a dataset."""
    return DataSummary(
        num_rows=data.num_rows,
        num_columns=data.num_columns,
    )


def compute_num_feature_kind(feature_mapping: Dict[str, Feature], kind: str) -> int:
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
    feature_mapping: Dict[str, Feature],
) -> Dict[str, FeatureSummary]:
    """Calculates drift statistics for all features."""
    results: Dict[str, FeatureSummary] = {}
    for feature_name, feature_details in feature_mapping.items():
        kind = feature_details.kind
        tests = statistical_tests[kind]
        for test_name, test_details in tests.items():
            result = DriftSummary(
                name=test_name,
                result=test_details["method"](
                    baseline_data.column(feature_name).to_pylist(),
                    test_data.column(feature_name).to_pylist(),
                ),
            )
            results[feature_name] = FeatureSummary(
                name=feature_name,
                kind=kind,
                statistical_test=result,
            )
    return results


def process_bundle(request: Request) -> DataDriftRecord:
    """Processes a data drift bundle."""
    bundle = create_bundle_from_zip(request.bundle_path)
    baseline_data_summary = create_data_summary(bundle.baseline_data)
    test_data_summary = create_data_summary(bundle.test_data)
    num_numerical_features = compute_num_feature_kind(
        bundle.job_config.feature_mapping, "numerical"
    )
    num_categorical_features = compute_num_feature_kind(
        bundle.job_config.feature_mapping, "categorical"
    )

    kolmogorov_smirnov_test = StatisticalTest(
        name="kolmogorov-smirnov",
        threshold=round(
            bonferroni_correction(num_numerical_features, alpha=0.05), ndigits=6
        ),
    )
    chi_squared_test = StatisticalTest(
        name="chi-squared",
        threshold=round(
            bonferroni_correction(num_categorical_features, alpha=0.05), ndigits=6
        ),
    )
    statistical_tests = {
        kolmogorov_smirnov_test.name: kolmogorov_smirnov_test,
        chi_squared_test.name: chi_squared_test,
    }

    drift_summary = create_drift_summary(
        bundle.baseline_data,
        bundle.test_data,
        bundle.job_config.feature_mapping,
    )

    record = DataDriftRecord(
        bundle_manifest=BundleManifest(
            metadata=BundleManifestMetadata(
                bundle_path=request.bundle_path,
                job_config_filename=bundle.job_config_filename,
                baseline_data_filename=bundle.baseline_data_filename,
                test_data_filename=bundle.test_data_filename,
            ),
            job_config=bundle.job_config,
            baseline_data_summary=baseline_data_summary,
            test_data_summary=test_data_summary,
        ),
        data_summary=DataDriftDataSummary(
            num_numerical_features=num_numerical_features,
            num_categorical_features=num_categorical_features,
        ),
        statistical_tests=statistical_tests,
        drift_summary=drift_summary,
    )

    return record
