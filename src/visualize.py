"""
visualize.py
------------
All plotting functions for the A/B test project.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from src.stats import FrequentistResult, BayesianResult

PALETTE = {"control": "#3266ad", "treatment": "#888780"}
FIG_SIZE = (10, 5)


def _style():
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "font.size": 12,
    })


def conversion_bar(result: FrequentistResult, save_path: str = None):
    """Bar chart comparing conversion rates with error bars."""
    _style()
    fig, ax = plt.subplots(figsize=(6, 5))

    groups = ["Control", "Treatment"]
    rates  = [result.p_ctrl, result.p_trt]
    ns     = [result.n_ctrl, result.n_trt]
    ses    = [np.sqrt(r * (1 - r) / n) for r, n in zip(rates, ns)]
    colors = [PALETTE["control"], PALETTE["treatment"]]

    bars = ax.bar(groups, [r * 100 for r in rates], color=colors,
                  yerr=[s * 100 * 1.96 for s in ses],
                  capsize=6, error_kw={"linewidth": 1.5, "color": "#444"}, width=0.5)

    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.15,
                f"{rate:.3%}", ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_ylabel("Conversion rate (%)")
    ax.set_title("Conversion rate: control vs treatment\n(error bars = 95% CI)", pad=12)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_ylim(0, max(rates) * 100 * 1.3)

    sig_text = "Statistically significant" if result.significant else "Not statistically significant"
    color    = "#2a9d2a" if result.significant else "#cc4444"
    ax.text(0.5, 0.02, f"p = {result.p_value:.3f} — {sig_text}",
            transform=ax.transAxes, ha="center", va="bottom",
            fontsize=10, color=color)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def daily_conversion(df: pd.DataFrame, save_path: str = None):
    """Daily conversion rate over time — checks for novelty effects."""
    _style()
    df = df.copy()
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date

    daily = (df.groupby(["date", "group"])["converted"]
               .agg(["sum", "count"])
               .reset_index())
    daily.columns = ["date", "group", "conversions", "visits"]
    daily["rate"] = daily["conversions"] / daily["visits"]

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    for group, color in PALETTE.items():
        d = daily[daily["group"] == group]
        ax.plot(d["date"], d["rate"] * 100, label=group.capitalize(),
                color=color, linewidth=2, marker="o", markersize=3)

    ax.set_xlabel("Date")
    ax.set_ylabel("Conversion rate (%)")
    ax.set_title("Daily conversion rate over time")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def confidence_interval_plot(result: FrequentistResult, save_path: str = None):
    """Visualize the 95% CI of the absolute difference."""
    _style()
    fig, ax = plt.subplots(figsize=(7, 3))

    diff   = result.abs_diff * 100
    ci_low = result.ci_low * 100
    ci_hi  = result.ci_high * 100

    ax.axvline(0, color="#888", linewidth=1, linestyle="--", label="No effect")
    ax.plot([ci_low, ci_hi], [0, 0], color="#3266ad", linewidth=3)
    ax.plot(diff, 0, "o", color="#3266ad", markersize=10, zorder=5, label=f"Observed diff: {diff:+.3f} pp")
    ax.fill_betweenx([-0.15, 0.15], ci_low, ci_hi, alpha=0.15, color="#3266ad")

    ax.set_yticks([])
    ax.set_xlabel("Absolute difference in conversion rate (percentage points)")
    ax.set_title("95% confidence interval: treatment − control")
    ax.legend(loc="upper right")
    ax.set_xlim(min(ci_low - 0.3, -0.5), max(ci_hi + 0.3, 0.5))

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def bayesian_posterior(result: BayesianResult, save_path: str = None):
    """Plot posterior distributions for both groups."""
    _style()
    fig, ax = plt.subplots(figsize=FIG_SIZE)

    from scipy.stats import gaussian_kde
    for samples, label, color in [
        (result.samples_ctrl, "Control", PALETTE["control"]),
        (result.samples_trt,  "Treatment", PALETTE["treatment"]),
    ]:
        kde = gaussian_kde(samples, bw_method=0.05)
        x   = np.linspace(samples.min(), samples.max(), 500)
        ax.plot(x * 100, kde(x), label=label, color=color, linewidth=2)
        ax.fill_between(x * 100, kde(x), alpha=0.15, color=color)

    ax.set_xlabel("Conversion rate (%)")
    ax.set_ylabel("Posterior density")
    ax.set_title(
        f"Bayesian posteriors — P(treatment > control) = {result.prob_trt_beats_ctrl:.1%}"
    )
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig
