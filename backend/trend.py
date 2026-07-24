from load_data import DataAgent


class TrendAgent:

    def __init__(self):
        self.data = DataAgent()

    def calculate_trend(self, country):
        """
        Returns whether water stress is increasing,
        decreasing or stable.
        """

        history = self.data.get_country_history(country)

        if history is None:
            return None

        first = history[0]["water_stress_pct"]
        last = history[-1]["water_stress_pct"]

        if last > first:
            return "Increasing"

        elif last < first:
            return "Decreasing"

        else:
            return "Stable"

    def average_stress(self, country):

        history = self.data.get_country_history(country)

        if history is None:
            return None

        values = [row["water_stress_pct"] for row in history]

        return round(sum(values) / len(values), 2)

    def highest_stress_year(self, country):

        history = self.data.get_country_history(country)

        if history is None:
            return None

        highest = max(history, key=lambda x: x["water_stress_pct"])

        return {
            "year": highest["year"],
            "water_stress": highest["water_stress_pct"]
        }

    def lowest_stress_year(self, country):

        history = self.data.get_country_history(country)

        if history is None:
            return None

        lowest = min(history, key=lambda x: x["water_stress_pct"])

        return {
            "year": lowest["year"],
            "water_stress": lowest["water_stress_pct"]
        }

    def trend_summary(self, country):

        history = self.data.get_country_history(country)

        if history is None:
            return None

        latest = history[-1]

        return {

            "Country": country,

            "Trend": self.calculate_trend(country),

            "Average Water Stress":
                self.average_stress(country),

            "Highest Stress Year":
                self.highest_stress_year(country),

            "Lowest Stress Year":
                self.lowest_stress_year(country),

            "Current Stress":
                latest["stress_category"],

            "5 Year Trend":
                latest["stress_5yr_trend_pp"]

        }


if __name__ == "__main__":

    trend = TrendAgent()

    print(trend.trend_summary("India"))