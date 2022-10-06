"""Test configuration for data drift."""


from pathlib import Path
from typing import Dict, List, Union
from zipfile import ZipFile

import pyarrow as pa
from pyarrow.csv import write_csv
import pytest

from raitools import __version__
from raitools.data_drift.domain.bundle import (
    get_data_from_bundle,
    get_job_config_filename_from_bundle,
    get_job_config_from_bundle,
)
from raitools.data_drift.domain.data_drift_record import DataDriftRecord
from raitools.data_drift.domain.job_config import DataDriftJobConfig
from raitools.data_drift.use_cases.process_bundle import (
    ProcessBundleRequest,
    bonferroni_correction,
)


@pytest.fixture
def simple_bundle_path(tmp_path: Path) -> Path:
    """Path to a simple bundle."""
    num_numerical_features = 2
    num_categorical_features = 3
    num_observations = 10
    job_config_filename = "some_job_config.json"

    bundle_path = _create_bundle(
        num_numerical_features,
        num_categorical_features,
        num_observations,
        job_config_filename,
        tmp_path,
    )

    return bundle_path


@pytest.fixture
def simple_request(simple_bundle_path: Path) -> ProcessBundleRequest:
    """A simple request."""
    return ProcessBundleRequest(bundle_path=simple_bundle_path)


@pytest.fixture
def simple_record(simple_request: ProcessBundleRequest) -> DataDriftRecord:
    """The expected record for the simple request."""
    job_config_filename = get_job_config_filename_from_bundle(
        simple_request.bundle_path
    )
    job_config = get_job_config_from_bundle(simple_request.bundle_path)

    num_numerical_features = _get_num_features_of_kind(
        simple_request.bundle_path, "numerical"
    )
    num_categorical_features = _get_num_features_of_kind(
        simple_request.bundle_path, "categorical"
    )
    num_features = num_numerical_features + num_categorical_features
    num_baseline_observations = _get_num_observations_in_dataset(
        simple_request.bundle_path, "baseline_data"
    )
    num_test_observations = _get_num_observations_in_dataset(
        simple_request.bundle_path, "test_data"
    )

    adjusted_significance_level = round(
        bonferroni_correction(num_features, alpha=0.05), ndigits=6
    )

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
                        "result": {"statistic": 0.0, "p_value": 1.0},
                        "significance_level": 0.05,
                        "adjusted_significance_level": adjusted_significance_level,
                        "outcome": "fail to reject null hypothesis",
                    },
                    "drift_status": "not drifted",
                },
                "numerical_feature_1": {
                    "name": "numerical_feature_1",
                    "kind": "numerical",
                    "rank": 2,
                    "statistical_test": {
                        "name": "kolmogorov-smirnov",
                        "result": {"statistic": 0.0, "p_value": 1.0},
                        "significance_level": 0.05,
                        "adjusted_significance_level": adjusted_significance_level,
                        "outcome": "fail to reject null hypothesis",
                    },
                    "drift_status": "not drifted",
                },
                "categorical_feature_0": {
                    "name": "categorical_feature_0",
                    "kind": "categorical",
                    "rank": 3,
                    "statistical_test": {
                        "name": "chi-squared",
                        "result": {
                            "statistic": 0.0,
                            "p_value": 1.0,
                        },
                        "significance_level": 0.05,
                        "adjusted_significance_level": adjusted_significance_level,
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
                            "statistic": 0.0,
                            "p_value": 1.0,
                        },
                        "significance_level": 0.05,
                        "adjusted_significance_level": adjusted_significance_level,
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
                            "statistic": 0.0,
                            "p_value": 1.0,
                        },
                        "significance_level": 0.05,
                        "adjusted_significance_level": adjusted_significance_level,
                        "outcome": "fail to reject null hypothesis",
                    },
                    "drift_status": "not drifted",
                },
            },
            "metadata": {
                "num_numerical_features": num_numerical_features,
                "num_categorical_features": num_categorical_features,
            },
        },
        "bundle": {
            "job_config": job_config,
            "data": {
                "baseline_data": {
                    "filename": job_config.baseline_data_filename,
                    "num_rows": num_baseline_observations,
                    "num_columns": num_features,
                },
                "test_data": {
                    "filename": job_config.test_data_filename,
                    "num_rows": num_test_observations,
                    "num_columns": num_features,
                },
            },
            "manifest": {
                "bundle_path": simple_request.bundle_path,
                "job_config_filename": job_config_filename,
                "baseline_data_filename": job_config.baseline_data_filename,
                "test_data_filename": job_config.test_data_filename,
            },
        },
    }

    expected_record = DataDriftRecord(**expected_record_dict)
    return expected_record


def _create_bundle(
    num_numerical_features: int,
    num_categorical_features: int,
    num_observations: int,
    job_config_filename: str,
    tmp_path: Path,
) -> Path:
    numerical_features = {
        f"numerical_feature_{index}": {
            "name": f"numerical_feature_{index}",
            "kind": "numerical",
            "rank": index + 1,
        }
        for index in range(num_numerical_features)
    }
    categorical_features = {
        f"categorical_feature_{index}": {
            "name": f"categorical_feature_{index}",
            "kind": "categorical",
            "rank": num_numerical_features + index + 1,
        }
        for index in range(num_categorical_features)
    }
    feature_mapping = {**numerical_features, **categorical_features}
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

    # Create data
    data_schema = pa.schema(
        [
            pa.field("numerical_feature_0", pa.int64()),
            pa.field("numerical_feature_1", pa.int64()),
            pa.field("categorical_feature_0", pa.string()),
            pa.field("categorical_feature_1", pa.string()),
            pa.field("categorical_feature_2", pa.string()),
        ]
    )
    baseline_data: Dict[str, List[Union[int, str]]] = {}
    for feature in numerical_features:
        baseline_data[feature] = [index for index in range(num_observations)]
    for feature in categorical_features:
        baseline_data[feature] = [
            f"category_{index}" for index in range(num_observations)
        ]
    baseline_data_table = pa.Table.from_pydict(baseline_data, schema=data_schema)
    baseline_data_path = tmp_path / job_config.baseline_data_filename
    write_csv(baseline_data_table, baseline_data_path)

    test_data: Dict[str, List[Union[int, str]]] = {}
    for feature in numerical_features:
        test_data[feature] = [index for index in range(num_observations)]
    for feature in categorical_features:
        test_data[feature] = [f"category_{index}" for index in range(num_observations)]
    test_data_table = pa.Table.from_pydict(test_data, schema=data_schema)
    test_data_path = tmp_path / job_config.test_data_filename
    write_csv(test_data_table, test_data_path)

    bundle_path = tmp_path / "bundle.zip"
    with ZipFile(bundle_path, "w") as zip_file:
        zip_file.write(job_config_path, arcname=job_config_filename)
        zip_file.write(baseline_data_path, arcname=job_config.baseline_data_filename)
        zip_file.write(test_data_path, arcname=job_config.test_data_filename)

    return bundle_path


def _get_num_features_of_kind(bundle_path: Path, kind: str) -> int:
    """Gets number of numerical features from the bundle at this path."""
    job_config = get_job_config_from_bundle(bundle_path)
    features_of_kind = [
        name
        for name, details in job_config.feature_mapping.items()
        if details.kind == kind
    ]
    return len(features_of_kind)


def _get_num_observations_in_dataset(bundle_path: Path, dataset: str) -> int:
    """Gets the number of observations in the specified dataset."""
    job_config = get_job_config_from_bundle(bundle_path)
    data_filename = getattr(job_config, f"{dataset}_filename")
    data = get_data_from_bundle(bundle_path, data_filename)
    return data.num_rows
