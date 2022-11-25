"""Tests for process bundle use case."""

import json
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import pytest
from raitools.services.data_drift.exceptions import (
    BadBundleZipFileError,
    BadDataFileError,
    BadJobConfigError,
    BadPathToBundleError,
)

from raitools.services.data_drift.use_cases.process_bundle import process_bundle

from tests.asserts import assert_equal_records
from tests.services.data_drift.use_cases.common import (
    prepare_bundle,
    prepare_record,
)


@pytest.mark.parametrize(
    "spec_filename,record_filename",
    [
        ("simple_undrifted_spec.json", "simple_undrifted_record.json"),
        ("simple_drifted_spec.json", "simple_drifted_record.json"),
        ("no_numerical_spec.json", "no_numerical_record.json"),
        ("no_categorical_spec.json", "no_categorical_record.json"),
        ("with_113_features_spec.json", "with_113_features_record.json"),
        ("with_13_features_spec.json", "with_13_features_record.json"),
    ],
)
def test_can_process_bundle(
    spec_filename: str, record_filename: str, tmp_path: Path
) -> None:
    """Tests that we can process a bundle."""
    bundle_path = prepare_bundle(spec_filename, tmp_path)

    actual_record = process_bundle(bundle_path)

    expected_record = prepare_record(record_filename)
    assert_equal_records(expected_record, actual_record)


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
        process_bundle(bundle_path)
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
        process_bundle(bundle_path)
    assert error_message in str(excinfo.value)


def test_bundle_zip_empty(tmp_path: Path) -> None:
    """Tests that we raise appropriate error if zip file is empty."""
    path_to_empty_zip = tmp_path / "empty.zip"
    ZipFile(path_to_empty_zip, "w").close()
    bundle_path = path_to_empty_zip
    error_message = f"Bundle zip file is empty: `{bundle_path}`"

    with pytest.raises(BadBundleZipFileError) as excinfo:
        process_bundle(bundle_path)

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
        process_bundle(bundle_path)

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
        process_bundle(bundle_path)

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
        process_bundle(bundle_path)

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
        process_bundle(bundle_path)

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
        process_bundle(bundle_path)

    assert error_message in str(excinfo.value)


def test_baseline_data_file_empty(tmp_path: Path) -> None:
    """Tests that error raised if given empty data file."""
    bundle_path = tmp_path / "bundle.zip"
    baseline_data_filename = "baseline_data.csv"
    test_data_filename = "test_data.csv"
    job_config = {
        "report_name": "report_name",
        "dataset_name": "dataset_name",
        "dataset_version": "dataset_version",
        "model_catalog_id": "model_catalog_id",
        "feature_mapping": {"f0": {"name": "f0", "kind": "numerical", "rank": 1}},
        "baseline_data_filename": baseline_data_filename,
        "test_data_filename": test_data_filename,
    }
    with ZipFile(bundle_path, "w") as zip_file:
        job_config_path = tmp_path / "job_config.json"
        job_config_path.write_text(json.dumps(job_config))
        zip_file.write(job_config_path, arcname=job_config_path.name)
        baseline_data_path = tmp_path / baseline_data_filename
        baseline_data_path.touch()
        test_data_path = tmp_path / test_data_filename
        test_data_path.write_text("f0\n")
        zip_file.write(baseline_data_path, arcname=baseline_data_path.name)
        zip_file.write(test_data_path, arcname=test_data_path.name)
    expected_error = BadDataFileError(f"Data file `{baseline_data_filename}` is empty.")

    with pytest.raises(BadDataFileError) as excinfo:
        process_bundle(bundle_path)

    assert (
        type(excinfo.value) == type(expected_error)
        and excinfo.value.args == expected_error.args
    )


def test_test_data_file_empty(tmp_path: Path) -> None:
    """Tests that error raised if given empty data file."""
    bundle_path = tmp_path / "bundle.zip"
    baseline_data_filename = "baseline_data.csv"
    test_data_filename = "test_data.csv"
    job_config = {
        "report_name": "report_name",
        "dataset_name": "dataset_name",
        "dataset_version": "dataset_version",
        "model_catalog_id": "model_catalog_id",
        "feature_mapping": {"f0": {"name": "f0", "kind": "numerical", "rank": 1}},
        "baseline_data_filename": baseline_data_filename,
        "test_data_filename": test_data_filename,
    }
    with ZipFile(bundle_path, "w") as zip_file:
        job_config_path = tmp_path / "job_config.json"
        job_config_path.write_text(json.dumps(job_config))
        zip_file.write(job_config_path, arcname=job_config_path.name)
        baseline_data_path = tmp_path / baseline_data_filename
        baseline_data_path.write_text("f0\n0.1\n")
        test_data_path = tmp_path / test_data_filename
        test_data_path.touch()
        zip_file.write(baseline_data_path, arcname=baseline_data_path.name)
        zip_file.write(test_data_path, arcname=test_data_path.name)
    expected_error = BadDataFileError(f"Data file `{test_data_filename}` is empty.")

    with pytest.raises(BadDataFileError) as excinfo:
        process_bundle(bundle_path)

    assert (
        type(excinfo.value) == type(expected_error)
        and excinfo.value.args == expected_error.args
    )


