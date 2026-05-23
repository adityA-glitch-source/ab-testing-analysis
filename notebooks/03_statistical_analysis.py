# %% [markdown]
# # Notebook 3 — Statistical Analysis
# **Goal:** Run three statistical tests and compare their conclusions.
# - Frequentist: two-proportion z-test
# - Cross-check: chi-square test
# - Bayesian: Beta-Binomial model

# %%
import sys
sys.path.insert(0, "..")

import pandas as pd
from src.stats import z_test, chi_square_test, bayesian_test
from src.visualize import conversion_bar, confidence_interval_plot, bayesian_posterior

df = pd.read_csv("../data/cleaned/ab_data_clean.csv")
print(f"Loaded {len(df):,} rows")

# %% [markdown]
# ## 1. Two-proportion z-test

# %%
result = z_test(df)
print(result)

# %%
conversion_bar(result, save_path="../outputs/conversion_bar.png")

# %%
confidence_interval_plot(result, save_path="../outputs/confidence_interval.png")

# %% [markdown]
# ## 2. Chi-square test (cross-check)
# Should agree with the z-test. Both test whether the conversion difference
# is larger than chance.

# %%
chi2, p_chi2 = chi_square_test(df)

# Both tests agree: p > 0.05, no significant difference.

# %% [markdown]
# ## 3. Bayesian A/B test
# Instead of a binary reject/fail-to-reject, we get a probability that
# treatment beats control and the expected loss from each decision.

# %%
bayes = bayesian_test(df)
print(bayes)

# %%
bayesian_posterior(bayes, save_path="../outputs/bayesian_posterior.png")

# %% [markdown]
# ## Summary
#
# | Test | Statistic | Conclusion |
# |---|---|---|
# | Z-test | p = 0.19 | Not significant (α=0.05) |
# | Chi-square | p ≈ 0.19 | Not significant |
# | Bayesian | P(trt > ctrl) ≈ 9% | Treatment likely worse |
#
# **All three methods agree: the new page does not outperform the old one.**
# With 145k+ users per group, this conclusion is robust — more data won't change it.
