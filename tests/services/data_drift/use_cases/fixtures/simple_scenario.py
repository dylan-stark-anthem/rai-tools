"""Setup for simple test scenario."""

from pathlib import Path
from typing import Dict, List, Union

import pyarrow as pa
import pytest

from raitools import __version__


@pytest.fixture
def simple_spec(tmp_path: Path) -> Dict:
    """Spec used to drive system into desired state for test."""
    spec = {
        "raitools_version": __version__,
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
        "adjusted_significance_level": 0.01,
    }
    return spec


@pytest.fixture
def simple_data_schema() -> pa.Schema:
    """Schema for simple data tables."""
    schema = pa.schema(
        [
            pa.field("numerical_feature_0", pa.int64()),
            pa.field("numerical_feature_1", pa.int64()),
            pa.field("categorical_feature_0", pa.string()),
            pa.field("categorical_feature_1", pa.string()),
            pa.field("categorical_feature_2", pa.string()),
        ]
    )
    return schema


@pytest.fixture
def simple_num_observations() -> int:
    """Number of observations in baseline and test data."""
    return 10


@pytest.fixture
def simple_num_numerical_features() -> int:
    """Number of numerical features."""
    return 2


@pytest.fixture
def simple_num_categorical_features() -> int:
    """Number of categorical features."""
    return 3


@pytest.fixture
def simple_numerical_features(simple_num_numerical_features: int) -> Dict:
    """Numerical features for simple scenario."""
    numerical_features = {
        f"numerical_feature_{index}": {
            "name": f"numerical_feature_{index}",
            "kind": "numerical",
            "rank": index + 1,
        }
        for index in range(simple_num_numerical_features)
    }
    return numerical_features


@pytest.fixture
def simple_categorical_features(
    simple_num_numerical_features: int, simple_num_categorical_features: int
) -> Dict:
    """Categorical features for simple scenario."""
    categorical_features = {
        f"categorical_feature_{index}": {
            "name": f"categorical_feature_{index}",
            "kind": "categorical",
            "rank": simple_num_numerical_features + index + 1,
        }
        for index in range(simple_num_categorical_features)
    }
    return categorical_features


@pytest.fixture
def simple_feature_mapping(
    simple_numerical_features: Dict, simple_categorical_features: Dict
) -> Dict:
    """Feature mapping for simple scenario."""
    feature_mapping = {**simple_numerical_features, **simple_categorical_features}
    return feature_mapping


@pytest.fixture
def simple_baseline_data(
    simple_num_observations: int,
    simple_numerical_features: Dict,
    simple_categorical_features: Dict,
    simple_data_schema: pa.Schema,
) -> pa.Table:
    """Table of baseline data for simple scenario."""
    data: Dict[str, List[Union[int, str]]] = {}
    for feature in simple_numerical_features:
        data[feature] = [index for index in range(simple_num_observations)]
    for feature in simple_categorical_features:
        data[feature] = [
            f"category_{index}" for index in range(simple_num_observations)
        ]
    table = pa.Table.from_pydict(data, schema=simple_data_schema)
    return table
