"""Tests for Z-IR statistical significance test."""

import math
from typing import List

import numpy
import pytest

from raitools.stats.z_ir import get_z_ir_parameters, z_ir, sample_size


def test_can_run_z_ir_test() -> None:
    """test can run using one example from Morris paper."""
    total_n = 200
    proportion_minority = 0.25
    n_minority = total_n * proportion_minority
    n_majority = total_n * (1 - proportion_minority)
    selection_rate_minority = 0.2
    selection_rate_majority = 0.33

    group_a_data = numpy.zeros(int(n_majority))
    group_a_data[: math.ceil(n_majority * selection_rate_majority)] = 1
    numpy.random.shuffle(group_a_data)
    group_b_data = numpy.zeros(int(n_minority))
    group_b_data[: int(n_minority * selection_rate_minority)] = 1
    numpy.random.shuffle(group_b_data)

    expected_statistic = -2.05
    expected_p_value = 0.0202
    SR_min, SR_maj, SR_T, N, P_min = get_z_ir_parameters(group_a_data, group_b_data)
    actual_statistic, actual_p_value = z_ir(SR_min, SR_maj, SR_T, N, P_min)
    assert abs(actual_statistic - expected_statistic) < 0.01
    assert abs(actual_p_value - expected_p_value) < 0.001


def test_can_not_run_z_ir_test_empty_list() -> None:
    """Tests that we can not run the Z-IR test."""
    group_a_data: List = []
    group_b_data: List = []

    with pytest.raises(IndexError):
        get_z_ir_parameters(group_a_data, group_b_data)


def test_can_not_run_z_ir_test_zero_value_list() -> None:
    """Tests that we can not run the Z-IR test."""
    group_a_data: List = [0, 0, 0, 0, 0, 0]
    group_b_data: List = [1, 1, 1, 0, 0, 0]
    try:
        SR_min, SR_maj, SR_T, N, P_min = get_z_ir_parameters(group_a_data, group_b_data)
        actual_statistic, actual_p_value = z_ir(SR_min, SR_maj, SR_T, N, P_min)
        SR_min, SR_maj, SR_T, N, P_min = get_z_ir_parameters(group_b_data, group_a_data)
        actual_statistic, actual_p_value = z_ir(SR_min, SR_maj, SR_T, N, P_min)
        assert False
    except:
        assert True


import pandas as pd
import pytest


diff_sample_size_cutoff = 3

morris_df = pd.read_csv(
    "/workspaces/rai-tools/examples/stats/z_ir/data/Morris_table_1_csv.csv"
)
testdata = morris_df.to_records(index=False)


@pytest.mark.parametrize(
    "sr_t_morris,impact_ratio_morris,sample_at_10pct_min_morris_zd,sample_at_10pct_min_morris_zir,sample_at_10pct_min_z45,sample_at_30pct_min_morris_zd,sample_at_30pct_min_morris_zir,sample_at_30pct_min_morris_z45,sample_at_50pct_min_morris_zd,sample_at_50pct_min_morris_zir,sample_at_50pct_min_z45",
    testdata,
)
def test_1(
    sr_t_morris,
    impact_ratio_morris,
    sample_at_10pct_min_morris_zd,
    sample_at_10pct_min_morris_zir,
    sample_at_10pct_min_z45,
    sample_at_30pct_min_morris_zd,
    sample_at_30pct_min_morris_zir,
    sample_at_30pct_min_morris_z45,
    sample_at_50pct_min_morris_zd,
    sample_at_50pct_min_morris_zir,
    sample_at_50pct_min_z45,
):

    p_min = 0.1
    pi_T = sr_t_morris
    impact_ratio = impact_ratio_morris
    pi_min = pi_T * impact_ratio / (1 + p_min * (impact_ratio - 1))
    pi_maj = pi_T / (1 + p_min * (impact_ratio - 1))
    # assert abs(N_IR(N,sr_t_morris,pi_min,pi_maj,p_min,alpha=0.05) - sample_at_10pct_min_morris_zir) < diff_sample_size_cutoff
    assert (
        abs(
            sample_size(
                sr_t_morris,
                pi_min,
                pi_maj,
                p_min,
                alpha=0.05,
                power=0.8,
                one_tailed_test=0,
            )[1]
            - sample_at_10pct_min_morris_zir
        )
        < diff_sample_size_cutoff
    )


