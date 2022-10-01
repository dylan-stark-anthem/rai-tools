"""Data Drift bundle."""


import json
from pathlib import Path
import zipfile

import pyarrow as pa
from pyarrow.csv import read_csv
from pydantic import BaseModel

from raitools.data_drift.domain.job_config import JobConfig


class Bundle(BaseModel):
    """A Data Drift bundle."""

    job_config_filename: str
    baseline_data_filename: str
    test_data_filename: str
    job_config: JobConfig
    baseline_data: pa.Table
    test_data: pa.Table

    class Config:
        """Configuration for bundle data model."""

        arbitrary_types_allowed = True


def create_bundle_from_zip(bundle_path: Path) -> Bundle:
    """Creates a bundle."""
    with zipfile.ZipFile(bundle_path, "r") as zip_file:
        files = zip_file.namelist()
        job_config_path = Path(
            [file_path for file_path in files if file_path.endswith(".json")][0]
        )
        job_config_json = json.loads(
            zipfile.Path(zip_file, at=str(job_config_path)).read_text()
        )
        job_config = JobConfig(**job_config_json)

    with zipfile.ZipFile(bundle_path, "r") as zip_file:
        with zip_file.open(job_config.baseline_data_filename) as data_file:
            baseline_data = read_csv(data_file)
        with zip_file.open(job_config.test_data_filename) as data_file:
            test_data = read_csv(data_file)

    bundle = Bundle(
        job_config_filename=job_config_path.name,
        baseline_data_filename=job_config.baseline_data_filename,
        test_data_filename=job_config.test_data_filename,
        job_config=job_config,
        baseline_data=baseline_data,
        test_data=test_data,
    )

    return bundle
