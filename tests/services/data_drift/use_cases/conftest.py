"""Test configuration for data drift."""


from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Union
from zipfile import ZipFile

import pyarrow as pa
from pyarrow.csv import write_csv
import pytest

from raitools import __version__
from raitools.services.data_drift.domain.bundle import (
    get_data_from_bundle,
    get_job_config_filename_from_bundle,
    get_job_config_from_bundle,
)
from raitools.services.data_drift.domain.data_drift_record import DataDriftRecord
from raitools.services.data_drift.domain.data_drift_report import DataDriftReport
from raitools.services.data_drift.domain.html_report_builder import (
    HtmlReportBuilder,
    basic_data_summary_maker,
    basic_drift_magnitude_maker,
    basic_drift_summary_maker,
)
from raitools.services.data_drift.domain.job_config import DataDriftJobConfig
from raitools.stats.bonferroni_correction import (
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
def simple_record(simple_bundle_path: Path) -> DataDriftRecord:
    """The expected record for the simple request."""
    job_config_filename = get_job_config_filename_from_bundle(simple_bundle_path)
    job_config = get_job_config_from_bundle(simple_bundle_path)

    num_numerical_features = _get_num_features_of_kind(simple_bundle_path, "numerical")
    num_categorical_features = _get_num_features_of_kind(
        simple_bundle_path, "categorical"
    )
    num_features = num_numerical_features + num_categorical_features
    num_baseline_observations = _get_num_observations_in_dataset(
        simple_bundle_path, "baseline_data"
    )
    num_test_observations = _get_num_observations_in_dataset(
        simple_bundle_path, "test_data"
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
                "bundle_path": simple_bundle_path,
                "job_config_filename": job_config_filename,
                "baseline_data_filename": job_config.baseline_data_filename,
                "test_data_filename": job_config.test_data_filename,
            },
        },
    }

    expected_record = DataDriftRecord(**expected_record_dict)
    return expected_record


@pytest.fixture
def simple_report_builder() -> HtmlReportBuilder:
    """Creates a report builder for the simple test case."""
    report_builder = HtmlReportBuilder()
    report_builder.data_summary_maker = basic_data_summary_maker
    report_builder.drift_summary_maker = basic_drift_summary_maker
    report_builder.drift_magnitude_maker = basic_drift_magnitude_maker
    return report_builder


@pytest.fixture
def simple_report_html(
    simple_record: DataDriftRecord, simple_report_builder: HtmlReportBuilder
) -> str:
    """Creates expected report html for simple test case."""
    job_config = simple_record.bundle.job_config
    data = simple_record.bundle.data

    thresholds: Dict[str, Dict[str, float]] = defaultdict(dict)
    for feature in simple_record.drift_summary.features.values():
        kind = feature.kind
        test_name = feature.statistical_test.name
        threshold = feature.statistical_test.adjusted_significance_level
        thresholds[kind][test_name] = threshold

    features = simple_record.drift_summary.features.values()
    num_total_features = len(features)

    drifted_features = [
        feature for feature in features if feature.drift_status == "drifted"
    ]
    num_features_drifted = len(drifted_features)

    top_10_drifted_features = [
        feature for feature in drifted_features if feature.rank <= 10
    ]
    num_top_10_features_drifted = len(top_10_drifted_features)

    top_20_drifted_features = [
        feature for feature in drifted_features if feature.rank <= 20
    ]
    num_top_20_features_drifted = len(top_20_drifted_features)

    fields = [
        "rank",
        "name",
        "kind",
        "p_value",
        "drift_status",
    ]
    ranked_features = sorted(features, key=lambda x: x.rank)
    observations: Dict[str, Any] = {
        "rank": [feature.rank for feature in ranked_features],
        "name": [feature.name for feature in ranked_features],
        "kind": [feature.kind for feature in ranked_features],
        "p_value": [
            feature.statistical_test.result.p_value for feature in ranked_features
        ],
        "drift_status": [feature.drift_status for feature in ranked_features],
    }

    report_data = DataDriftReport(
        report_name=job_config.report_name,
        dataset_name=job_config.dataset_name,
        dataset_version=job_config.dataset_version,
        model_catalog_id=job_config.model_catalog_id,
        thresholds=thresholds,
        num_total_features=num_total_features,
        num_features_drifted=num_features_drifted,
        top_10_features_drifted=num_top_10_features_drifted,
        top_20_features_drifted=num_top_20_features_drifted,
        fields=fields,
        observations=observations,
        num_rows_baseline_data=data["baseline_data"].num_rows,
        num_columns_baseline_data=data["baseline_data"].num_columns,
        num_rows_test_data=data["test_data"].num_rows,
        num_columns_test_data=data["test_data"].num_columns,
        num_numerical_features=(
            simple_record.drift_summary.metadata.num_numerical_features
        ),
        num_categorical_features=(
            simple_record.drift_summary.metadata.num_categorical_features
        ),
    )

    simple_report_builder.report_data = report_data
    simple_report_builder.compile()
    simple_report_html = simple_report_builder.get()

    return simple_report_html


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