@pytest.mark.parametrize(
    "sr_t_morris,impact_ratio_morris,sample_at_10pct_min_morris_zd,sample_at_10pct_min_morris_zir,sample_at_10pct_min_z45,sample_at_30pct_min_morris_zd,sample_at_30pct_min_morris_zir,sample_at_30pct_min_morris_z45,sample_at_50pct_min_morris_zd,sample_at_50pct_min_morris_zir,sample_at_50pct_min_z45",
    testdata,
)
def test_2(
    sr_t_morris,
    impact_ratio_morris,
    sample_at_10pct_min_morris_zd,
    sample_at_10pct_min_morris_zir,
    sample_at_10pct_min_z45,
    sample_at_30pct_min_morris_zd,
    sample_at_30pct_min_morris_zir,
    sample_at_30pct_min_morris_z45,
    sample_at_50pct_min_morris_zd,
    sample_at_50pct_min_morris_zir,
    sample_at_50pct_min_z45,
):
    p_min = 0.3
    pi_T = sr_t_morris
    impact_ratio = impact_ratio_morris
    pi_min = pi_T * impact_ratio / (1 + p_min * (impact_ratio - 1))
    pi_maj = pi_T / (1 + p_min * (impact_ratio - 1))
    # assert abs(N_IR(N,sr_t_morris,pi_min,pi_maj,p_min,alpha=0.05) - sample_at_10pct_min_morris_zir) < diff_sample_size_cutoff
    assert (
        abs(
            sample_size(
                sr_t_morris,
                pi_min,
                pi_maj,
                p_min,
                alpha=0.05,
                power=0.8,
                one_tailed_test=0,
            )[1]
            - sample_at_30pct_min_morris_zir
        )
        < diff_sample_size_cutoff
    )


@pytest.mark.parametrize(
    "sr_t_morris,impact_ratio_morris,sample_at_10pct_min_morris_zd,sample_at_10pct_min_morris_zir,sample_at_10pct_min_z45,sample_at_30pct_min_morris_zd,sample_at_30pct_min_morris_zir,sample_at_30pct_min_morris_z45,sample_at_50pct_min_morris_zd,sample_at_50pct_min_morris_zir,sample_at_50pct_min_z45",
    testdata,
)
def test_3(
    sr_t_morris,
    impact_ratio_morris,
    sample_at_10pct_min_morris_zd,
    sample_at_10pct_min_morris_zir,
    sample_at_10pct_min_z45,
    sample_at_30pct_min_morris_zd,
    sample_at_30pct_min_morris_zir,
    sample_at_30pct_min_morris_z45,
    sample_at_50pct_min_morris_zd,
    sample_at_50pct_min_morris_zir,
    sample_at_50pct_min_z45,
):
    p_min = 0.5
    pi_T = sr_t_morris
    impact_ratio = impact_ratio_morris
    pi_min = pi_T * impact_ratio / (1 + p_min * (impact_ratio - 1))
    pi_maj = pi_T / (1 + p_min * (impact_ratio - 1))
    # assert abs(N_IR(N,sr_t_morris,pi_min,pi_maj,p_min,alpha=0.05) - sample_at_10pct_min_morris_zir) < diff_sample_size_cutoff
    assert (
        abs(
            sample_size(
                sr_t_morris,
                pi_min,
                pi_maj,
                p_min,
                alpha=0.05,
                power=0.8,
                one_tailed_test=0,
            )[1]
            - sample_at_50pct_min_morris_zir
        )
        < diff_sample_size_cutoff
    )


@pytest.mark.parametrize(
    "sr_t_morris,impact_ratio_morris,sample_at_10pct_min_morris_zd,sample_at_10pct_min_morris_zir,sample_at_10pct_min_z45,sample_at_30pct_min_morris_zd,sample_at_30pct_min_morris_zir,sample_at_30pct_min_morris_z45,sample_at_50pct_min_morris_zd,sample_at_50pct_min_morris_zir,sample_at_50pct_min_z45",
    testdata,
)
def test_1_zd(
    sr_t_morris,
    impact_ratio_morris,
    sample_at_10pct_min_morris_zd,
    sample_at_10pct_min_morris_zir,
    sample_at_10pct_min_z45,
    sample_at_30pct_min_morris_zd,
    sample_at_30pct_min_morris_zir,
    sample_at_30pct_min_morris_z45,
    sample_at_50pct_min_morris_zd,
    sample_at_50pct_min_morris_zir,
    sample_at_50pct_min_z45,
):

    p_min = 0.1
    pi_T = sr_t_morris
    impact_ratio = impact_ratio_morris
    pi_min = pi_T * impact_ratio / (1 + p_min * (impact_ratio - 1))
    pi_maj = pi_T / (1 + p_min * (impact_ratio - 1))
    # assert abs(N_IR(N,sr_t_morris,pi_min,pi_maj,p_min,alpha=0.05) - sample_at_10pct_min_morris_zir) < diff_sample_size_cutoff
    assert (
        abs(
            sample_size(
                sr_t_morris,
                pi_min,
                pi_maj,
                p_min,
                alpha=0.05,
                power=0.8,
                one_tailed_test=0,
            )[0]
            - sample_at_10pct_min_morris_zd
        )
        < diff_sample_size_cutoff
    )


