"""Example using the UCI Adult data set."""


from pathlib import Path
from zipfile import ZipFile

from raitools.data_drift.helpers.plotly import (
    plotly_data_summary_maker,
    plotly_drift_magnitude_maker,
    plotly_drift_summary_maker,
)
from raitools.data_drift.use_cases.generate_report import generate_report
from raitools.data_drift.use_cases.process_bundle import process_bundle


def create_bundle(
    job_config_path: Path,
    baseline_data_path: Path,
    test_data_path: Path,
    output_path: Path,
) -> Path:
    """Creates the bundle."""
    bundle_path = output_path / "bundle.zip"
    with ZipFile(bundle_path, "w") as zip_file:
        zip_file.write(job_config_path, arcname=job_config_path.name)
        zip_file.write(baseline_data_path, arcname=baseline_data_path.name)
        zip_file.write(test_data_path, arcname=test_data_path.name)

    return bundle_path


def run_uci_adult(bundle_path: Path, output_path: Path) -> None:
    """Runs UCI Adult data set example."""
    print("Running UCI Adult data set example ...")
    print(f"Using bundle at {bundle_path}")
    print(f"Writing results to {output_path}")

    record = process_bundle(bundle_path)
    generate_report(
        record,
        output_path=output_path,
        data_summary_maker=plotly_data_summary_maker,
        drift_summary_maker=plotly_drift_summary_maker,
        drift_magnitude_maker=plotly_drift_magnitude_maker,
    )

    print("Done.")


def main() -> None:
    """Runs UCI Adult data set example."""
    job_config_path = Path("examples/data_drift/uci_adult/adult_job_config.json")
    baseline_data_path = Path("examples/data_drift/uci_adult/data/adult_baseline.csv")
    test_data_path = Path("examples/data_drift/uci_adult/data/adult_test.csv")
    output_path = Path("scratch/examples/data_drift/uci_adult/")
    output_path.mkdir(parents=True, exist_ok=True)

    bundle_path = create_bundle(
        job_config_path, baseline_data_path, test_data_path, output_path
    )

    run_uci_adult(bundle_path, output_path)


if __name__ == "__main__":
    main()
