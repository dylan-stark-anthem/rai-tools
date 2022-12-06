"""Tests for bundles."""

import json
from pathlib import Path
from typing import Any, Dict
from zipfile import ZipFile

import pytest
from raitools.exceptions import (
    BadBundleZipFileError,
    BadDataFileError,
    BadFeatureMappingError,
    BadJobConfigError,
    BadPathToBundleError,
)
from raitools.services.data_drift.bundles import create_bundle_from_zip


@pytest.mark.parametrize(
    "bundle_path,error_message",
    [
        (
            "/some/str/path",
            "Path to bundle is not a valid `pathlib.Path`, it's a(n) `<class 'str'>`.",
        ),
        (
            42,
            "Path to bundle is not a valid `pathlib.Path`, it's a(n) `<class 'int'>`.",
        ),
        (
            4.2,
            "Path to bundle is not a valid `pathlib.Path`, it's a(n) `<class 'float'>`.",
        ),
    ],
)
def test_path_to_bundle_not_a_path(bundle_path: Any, error_message: str) -> None:
    """Tests that we raise appropriate error if path to bundle is not a Path."""
    with pytest.raises(BadPathToBundleError) as excinfo:
        create_bundle_from_zip(bundle_path)
    assert error_message in str(excinfo.value)


@pytest.mark.parametrize(
    "bundle_path,error_message",
    [
        (
            Path("some/path/that/does/not/exist"),
            "Path to bundle does not reference a valid zip file: `some/path/that/does/not/exist`",
        ),
        (
            Path("tests/services/data_drift/use_cases/resources"),
            "Path to bundle does not reference a valid zip file: `tests/services/data_drift/use_cases/resources`",
        ),
        (
            Path(
                "tests/services/data_drift/use_cases/resources/no_categorical_record.json"
            ),
            "Path to bundle does not reference a valid zip file: "
            "`tests/services/data_drift/use_cases/resources/no_categorical_record.json`",
        ),
    ],
)
def test_path_to_bundle_not_a_zip(bundle_path: Path, error_message: str) -> None:
    """Tests that we raise appropriate error if path not a zip file."""
    with pytest.raises(BadPathToBundleError) as excinfo:
        create_bundle_from_zip(bundle_path)
    assert error_message in str(excinfo.value)


def test_bundle_zip_empty(tmp_path: Path) -> None:
    """Tests that we raise appropriate error if zip file is empty."""
    path_to_empty_zip = tmp_path / "empty.zip"
    ZipFile(path_to_empty_zip, "w").close()
    bundle_path = path_to_empty_zip
    error_message = f"Bundle zip file is empty: `{bundle_path}`"

    with pytest.raises(BadBundleZipFileError) as excinfo:
        create_bundle_from_zip(bundle_path)

    assert error_message in str(excinfo.value)


def test_bundle_zip_without_json(tmp_path: Path) -> None:
    """Tests that we raise error if no JSON in zip."""
    path_to_no_json_zip = tmp_path / "no_json.zip"
    with ZipFile(path_to_no_json_zip, "w") as zip_file:
        some_file = tmp_path / "some_file.txt"
        some_file.touch()
        zip_file.write(some_file)
    bundle_path = path_to_no_json_zip
    error_message = f"Bundle zip file does not have any `.json` files: `{bundle_path}`"

    with pytest.raises(BadBundleZipFileError) as excinfo:
        create_bundle_from_zip(bundle_path)

    assert error_message in str(excinfo.value)


def test_bundle_zip_with_too_many_json(tmp_path: Path) -> None:
    """Tests that we raise error if more than one JSON in zip."""
    path_to_no_json_zip = tmp_path / "no_json.zip"
    with ZipFile(path_to_no_json_zip, "w") as zip_file:
        one_json = tmp_path / "one.json"
        one_json.touch()
        zip_file.write(one_json)
        two_json = tmp_path / "two.json"
        two_json.touch()
        zip_file.write(two_json)
    bundle_path = path_to_no_json_zip
    error_message = f"Bundle zip file has too many `.json` files: `{bundle_path}`"

    with pytest.raises(BadBundleZipFileError) as excinfo:
        create_bundle_from_zip(bundle_path)

    assert error_message in str(excinfo.value)


def test_job_config_not_well_formed(tmp_path: Path) -> None:
    """Tests that we raise error if job config is empty."""
    bundle_path = tmp_path / "bundle.zip"
    with ZipFile(bundle_path, "w") as zip_file:
        job_config_path = tmp_path / "job_config.json"
        job_config_path.touch()
        zip_file.write(job_config_path, arcname=job_config_path.name)
    error_message = (
        f"Job config `{job_config_path.name}` in `{bundle_path}` is not well-formed."
    )

    with pytest.raises(BadJobConfigError) as excinfo:
        create_bundle_from_zip(bundle_path)

    assert error_message in str(excinfo.value)


