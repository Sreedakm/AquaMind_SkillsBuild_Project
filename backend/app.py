# backend/app.py

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests

from load_data import get_country_year_stats, get_trend

app = Flask(__name__)
CORS(app)  # allows index.html (opened in a browser) to call this server

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

# NOTE: switch this to your PRODUCTION webhook URL once the n8n workflow
# is built and the workflow is toggled "Active".
# Test URL only works while you have clicked "Listen for Test Event" in n8n.
N8N_WEBHOOK_URL = "https://goury2004.app.n8n.cloud/webhook/water-analyze"


@app.route("/")
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    country = payload.get("country")
    year = payload.get("year")

    if not country or not year:
        return jsonify({"error": "country and year are required"}), 400

    # --- Agent 1: Data Agent (not AI) ---
    data = get_country_year_stats(country, year)

    # --- Agent 2: Trend Agent (not AI) ---
    trend = get_trend(country, year)

    # --- Agents 3, 4, 5: Explanation / Recommendation / Risk (AI, via n8n) ---
    n8n_payload = {
        "country": country,
        "year": year,
        "data": data,
        "trend": trend
    }

    try:
        response = requests.post(N8N_WEBHOOK_URL, json=n8n_payload, timeout=90)
        response.raise_for_status()
        ai_output = response.json()
    except requests.exceptions.Timeout:
        return jsonify({"error": "n8n webhook timed out"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Could not reach n8n webhook. Is the workflow active / are you listening for a test event?"}), 502
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"n8n webhook returned an error: {str(e)}"}), 502
    except ValueError:
        # response.json() failed to parse — n8n probably returned non-JSON
        return jsonify({"error": "n8n webhook did not return valid JSON"}), 502

    return jsonify({
        "country": country,
        "year": year,
        "data": data,
        "trend": trend,
        "explanation": ai_output.get("explanation"),
        "recommendation": ai_output.get("recommendation"),
        "risk": ai_output.get("risk")
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)