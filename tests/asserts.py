"""Custom asserts."""


from typing import Dict

from pydantic import BaseModel


def assert_equal_records(expected: BaseModel, actual: BaseModel) -> None:
    """Asserts that two records have the same members.

    This is a bit nicer than just `==`ing the dictionaries because any
    assertion error is thrown at the spot that it occurs.
    """
    expected_dict = expected.dict()
    actual_dict = actual.dict()
    assert_equal_dicts(expected_dict, actual_dict)


def assert_equal_dicts(expected_dict: Dict, actual_dict: Dict) -> None:
    """Asserts that two dictionaries have the same members.

    This is a bit nicer than just `==`ing the dictionaries because any
    assertion error is thrown at the spot that it occurs.
    """
    for key in expected_dict:
        assert key in actual_dict
        if isinstance(expected_dict[key], dict):
            assert_equal_dicts(expected_dict[key], actual_dict[key])
        else:
            assert expected_dict[key] == actual_dict[key]
