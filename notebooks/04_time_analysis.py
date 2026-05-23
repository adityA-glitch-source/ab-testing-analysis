# %% [markdown]
# # Notebook 4 — Time Analysis
# **Goal:** Check for novelty effects — did the new page look better early on
# and fade? Or was it consistently flat throughout?

# %%
import sys
sys.path.insert(0, "..")

import pandas as pd
import matplotlib.pyplot as plt
from src.visualize import daily_conversion

df = pd.read_csv("../data/cleaned/ab_data_clean.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["date"] = df["timestamp"].dt.date

# %% [markdown]
# ## Daily conversion rate over time

# %%
daily_conversion(df, save_path="../outputs/daily_conversion.png")

# %% [markdown]
# ## Cumulative conversion rate
# Watch how the rate stabilises as sample size grows.

# %%
df_sorted = df.sort_values("timestamp")

fig, ax = plt.subplots(figsize=(10, 4))
for group, color in [("control", "#3266ad"), ("treatment", "#888780")]:
    g = df_sorted[df_sorted["group"] == group].copy()
    g["cumulative_rate"] = g["converted"].expanding().mean() * 100
    g = g.reset_index(drop=True)
    ax.plot(g.index, g["cumulative_rate"], label=group.capitalize(),
            color=color, linewidth=1.5, alpha=0.8)

ax.set_xlabel("Users (ordered by time)")
ax.set_ylabel("Cumulative conversion rate (%)")
ax.set_title("Cumulative conversion rate — stabilises quickly")
ax.legend()
ax.grid(alpha=0.3)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("../outputs/cumulative_conversion.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## Day-of-week effect
# Are certain days more likely to convert?

# %%
df["weekday"] = df["timestamp"].dt.day_name()
order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

weekly = (df.groupby(["weekday", "group"])["converted"]
            .mean()
            .unstack()
            .reindex(order))

weekly.plot(kind="bar", figsize=(10, 4), color=["#3266ad","#888780"])
plt.ylabel("Conversion rate")
plt.title("Conversion rate by day of week")
plt.xticks(rotation=30)
plt.legend(title="Group")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("../outputs/weekday_conversion.png", dpi=150, bbox_inches="tight")
plt.show()
