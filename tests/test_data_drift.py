"""Tests for data drift."""

from pathlib import Path
from raitools.data_drift.use_cases.process_bundle import Request, process_bundle


def test_can_process_bundle() -> None:
    """Tests that we can process a bundle."""
    bundle_path = Path("/some/path/to/a/bundle.zip")
    request = Request(bundle_path=bundle_path)
    record = process_bundle(request)

    assert record.manifest.metadata.bundle_path == bundle_path
