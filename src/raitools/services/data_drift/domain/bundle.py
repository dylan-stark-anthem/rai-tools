"""Data Drift bundle."""


import json
from pathlib import Path
import zipfile

import pyarrow as pa
from pyarrow.csv import read_csv
from pydantic import BaseModel

from raitools.services.data_drift.domain.job_config import DataDriftJobConfig
from raitools.services.data_drift.exceptions import (
    BadBundleZipFileError,
    BadJobConfigError,
    BadPathToBundleError,
)


class DataDriftBundle(BaseModel):
    """A Data Drift bundle."""

    job_config_filename: str
    baseline_data_filename: str
    test_data_filename: str
    job_config: DataDriftJobConfig
    baseline_data: pa.Table
    test_data: pa.Table

    class Config:
        """Configuration for bundle data model."""

        arbitrary_types_allowed = True


def create_bundle_from_zip(bundle_path: Path) -> DataDriftBundle:
    """Creates a bundle."""
    job_config = get_job_config_from_bundle(bundle_path)
    job_config_filename = get_job_config_filename_from_bundle(bundle_path)
    baseline_data = get_data_from_bundle(bundle_path, job_config.baseline_data_filename)
    test_data = get_data_from_bundle(bundle_path, job_config.test_data_filename)

    bundle = DataDriftBundle(
        job_config_filename=job_config_filename,
        baseline_data_filename=job_config.baseline_data_filename,
        test_data_filename=job_config.test_data_filename,
        job_config=job_config,
        baseline_data=baseline_data,
        test_data=test_data,
    )

    return bundle


def get_job_config_filename_from_bundle(bundle_path: Path) -> str:
    """Gets the job config filename from the bundle at this path."""
    with zipfile.ZipFile(bundle_path, "r") as zip_file:
        files = zip_file.namelist()
        job_config_path = Path(
            [file_path for file_path in files if file_path.endswith(".json")][0]
        )
    return job_config_path.name


def get_job_config_from_bundle(bundle_path: Path) -> DataDriftJobConfig:
    """Gets the job config from the bundle at this path."""
    _validate_is_zip_file(bundle_path)
    _validate_is_not_empty_zip_file(bundle_path)
    _validate_json_in_zip_file(bundle_path)
    _validate_job_config_is_well_formed(bundle_path)
    _validate_data_in_zip_file(bundle_path)

    with zipfile.ZipFile(bundle_path, "r") as zip_file:
        files = zip_file.namelist()
        job_config_path = Path(
            [file_path for file_path in files if file_path.endswith(".json")][0]
        )
        job_config_json = json.loads(
            zipfile.Path(zip_file, at=str(job_config_path)).read_text()
        )
        job_config = DataDriftJobConfig(**job_config_json)
    return job_config


def get_data_from_bundle(bundle_path: Path, data_filename: str) -> pa.Table:
    """Gets specified dataset from the bundle."""
    with zipfile.ZipFile(bundle_path, "r") as zip_file:
        with zip_file.open(data_filename) as data_file:
            data = read_csv(data_file)
    return data


def _validate_is_zip_file(bundle_path: Path) -> None:
    if not zipfile.is_zipfile(bundle_path):
        raise BadPathToBundleError(
            f"Path to bundle does not reference a valid zip file: `{bundle_path}`"
        )


def _validate_is_not_empty_zip_file(bundle_path: Path) -> None:
    with zipfile.ZipFile(bundle_path, "r") as zip_file:
        files = zip_file.namelist()
        if len(files) == 0:
            raise BadBundleZipFileError(f"Bundle zip file is empty: `{bundle_path}`")


def _validate_json_in_zip_file(bundle_path: Path) -> None:
    with zipfile.ZipFile(bundle_path, "r") as zip_file:
        filenames = zip_file.namelist()
        json_files = [filename for filename in filenames if filename.endswith(".json")]
        if len(json_files) == 0:
            raise BadBundleZipFileError(
                f"Bundle zip file does not have any `.json` files: `{bundle_path}`"
            )
        elif len(json_files) > 1:
            raise BadBundleZipFileError(
                f"Bundle zip file has too many `.json` files: `{bundle_path}`"
            )


def _validate_job_config_is_well_formed(bundle_path: Path) -> None:
    with zipfile.ZipFile(bundle_path, "r") as zip_file:
        filenames = zip_file.namelist()
        json_files = [filename for filename in filenames if filename.endswith(".json")]
        job_config_filename = json_files[0]
        job_config_text = zipfile.Path(zip_file, at=job_config_filename).read_text()
    try:
        json.loads(job_config_text)
    except json.JSONDecodeError as exc:
        raise BadJobConfigError(
            f"Job config `{job_config_filename}` in `{bundle_path}` is not well-formed."
        ) from exc


def _validate_data_in_zip_file(bundle_path: Path) -> None:
    with zipfile.ZipFile(bundle_path, "r") as zip_file:
        filenames = zip_file.namelist()
        json_files = [filename for filename in filenames if filename.endswith(".json")]
        job_config_filename = json_files[0]
        job_config_json = json.loads(
            zipfile.Path(zip_file, at=job_config_filename).read_text()
        )
        baseline_data_filename = job_config_json["baseline_data_filename"]
        test_data_filename = job_config_json["test_data_filename"]
    if baseline_data_filename not in filenames:
        raise BadJobConfigError(
            f"Baseline data file `{baseline_data_filename}` referenced in `{job_config_filename}` not in `{bundle_path}`."
        )
    if test_data_filename not in filenames:
        raise BadJobConfigError(
            f"Test data file `{test_data_filename}` referenced in `{job_config_filename}` not in `{bundle_path}`."
        )
