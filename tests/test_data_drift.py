"""Tests for data drift."""

from pathlib import Path
from zipfile import ZipFile

import pyarrow as pa
from pyarrow.csv import write_csv

from raitools.data_drift.domain.job_config import JobConfig
from raitools.data_drift.use_cases.process_bundle import Request, process_bundle


def test_can_process_bundle(tmp_path: Path) -> None:
    """Tests that we can process a bundle."""
    job_config_json = {
        "dataset_name": "Some name for this dataset",
        "baseline_data_filename": "some_baseline_data.csv",
        "test_data_filename": "some_test_data.csv",
        "model_catalog_id": "123",
        "feature_mapping": [],
    }
    job_config_filename = "some_job_config.json"
    job_config = JobConfig(**job_config_json)
    job_config_path = tmp_path / job_config_filename
    job_config_path.write_text(job_config.json())

    num_rows = 10
    num_columns = 3

    baseline_data = {
        f"feature_{column}": range(num_rows) for column in range(num_columns)
    }
    baseline_data_table = pa.Table.from_pydict(baseline_data)
    baseline_data_path = tmp_path / job_config.baseline_data_filename
    write_csv(baseline_data_table, baseline_data_path)

    test_data = {f"feature_{column}": range(num_rows) for column in range(num_columns)}
    test_data_table = pa.Table.from_pydict(test_data)
    test_data_path = tmp_path / job_config.test_data_filename
    write_csv(test_data_table, test_data_path)

    bundle_path = tmp_path / "bundle.zip"
    with ZipFile(bundle_path, "w") as zip_file:
        zip_file.write(job_config_path, arcname=job_config_filename)
        zip_file.write(baseline_data_path, arcname=job_config.baseline_data_filename)
        zip_file.write(test_data_path, arcname=job_config.test_data_filename)

    request = Request(bundle_path=bundle_path)
    record = process_bundle(request)

    assert record.bundle_manifest.metadata.bundle_path == bundle_path
    assert record.bundle_manifest.metadata.job_config_filename == job_config_filename
    assert (
        record.bundle_manifest.metadata.baseline_data_filename
        == job_config.baseline_data_filename
    )
    assert (
        record.bundle_manifest.metadata.test_data_filename
        == job_config.test_data_filename
    )
    assert record.bundle_manifest.job_config == job_config
    assert record.bundle_manifest.baseline_data_summary.num_rows == num_rows
    assert record.bundle_manifest.baseline_data_summary.num_columns == num_columns
    assert record.bundle_manifest.test_data_summary.num_rows == num_rows
    assert record.bundle_manifest.test_data_summary.num_columns == num_columns
