"""Tests for data file readers."""

import io
from typing import Callable

import pyarrow as pa
import pytest

from raitools.exceptions import BadDataFileError
from raitools.services.data_drift.data_file_readers import read_data_file


@pytest.mark.parametrize(
    "data_text,type_check_fn",
    [
        # Cases for integer fields
        ("f0\n1", pa.types.is_integer),
        ("f0\n2022", pa.types.is_integer),
        # Cases for floating point fields
        ("f0\n0.1", pa.types.is_floating),
        ("f0\n0.1\n42", pa.types.is_floating),
        # Cases for string fields
        ("f0\nfoo", pa.types.is_string),
        ("f0\n1\nfoo", pa.types.is_string),
        ("f0\n0.1\ntrue", pa.types.is_string),
        ("f0\n0.1\nTrue", pa.types.is_string),
        # Cases for dates and times
        ("f0\n1970-01-01", pa.types.is_date),
        ("f0\n01:01:01", pa.types.is_time),
        ("f0\n1970-01-01 01:01:01", pa.types.is_timestamp),
    ],
)
def test_can_infer_various_types(data_text: str, type_check_fn: Callable) -> None:
    """Tests that we correctly infer various types from raw strings."""
    data = io.BytesIO(data_text.encode())
    data_filename = "some_data_filename.csv"

    actual_table = read_data_file(data, data_filename)

    assert type_check_fn(actual_table.field("f0").type)


def test_error_if_empty() -> None:
    """Tests that we raise an error if the file is empty.

    In this case, it's really if there are no bytes to read.
    """
    data = io.BytesIO()
    data_filename = "some_empty.csv"
    expected_error = BadDataFileError(f"Data file `{data_filename}` is empty.")

    with pytest.raises(BadDataFileError) as excinfo:
        read_data_file(data, data_filename)

    assert (
        type(excinfo.value) == type(expected_error)
        and excinfo.value.args == expected_error.args
    )


def test_error_if_bad_csv() -> None:
    """Tests that we raise an error if the file is empty.

    In this case, it's really if there are no bytes to read.
    """
    data = io.BytesIO("f0,f1\n32\n14,17".encode())
    data_filename = "some_bad.csv"
    expected_error = BadDataFileError(
        f"Data file `{data_filename}` could not be parsed",
        "CSV parse error: Expected 2 columns, got 1: 32",
    )

    with pytest.raises(BadDataFileError) as excinfo:
        read_data_file(data, data_filename)

    assert (
        type(excinfo.value) == type(expected_error)
        and excinfo.value.args == expected_error.args
    )
