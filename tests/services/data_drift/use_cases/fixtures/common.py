"""Common helpers for test setup."""

from pathlib import Path
from typing import Any, Dict
from zipfile import ZipFile

import pyarrow as pa
from pyarrow.csv import write_csv

from raitools import __version__
from raitools.services.data_drift.domain.bundle import (
    get_data_from_bundle,
    get_job_config_from_bundle,
)
from raitools.services.data_drift.domain.data_drift_record import DataDriftRecord
from raitools.services.data_drift.domain.job_config import DataDriftJobConfig


def create_bundle(
    job_config_filename: str,
    feature_mapping: Dict,
    baseline_data_table: pa.Table,
    test_data_table: pa.Table,
    tmp_path: Path,
) -> Path:
    """Creates a "physical" bundle on disk."""
    job_config_json = {
        "report_name": "Some simple report",
        "dataset_name": "Some name for this dataset",
        "dataset_version": "v0.1.0",
        "baseline_data_filename": "some_baseline_data.csv",
        "test_data_filename": "some_test_data.csv",
        "model_catalog_id": "123",
        "feature_mapping": feature_mapping,
    }
    job_config = DataDriftJobConfig(**job_config_json)
    job_config_path = tmp_path / job_config_filename
    job_config_path.write_text(job_config.json())

    baseline_data_path = tmp_path / job_config.baseline_data_filename
    write_csv(baseline_data_table, baseline_data_path)

    test_data_path = tmp_path / job_config.test_data_filename
    write_csv(test_data_table, test_data_path)

    bundle_path = tmp_path / "bundle.zip"
    with ZipFile(bundle_path, "w") as zip_file:
        zip_file.write(job_config_path, arcname=job_config_filename)
        zip_file.write(baseline_data_path, arcname=job_config.baseline_data_filename)
        zip_file.write(test_data_path, arcname=job_config.test_data_filename)

    return bundle_path


def get_num_features_of_kind(bundle_path: Path, kind: str) -> int:
    """Gets number of numerical features from the bundle at this path."""
    job_config = get_job_config_from_bundle(bundle_path)
    features_of_kind = [
        name
        for name, details in job_config.feature_mapping.items()
        if details.kind == kind
    ]
    return len(features_of_kind)


def get_num_observations_in_dataset(bundle_path: Path, dataset: str) -> int:
    """Gets the number of observations in the specified dataset."""
    job_config = get_job_config_from_bundle(bundle_path)
    data_filename = getattr(job_config, f"{dataset}_filename")
    data = get_data_from_bundle(bundle_path, data_filename)
    return data.num_rows


def create_expected_record(**spec: Any) -> DataDriftRecord:
    """Creates an expected record for given spec.

    Note that we are trading off high cost of maintaining the explicit record
    dictionary for the high value of having a clear, unambiguous declaration
    of the true expected record payload.
    """
    expected_record_dict = {
        "apiVersion": "raitools/v1",
        "kind": "DataDriftRecord",
        "metadata": {
            "raitools_version": __version__,
        },
        "drift_summary": {
            "features": {
                "numerical_feature_0": {
                    "name": "numerical_feature_0",
                    "kind": "numerical",
                    "rank": 1,
                    "statistical_test": {
                        "name": "kolmogorov-smirnov",
                        "result": {"test_statistic": 1.0, "p_value": 0.0},
                        "significance_level": 0.05,
                        "adjusted_significance_level": spec[
                            "adjusted_significance_level"
                        ],
                        "outcome": "reject null hypothesis",
                    },
                    "drift_status": "drifted",
                },
                "numerical_feature_1": {
                    "name": "numerical_feature_1",
                    "kind": "numerical",
                    "rank": 2,
                    "statistical_test": {
                        "name": "kolmogorov-smirnov",
                        "result": {"test_statistic": 1.0, "p_value": 0.0},
                        "significance_level": 0.05,
                        "adjusted_significance_level": spec[
                            "adjusted_significance_level"
                        ],
                        "outcome": "reject null hypothesis",
                    },
                    "drift_status": "drifted",
                },
                "categorical_feature_0": {
                    "name": "categorical_feature_0",
                    "kind": "categorical",
                    "rank": 3,
                    "statistical_test": {
                        "name": "chi-squared",
                        "result": {
                            "test_statistic": 0.0,
                            "p_value": 1.0,
                        },
                        "significance_level": 0.05,
                        "adjusted_significance_level": spec[
                            "adjusted_significance_level"
                        ],
                        "outcome": "fail to reject null hypothesis",
                    },
                    "drift_status": "not drifted",
                },
                "categorical_feature_1": {
                    "name": "categorical_feature_1",
                    "kind": "categorical",
                    "rank": 4,
                    "statistical_test": {
                        "name": "chi-squared",
                        "result": {
                            "test_statistic": 0.0,
                            "p_value": 1.0,
                        },
                        "significance_level": 0.05,
                        "adjusted_significance_level": spec[
                            "adjusted_significance_level"
                        ],
                        "outcome": "fail to reject null hypothesis",
                    },
                    "drift_status": "not drifted",
                },
                "categorical_feature_2": {
                    "name": "categorical_feature_2",
                    "kind": "categorical",
                    "rank": 5,
                    "statistical_test": {
                        "name": "chi-squared",
                        "result": {
                            "test_statistic": 0.0,
                            "p_value": 1.0,
                        },
                        "significance_level": 0.05,
                        "adjusted_significance_level": spec[
                            "adjusted_significance_level"
                        ],
                        "outcome": "fail to reject null hypothesis",
                    },
                    "drift_status": "not drifted",
                },
            },
            "metadata": {
                "num_numerical_features": spec["num_numerical_features"],
                "num_categorical_features": spec["num_categorical_features"],
            },
        },
        "bundle": {
            "job_config": spec["job_config"],
            "data": {
                "baseline_data": {
                    "filename": spec["job_config"]["baseline_data_filename"],
                    "num_rows": spec["num_baseline_observations"],
                    "num_columns": spec["num_features"],
                },
                "test_data": {
                    "filename": spec["job_config"]["test_data_filename"],
                    "num_rows": spec["num_test_observations"],
                    "num_columns": spec["num_features"],
                },
            },
            "manifest": {
                "bundle_path": spec["bundle_path"],
                "job_config_filename": spec["job_config_filename"],
                "baseline_data_filename": spec["job_config"]["baseline_data_filename"],
                "test_data_filename": spec["job_config"]["test_data_filename"],
            },
        },
    }

    expected_record = DataDriftRecord(**expected_record_dict)
    return expected_record
