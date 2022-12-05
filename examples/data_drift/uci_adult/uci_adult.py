"""Example using the UCI Adult data set."""

import json
from pathlib import Path
from zipfile import ZipFile
from raitools.domain.bundle import create_bundle_from_zip

from raitools.services.data_drift.use_cases.create_record import (
    create_record_from_bundle,
)
from raitools.services.data_drift.use_cases.create_report import create_report


def create_bundle(
    job_config_path: Path,
    feature_mapping_path: Path,
    baseline_data_path: Path,
    test_data_path: Path,
    output_path: Path,
) -> Path:
    """Creates the bundle."""
    bundle_path = output_path / "bundle.zip"
    with ZipFile(bundle_path, "w") as zip_file:
        zip_file.write(job_config_path, arcname=job_config_path.name)
        zip_file.write(feature_mapping_path, arcname=feature_mapping_path.name)
        zip_file.write(baseline_data_path, arcname=baseline_data_path.name)
        zip_file.write(test_data_path, arcname=test_data_path.name)

    return bundle_path


def run_uci_adult_example(bundle_path: Path, output_path: Path) -> None:
    """Runs UCI Adult data set example."""
    print("Running UCI Adult data set example ...")

    print(f"Using bundle at {bundle_path}")
    bundle = create_bundle_from_zip(bundle_path)
    record = create_record_from_bundle(bundle=bundle, bundle_filename=bundle_path.name)
    report = create_report(record, report_builder="plotly")

    record_filename = f"{record.bundle.job_config.report_name}.json"
    record_path = output_path / record_filename
    record_path.write_text(json.dumps(record.dict(), indent=4))

    report_filename = f"{record.bundle.job_config.report_name}.html"
    report_path = output_path / report_filename
    report_path.write_text(report)

    print(f"Wrote record to {record_path}")
    print(f"Wrote report to {report_path}")
    print("Done.")


def main() -> None:
    """Runs UCI Adult data set example."""
    job_config_path = Path("examples/data_drift/uci_adult/adult_job_config.json")
    feature_mapping_path = Path("examples/data_drift/uci_adult/feature_mapping.csv")
    baseline_data_path = Path("examples/data_drift/uci_adult/data/adult_baseline.csv")
    test_data_path = Path("examples/data_drift/uci_adult/data/adult_test.csv")
    output_path = Path("scratch/examples/data_drift/uci_adult/")
    output_path.mkdir(parents=True, exist_ok=True)

    bundle_path = create_bundle(
        job_config_path,
        feature_mapping_path,
        baseline_data_path,
        test_data_path,
        output_path,
    )

    run_uci_adult_example(bundle_path, output_path)


if __name__ == "__main__":
    main()
