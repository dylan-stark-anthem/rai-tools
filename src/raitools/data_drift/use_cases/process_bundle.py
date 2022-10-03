"""Process data drift bundle."""

from pathlib import Path
from typing import Dict

import pyarrow as pa
from pydantic import BaseModel
import raitools

from raitools.data_drift.domain.bundle import create_bundle_from_zip
from raitools.data_drift.domain.data_drift_record import (
    Bundle,
    BundleData,
    BundleManifest,
    DataDriftMetadata,
    DataDriftRecord,
    DataDriftRecordDriftSummary,
)
from raitools.data_drift.domain.data_drift_summary import DataDriftDataSummary
from raitools.data_drift.domain.data_summary import DataSummary
from raitools.data_drift.domain.drift_summary import (
    DriftSummary,
    Feature,
    FeatureSummary,
)
from raitools.data_drift.domain import job_config
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


def compute_num_feature_kind(
    feature_mapping: Dict[str, job_config.Feature], kind: str
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
    feature: Dict[str, Feature],
    test_corrections: Dict[str, StatisticalTest],
) -> Dict[str, FeatureSummary]:
    """Calculates drift statistics for all features."""
    significance_level = 0.05

    results: Dict[str, FeatureSummary] = {}
    for feature_name, feature_details in feature.items():
        kind = feature_details.kind
        tests = statistical_tests[kind]
        for test_name, test_details in tests.items():
            result = test_details["method"](
                baseline_data.column(feature_name).to_pylist(),
                test_data.column(feature_name).to_pylist(),
            )
            adjusted_significance_level = test_corrections[test_name].threshold
            if result.p_value <= adjusted_significance_level:
                outcome = "reject null hypothesis"
            else:
                outcome = "fail to reject null hypothesis"
            result = DriftSummary(
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
            results[feature_name] = FeatureSummary(
                name=feature_name,
                kind=kind,
                rank=feature_details.rank,
                statistical_test=result,
                drift_status=drift_status,
            )
    return results


def process_bundle(request: Request) -> DataDriftRecord:
    """Processes a data drift bundle."""
    bundle = create_bundle_from_zip(request.bundle_path)
    baseline_data_summary = create_data_summary(bundle.baseline_data)
    test_data_summary = create_data_summary(bundle.test_data)
    features = {
        name: Feature(**feature.dict())
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
            num_rows=baseline_data_summary.num_rows,
            num_columns=baseline_data_summary.num_columns,
        ),
        "test_data": BundleData(
            filename=bundle.job_config.test_data_filename,
            num_rows=test_data_summary.num_rows,
            num_columns=test_data_summary.num_columns,
        ),
    }

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
    test_corrections = {
        kolmogorov_smirnov_test.name: kolmogorov_smirnov_test,
        chi_squared_test.name: chi_squared_test,
    }

    drift_summary = create_drift_summary(
        bundle.baseline_data,
        bundle.test_data,
        features,
        test_corrections,
    )

    record = DataDriftRecord(
        metadata=DataDriftMetadata(
            raitools_version=raitools.__version__,
        ),
        bundle=Bundle(
            job_config=bundle.job_config,
            data=bundle_data,
            manifest=BundleManifest(
                bundle_path=request.bundle_path,
                job_config_filename=bundle.job_config_filename,
                baseline_data_filename=bundle.baseline_data_filename,
                test_data_filename=bundle.test_data_filename,
            ),
        ),
        statistical_tests=test_corrections,
        drift_summary=DataDriftRecordDriftSummary(
            features=drift_summary,
            metadata=DataDriftDataSummary(
                features=features,
                num_numerical_features=num_numerical_features,
                num_categorical_features=num_categorical_features,
            ),
        ),
    )

    return record
