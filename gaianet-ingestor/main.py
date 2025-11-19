import requests
import os
import time
from datetime import datetime, timedelta

# --- 1. CONFIGURATION ---
# IMPORTANT: These should be secured via Secret Manager and environment variables in Cloud Run.
# We retrieve them using os.environ.get() as a best practice for serverless environments.
GBIF_USER = os.environ.get("GBIF_USERNAME") 
GBIF_PASSWORD = os.environ.get("GBIF_PASSWORD") 
GBIF_EMAIL = os.environ.get("GBIF_EMAIL")

# --- 2. GBIF PREDICATE DEFINITION ---
def define_gbif_query_predicate(days_back=7):
    """Defines the complex JSON query body (predicate) for the GBIF API."""
    
    # Calculate the date 7 days ago in the required ISO 8601 format (e.g., 2025-11-11T00:00:00Z)
    start_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat() + 'Z'
    
    # Define filters to ensure high-quality data for the GaiaNet prediction models
    predicate_body = {
        "creator": GBIF_USER,
        "notificationAddresses": [GBIF_EMAIL],
        "format": "DWCA", # Request the data in Darwin Core Archive format
        "predicate": {
            "type": "and",
            "predicates": [
                # Filter 1: Only data added/modified in the last 'days_back' days
                {"type": "within", "key": "eventDate", "value": f"{start_date},"}, 
                
                # Filter 2: Must have geographic coordinates (REQUIRED for your BigQuery schema)
                {"type": "isNotNull", "key": "decimalLatitude"},
                {"type": "isNotNull", "key": "decimalLongitude"},
                
                # Filter 3: Must be a verifiable human or machine observation (basisOfRecord)
                {"type": "in", "key": "basisOfRecord", "values": ["HUMAN_OBSERVATION", "MACHINE_OBSERVATION", "PRESERVED_SPECIMEN"]}
            ]
        }
    }
    return predicate_body

# --- 3. MAIN CLOUD RUN ENTRY POINT ---
def ingest_gbif_data(request):
    """Handles the Cloud Run request, initiates GBIF download, and returns status."""
    
    download_url = "https://api.gbif.org/v1/occurrence/download/request"
    
    # 3.1. Build the query body
    download_request_body = define_gbif_query_predicate(days_back=7)

    # 3.2. Send the download request to GBIF
    try:
        response = requests.post(
            download_url,
            json=download_request_body,
            auth=(GBIF_USER, GBIF_PASSWORD) # Authenticate using the credentials
        )
    except Exception as e:
        # Handle connection errors
        return f"Error connecting to GBIF API: {e}", 500

    # 3.3. Check the response status
    if response.status_code == 202:
        # Status 202 means the request was accepted, and the download is being generated
        download_key = response.text.strip()
        
        # Log the key. This key is crucial for checking the download status later.
        print(f"GBIF Download initiated successfully. Key: {download_key}")
        
        # NOTE: The next function in the pipeline will use this key to monitor the status.
        return f"GBIF Download Request submitted. Key: {download_key}", 200
    
    else:
        # Log and return errors from GBIF
        print(f"GBIF Download Request failed. Status: {response.status_code}. Response: {response.text}")
        return f"GBIF Request failed. Check logs for details.", 500

# --- 4. REQUIRED DEPENDENCIES ---

# The Cloud Run environment will need a 'requirements.txt' file defining these dependencies:
# requests
# google-cloud-bigquery
# pandas