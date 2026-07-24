# backend/app.py

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from load_data import get_country_year_stats, get_trend

app = Flask(__name__)
CORS(app)  # allows index.html (opened in a browser) to call this server

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


@app.route("/")
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    payload = request.get_json()
    country = payload.get("country")
    year = payload.get("year")

    if not country or not year:
        return jsonify({"error": "country and year are required"}), 400

    # --- Agent 1: Data Agent (not AI) ---
    data = get_country_year_stats(country, year)

    # --- Agent 2: Trend Agent (not AI) ---
    trend = get_trend(country, year)

    # --- Agents 3, 4, 5: Explanation / Recommendation / Report (AI) ---
    # For now we return placeholder text so you can test the whole flow
    # before wiring up n8n + watsonx. We'll replace this block next.
    explanation = f"(placeholder) {country} had a water stress index of {data.get('water_stress_index')} in {year}."
    recommendation = [
        "(placeholder) Improve irrigation efficiency.",
        "(placeholder) Invest in wastewater recycling."
    ]
    report = f"(placeholder) Overall, {country}'s water situation in {year} is {trend['direction']}."

    return jsonify({
        "data": data,
        "trend": trend,
        "explanation": explanation,
        "recommendation": recommendation,
        "report": report
    })


#if __name__ == "__main__":
    #app.run(debug=True, port=5000)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)