@pytest.mark.parametrize(
    "sr_t_morris,impact_ratio_morris,sample_at_10pct_min_morris_zd,sample_at_10pct_min_morris_zir,sample_at_10pct_min_z45,sample_at_30pct_min_morris_zd,sample_at_30pct_min_morris_zir,sample_at_30pct_min_morris_z45,sample_at_50pct_min_morris_zd,sample_at_50pct_min_morris_zir,sample_at_50pct_min_z45",
    testdata,
)
def test_2_zd(
    sr_t_morris,
    impact_ratio_morris,
    sample_at_10pct_min_morris_zd,
    sample_at_10pct_min_morris_zir,
    sample_at_10pct_min_z45,
    sample_at_30pct_min_morris_zd,
    sample_at_30pct_min_morris_zir,
    sample_at_30pct_min_morris_z45,
    sample_at_50pct_min_morris_zd,
    sample_at_50pct_min_morris_zir,
    sample_at_50pct_min_z45,
):

    p_min = 0.3
    pi_T = sr_t_morris
    impact_ratio = impact_ratio_morris
    pi_min = pi_T * impact_ratio / (1 + p_min * (impact_ratio - 1))
    pi_maj = pi_T / (1 + p_min * (impact_ratio - 1))
    # assert abs(N_IR(N,sr_t_morris,pi_min,pi_maj,p_min,alpha=0.05) - sample_at_10pct_min_morris_zir) < diff_sample_size_cutoff
    assert (
        abs(
            sample_size(
                sr_t_morris,
                pi_min,
                pi_maj,
                p_min,
                alpha=0.05,
                power=0.8,
                one_tailed_test=0,
            )[0]
            - float(sample_at_30pct_min_morris_zd)
        )
        < diff_sample_size_cutoff
    )


@pytest.mark.parametrize(
    "sr_t_morris,impact_ratio_morris,sample_at_10pct_min_morris_zd,sample_at_10pct_min_morris_zir,sample_at_10pct_min_z45,sample_at_30pct_min_morris_zd,sample_at_30pct_min_morris_zir,sample_at_30pct_min_morris_z45,sample_at_50pct_min_morris_zd,sample_at_50pct_min_morris_zir,sample_at_50pct_min_z45",
    testdata,
)
def test_3_zd(
    sr_t_morris,
    impact_ratio_morris,
    sample_at_10pct_min_morris_zd,
    sample_at_10pct_min_morris_zir,
    sample_at_10pct_min_z45,
    sample_at_30pct_min_morris_zd,
    sample_at_30pct_min_morris_zir,
    sample_at_30pct_min_morris_z45,
    sample_at_50pct_min_morris_zd,
    sample_at_50pct_min_morris_zir,
    sample_at_50pct_min_z45,
):

    p_min = 0.5
    pi_T = sr_t_morris
    impact_ratio = impact_ratio_morris
    pi_min = pi_T * impact_ratio / (1 + p_min * (impact_ratio - 1))
    pi_maj = pi_T / (1 + p_min * (impact_ratio - 1))
    # assert abs(N_IR(N,sr_t_morris,pi_min,pi_maj,p_min,alpha=0.05) - sample_at_10pct_min_morris_zir) < diff_sample_size_cutoff
    assert (
        abs(
            sample_size(
                sr_t_morris,
                pi_min,
                pi_maj,
                p_min,
                alpha=0.05,
                power=0.8,
                one_tailed_test=0,
            )[0]
            - float(sample_at_50pct_min_morris_zd)
        )
        < diff_sample_size_cutoff
    )