def test_baseline_data_filename_not_in_zip(tmp_path: Path) -> None:
    """Tests that we raise error if baseline data filename in config is not in zip."""
    bundle_path = tmp_path / "bundle.zip"
    baseline_data_filename = "file_not_in_zip.csv"
    test_data_filename = "file_in_zip.csv"
    job_config = {
        "baseline_data_filename": baseline_data_filename,
        "test_data_filename": test_data_filename,
    }
    with ZipFile(bundle_path, "w") as zip_file:
        job_config_path = tmp_path / "job_config.json"
        job_config_path.write_text(json.dumps(job_config))
        zip_file.write(job_config_path, arcname=job_config_path.name)
        test_data_path = tmp_path / test_data_filename
        test_data_path.touch()
        zip_file.write(test_data_path, arcname=test_data_path.name)
    error_message = f"Baseline data file `{baseline_data_filename}` referenced in `{job_config_path.name}` not in `{bundle_path}`."

    with pytest.raises(BadJobConfigError) as excinfo:
        create_bundle_from_zip(bundle_path)

    assert error_message in str(excinfo.value)


def test_test_data_filename_not_in_zip(tmp_path: Path) -> None:
    """Tests that we raise error if baseline data filename in config is not in zip."""
    bundle_path = tmp_path / "bundle.zip"
    baseline_data_filename = "file_in_zip.csv"
    test_data_filename = "file_not_in_zip.csv"
    job_config = {
        "baseline_data_filename": baseline_data_filename,
        "test_data_filename": test_data_filename,
    }
    with ZipFile(bundle_path, "w") as zip_file:
        job_config_path = tmp_path / "job_config.json"
        job_config_path.write_text(json.dumps(job_config))
        zip_file.write(job_config_path, arcname=job_config_path.name)
        baseline_data_path = tmp_path / baseline_data_filename
        baseline_data_path.touch()
        zip_file.write(baseline_data_path, arcname=baseline_data_path.name)
    error_message = f"Test data file `{test_data_filename}` referenced in `{job_config_path.name}` not in `{bundle_path}`."

    with pytest.raises(BadJobConfigError) as excinfo:
        create_bundle_from_zip(bundle_path)

    assert error_message in str(excinfo.value)


@pytest.fixture
def job_config() -> Dict:
    """A basic job config."""
    feature_mapping_filename = "feature_mapping.csv"
    baseline_data_filename = "baseline_data.csv"
    test_data_filename = "test_data.csv"
    job_config = {
        "service_name": "data_drift",
        "report_name": "report_name",
        "dataset_name": "dataset_name",
        "dataset_version": "dataset_version",
        "model_catalog_id": "model_catalog_id",
        "feature_mapping_filename": feature_mapping_filename,
        "baseline_data_filename": baseline_data_filename,
        "test_data_filename": test_data_filename,
    }
    return job_config


@pytest.fixture
def empty_feature_mapping_file_path(job_config: Dict, tmp_path: Path) -> Path:
    """A path to an empty feature mapping file."""
    feature_mapping_filename = job_config["feature_mapping_filename"]
    feature_mapping_path = tmp_path / feature_mapping_filename
    feature_mapping_path.touch()
    return feature_mapping_path


@pytest.fixture
def empty_feature_mapping_file_error(
    empty_feature_mapping_file_path: Path,
) -> Exception:
    """The error raised when the feature mapping is empty."""
    return BadFeatureMappingError(
        f"Feature mapping file `{empty_feature_mapping_file_path.name}` is empty."
    )


@pytest.fixture
def no_observations_feature_mapping_file_path(job_config: Dict, tmp_path: Path) -> Path:
    """A path to an empty feature mapping file."""
    feature_mapping_filename = job_config["feature_mapping_filename"]
    feature_mapping_path = tmp_path / feature_mapping_filename
    feature_mapping_path.write_text("name,kind,importance_score\n")
    return feature_mapping_path


@pytest.fixture
def no_observations_feature_mapping_file_error(
    no_observations_feature_mapping_file_path: Path,
) -> Exception:
    """The error raised when the feature mapping is empty."""
    return BadFeatureMappingError(
        f"Feature mapping file `{no_observations_feature_mapping_file_path.name}` does not contain any observations (only header)."
    )


