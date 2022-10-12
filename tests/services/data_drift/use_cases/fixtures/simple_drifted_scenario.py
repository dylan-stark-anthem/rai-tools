"""Setup for simple drifted test scenario."""

from pathlib import Path
from typing import Any, Dict, List, Union

import pyarrow as pa
import pytest

from raitools import __version__
from raitools.services.data_drift.domain.data_drift_record import DataDriftRecord
from raitools.stats.bonferroni_correction import bonferroni_correction

from tests.services.data_drift.use_cases.fixtures.common import create_bundle


@pytest.fixture
def simple_drifted_test_data(
    simple_num_observations: int,
    simple_numerical_features: Dict,
    simple_categorical_features: Dict,
    simple_data_schema: pa.Schema,
) -> pa.Table:
    """Creates drifted data for simple scenario."""
    numerical_drift_amount = 10000

    data: Dict[str, List[Union[int, str]]] = {}
    for feature in simple_numerical_features:
        data[feature] = [
            index + numerical_drift_amount for index in range(simple_num_observations)
        ]
    for feature in simple_categorical_features:
        data[feature] = [
            f"category_{index}" for index in range(simple_num_observations)
        ]
    table = pa.Table.from_pydict(data, schema=simple_data_schema)
    return table


@pytest.fixture
def simple_drifted_bundle_path(
    simple_feature_mapping: Dict,
    simple_baseline_data: pa.Table,
    simple_drifted_test_data: pa.Table,
    tmp_path: Path,
) -> Path:
    """Path to a simple bundle."""
    job_config_filename = "some_job_config.json"

    bundle_path = create_bundle(
        job_config_filename,
        simple_feature_mapping,
        simple_baseline_data,
        simple_drifted_test_data,
        tmp_path,
    )

    return bundle_path


@pytest.fixture
def simple_drifted_spec(tmp_path: Path) -> Dict:
    """Spec used to drive system into desired state for test."""
    spec = {
        "bundle_path": tmp_path / "bundle.zip",
        "job_config_filename": "some_job_config.json",
        "job_config": {
            "report_name": "Some simple report",
            "dataset_name": "Some name for this dataset",
            "dataset_version": "v0.1.0",
            "baseline_data_filename": "some_baseline_data.csv",
            "test_data_filename": "some_test_data.csv",
            "model_catalog_id": "123",
            "feature_mapping": {
                "numerical_feature_0": {
                    "name": "numerical_feature_0",
                    "kind": "numerical",
                    "rank": 1,
                },
                "numerical_feature_1": {
                    "name": "numerical_feature_1",
                    "kind": "numerical",
                    "rank": 2,
                },
                "categorical_feature_0": {
                    "name": "categorical_feature_0",
                    "kind": "categorical",
                    "rank": 3,
                },
                "categorical_feature_1": {
                    "name": "categorical_feature_1",
                    "kind": "categorical",
                    "rank": 4,
                },
                "categorical_feature_2": {
                    "name": "categorical_feature_2",
                    "kind": "categorical",
                    "rank": 5,
                },
            },
        },
        "num_features": 5,
        "num_numerical_features": 2,
        "num_categorical_features": 3,
        "num_baseline_observations": 10,
        "num_test_observations": 10,
    }
    return spec


@pytest.fixture
def simple_drifted_record(simple_drifted_spec: Dict) -> DataDriftRecord:
    """The expected record for the simple request.

    The job of this fixture is to take the more general spec for the test
    scenario and extend it with more specific details.
    """
    spec = simple_drifted_spec

    spec["adjusted_significance_level"] = round(
        bonferroni_correction(spec["num_features"], alpha=0.05), ndigits=6
    )

    expected_record = create_expected_record(**spec)
    return expected_record


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
