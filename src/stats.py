"""
stats.py
--------
Statistical tests for A/B experiment results.

Tests included:
  - Two-proportion z-test (frequentist)
  - Chi-square test (cross-check)
  - Bayesian A/B test (Beta-Binomial conjugate)
"""

import numpy as np
import pandas as pd
from scipy import stats
from dataclasses import dataclass
from typing import Tuple


@dataclass
class FrequentistResult:
    p_ctrl: float
    p_trt: float
    n_ctrl: int
    n_trt: int
    abs_diff: float
    rel_lift: float
    z_stat: float
    p_value: float
    ci_low: float
    ci_high: float
    significant: bool
    alpha: float

    def __str__(self):
        sig = "YES" if self.significant else "NO"
        return (
            f"Control   : {self.p_ctrl:.4%}  (n={self.n_ctrl:,})\n"
            f"Treatment : {self.p_trt:.4%}  (n={self.n_trt:,})\n"
            f"Abs diff  : {self.abs_diff*100:+.4f} pp\n"
            f"Rel lift  : {self.rel_lift:+.2f}%\n"
            f"Z-stat    : {self.z_stat:.4f}\n"
            f"P-value   : {self.p_value:.4f}\n"
            f"95% CI    : [{self.ci_low*100:.4f} pp, {self.ci_high*100:.4f} pp]\n"
            f"Significant (α={self.alpha}): {sig}"
        )


@dataclass
class BayesianResult:
    prob_trt_beats_ctrl: float
    expected_loss_ctrl: float   # loss if we keep control when treatment is better
    expected_loss_trt: float    # loss if we ship treatment when control is better
    samples_ctrl: np.ndarray
    samples_trt: np.ndarray

    def __str__(self):
        return (
            f"P(treatment > control) : {self.prob_trt_beats_ctrl:.2%}\n"
            f"Expected loss (keep control) : {self.expected_loss_ctrl:.4%}\n"
            f"Expected loss (ship treatment): {self.expected_loss_trt:.4%}"
        )


def z_test(df: pd.DataFrame, alpha: float = 0.05) -> FrequentistResult:
    """Two-proportion z-test on a cleaned A/B dataframe."""
    ctrl = df[df["group"] == "control"]["converted"]
    trt  = df[df["group"] == "treatment"]["converted"]

    p_ctrl, p_trt = ctrl.mean(), trt.mean()
    n_ctrl, n_trt = len(ctrl), len(trt)

    p_pool = (ctrl.sum() + trt.sum()) / (n_ctrl + n_trt)
    se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / n_ctrl + 1 / n_trt))
    z = (p_trt - p_ctrl) / se_pool
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    se_diff = np.sqrt(p_ctrl * (1 - p_ctrl) / n_ctrl + p_trt * (1 - p_trt) / n_trt)
    ci_low  = (p_trt - p_ctrl) - 1.96 * se_diff
    ci_high = (p_trt - p_ctrl) + 1.96 * se_diff

    return FrequentistResult(
        p_ctrl=p_ctrl, p_trt=p_trt,
        n_ctrl=n_ctrl, n_trt=n_trt,
        abs_diff=p_trt - p_ctrl,
        rel_lift=(p_trt - p_ctrl) / p_ctrl * 100,
        z_stat=z, p_value=p_value,
        ci_low=ci_low, ci_high=ci_high,
        significant=p_value < alpha,
        alpha=alpha,
    )


def chi_square_test(df: pd.DataFrame) -> Tuple[float, float]:
    """Chi-square test of independence as a cross-check."""
    contingency = pd.crosstab(df["group"], df["converted"])
    chi2, p, dof, expected = stats.chi2_contingency(contingency)
    print(f"Chi-square: {chi2:.4f}  p={p:.4f}  dof={dof}")
    return chi2, p


def bayesian_test(df: pd.DataFrame,
                  n_samples: int = 50_000,
                  prior_alpha: float = 1.0,
                  prior_beta: float = 1.0) -> BayesianResult:
    """
    Bayesian A/B test using Beta-Binomial conjugate model.

    Prior: Beta(alpha, beta) — default is uniform Beta(1,1)
    Posterior: Beta(alpha + successes, beta + failures)
    """
    ctrl = df[df["group"] == "control"]["converted"]
    trt  = df[df["group"] == "treatment"]["converted"]

    # Posterior parameters
    a_ctrl = prior_alpha + ctrl.sum()
    b_ctrl = prior_beta  + (len(ctrl) - ctrl.sum())
    a_trt  = prior_alpha + trt.sum()
    b_trt  = prior_beta  + (len(trt)  - trt.sum())

    rng = np.random.default_rng(42)
    samples_ctrl = rng.beta(a_ctrl, b_ctrl, n_samples)
    samples_trt  = rng.beta(a_trt,  b_trt,  n_samples)

    prob_trt_wins = (samples_trt > samples_ctrl).mean()

    # Expected loss
    loss_keep_ctrl = np.maximum(samples_trt - samples_ctrl, 0).mean()
    loss_ship_trt  = np.maximum(samples_ctrl - samples_trt, 0).mean()

    return BayesianResult(
        prob_trt_beats_ctrl=prob_trt_wins,
        expected_loss_ctrl=loss_keep_ctrl,
        expected_loss_trt=loss_ship_trt,
        samples_ctrl=samples_ctrl,
        samples_trt=samples_trt,
    )
