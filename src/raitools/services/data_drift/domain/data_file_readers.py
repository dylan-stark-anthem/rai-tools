"""Data file readers."""

from typing import IO

import pyarrow as pa
from pyarrow.csv import read_csv

from raitools.services.data_drift.exceptions import BadDataFileError


def read_data_file(data_file: IO[bytes], data_filename: str) -> pa.Table:
    """Reads user-provided data file."""
    try:
        return read_csv(data_file)
    except pa.lib.ArrowInvalid as err:
        if "Empty CSV file" in err.args:
            raise BadDataFileError(f"Data file `{data_filename}` is empty.") from err
        raise BadDataFileError(
            f"Data file `{data_filename}` could not be parsed", *err.args
        ) from err
