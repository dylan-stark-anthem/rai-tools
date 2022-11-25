"""Data Drift bundle."""


import json
from pathlib import Path
from typing import IO, List
import zipfile

import pyarrow as pa
from pyarrow.csv import read_csv
from pydantic import BaseModel
from raitools.services.data_drift.domain.feature_mapping import FeatureMapping

from raitools.services.data_drift.domain.job_config import DataDriftJobConfig
from raitools.services.data_drift.exceptions import (
    BadBundleZipFileError,
    BadDataFileError,
    BadFeatureMappingError,
    BadJobConfigError,
    BadPathToBundleError,
)


class DataDriftBundle(BaseModel):
    """A Data Drift bundle."""

    job_config_filename: str
    baseline_data_filename: str
    test_data_filename: str
    job_config: DataDriftJobConfig
    feature_mapping: FeatureMapping
    baseline_data: pa.Table
    test_data: pa.Table

    class Config:
        """Configuration for bundle data model."""

        arbitrary_types_allowed = True


def create_bundle_from_zip(bundle_path: Path) -> DataDriftBundle:
    """Creates a bundle."""
    job_config = get_job_config_from_bundle(bundle_path)
    job_config_filename = get_job_config_filename_from_bundle(bundle_path)
    feature_mapping = get_feature_mapping_from_bundle(
        bundle_path, job_config.feature_mapping_filename
    )
    baseline_data = get_data_from_bundle(
        bundle_path,
        job_config.baseline_data_filename,
        list(feature_mapping.feature_mapping.keys()),
        list(feature_mapping.feature_mapping.values()),
    )
    test_data = get_data_from_bundle(
        bundle_path,
        job_config.test_data_filename,
        list(feature_mapping.feature_mapping.keys()),
        list(feature_mapping.feature_mapping.values()),
    )

    bundle = DataDriftBundle(
        job_config_filename=job_config_filename,
        baseline_data_filename=job_config.baseline_data_filename,
        test_data_filename=job_config.test_data_filename,
        job_config=job_config,
        feature_mapping=feature_mapping,
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


def get_feature_mapping_from_bundle(
    bundle_path: Path, feature_mapping_filename: str
) -> FeatureMapping:
    """Gets specified feature mapping from the bundle."""
    with zipfile.ZipFile(bundle_path, "r") as zip_file:
        with zip_file.open(feature_mapping_filename) as feature_mapping_file:
            feature_mapping_table = read_feature_mapping_file(
                feature_mapping_file, feature_mapping_filename
            )

    _validate_feature_mapping_file_has_observations(
        feature_mapping_table, feature_mapping_filename
    )

    feature_mapping_values = {
        feature["name"]: feature for feature in feature_mapping_table.to_pylist()
    }
    feature_mapping = FeatureMapping(feature_mapping=feature_mapping_values)
    return feature_mapping


def get_data_from_bundle(
    bundle_path: Path,
    data_filename: str,
    required_fields: List[str],
    features: List,
) -> pa.Table:
    """Gets specified dataset from the bundle."""
    with zipfile.ZipFile(bundle_path, "r") as zip_file:
        with zip_file.open(data_filename) as data_file:
            data = read_data_file(data_file, data_filename)

    _validate_data_file_has_observations(data, data_filename)
    _validate_data_file_has_required_fields(data, data_filename, required_fields)
    _validate_fields_compatible_with_features(data, data_filename, features)
    return data


def read_feature_mapping_file(data_file: IO[bytes], data_filename: str) -> pa.Table:
    """Reads user-provided data file."""
    try:
        return read_csv(data_file)
    except pa.lib.ArrowInvalid as err:
        if "Empty CSV file" in err.args:
            raise BadFeatureMappingError(
                f"Feature mapping file `{data_filename}` is empty."
            ) from err
        raise


def read_data_file(data_file: IO[bytes], data_filename: str) -> pa.Table:
    """Reads user-provided data file."""
    try:
        return read_csv(data_file)
    except pa.lib.ArrowInvalid as err:
        if "Empty CSV file" in err.args:
            raise BadDataFileError(f"Data file `{data_filename}` is empty.") from err
        raise


def _validate_data_file_has_observations(data: pa.Table, data_filename: str) -> None:
    if data.num_rows == 0:
        raise BadDataFileError(
            f"Data file `{data_filename}` does not contain any observations (only header)."
        )


def _validate_feature_mapping_file_has_observations(
    data: pa.Table, data_filename: str
) -> None:
    if data.num_rows == 0:
        raise BadFeatureMappingError(
            f"Feature mapping file `{data_filename}` does not contain any observations (only header)."
        )


def _validate_data_file_has_required_fields(
    data: pa.Table, data_filename: str, required_fields: List[str]
) -> None:
    for required_field in required_fields:
        if required_field not in data.column_names:
            raise BadDataFileError(
                f"Data file `{data_filename}` does not contain feature '{required_field}' from feature mapping."
            )

    return data


def _validate_fields_compatible_with_features(
    data: pa.Table, data_filename: str, features: List
) -> None:
    def _check_compatibility_with_numeric(field_type: pa.DataType) -> bool:
        return pa.types.is_integer(field_type) or pa.types.is_floating(field_type)

    def _check_compatibility_with_categorical(field_type: pa.DataType) -> bool:
        return pa.types.is_string(field_type)

    compatible_kind = {
        "numerical": _check_compatibility_with_numeric,
        "categorical": _check_compatibility_with_categorical,
    }

    for feature in features:
        field_type = data.schema.field(feature.name).type
        if not compatible_kind[feature.kind](field_type):
            raise BadDataFileError(
                f"{feature.kind.capitalize()} feature `f0` in `{data_filename}` parsed as `{field_type}`."
            )


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
