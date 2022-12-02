"""Setup for tests."""

from pathlib import Path
import re
import shutil
import time
import uuid

from behave.model import Feature, Scenario
from behave.runner import Context


def before_all(context: Context) -> None:
    """Sets up ahead of all tests."""
    run_id = generate_run_id()

    scratch_path = Path("scratch/acceptance_tests") / run_id
    scratch_path.mkdir(parents=True, exist_ok=True)

    context.scratch_path = scratch_path


def before_feature(context: Context, feature: Feature) -> None:
    """Sets up ahead of feature tests."""
    if "skip" in feature.tags:
        feature.skip("Marked with @skip")
        return

    context.scratch_path /= get_valid_filename(context.feature.name)
    context.scratch_path.mkdir(parents=True, exist_ok=True)


def before_scenario(context: Context, scenario: Scenario) -> None:
    """Sets up ahead of scenario steps."""
    if "skip" in scenario.effective_tags:
        scenario.skip("Marked with @skip")
        return

    context.scratch_path /= get_valid_filename(context.scenario.name)
    context.scratch_path.mkdir(parents=True, exist_ok=True)

    context.tmp_path = context.scratch_path / "tmp"
    context.tmp_path.mkdir(parents=False, exist_ok=False)


def after_scenario(context: Context, scenario: Scenario) -> None:
    """Cleans up after scenario steps."""
    shutil.rmtree(context.tmp_path)


def generate_run_id() -> str:
    """Generates a unique run identifier."""
    run_uuid = uuid.uuid4().hex
    run_time = time.time()
    run_id = f"{str(int(run_time))}-{run_uuid[:6]}"

    return run_id


def get_valid_filename(name: str) -> str:
    """Converts name into a valid filename, if necessary."""
    s = str(name).strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    if s in {"", ".", ".."}:
        s = "unknown_scenario"
    return s
