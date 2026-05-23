"""
data_loader.py
--------------
Load and clean the raw A/B test dataset.
"""

import pandas as pd


def load_raw(path: str = "data/raw/ab_data.csv") -> pd.DataFrame:
    """Load the raw CSV."""
    df = pd.read_csv(path, parse_dates=["timestamp"])
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove data quality issues:
    - Mismatched group/page assignments
    - Duplicate user IDs (keep first occurrence by timestamp)

    Returns a clean DataFrame and prints a summary.
    """
    n_raw = len(df)

    # Remove mismatches
    mismatch = (
        ((df["group"] == "treatment") & (df["landing_page"] == "old_page")) |
        ((df["group"] == "control")   & (df["landing_page"] == "new_page"))
    )
    df = df[~mismatch].copy()
    n_after_mismatch = len(df)

    # Remove duplicate user IDs
    df = df.sort_values("timestamp").drop_duplicates(subset="user_id", keep="first")
    n_final = len(df)

    print(f"Raw rows        : {n_raw:,}")
    print(f"After mismatch  : {n_after_mismatch:,}  (removed {n_raw - n_after_mismatch:,})")
    print(f"After dedup     : {n_final:,}  (removed {n_after_mismatch - n_final:,})")
    print(f"Group balance   :\n{df['group'].value_counts().to_string()}")

    return df


def load_clean(raw_path: str = "data/raw/ab_data.csv",
               save_path: str = "data/cleaned/ab_data_clean.csv") -> pd.DataFrame:
    """Load, clean, and optionally save the cleaned dataset."""
    df = clean(load_raw(raw_path))
    if save_path:
        df.to_csv(save_path, index=False)
        print(f"\nSaved to {save_path}")
    return df
