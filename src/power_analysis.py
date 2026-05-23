"""
power_analysis.py
-----------------
Pre-experiment: calculate required sample size.
Post-experiment: calculate achieved statistical power.
"""

import numpy as np
from scipy import stats


def required_sample_size(
    baseline_rate: float,
    mde: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    """
    Calculate the minimum per-group sample size for a two-proportion z-test.

    Parameters
    ----------
    baseline_rate : float
        Expected conversion rate in the control group (e.g. 0.12)
    mde : float
        Minimum detectable effect — absolute change (e.g. 0.02 for +2 pp)
    alpha : float
        Significance level (default 0.05)
    power : float
        Desired statistical power (default 0.80)

    Returns
    -------
    int
        Required sample size per group
    """
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta  = stats.norm.ppf(power)

    p1 = baseline_rate
    p2 = baseline_rate + mde
    p_bar = (p1 + p2) / 2

    n = (z_alpha * np.sqrt(2 * p_bar * (1 - p_bar)) +
         z_beta  * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p2 - p1) ** 2

    return int(np.ceil(n))


def achieved_power(
    p_ctrl: float,
    p_trt: float,
    n_ctrl: int,
    n_trt: int,
    alpha: float = 0.05,
) -> float:
    """
    Estimate the statistical power of the experiment that was actually run.

    Returns
    -------
    float
        Power between 0 and 1
    """
    effect = abs(p_trt - p_ctrl)
    p_bar  = (p_ctrl * n_ctrl + p_trt * n_trt) / (n_ctrl + n_trt)
    se     = np.sqrt(p_bar * (1 - p_bar) * (1 / n_ctrl + 1 / n_trt))
    z_crit = stats.norm.ppf(1 - alpha / 2)
    ncp    = effect / se
    power  = 1 - stats.norm.cdf(z_crit - ncp) + stats.norm.cdf(-z_crit - ncp)
    return power


def print_summary(baseline_rate: float, mde: float,
                  alpha: float = 0.05, power: float = 0.80) -> None:
    n = required_sample_size(baseline_rate, mde, alpha, power)
    print(f"Baseline rate : {baseline_rate:.2%}")
    print(f"MDE           : {mde:+.2%}  ({baseline_rate + mde:.2%} target)")
    print(f"Alpha         : {alpha}")
    print(f"Power         : {power:.0%}")
    print(f"Required n    : {n:,} per group  ({2*n:,} total)")