def test_test_data_file_has_no_observations(tmp_path: Path) -> None:
    """Tests that error raised if data file has no observations."""
    bundle_path = tmp_path / "bundle.zip"
    baseline_data_filename = "baseline_data.csv"
    test_data_filename = "test_data.csv"
    job_config = {
        "report_name": "report_name",
        "dataset_name": "dataset_name",
        "dataset_version": "dataset_version",
        "model_catalog_id": "model_catalog_id",
        "feature_mapping": {"f0": {"name": "f0", "kind": "numerical", "rank": 1}},
        "baseline_data_filename": baseline_data_filename,
        "test_data_filename": test_data_filename,
    }
    with ZipFile(bundle_path, "w") as zip_file:
        job_config_path = tmp_path / "job_config.json"
        job_config_path.write_text(json.dumps(job_config))
        zip_file.write(job_config_path, arcname=job_config_path.name)
        baseline_data_path = tmp_path / baseline_data_filename
        baseline_data_path.write_text("f0\n1.0\n")
        test_data_path = tmp_path / test_data_filename
        test_data_path.write_text("f0\n")
        zip_file.write(baseline_data_path, arcname=baseline_data_path.name)
        zip_file.write(test_data_path, arcname=test_data_path.name)
    expected_error = BadDataFileError(
        f"Data file `{test_data_filename}` does not contain any observations (only header)."
    )

    with pytest.raises(BadDataFileError) as excinfo:
        process_bundle(bundle_path)

    assert (
        type(excinfo.value) == type(expected_error)
        and excinfo.value.args == expected_error.args
    )


def test_baseline_data_file_has_no_observations(tmp_path: Path) -> None:
    """Tests that error raised if data file has no observations."""
    bundle_path = tmp_path / "bundle.zip"
    baseline_data_filename = "baseline_data.csv"
    test_data_filename = "test_data.csv"
    job_config = {
        "report_name": "report_name",
        "dataset_name": "dataset_name",
        "dataset_version": "dataset_version",
        "model_catalog_id": "model_catalog_id",
        "feature_mapping": {"f0": {"name": "f0", "kind": "numerical", "rank": 1}},
        "baseline_data_filename": baseline_data_filename,
        "test_data_filename": test_data_filename,
    }
    with ZipFile(bundle_path, "w") as zip_file:
        job_config_path = tmp_path / "job_config.json"
        job_config_path.write_text(json.dumps(job_config))
        zip_file.write(job_config_path, arcname=job_config_path.name)
        baseline_data_path = tmp_path / baseline_data_filename
        baseline_data_path.write_text("f0\n")
        test_data_path = tmp_path / test_data_filename
        test_data_path.write_text("f0\n1.0\n")
        zip_file.write(baseline_data_path, arcname=baseline_data_path.name)
        zip_file.write(test_data_path, arcname=test_data_path.name)
    expected_error = BadDataFileError(
        f"Data file `{baseline_data_filename}` does not contain any observations (only header)."
    )

    with pytest.raises(BadDataFileError) as excinfo:
        process_bundle(bundle_path)

    assert (
        type(excinfo.value) == type(expected_error)
        and excinfo.value.args == expected_error.args
    )