@pytest.fixture
def non_empty_feature_mapping_file_path(job_config: Dict, tmp_path: Path) -> Path:
    """A path to an empty feature mapping file."""
    feature_mapping_filename = job_config["feature_mapping_filename"]
    feature_mapping_path = tmp_path / feature_mapping_filename
    feature_mapping_path.write_text(
        "\n".join(["name,kind,importance_score", "f0,numerical,0.9"])
    )
    return feature_mapping_path


@pytest.fixture
def numerical_feature_feature_mapping_file_path(
    job_config: Dict, tmp_path: Path
) -> Path:
    """A path to feature mapping file for single numerical feature."""
    feature_mapping_filename = job_config["feature_mapping_filename"]
    feature_mapping_path = tmp_path / feature_mapping_filename
    feature_mapping_path.write_text(
        "\n".join(["name,kind,importance_score", "f0,numerical,0.9"])
    )
    return feature_mapping_path


@pytest.fixture
def categorical_feature_feature_mapping_file_path(
    job_config: Dict, tmp_path: Path
) -> Path:
    """A path to feature mapping file for single categorical feature."""
    feature_mapping_filename = job_config["feature_mapping_filename"]
    feature_mapping_path = tmp_path / feature_mapping_filename
    feature_mapping_path.write_text(
        "\n".join(["name,kind,importance_score", "f0,categorical,0.9"])
    )
    return feature_mapping_path


@pytest.fixture
def empty_baseline_data_path(job_config: Dict, tmp_path: Path) -> Path:
    """A path to a non-empty baseline data file."""
    baseline_data_filename = job_config["baseline_data_filename"]
    baseline_data_path = tmp_path / baseline_data_filename
    baseline_data_path.touch()
    return baseline_data_path


@pytest.fixture
def empty_baseline_data_error(
    empty_baseline_data_path: Path,
) -> Exception:
    """The error raised when the baseline data file is empty."""
    return BadDataFileError(f"Data file `{empty_baseline_data_path.name}` is empty.")


@pytest.fixture
def no_observations_baseline_data_path(job_config: Dict, tmp_path: Path) -> Path:
    """A path to a baseline data file with no observations."""
    baseline_data_filename = job_config["baseline_data_filename"]
    baseline_data_path = tmp_path / baseline_data_filename
    baseline_data_path.write_text("f0\n")
    return baseline_data_path


@pytest.fixture
def no_observations_baseline_data_error(
    no_observations_baseline_data_path: Path,
) -> Exception:
    """The error raised when the baseline data file has no observations."""
    return BadDataFileError(
        f"Data file `{no_observations_baseline_data_path.name}` does not contain any observations (only header)."
    )


@pytest.fixture
def different_fields_baseline_data_file_path(job_config: Dict, tmp_path: Path) -> Path:
    """A path to a baseline data file with different fields."""
    baseline_data_filename = job_config["baseline_data_filename"]
    baseline_data_path = tmp_path / baseline_data_filename
    baseline_data_path.write_text("f1\n0.1\n")
    return baseline_data_path


@pytest.fixture
def different_fields_baseline_data_file_error(
    different_fields_baseline_data_file_path: Path,
) -> Exception:
    """The error raised when the feature mapping has different fields."""
    return BadDataFileError(
        f"Data file `{different_fields_baseline_data_file_path.name}` does not contain feature 'f0' from feature mapping."
    )


@pytest.fixture
def non_empty_baseline_data_path(job_config: Dict, tmp_path: Path) -> Path:
    """A path to a non-empty baseline data file."""
    baseline_data_filename = job_config["baseline_data_filename"]
    baseline_data_path = tmp_path / baseline_data_filename
    baseline_data_path.write_text("f0\n0.1\n")
    return baseline_data_path


@pytest.fixture
def string_feature_baseline_data_path(job_config: Dict, tmp_path: Path) -> Path:
    """A path to baseline data file with single string-valued feature."""
    baseline_data_filename = job_config["baseline_data_filename"]
    baseline_data_path = tmp_path / baseline_data_filename
    baseline_data_path.write_text("f0\n'0.1'\n")
    return baseline_data_path


@pytest.fixture
def bool_feature_baseline_data_path(job_config: Dict, tmp_path: Path) -> Path:
    """A path to baseline data file with single bool-valued feature."""
    baseline_data_filename = job_config["baseline_data_filename"]
    baseline_data_path = tmp_path / baseline_data_filename
    baseline_data_path.write_text("f0\nTrue\n")
    return baseline_data_path


