"""Setup for simple test scenario."""

from typing import Dict, List, Union

import pyarrow as pa
import pytest


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
