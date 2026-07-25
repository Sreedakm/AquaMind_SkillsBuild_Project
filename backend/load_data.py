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


def _latest_value_upto_year(df: pd.DataFrame, country: str, year: int, column: str):
    """
    Walks backward from `year` and returns the first (value, year) pair
    where `column` actually has a non-null value for this country.
    This is stricter than just taking the latest row, since the latest
    row can exist but still have a NaN in the specific column we want.
    """
    subset = df[(df["country"] == country) & (df["year"] <= year) & df[column].notna()]
    if subset.empty:
        return None, None
    best_year = subset["year"].max()
    row = subset[subset["year"] == best_year].iloc[0]
    value = row[column]
    if hasattr(value, "item"):
        value = value.item()
    return value, int(best_year)


def get_country_year_stats(country: str, year: int) -> dict:
    """
    Looks up one country + one year across all 4 sheets
    and returns a single clean dictionary of stats.

    For each stat, falls back independently to the most recent year
    <= the requested year that actually has a non-null value for
    that specific column.
    """
    water_stress_panel, water_stress_panel_year = _latest_value_upto_year(
        stress_df, country, year, "water_stress_pct"
    )
    freshwater_withdrawal, freshwater_withdrawal_year = _latest_value_upto_year(
        freshwater_df, country, year, "withdrawal_bcm"
    )
    renewable_resources, renewable_resources_year = _latest_value_upto_year(
        resources_df, country, year, "total_renewable_bcm"
    )
    access_to_safe_water, access_to_safe_water_year = _latest_value_upto_year(
        access_df, country, year, "basic_water_access_pct"
    )

    return {
        "water_stress_panel": water_stress_panel,
        "water_stress_panel_year": water_stress_panel_year,
        "freshwater_withdrawal": freshwater_withdrawal,
        "freshwater_withdrawal_year": freshwater_withdrawal_year,
        "renewable_resources": renewable_resources,
        "renewable_resources_year": renewable_resources_year,
        "access_to_safe_water": access_to_safe_water,
        "access_to_safe_water_year": access_to_safe_water_year,
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
        {"year": int(r["year"]), "value": float(r["water_stress_pct"])}
        for _, r in history_df.iterrows()
        if pd.notna(r["water_stress_pct"])
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