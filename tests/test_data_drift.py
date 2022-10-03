"""Tests for data drift."""

from pathlib import Path
from typing import Dict, List, Union
from zipfile import ZipFile

import pyarrow as pa
from pyarrow.csv import write_csv

from raitools.data_drift.domain.job_config import JobConfig
from raitools.data_drift.use_cases.process_bundle import (
    Request,
    bonferroni_correction,
    process_bundle,
)


def test_can_process_bundle(tmp_path: Path) -> None:
    """Tests that we can process a bundle."""
    num_numerical_features = 2
    num_categorical_features = 3
    num_observations = 10
    kolmogorov_smirnov_test_threshold = round(
        bonferroni_correction(num_numerical_features, alpha=0.05), ndigits=6
    )
    chi_squared_test_threshold = round(
        bonferroni_correction(num_categorical_features, alpha=0.05), ndigits=6
    )

    # Create config
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
            "rank": num_numerical_features + index,
        }
        for index in range(num_categorical_features)
    }
    feature_mapping = {**numerical_features, **categorical_features}
    job_config_json = {
        "dataset_name": "Some name for this dataset",
        "baseline_data_filename": "some_baseline_data.csv",
        "test_data_filename": "some_test_data.csv",
        "model_catalog_id": "123",
        "feature_mapping": feature_mapping,
    }
    job_config_filename = "some_job_config.json"
    job_config = JobConfig(**job_config_json)
    job_config_path = tmp_path / job_config_filename
    job_config_path.write_text(job_config.json())

    num_columns = num_numerical_features + num_categorical_features
    num_rows = num_observations

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
        baseline_data[feature] = [index for index in range(num_rows)]
    for feature in categorical_features:
        baseline_data[feature] = [f"category_{index}" for index in range(num_rows)]
    baseline_data_table = pa.Table.from_pydict(baseline_data, schema=data_schema)
    baseline_data_path = tmp_path / job_config.baseline_data_filename
    write_csv(baseline_data_table, baseline_data_path)

    test_data: Dict[str, List[Union[int, str]]] = {}
    for feature in numerical_features:
        test_data[feature] = [index for index in range(num_rows)]
    for feature in categorical_features:
        test_data[feature] = [f"category_{index}" for index in range(num_rows)]
    test_data_table = pa.Table.from_pydict(test_data, schema=data_schema)
    test_data_path = tmp_path / job_config.test_data_filename
    write_csv(test_data_table, test_data_path)

    bundle_path = tmp_path / "bundle.zip"
    with ZipFile(bundle_path, "w") as zip_file:
        zip_file.write(job_config_path, arcname=job_config_filename)
        zip_file.write(baseline_data_path, arcname=job_config.baseline_data_filename)
        zip_file.write(test_data_path, arcname=job_config.test_data_filename)

    request = Request(bundle_path=bundle_path)
    record = process_bundle(request)

    assert record.bundle_manifest.metadata.bundle_path == bundle_path
    assert record.bundle_manifest.metadata.job_config_filename == job_config_filename
    assert (
        record.bundle_manifest.metadata.baseline_data_filename
        == job_config.baseline_data_filename
    )
    assert (
        record.bundle_manifest.metadata.test_data_filename
        == job_config.test_data_filename
    )
    assert record.bundle_manifest.job_config == job_config
    assert record.bundle_manifest.baseline_data_summary.num_rows == num_rows
    assert record.bundle_manifest.baseline_data_summary.num_columns == num_columns
    assert record.bundle_manifest.test_data_summary.num_rows == num_rows
    assert record.bundle_manifest.test_data_summary.num_columns == num_columns
    assert record.data_summary.num_numerical_features == num_numerical_features
    assert record.data_summary.num_categorical_features == num_categorical_features

    expected_record_dict = {
        "data_summary": {
            "num_numerical_features": num_numerical_features,
            "num_categorical_features": num_categorical_features,
        },
        "drift_summary": {
            "numerical_feature_0": {
                "name": "numerical_feature_0",
                "kind": "numerical",
                "statistical_test": {
                    "name": "kolmogorov-smirnov",
                    "result": {"statistic": 0.0, "p_value": 1.0},
                },
            },
            "numerical_feature_1": {
                "name": "numerical_feature_1",
                "kind": "numerical",
                "statistical_test": {
                    "name": "kolmogorov-smirnov",
                    "result": {"statistic": 0.0, "p_value": 1.0},
                },
            },
            "categorical_feature_0": {
                "name": "categorical_feature_0",
                "kind": "categorical",
                "statistical_test": {
                    "name": "chi-squared",
                    "result": {
                        "statistic": 0.0,
                        "p_value": 1.0,
                    },
                },
            },
            "categorical_feature_1": {
                "name": "categorical_feature_1",
                "kind": "categorical",
                "statistical_test": {
                    "name": "chi-squared",
                    "result": {
                        "statistic": 0.0,
                        "p_value": 1.0,
                    },
                },
            },
            "categorical_feature_2": {
                "name": "categorical_feature_2",
                "kind": "categorical",
                "statistical_test": {
                    "name": "chi-squared",
                    "result": {
                        "statistic": 0.0,
                        "p_value": 1.0,
                    },
                },
            },
        },
        "statistical_tests": {
            "kolmogorov-smirnov": {
                "name": "kolmogorov-smirnov",
                "threshold": kolmogorov_smirnov_test_threshold,
            },
            "chi-squared": {
                "name": "chi-squared",
                "threshold": chi_squared_test_threshold,
            },
        },
        "bundle_manifest": {
            "job_config": job_config,
            "baseline_data_summary": {
                "num_rows": num_rows,
                "num_columns": num_columns,
            },
            "test_data_summary": {
                "num_rows": num_rows,
                "num_columns": num_columns,
            },
            "metadata": {
                "bundle_path": bundle_path,
                "job_config_filename": job_config_filename,
                "baseline_data_filename": baseline_data_path.name,
            },
        },
    }

    def _assert_equal_dicts(expected_dict: Dict, actual_dict: Dict) -> None:
        for key in expected_dict:
            assert key in actual_dict
            if isinstance(expected_dict[key], dict):
                _assert_equal_dicts(expected_dict[key], actual_dict[key])
            else:
                assert expected_dict[key] == actual_dict[key]

    _assert_equal_dicts(expected_record_dict, record.dict())