def test_baseline_data_file_missing_required_field(tmp_path: Path) -> None:
    """Tests that error raised if data file missing required field."""
    bundle_path = tmp_path / "bundle.zip"
    baseline_data_filename = "baseline_data.csv"
    test_data_filename = "test_data.csv"
    job_config = {
        "report_name": "report_name",
        "dataset_name": "dataset_name",
        "dataset_version": "dataset_version",
        "model_catalog_id": "model_catalog_id",
        "feature_mapping": {"f0": {"name": "f0", "kind": "numerical", "rank": 1}},
        "baseline_data_filename": baseline_data_filename,
        "test_data_filename": test_data_filename,
    }
    with ZipFile(bundle_path, "w") as zip_file:
        job_config_path = tmp_path / "job_config.json"
        job_config_path.write_text(json.dumps(job_config))
        zip_file.write(job_config_path, arcname=job_config_path.name)
        baseline_data_path = tmp_path / baseline_data_filename
        baseline_data_path.write_text("f1\n1.0\n")
        test_data_path = tmp_path / test_data_filename
        test_data_path.write_text("f0\n1.0\n")
        zip_file.write(baseline_data_path, arcname=baseline_data_path.name)
        zip_file.write(test_data_path, arcname=test_data_path.name)
    expected_error = BadDataFileError(
        f"Data file `{baseline_data_filename}` does not contain feature 'f0' from feature mapping."
    )

    with pytest.raises(BadDataFileError) as excinfo:
        process_bundle(bundle_path)

    assert (
        type(excinfo.value) == type(expected_error)
        and excinfo.value.args == expected_error.args
    )


def test_test_data_file_missing_required_field(tmp_path: Path) -> None:
    """Tests that error raised if data file missing required field."""
    bundle_path = tmp_path / "bundle.zip"
    baseline_data_filename = "baseline_data.csv"
    test_data_filename = "test_data.csv"
    job_config = {
        "report_name": "report_name",
        "dataset_name": "dataset_name",
        "dataset_version": "dataset_version",
        "model_catalog_id": "model_catalog_id",
        "feature_mapping": {"f0": {"name": "f0", "kind": "numerical", "rank": 1}},
        "baseline_data_filename": baseline_data_filename,
        "test_data_filename": test_data_filename,
    }
    with ZipFile(bundle_path, "w") as zip_file:
        job_config_path = tmp_path / "job_config.json"
        job_config_path.write_text(json.dumps(job_config))
        zip_file.write(job_config_path, arcname=job_config_path.name)
        baseline_data_path = tmp_path / baseline_data_filename
        baseline_data_path.write_text("f0\n1.0\n")
        test_data_path = tmp_path / test_data_filename
        test_data_path.write_text("f1\n1.0\n")
        zip_file.write(baseline_data_path, arcname=baseline_data_path.name)
        zip_file.write(test_data_path, arcname=test_data_path.name)
    expected_error = BadDataFileError(
        f"Data file `{test_data_filename}` does not contain feature 'f0' from feature mapping."
    )

    with pytest.raises(BadDataFileError) as excinfo:
        process_bundle(bundle_path)

    assert (
        type(excinfo.value) == type(expected_error)
        and excinfo.value.args == expected_error.args
    )


@pytest.mark.parametrize(
    "feature_kind,field_value,field_type",
    [
        ("numerical", "'1.0'", "string"),
        ("numerical", "True", "bool"),
        ("categorical", "10", "int64"),
        ("categorical", "1.0", "double"),
    ],
)
def test_baseline_data_incompatible_field_type(
    feature_kind: str, field_value: str, field_type: str, tmp_path: Path
) -> None:
    """Tests that error raised if data file has incompatible field type."""
    bundle_path = tmp_path / "bundle.zip"
    baseline_data_filename = "baseline_data.csv"
    test_data_filename = "test_data.csv"
    job_config = {
        "report_name": "report_name",
        "dataset_name": "dataset_name",
        "dataset_version": "dataset_version",
        "model_catalog_id": "model_catalog_id",
        "feature_mapping": {"f0": {"name": "f0", "kind": feature_kind, "rank": 1}},
        "baseline_data_filename": baseline_data_filename,
        "test_data_filename": test_data_filename,
    }
    with ZipFile(bundle_path, "w") as zip_file:
        job_config_path = tmp_path / "job_config.json"
        job_config_path.write_text(json.dumps(job_config))
        zip_file.write(job_config_path, arcname=job_config_path.name)
        baseline_data_path = tmp_path / baseline_data_filename
        baseline_data_path.write_text(f"f0\n{field_value}\n")
        test_data_path = tmp_path / test_data_filename
        test_data_path.write_text("f0\n1.0\n")
        zip_file.write(baseline_data_path, arcname=baseline_data_path.name)
        zip_file.write(test_data_path, arcname=test_data_path.name)
    expected_error = BadDataFileError(
        f"{feature_kind.capitalize()} feature `f0` in `{baseline_data_filename}` parsed as `{field_type}`."
    )

    with pytest.raises(BadDataFileError) as excinfo:
        process_bundle(bundle_path)

    assert (
        type(excinfo.value) == type(expected_error)
        and excinfo.value.args == expected_error.args
    )
