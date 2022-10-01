"""Tests for data drift."""

from pathlib import Path
from zipfile import ZipFile
from raitools.data_drift.use_cases.process_bundle import Request, process_bundle


def test_can_process_bundle(tmp_path: Path) -> None:
    """Tests that we can process a bundle."""
    job_config_filename = "some_job_config.json"
    job_config_path = tmp_path / job_config_filename
    job_config_path.touch()

    data_filename = "some_data.csv"
    data_path = tmp_path / data_filename
    data_path.touch()

    bundle_path = tmp_path / "bundle.zip"
    with ZipFile(bundle_path, "w") as zip_file:
        zip_file.write(job_config_path)
        zip_file.write(data_path)

    request = Request(bundle_path=bundle_path)
    record = process_bundle(request)

    assert record.bundle_manifest.metadata.bundle_path == bundle_path
    assert record.bundle_manifest.metadata.job_config_filename == job_config_filename
    assert record.bundle_manifest.metadata.data_filename == data_filename
