import requests
import csv
import os

TOKEN = os.getenv("IUCN_API_TOKEN")
BUCKET = "gaia-net-raw-biodiversity-data-v1"
OUTPUT_FILE = "iucn_species_raw.csv"

BASE_URL = f"https://apiv3.iucnredlist.org/api/v3/species?token={TOKEN}"

def main():
    print("Fetching species list from IUCN Red List API...")

    r = requests.get(BASE_URL)
    r.raise_for_status()
    data = r.json()

    species_list = data.get("result", [])

    print(f"Fetched {len(species_list)} species")

    # Write CSV
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["scientific_name", "category"])
        
        for sp in species_list:
            writer.writerow([sp.get("scientific_name"), sp.get("category")])

    print("Local CSV created:", OUTPUT_FILE)

    # Upload to GCS
    os.system(f"gsutil cp {OUTPUT_FILE} gs://{BUCKET}/{OUTPUT_FILE}")

    print("Upload complete → gs://{BUCKET}/{OUTPUT_FILE}")

if __name__ == "__main__":
    main()