@pytest.mark.parametrize(
    "sr_t_morris,impact_ratio_morris,sample_at_10pct_min_morris_zd,sample_at_10pct_min_morris_zir,sample_at_10pct_min_z45,sample_at_30pct_min_morris_zd,sample_at_30pct_min_morris_zir,sample_at_30pct_min_morris_z45,sample_at_50pct_min_morris_zd,sample_at_50pct_min_morris_zir,sample_at_50pct_min_z45",
    testdata,
)
def test_1_z45(
    sr_t_morris,
    impact_ratio_morris,
    sample_at_10pct_min_morris_zd,
    sample_at_10pct_min_morris_zir,
    sample_at_10pct_min_z45,
    sample_at_30pct_min_morris_zd,
    sample_at_30pct_min_morris_zir,
    sample_at_30pct_min_morris_z45,
    sample_at_50pct_min_morris_zd,
    sample_at_50pct_min_morris_zir,
    sample_at_50pct_min_z45,
):

    p_min = 0.1
    pi_T = sr_t_morris
    impact_ratio = impact_ratio_morris
    pi_min = pi_T * impact_ratio / (1 + p_min * (impact_ratio - 1))
    pi_maj = pi_T / (1 + p_min * (impact_ratio - 1))
    # assert abs(N_IR(N,sr_t_morris,pi_min,pi_maj,p_min,alpha=0.05) - sample_at_10pct_min_morris_zir) < 3
    assert (
        abs(
            sample_size(
                sr_t_morris,
                pi_min,
                pi_maj,
                p_min,
                alpha=0.05,
                power=0.8,
                one_tailed_test=0,
            )[2]
            - sample_at_10pct_min_z45
        )
        < diff_sample_size_cutoff
    )


@pytest.mark.parametrize(
    "sr_t_morris,impact_ratio_morris,sample_at_10pct_min_morris_zd,sample_at_10pct_min_morris_zir,sample_at_10pct_min_z45,sample_at_30pct_min_morris_zd,sample_at_30pct_min_morris_zir,sample_at_30pct_min_morris_z45,sample_at_50pct_min_morris_zd,sample_at_50pct_min_morris_zir,sample_at_50pct_min_z45",
    testdata,
)
def test_2_z45(
    sr_t_morris,
    impact_ratio_morris,
    sample_at_10pct_min_morris_zd,
    sample_at_10pct_min_morris_zir,
    sample_at_10pct_min_z45,
    sample_at_30pct_min_morris_zd,
    sample_at_30pct_min_morris_zir,
    sample_at_30pct_min_morris_z45,
    sample_at_50pct_min_morris_zd,
    sample_at_50pct_min_morris_zir,
    sample_at_50pct_min_z45,
):

    p_min = 0.3
    pi_T = sr_t_morris
    impact_ratio = impact_ratio_morris
    pi_min = pi_T * impact_ratio / (1 + p_min * (impact_ratio - 1))
    pi_maj = pi_T / (1 + p_min * (impact_ratio - 1))
    # assert abs(N_IR(N,sr_t_morris,pi_min,pi_maj,p_min,alpha=0.05) - sample_at_10pct_min_morris_zir) < 3
    assert (
        abs(
            sample_size(
                sr_t_morris,
                pi_min,
                pi_maj,
                p_min,
                alpha=0.05,
                power=0.8,
                one_tailed_test=0,
            )[2]
            - sample_at_30pct_min_morris_z45
        )
        < diff_sample_size_cutoff
    )


@pytest.mark.parametrize(
    "sr_t_morris,impact_ratio_morris,sample_at_10pct_min_morris_zd,sample_at_10pct_min_morris_zir,sample_at_10pct_min_z45,sample_at_30pct_min_morris_zd,sample_at_30pct_min_morris_zir,sample_at_30pct_min_morris_z45,sample_at_50pct_min_morris_zd,sample_at_50pct_min_morris_zir,sample_at_50pct_min_z45",
    testdata,
)
def test_3_z45(
    sr_t_morris,
    impact_ratio_morris,
    sample_at_10pct_min_morris_zd,
    sample_at_10pct_min_morris_zir,
    sample_at_10pct_min_z45,
    sample_at_30pct_min_morris_zd,
    sample_at_30pct_min_morris_zir,
    sample_at_30pct_min_morris_z45,
    sample_at_50pct_min_morris_zd,
    sample_at_50pct_min_morris_zir,
    sample_at_50pct_min_z45,
):

    p_min = 0.5
    pi_T = sr_t_morris
    impact_ratio = impact_ratio_morris
    pi_min = pi_T * impact_ratio / (1 + p_min * (impact_ratio - 1))
    pi_maj = pi_T / (1 + p_min * (impact_ratio - 1))
    # assert abs(N_IR(N,sr_t_morris,pi_min,pi_maj,p_min,alpha=0.05) - sample_at_10pct_min_morris_zir) < 3
    assert (
        abs(
            sample_size(
                sr_t_morris,
                pi_min,
                pi_maj,
                p_min,
                alpha=0.05,
                power=0.8,
                one_tailed_test=0,
            )[2]
            - sample_at_50pct_min_z45
        )
        < diff_sample_size_cutoff
    )
