import pandas as pd
import os

# --------------------------------------------------
# Load Dataset
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "water_stress_panel.csv")


class DataAgent:

    def __init__(self):
        """Load the dataset once."""
        self.df = pd.read_csv(DATA_PATH)

    # --------------------------------------------------

    def get_available_countries(self):
        """Return all countries."""

        return sorted(self.df["country"].unique().tolist())

    # --------------------------------------------------

    def get_available_years(self):
        """Return all years."""

        return sorted(self.df["year"].unique().tolist())

    # --------------------------------------------------

    def get_country_data(self, country, year):
        """
        Return one country's data for a specific year.
        """

        result = self.df[
            (self.df["country"].str.lower() == country.lower()) &
            (self.df["year"] == year)
        ]

        if result.empty:
            return None

        return result.iloc[0].to_dict()

    # --------------------------------------------------

    def get_country_history(self, country):
        """
        Return all years of one country.
        """

        history = self.df[
            self.df["country"].str.lower() == country.lower()
        ].sort_values("year")

        if history.empty:
            return None

        return history.to_dict(orient="records")

    # --------------------------------------------------

    def get_high_risk_countries(self):
        """
        Countries with High Water Stress.
        """

        high = self.df[
            self.df["stress_category"] == "high"
        ]

        return high[
            [
                "country",
                "year",
                "water_stress_pct",
                "stress_category",
                "scarcity_risk_flag"
            ]
        ].to_dict(orient="records")

    # --------------------------------------------------

    def get_country_summary(self, country, year):
        """
        Returns only the important fields
        that will be sent to the AI agents.
        """

        row = self.get_country_data(country, year)

        if row is None:
            return None

        return {
            "Country": row["country"],
            "Year": row["year"],
            "Water Stress (%)": row["water_stress_pct"],
            "Stress Category": row["stress_category"],
            "Freshwater Per Capita": row["freshwater_per_capita_m3"],
            "Water Access (%)": row["basic_water_access_pct"],
            "Safely Managed Water (%)": row["safely_managed_water_pct"],
            "Agriculture Withdrawal (%)": row["agri_withdrawal_pct"],
            "Population": row["population"],
            "GDP Per Capita": row["gdp_per_capita_usd"],
            "Scarcity Category": row["falkenmark_category"],
            "Scarcity Risk": row["scarcity_risk_flag"],
            "5 Year Stress Trend": row["stress_5yr_trend_pp"]
        }


# --------------------------------------------------
# Testing
# --------------------------------------------------

if __name__ == "__main__":

    agent = DataAgent()

    print("\nAvailable Countries")
    print(agent.get_available_countries()[:10])

    print("\nAvailable Years")
    print(agent.get_available_years())

    print("\nIndia (2024)")
    print(agent.get_country_summary("India", 2024))

    print("\nHistory of India")
    print(agent.get_country_history("India")[:3])

    print("\nHigh Risk Countries")
    print(agent.get_high_risk_countries()[:5])