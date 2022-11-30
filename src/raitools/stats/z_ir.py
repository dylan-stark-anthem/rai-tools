import math
import scipy.stats
from scipy.stats import norm
import pandas as pd
from csv import DictWriter
import os
import math
from typing import List
from raitools.stats.types import StatisticalTestResultType
from raitools.stats.chi_squared import create_contingency_table


def z_ir(
    SR_min: float, SR_maj: float, SR_T: float, N: int, P_min: float
) -> StatisticalTestResultType:
    """to get the p-value using ratio of two groups.only support the comparison of dichotomous outcome and group variables.
        Implement one-tailed Z-test of the ratio of outcome rates (Z_IR) with an alpha of 0.1 (Morris 2001)

    Args:
        SR_min (float): The selection rate for minority,user-specified “unprivileged” groups
        SR_maj (float): The selection rate for majority,user-specified “privileged” groups
        SR_T (float): The overall selection rate
        N (int): total observation size N
        P_min (float): the proportion of minority

    Returns:
        float: p-value
    """

    Z_IR = math.log(SR_min / SR_maj) / (
        ((1 - SR_T) / (SR_T * N * P_min * (1 - P_min))) ** 0.5
    )
    # finding p-value
    p_value = scipy.stats.norm.sf(abs(Z_IR))

    return Z_IR, p_value


def get_z_ir_parameters(baseline_data: List, test_data: List) -> List[List[int]]:
    "get the list of parameters from list to z_IR test"
    freq_result = create_contingency_table(
        baseline_data, test_data
    )  # call tabulate freq function
    freq_result = [item for sublist in freq_result for item in sublist]
    SR_min = freq_result[3] / (freq_result[2] + freq_result[3])
    SR_maj = freq_result[1] / (freq_result[0] + freq_result[1])
    N = sum(freq_result)
    SR_T = (freq_result[1] + freq_result[3]) / N
    P_min = (freq_result[2] + freq_result[3]) / N

    return SR_min, SR_maj, SR_T, N, P_min


def sample_size(
    pi_T: float,
    pi_min: float,
    pi_maj: float,
    p_min: float,
    alpha=0.05,
    power=0.8,
    one_tailed_test=1,
) -> (int, int, int, int):
    """calculate the minimum sample size. only support the dichotomous outcome and group variables

    Args:
        pi_T (float): The overall selection rate
        pi_min (float): The selection rate for minority
        pi_maj (float): The selection rate for majority
        p_min (float): the proportion of minority
        alpha (float, optional): alpha. Defaults to 0.05. It might change to 0.1.
        power (float, optional): power. Defaults to 0.8.
        one_tailed_test : Defaultsto be 1, otherwise(such as 0) it is a two tailed test

    Returns:
        int: the minimum sample size for N_D(based on the proportion difference),N_IR(based on the ratio of proportions),N_45(based on the ratio of proportions,4/5 rule,N_normality())
    """
    if one_tailed_test == 1:
        Z_crit = norm.ppf(1 - alpha)
    else:
        Z_crit = norm.ppf(1 - alpha / 2)

    Z_power = norm.ppf(power)
    phi = pi_min / pi_maj
    N_IR = (
        (
            Z_crit * ((1 - pi_T) / pi_T / p_min / (1 - p_min)) ** 0.5
            + Z_power
            * ((1 - pi_min) / pi_min / p_min + (1 - pi_maj) / pi_maj / (1 - p_min))
            ** 0.5
        )
        / math.log(phi)
    ) ** 2
    N_IR = int(math.ceil(N_IR))

    N_45 = math.ceil(
        (
            Z_power
            * (
                ((1 - pi_min) / pi_min / p_min + (1 - pi_maj) / pi_maj / (1 - p_min))
                ** 0.5
            )
            / (math.log(0.8 / phi))
        )
        ** 2
    )

    N_D = math.ceil(
        (
            (
                Z_crit * (pi_T * (1 - pi_T) / p_min / (1 - p_min)) ** 0.5
                + Z_power
                * (pi_min * (1 - pi_min) / p_min + pi_maj * (1 - pi_maj) / (1 - p_min))
                ** 0.5
            )
            / (pi_min - pi_maj)
        )
        ** 2
    )

    N_normality = 5 / (p_min * pi_T)

    return (N_D, N_IR, N_45, N_normality)