@pytest.fixture
def int64_feature_baseline_data_path(job_config: Dict, tmp_path: Path) -> Path:
    """A path to baseline data file with single int64-valued feature."""
    baseline_data_filename = job_config["baseline_data_filename"]
    baseline_data_path = tmp_path / baseline_data_filename
    baseline_data_path.write_text("f0\n10\n")
    return baseline_data_path


@pytest.fixture
def double_feature_baseline_data_path(job_config: Dict, tmp_path: Path) -> Path:
    """A path to baseline data file with single double-valued feature."""
    baseline_data_filename = job_config["baseline_data_filename"]
    baseline_data_path = tmp_path / baseline_data_filename
    baseline_data_path.write_text("f0\n1.0\n")
    return baseline_data_path


@pytest.fixture
def empty_test_data_path(job_config: Dict, tmp_path: Path) -> Path:
    """A path to a non-empty test data file."""
    test_data_filename = job_config["test_data_filename"]
    test_data_path = tmp_path / test_data_filename
    test_data_path.touch()
    return test_data_path


@pytest.fixture
def empty_test_data_error(
    empty_test_data_path: Path,
) -> Exception:
    """The error raised when the test data file is empty."""
    return BadDataFileError(f"Data file `{empty_test_data_path.name}` is empty.")


@pytest.fixture
def no_observations_test_data_path(job_config: Dict, tmp_path: Path) -> Path:
    """A path to a test data file with no observations."""
    test_data_filename = job_config["test_data_filename"]
    test_data_path = tmp_path / test_data_filename
    test_data_path.write_text("f0\n")
    return test_data_path


@pytest.fixture
def no_observations_test_data_error(
    no_observations_test_data_path: Path,
) -> Exception:
    """The error raised when the test data file has no observations."""
    return BadDataFileError(
        f"Data file `{no_observations_test_data_path.name}` does not contain any observations (only header)."
    )


@pytest.fixture
def different_fields_test_data_file_path(job_config: Dict, tmp_path: Path) -> Path:
    """A path to a test data file with different fields."""
    test_data_filename = job_config["test_data_filename"]
    test_data_path = tmp_path / test_data_filename
    test_data_path.write_text("f1\n0.2\n")
    return test_data_path


@pytest.fixture
def different_fields_test_data_file_error(
    different_fields_test_data_file_path: Path,
) -> Exception:
    """The error raised when the feature mapping has different fields."""
    return BadDataFileError(
        f"Data file `{different_fields_test_data_file_path.name}` does not contain feature 'f0' from feature mapping."
    )


@pytest.fixture
def non_empty_test_data_path(job_config: Dict, tmp_path: Path) -> Path:
    """A path to a non-empty test data file."""
    test_data_filename = job_config["test_data_filename"]
    test_data_path = tmp_path / test_data_filename
    test_data_path.write_text("f0\n0.2\n")
    return test_data_path


@pytest.fixture
def numerical_test_data_path(job_config: Dict, tmp_path: Path) -> Path:
    """A path to test data file with valid numerical feature."""
    test_data_filename = job_config["test_data_filename"]
    test_data_path = tmp_path / test_data_filename
    test_data_path.write_text("f0\n0.2\n")
    return test_data_path


@pytest.fixture
def categorical_test_data_path(job_config: Dict, tmp_path: Path) -> Path:
    """A path to test data file with valid categorical feature."""
    test_data_filename = job_config["test_data_filename"]
    test_data_path = tmp_path / test_data_filename
    test_data_path.write_text("f0\nB\n")
    return test_data_path


@pytest.fixture
def string_numerical_field_error(
    string_feature_baseline_data_path: Path,
) -> Exception:
    """The error raised when the feature mapping has different fields."""
    return BadDataFileError(
        f"Numerical feature `f0` in `{string_feature_baseline_data_path.name}` parsed as `string`."
    )


@pytest.fixture
def bool_numerical_field_error(
    bool_feature_baseline_data_path: Path,
) -> Exception:
    """The error raised when the feature mapping has different fields."""
    return BadDataFileError(
        f"Numerical feature `f0` in `{bool_feature_baseline_data_path.name}` parsed as `bool`."
    )


@pytest.fixture
def int64_categorical_field_error(
    int64_feature_baseline_data_path: Path,
) -> Exception:
    """The error raised when the feature mapping has different fields."""
    return BadDataFileError(
        f"Categorical feature `f0` in `{int64_feature_baseline_data_path.name}` parsed as `int64`."
    )


@pytest.fixture
def double_categorical_field_error(
    double_feature_baseline_data_path: Path,
) -> Exception:
    """The error raised when the feature mapping has different fields."""
    return BadDataFileError(
        f"Categorical feature `f0` in `{double_feature_baseline_data_path.name}` parsed as `double`."
    )


