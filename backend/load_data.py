# backend/load_data.py

import pandas as pd
import os

# Folder where your CSVs live
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Load each CSV once when the app starts (faster than reading every request)
freshwater_df = pd.read_csv(os.path.join(DATA_DIR, "freshwater_withdrawal.csv"))
resources_df  = pd.read_csv(os.path.join(DATA_DIR, "water_resources.csv"))
access_df     = pd.read_csv(os.path.join(DATA_DIR, "water_access.csv"))
stress_df     = pd.read_csv(os.path.join(DATA_DIR, "water_stress_panel.csv"))


def get_country_year_stats(country: str, year: int) -> dict:
    """
    Looks up one country + one year across all 4 sheets
    and returns a single clean dictionary of stats.
    """

    # NOTE: column names below are PLACEHOLDERS.
    # Once you paste your real CSV, I'll fix these to match exactly.

    stress_row = stress_df[
        (stress_df["country"] == country) & (stress_df["year"] == year)
    ]

    withdrawal_row = freshwater_df[
        (freshwater_df["country"] == country) & (freshwater_df["year"] == year)
    ]

    resources_row = resources_df[
        (resources_df["country"] == country) & (resources_df["year"] == year)
    ]

    access_row = access_df[
        (access_df["country"] == country) & (access_df["year"] == year)
    ]

    def safe_get(row, column):
        if row.empty or column not in row.columns:
            return None
        return row.iloc[0][column]

    return {
        "water_stress_index": safe_get(stress_row, "water_stress_index"),
        "freshwater_withdrawal": safe_get(withdrawal_row, "freshwater_withdrawal_bcm"),
        "renewable_resources": safe_get(resources_row, "renewable_resources_bcm"),
        "access_to_safe_water": safe_get(access_row, "access_percent"),
    }


def get_trend(country: str, upto_year: int) -> dict:
    """
    Looks at the country's history up to (and including) the chosen year,
    and works out whether stress is going up, down, or flat.
    """
    history_df = stress_df[
        (stress_df["country"] == country) & (stress_df["year"] <= upto_year)
    ].sort_values("year")

    if history_df.empty:
        return {"direction": "stable", "summary": "Not enough history for this country.", "history": []}

    history = [
        {"year": int(r["year"]), "value": float(r["water_stress_index"])}
        for _, r in history_df.iterrows()
    ]

    if len(history) < 2:
        direction = "stable"
    else:
        change = history[-1]["value"] - history[0]["value"]
        if change > 2:
            direction = "increasing"
        elif change < -2:
            direction = "decreasing"
        else:
            direction = "stable"

    summary = f"Water stress in {country} has been {direction} from {history[0]['year']} to {history[-1]['year']}."

    return {"direction": direction, "summary": summary, "history": history}