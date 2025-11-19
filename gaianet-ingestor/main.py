import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

# ----------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# ----------------------------

GBIF_USER = os.environ.get("GBIF_USERNAME")
GBIF_PASSWORD = os.environ.get("GBIF_PASSWORD")
GBIF_EMAIL = os.environ.get("GBIF_EMAIL")

# Validate credentials exist
if not GBIF_USER or not GBIF_PASSWORD or not GBIF_EMAIL:
    print("⚠️ WARNING: GBIF credentials not set. Add them in Cloud Run → Edit & Deploy New Revision → Environment Variables.")

# ----------------------------
# 2. DEFINE GBIF QUERY
# ----------------------------

def define_gbif_query_predicate(days_back=7):
    """Build GBIF predicate for Darwin Core Archive download."""

    start_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat() + 'Z'

    predicate_body = {
        "creator": GBIF_USER,
        "notificationAddresses": [GBIF_EMAIL],
        "format": "DWCA",
        "predicate": {
            "type": "and",
            "predicates": [
                {"type": "within", "key": "eventDate", "value": f"{start_date},"},
                {"type": "isNotNull", "key": "decimalLatitude"},
                {"type": "isNotNull", "key": "decimalLongitude"},
                {
                    "type": "in",
                    "key": "basisOfRecord",
                    "values": ["HUMAN_OBSERVATION", "MACHINE_OBSERVATION", "PRESERVED_SPECIMEN"]
                }
            ]
        }
    }

    return predicate_body


# ----------------------------
# 3. MAIN INGEST FUNCTION
# ----------------------------

def ingest_gbif_data(req):
    """Start a GBIF DWCA download job."""
    print("📥 Received ingestion request.")

    download_url = "https://api.gbif.org/v1/occurrence/download/request"
    body = define_gbif_query_predicate(days_back=7)

    try:
        response = requests.post(
            download_url,
            json=body,
            auth=(GBIF_USER, GBIF_PASSWORD)
        )
    except Exception as e:
        print(f"❌ Error contacting GBIF: {e}")
        return jsonify({"error": str(e)}), 500

    if response.status_code == 202:
        download_key = response.text.strip()
        print(f"✅ GBIF download started. Key: {download_key}")
        return jsonify({"status": "submitted", "download_key": download_key}), 200

    else:
        print(f"❌ GBIF error: {response.status_code} — {response.text}")
        return jsonify({
            "status": "failed",
            "code": response.status_code,
            "details": response.text
        }), 500


# ----------------------------
# 4. FLASK SERVER FOR CLOUD RUN
# ----------------------------

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def root():
    """
    Cloud Run entrypoint:
    - GET → health check
    - POST → trigger GBIF ingestion
    """
    if request.method == "GET":
        return jsonify({
            "service": "gaianet-ingestor",
            "status": "running",
            "message": "Send POST to trigger GBIF ingestion."
        }), 200

    # POST = run the ingestion job
    return ingest_gbif_data(request)


# Cloud Run requires listening on $PORT
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port)
