# %% [markdown]
# # Notebook 2 — EDA & Data Cleaning
# **Goal:** Understand the raw data, surface quality issues, and produce a clean dataset.

# %%
import sys
sys.path.insert(0, "..")

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.data_loader import load_raw, clean

# %%
df_raw = load_raw("../data/raw/ab_data.csv")
print(f"Shape: {df_raw.shape}")
df_raw.head()

# %% [markdown]
# ## Basic profile

# %%
print(df_raw.dtypes)
print()
print(df_raw["group"].value_counts())
print()
print(df_raw["landing_page"].value_counts())
print()
print(f"Conversion rate (raw): {df_raw['converted'].mean():.4%}")

# %% [markdown]
# ## Data quality issues

# %%
# Check group/page consistency
mismatch = df_raw[
    ((df_raw["group"] == "treatment") & (df_raw["landing_page"] == "old_page")) |
    ((df_raw["group"] == "control")   & (df_raw["landing_page"] == "new_page"))
]
print(f"Mismatched rows: {len(mismatch):,}")

# Check duplicate users
dupes = df_raw[df_raw["user_id"].duplicated(keep=False)]
print(f"Rows from duplicate user_ids: {len(dupes):,}")
print(f"Unique duplicate user_ids:    {df_raw['user_id'].duplicated().sum():,}")

# %% [markdown]
# ## Clean the data

# %%
df = clean(df_raw)

# %% [markdown]
# ## Distribution of conversions

# %%
fig, axes = plt.subplots(1, 2, figsize=(10, 4))

conv = df.groupby("group")["converted"].agg(["sum", "count", "mean"])
conv.columns = ["conversions", "total", "rate"]

axes[0].bar(conv.index, conv["rate"] * 100,
            color=["#3266ad", "#888780"], width=0.5)
axes[0].set_ylabel("Conversion rate (%)")
axes[0].set_title("Conversion rate by group")
for i, (idx, row) in enumerate(conv.iterrows()):
    axes[0].text(i, row["rate"] * 100 + 0.1, f"{row['rate']:.3%}", ha="center")

axes[1].bar(conv.index, conv["total"],
            color=["#3266ad", "#888780"], width=0.5)
axes[1].set_ylabel("Number of users")
axes[1].set_title("Sample size by group")

plt.tight_layout()
plt.savefig("../outputs/eda_overview.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## Time range

# %%
df["timestamp"] = pd.to_datetime(df["timestamp"])
print(f"Experiment ran: {df['timestamp'].min().date()} → {df['timestamp'].max().date()}")
print(f"Duration: {(df['timestamp'].max() - df['timestamp'].min()).days} days")

# Save clean data
df.to_csv("../data/cleaned/ab_data_clean.csv", index=False)
print("\nClean data saved.")
