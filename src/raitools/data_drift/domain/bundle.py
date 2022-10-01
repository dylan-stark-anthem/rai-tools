"""Data Drift bundle."""


import json
from pathlib import Path
import zipfile

from pydantic import BaseModel

from raitools.data_drift.domain.job_config import JobConfig


class Bundle(BaseModel):
    """A Data Drift bundle."""

    job_config_filename: str
    data_filename: str
    job_config: JobConfig


def create_bundle_from_zip(bundle_path: Path) -> Bundle:
    """Creates a bundle."""
    with zipfile.ZipFile(bundle_path, "r") as zip_file:
        files = zip_file.namelist()
        job_config_path = Path(
            [file_path for file_path in files if file_path.endswith(".json")][0]
        )
        job_config = json.loads(
            zipfile.Path(zip_file, at=str(job_config_path)).read_text()
        )

        data_path = Path(
            [file_path for file_path in files if file_path.endswith(".csv")][0]
        )

    bundle = Bundle(
        job_config_filename=job_config_path.name,
        data_filename=data_path.name,
        job_config=JobConfig(**job_config),
    )

    return bundle
