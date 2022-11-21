"""Tests for Z-IR statistical significance test."""


from typing import List

from raitools.stats.z_ir import get_z_ir_parameters, z_ir


def test_can_run_z_ir_test() -> None:
    """Tests that we can run the Z-IR test."""
    group_a_data: List = [0, 1, 0, 1]
    group_b_data: List = [0, 0, 0, 1]
    expected_statistic = 0.123456
    expected_p_value = 0.123

    SR_min, SR_maj, SR_T, N, P_min = get_z_ir_parameters(group_a_data, group_b_data)
    actual_statistic, actual_p_value = z_ir(SR_min, SR_maj, SR_T, N, P_min)

    assert actual_statistic == expected_statistic
    assert actual_p_value == expected_p_value
