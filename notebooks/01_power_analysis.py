# %% [markdown]
# # Notebook 1 — Power Analysis
# **Goal:** Determine the required sample size *before* looking at results.
# This is how professional A/B tests are designed.

# %%
import sys
sys.path.insert(0, "..")

import numpy as np
import matplotlib.pyplot as plt
from src.power_analysis import required_sample_size, print_summary

# %% [markdown]
# ## Define experiment parameters
# Based on the landing page experiment:
# - Baseline conversion rate: ~12% (from historical data)
# - Minimum detectable effect (MDE): we only care if the new page lifts conversions by ≥2%
# - Significance level α = 0.05, Power = 80%

# %%
BASELINE = 0.12
MDE      = 0.02   # 2 percentage points
ALPHA    = 0.05
POWER    = 0.80

print_summary(BASELINE, MDE, ALPHA, POWER)

# %% [markdown]
# ## How does required sample size change with MDE?
# Smaller effects require much larger samples.

# %%
mdes = np.arange(0.005, 0.051, 0.005)
ns   = [required_sample_size(BASELINE, m, ALPHA, POWER) for m in mdes]

plt.figure(figsize=(8, 4))
plt.plot(mdes * 100, ns, marker="o", color="#3266ad", linewidth=2)
plt.axvline(MDE * 100, color="#cc4444", linestyle="--", label=f"Our MDE ({MDE:.0%})")
plt.xlabel("Minimum detectable effect (pp)")
plt.ylabel("Required n per group")
plt.title("Sample size vs minimum detectable effect")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("../outputs/power_curve.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## Verdict
# With a baseline of 12% and wanting to detect a 2 pp lift:
# we need roughly **~3,800 users per group**.
# Our actual dataset has **145k+ per group** — massively overpowered for a 2pp MDE.
# This means if the new page had any meaningful effect, we would have caught it.
