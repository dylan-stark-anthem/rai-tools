"""Common helpers for test setup."""

from importlib import import_module
import json
from pathlib import Path
import random
from typing import Callable, Dict, List
from zipfile import ZipFile

import pyarrow as pa
from pyarrow.csv import write_csv

from raitools.services.data_drift.domain.data_drift_record import DataDriftRecord


def write_bundle_zip_to_disk(
    job_config_path: Path,
    feature_mapping_path: Path,
    baseline_data_path: Path,
    test_data_path: Path,
    job_config_filename: str,
    feature_mapping_filename: str,
    baseline_data_filename: str,
    test_data_filename: str,
    bundle_filename: str,
    tmp_path: Path,
) -> Path:
    """Creates a "physical" bundle on disk."""
    bundle_path = tmp_path / bundle_filename
    with ZipFile(bundle_path, "w") as zip_file:
        zip_file.write(job_config_path, arcname=job_config_filename)
        zip_file.write(feature_mapping_path, arcname=feature_mapping_filename)
        zip_file.write(baseline_data_path, arcname=baseline_data_filename)
        zip_file.write(test_data_path, arcname=test_data_filename)

    return bundle_path


def write_job_config_to_disk(
    job_config: Dict, job_config_filename: str, output_path: Path
) -> Path:
    """Writes job config to disk."""
    job_config_path = output_path / job_config_filename
    job_config_path.write_text(json.dumps(job_config))
    return job_config_path


def write_data_to_disk(data: pa.Table, data_filename: str, output_path: Path) -> Path:
    """Writes data to disk."""
    data_path = output_path / data_filename
    write_csv(data, data_path)
    return data_path


def data_generator(method: str, seed: int, kwargs: Dict) -> Callable:
    """Creates a method to reproducibly generate data."""
    module_path, method_name = method.rsplit(".", 1)
    fn = getattr(import_module(module_path), method_name)

    def data_generator_impl(count: int) -> List:
        random.seed(seed)
        return [fn(**kwargs) for _ in range(count)]

    return data_generator_impl


def create_data_table(data_spec: Dict, dataset: str, count: int) -> pa.Table:
    """Creates a data table based on given spec."""
    PA_TYPE = {
        "int64": pa.int64(),
        "float32": pa.float32(),
        "string": pa.string(),
    }

    data = {}
    schema = pa.schema([])

    for feature in data_spec.values():
        values = data_generator(**feature[dataset])(count)
        data[feature["name"]] = values

        field = pa.field(feature["name"], PA_TYPE[feature["kind"]])
        schema = schema.append(field)

    table = pa.Table.from_pydict(data, schema=schema)
    return table


def create_feature_mapping_table(data_spec: Dict) -> pa.Table:
    """Creates a feature mapping table based on given spec."""
    FEATURE_KIND = {
        "int64": "numerical",
        "float32": "numerical",
        "string": "categorical",
    }

    data = []
    schema = pa.schema(
        [
            pa.field("name", pa.string()),
            pa.field("kind", pa.string()),
            pa.field("importance_score", pa.float32()),
        ]
    )

    random.seed(0)
    for feature in data_spec.values():
        importance_score = random.random()
        data.append(
            {
                "name": feature["name"],
                "kind": FEATURE_KIND[feature["kind"]],
                "importance_score": importance_score,
            }
        )

    table = pa.Table.from_pylist(data, schema=schema)
    return table


def load_spec(spec_path: Path) -> Dict:
    """Loads specified spec from test resources."""
    spec = json.load(spec_path.open())
    return spec


def prepare_bundle(spec_filename: str, tmp_path: Path) -> Path:
    """Prepares bundle based on spec and returns path to it."""
    resources_path = Path("tests/services/data_drift/use_cases/resources")
    spec_path = resources_path / spec_filename
    spec = load_spec(spec_path)

    job_config_path = write_job_config_to_disk(
        spec["job_config"], spec["job_config_filename"], tmp_path
    )

    feature_mapping = create_feature_mapping_table(spec["data"])
    feature_mapping_path = write_data_to_disk(
        feature_mapping,
        spec["job_config"]["feature_mapping_filename"],
        tmp_path,
    )

    baseline_data = create_data_table(
        spec["data"], "baseline_data", spec["num_baseline_observations"]
    )
    baseline_data_path = write_data_to_disk(
        baseline_data, spec["job_config"]["baseline_data_filename"], tmp_path
    )

    test_data = create_data_table(
        spec["data"], "test_data", spec["num_test_observations"]
    )
    test_data_path = write_data_to_disk(
        test_data, spec["job_config"]["test_data_filename"], tmp_path
    )

    bundle_path = write_bundle_zip_to_disk(
        job_config_path,
        feature_mapping_path,
        baseline_data_path,
        test_data_path,
        spec["job_config_filename"],
        spec["job_config"]["feature_mapping_filename"],
        spec["job_config"]["baseline_data_filename"],
        spec["job_config"]["test_data_filename"],
        spec["bundle_filename"],
        tmp_path,
    )

    return bundle_path


def prepare_record(record_filename: str) -> DataDriftRecord:
    """Prepares record based on specified resource and returns it."""
    record_path = _path_under_resource_for(record_filename)
    expected_record_dict = json.load(record_path.open())
    expected_record = DataDriftRecord(**expected_record_dict)
    return expected_record


def prepare_report(report_filename: str) -> str:
    """Prepares report based on specified resource and returns it."""
    report_path = _path_under_resource_for(report_filename)
    expected_report = report_path.read_text()
    return expected_report


def _path_under_resource_for(filename: str) -> Path:
    """Constructs full path for file under resources directory."""
    resources_path = Path("tests/services/data_drift/use_cases/resources")
    path = resources_path / filename
    return path