def _create_bundle(
    job_config: Dict,
    feature_mapping_path_fixture: str,
    baseline_data_path_fixture: str,
    test_data_path_fixture: str,
    tmp_path: Path,
    request: pytest.FixtureRequest,
) -> Path:
    """A path to a bundle with an empty feature mapping file."""
    feature_mapping_path = request.getfixturevalue(feature_mapping_path_fixture)
    baseline_data_path = request.getfixturevalue(baseline_data_path_fixture)
    test_data_path = request.getfixturevalue(test_data_path_fixture)
    bundle_path = tmp_path / "bundle.zip"
    with ZipFile(bundle_path, "w") as zip_file:
        job_config_path = tmp_path / "job_config.json"
        job_config_path.write_text(json.dumps(job_config))
        zip_file.write(job_config_path, arcname=job_config_path.name)
        zip_file.write(
            feature_mapping_path,
            arcname=feature_mapping_path.name,
        )
        zip_file.write(baseline_data_path, arcname=baseline_data_path.name)
        zip_file.write(test_data_path, arcname=test_data_path.name)
    return bundle_path


@pytest.mark.parametrize(
    ",".join(
        [
            "feature_mapping_path_fixture",
            "baseline_data_path_fixture",
            "test_data_path_fixture",
            "expected_error_fixture",
        ]
    ),
    [
        # Cases in which one of the CSV files is empty
        (
            "empty_feature_mapping_file_path",
            "non_empty_baseline_data_path",
            "non_empty_test_data_path",
            "empty_feature_mapping_file_error",
        ),
        (
            "non_empty_feature_mapping_file_path",
            "empty_baseline_data_path",
            "non_empty_test_data_path",
            "empty_baseline_data_error",
        ),
        (
            "non_empty_feature_mapping_file_path",
            "non_empty_baseline_data_path",
            "empty_test_data_path",
            "empty_test_data_error",
        ),
        # Cases in which one of the CSV files only has a header
        (
            "no_observations_feature_mapping_file_path",
            "non_empty_baseline_data_path",
            "non_empty_test_data_path",
            "no_observations_feature_mapping_file_error",
        ),
        (
            "non_empty_feature_mapping_file_path",
            "no_observations_baseline_data_path",
            "non_empty_test_data_path",
            "no_observations_baseline_data_error",
        ),
        (
            "non_empty_feature_mapping_file_path",
            "non_empty_baseline_data_path",
            "no_observations_test_data_path",
            "no_observations_test_data_error",
        ),
        # Cases in which one of the CSV files has a different set of fields
        (
            "non_empty_feature_mapping_file_path",
            "different_fields_baseline_data_file_path",
            "non_empty_test_data_path",
            "different_fields_baseline_data_file_error",
        ),
        (
            "non_empty_feature_mapping_file_path",
            "non_empty_baseline_data_path",
            "different_fields_test_data_file_path",
            "different_fields_test_data_file_error",
        ),
        # Cases in which data file features are parsed as incompatible types
        (
            "numerical_feature_feature_mapping_file_path",
            "string_feature_baseline_data_path",
            "numerical_test_data_path",
            "string_numerical_field_error",
        ),
        (
            "numerical_feature_feature_mapping_file_path",
            "bool_feature_baseline_data_path",
            "numerical_test_data_path",
            "bool_numerical_field_error",
        ),
        (
            "categorical_feature_feature_mapping_file_path",
            "int64_feature_baseline_data_path",
            "categorical_test_data_path",
            "int64_categorical_field_error",
        ),
        (
            "categorical_feature_feature_mapping_file_path",
            "double_feature_baseline_data_path",
            "categorical_test_data_path",
            "double_categorical_field_error",
        ),
    ],
)
def test_csv_files(
    job_config: Dict,
    feature_mapping_path_fixture: str,
    baseline_data_path_fixture: str,
    test_data_path_fixture: str,
    expected_error_fixture: str,
    tmp_path: Path,
    request: pytest.FixtureRequest,
) -> None:
    """Tests that error raised if given empty data file."""
    bundle_path = _create_bundle(
        job_config,
        feature_mapping_path_fixture,
        baseline_data_path_fixture,
        test_data_path_fixture,
        tmp_path,
        request,
    )
    expected_error = request.getfixturevalue(expected_error_fixture)

    with pytest.raises(expected_error.__class__) as excinfo:
        create_bundle_from_zip(bundle_path)

    assert (
        type(excinfo.value) == type(expected_error)
        and excinfo.value.args == expected_error.args
    )
