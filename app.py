from google.cloud import bigquery

# BigQuery will automatically use GOOGLE_APPLICATION_CREDENTIALS
bq_client = bigquery.Client()
 

import os
import io
import json
from datetime import datetime
from typing import List, Dict

import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt

# ================= CUSTOM CSS FOR UI ENHANCEMENT ====================
# ===================== DARK MODE (GLOBAL) ======================
st.markdown("""
<style>
/* Main layout background */
body, .main, .block-container { 
    background-color: #1b1b1b !important; 
    color: #e0e0e0 !important;
}

/* Card styling */
.card {
    background-color: #262626 !important;
    padding: 22px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.45);
    margin-bottom: 20px;
}

/* Section headers */
.section-header {
    font-size: 28px; 
    font-weight: 700;
    padding-bottom: 6px;
    border-bottom: 2px solid #444;
    margin-bottom: 15px;
    color: #f3f3f3;
}

/* Buttons */
.stButton>button {
    background-color: #3a6df0 !important;
    color: #ffffff !important;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    border: none;
}

.stButton>button:hover {
    background-color: #2c56cc !important;
}

/* File uploader */
.css-1n76uvr, .stFileUploader {
    background-color: #2a2a2a !important;
    border-radius: 10px;
    padding: 10px;
}

/* Text inputs */
.stTextInput>div>div>input {
    background-color: #2a2a2a !important;
    color: #f0f0f0 !important;
}

/* DataFrames */
.dataframe, .stDataFrame {
    color: #ffffff !important;
}

/* JSON box */
.stJson {
    background-color: #262626 !important;
    padding: 15px;
    border-radius: 10px;
}

/* Tabs */
.stTabs [role="tab"] {
    background-color: #2a2a2a !important;
    color: #cccccc !important;
    padding: 8px 14px;
    border-radius: 6px;
}

.stTabs [role="tab"][aria-selected="true"] {
    background-color: #3a3a3a !important;
    color: #ffffff !important;
}

/* Chart background */
.stPlotlyChart, .stAltairChart, .stPyplotChart {
    background-color: #1b1b1b !important;
}

/* Titles */
h1, h2, h3, h4, h5, h6 {
    color: #f5f5f5 !important;
}

</style>
""", unsafe_allow_html=True)

# CLIP fallback
from transformers import pipeline

# Gemini SDK import
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except:
    HAS_GEMINI = False


# =========================================================
# STREAMLIT CONFIG
# =========================================================
st.set_page_config(page_title="GaiaNet — Gemini Hybrid Mode", layout="wide")

st.title("🌍 GaiaNet — Biodiversity AI Platform (Gemini Hybrid Mode)")
st.write("Upload an image → get species detection → forecast population → ecosystem modeling → recommendations.")




# =========================================================
# SIDEBAR — API KEY
# =========================================================
st.sidebar.header("Configuration")

api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    os.environ["GEMINI_API_KEY"] = api_key

if HAS_GEMINI and "GEMINI_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    GEMINI_MODEL = "gemini-2.5-pro"
    st.sidebar.success("Gemini Ready ✔")
else:
    st.sidebar.warning("Gemini key missing → CLIP fallback only.")


# =========================================================
# UTILITY HELPERS
# =========================================================
def image_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def safe_json_parse(text):
    try:
        return json.loads(text)
    except:
        try:
            s = text.find("{")
            e = text.rfind("}")
            if s != -1 and e != -1:
                return json.loads(text[s:e+1])
        except:
            return None
    return None


# =========================================================
# CLIP FALLBACK MODEL
# =========================================================
@st.cache_resource
def load_clip():
    try:
        return pipeline("zero-shot-image-classification", model="openai/clip-vit-base-patch32")
    except:
        return None

clip_pipe = load_clip()


# =========================================================
# GEMINI FUNCTIONS — SAFE (no f-string braces)
# =========================================================

# ---------- Species Detection ----------
def gemini_species_analysis(image_bytes):
    if not HAS_GEMINI or "GEMINI_API_KEY" not in os.environ:
        return {"error": "Gemini unavailable"}

    prompt = """
You are a wildlife biologist. Analyze the image and return ONLY JSON in this structure:

{
  "species_detected": [
    {"common_name": "...", "scientific_name": "...", "confidence": "high|medium|low"}
  ],
  "count": 0,
  "habitat_type": "...",
  "observations": "...",
  "recommendation_summary": "..."
}
"""

    model = genai.GenerativeModel(
        GEMINI_MODEL,
        generation_config={
            "temperature": 0.1,
            "top_p": 0.9
        }
    )

    result = model.generate_content(
        [
            prompt,
            {"mime_type": "image/jpeg", "data": image_bytes}
        ]
    )

    return {"raw": result.text, "parsed": safe_json_parse(result.text)}


# ---------- Population Forecast ----------
def gemini_population_forecast(species_name, history_list):
    if not HAS_GEMINI or "GEMINI_API_KEY" not in os.environ:
        return {"error": "Gemini unavailable"}

    csv_data = "date,count\n" + "\n".join(
        f"{r['date']},{r['count']}" for r in history_list
    )

    prompt = """
You are an ecologist. Given species NAME_HERE and historical monthly counts:

CSV_DATA_HERE

Return ONLY JSON:

{
  "forecast": [
    {"month": "...", "population": 0, "confidence": "high|medium|low"}
  ],
  "risk_level": "Low|Medium|High|Critical",
  "reasoning": "..."
}
"""
    prompt = prompt.replace("NAME_HERE", species_name)
    prompt = prompt.replace("CSV_DATA_HERE", csv_data)

    model = genai.GenerativeModel(
        GEMINI_MODEL,
        generation_config={
            "temperature": 0.1,
            "top_p": 0.9
        }
    )

    result = model.generate_content(prompt)
    return {"raw": result.text, "parsed": safe_json_parse(result.text)}


# ---------- Ecosystem Modeling ----------
def gemini_ecosystem_model(species_list, context=""):
    if not HAS_GEMINI or "GEMINI_API_KEY" not in os.environ:
        return {"error": "Gemini unavailable"}

    species_csv = ", ".join(species_list)
    first_species = species_list[0] if species_list else "unknown species"

    prompt = """
You are an ecosystem modeler.
Species: SPECIES_LIST
Context: CONTEXT_INFO

Return ONLY JSON:

{
  "keystone_species": ["..."],
  "interaction_graph": {
    "species": ["interaction1", "interaction2"]
  },
  "health_score": 0,
  "collapse_risk": "Low|Medium|High|Critical",
  "simulate": {
    "decline_30pct": {
      "focal_species": "FSP",
      "affected_species": {
        "speciesA": 0,
        "speciesB": 0
      }
    }
  }
}
"""

    prompt = prompt.replace("SPECIES_LIST", species_csv)
    prompt = prompt.replace("CONTEXT_INFO", context)
    prompt = prompt.replace("FSP", first_species)

    model = genai.GenerativeModel(
        GEMINI_MODEL,
        generation_config={
            "temperature": 0.1,
            "top_p": 0.9
        }
    )

    result = model.generate_content(prompt)
    return {"raw": result.text, "parsed": safe_json_parse(result.text)}


# ---------- Recommendations ----------
def gemini_recommendations(species, status, eco_summary):
    if not HAS_GEMINI or "GEMINI_API_KEY" not in os.environ:
        return {"error": "Gemini unavailable"}

    eco_json = json.dumps(eco_summary)

    prompt = """
You are a conservation planner.

Given:
Species: SPECIES_NAME
Status: SPECIES_STATUS
Ecosystem Summary: ECO_SUMMARY

Return ONLY JSON:

{
  "recommended_actions": [
    {"action": "...", "impact": 0.0, "urgency": "...", "cost_estimate": "..."}
  ],
  "rationale": "..."
}
"""

    prompt = prompt.replace("SPECIES_NAME", species)
    prompt = prompt.replace("SPECIES_STATUS", status)
    prompt = prompt.replace("ECO_SUMMARY", eco_json)

    model = genai.GenerativeModel(
        GEMINI_MODEL,
        generation_config={
            "temperature": 0.1,
            "top_p": 0.9
        }
    )

    result = model.generate_content(prompt)
    return {"raw": result.text, "parsed": safe_json_parse(result.text)}


# =========================================================
# TABS
# =========================================================
tabs = st.tabs(["Home", "Species Detection", "Forecast", "Ecosystem", "Recommendations", "Raw JSON"])


# =========================================================
# 0) HOME PAGE TAB
# =========================================================
with tabs[0]:
    st.markdown("<div class='section-header'>🌍 Welcome to GaiaNet</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='card'>
    <h3>What is GaiaNet?</h3>
    <p style='font-size:17px;'>
    GaiaNet is an AI-powered biodiversity monitoring platform built using Google Gemini 2.5 Pro.
    It helps conservationists, researchers, and policymakers understand ecosystem conditions
    through intelligent analysis of wildlife images and ecological data.
    </p>

    <h3>✨ Key Features</h3>
    <ul style='font-size:17px;'>
        <li><b>Species Detection:</b> Upload a wildlife image to detect species and habitat type.</li>
        <li><b>Population Forecasting:</b> Predict future population health using Gemini reasoning.</li>
        <li><b>Ecosystem Modeling:</b> Build interaction networks and assess collapse risk.</li>
        <li><b>Conservation Recommendations:</b> Get ranked interventions for maximum impact.</li>
        <li><b>AI Reasoning:</b> All insights are explained with ecological logic and structured JSON.</li>
    </ul>

    <h3>📌 How to Use</h3>
    <ol style='font-size:17px;'>
        <li>Go to <b>Species Detection</b> and upload a wildlife image.</li>
        <li>Review detected species and auto-generated ecosystem info.</li>
        <li>Check <b>Forecast</b> for trends and <b>Ecosystem</b> for stability assessment.</li>
        <li>See <b>Recommendations</b> for actionable ideas.</li>
    </ol>

    <p style='font-size:17px;'>GaiaNet is built for the <b>SEED Hackathon</b> to showcase the future of AI-driven conservation.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🔎 WDPA Test Query (BigQuery Connection Check)")

    query = """
    SELECT *
    FROM `gen-lang-client-0789978240.gaia_net_dwc_data.wdpa_temp_1`
    LIMIT 5
    """

    df = bq_client.query(query).to_dataframe()
    st.dataframe(df)




# =========================================================
# 1) SPECIES DETECTION TAB
# =========================================================
with tabs[1]:
    st.markdown("<div class='section-header'>🦜 Species Detection</div>", unsafe_allow_html=True)

    colA, colB = st.columns([1, 2])

    with colA:
        uploaded = st.file_uploader("📤 Upload wildlife image", type=["jpg", "png"])
        history_csv = st.file_uploader("📊 Optional: Population History CSV", type=["csv"])
        auto_run = st.checkbox("⚡ Auto-run advanced analysis", value=True)

    with colB:
        if uploaded:
            img = Image.open(uploaded).convert("RGB")
            st.image(img, width=450, caption="Uploaded Image")

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("🔍 Running Species Detection…")

            img_bytes = image_to_bytes(img)

            if HAS_GEMINI and "GEMINI_API_KEY" in os.environ:
                with st.spinner("Analyzing image with Gemini..."):
                    analysis = gemini_species_analysis(img_bytes)
            else:
                st.info("Using CLIP fallback (Gemini not available).")
                labels = ["bear", "lion", "tiger", "wolf", "elephant", "deer"]
                preds = clip_pipe(img, labels)
                top = preds[0]["label"]

                analysis = {
                    "parsed": {
                        "species_detected": [{"common_name": top, "scientific_name": "", "confidence": "medium"}],
                        "count": 1,
                        "habitat_type": "unknown",
                        "observations": "CLIP fallback",
                        "recommendation_summary": "Observe habitat quality."
                    },
                    "raw": preds
                }

            st.session_state["analysis"] = analysis

            parsed = analysis["parsed"]
            if parsed:
                st.success(f"**Species Detected:** {parsed['species_detected'][0]['common_name']}")
                st.write(f"**Scientific Name:** {parsed['species_detected'][0]['scientific_name']}")
                st.write(f"**Confidence:** {parsed['species_detected'][0]['confidence']}")
                st.write(f"**Habitat:** {parsed['habitat_type']}")
                st.write(f"**Notes:** {parsed['observations']}")
            else:
                st.warning("Could not parse model output.")
            st.markdown("</div>", unsafe_allow_html=True)

            # History Handling
            if history_csv:
                df = pd.read_csv(history_csv, parse_dates=["date"])
            else:
                today = datetime.utcnow().date()
                hist = []
                base = 120
                for i in range(6):
                    d = today.replace(day=1) - pd.DateOffset(months=i)
                    hist.append({"date": d.strftime("%Y-%m-%d"), "count": base - i * 12})
                df = pd.DataFrame(hist[::-1])

            st.session_state["history"] = df

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            if auto_run:
                species = parsed["species_detected"][0]["common_name"]
                history_list = [
                    {"date": r["date"].strftime("%Y-%m-%d"), "count": int(r["count"])}
                    for _, r in df.iterrows()
                ]

                with st.spinner("📈 Forecasting population..."):
                    st.session_state["forecast"] = gemini_population_forecast(species, history_list)

                with st.spinner("🕸 Modeling ecosystem..."):
                    species_list = [s["common_name"] for s in parsed["species_detected"]]
                    st.session_state["ecosystem"] = gemini_ecosystem_model(species_list)

                with st.spinner("🛠 Generating conservation recommendations..."):
                    status = parsed["recommendation_summary"]
                    st.session_state["recs"] = gemini_recommendations(
                        species, status, st.session_state["ecosystem"]["parsed"]
                    )
                st.success("All advanced analyses completed.")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Upload an image to begin analysis.")



# =========================================================
# 2) FORECAST TAB
# =========================================================
with tabs[2]:
    st.markdown("<div class='section-header'>📈 Population Forecast</div>", unsafe_allow_html=True)

    if "forecast" in st.session_state:
        parsed = st.session_state["forecast"]["parsed"]

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🔮 Forecast Summary")
        st.json(parsed)
        st.markdown("</div>", unsafe_allow_html=True)

        if parsed and "forecast" in parsed:
            df = pd.DataFrame(parsed["forecast"])

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("📉 Population Trend Visualization")

            fig, ax = plt.subplots(figsize=(6, 3))  # Smaller width and height
            ax.plot(pd.to_datetime(df["month"]), df["population"],marker="o", linewidth=2,markersize=6)
            ax.set_title("Population Forecast",fontsize=14)
            ax.set_ylabel("Population",fontsize=12)
            ax.grid(alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Run detection to generate forecast data.")



# =========================================================
# 3) ECOSYSTEM TAB
# =========================================================
with tabs[3]:
    st.markdown("<div class='section-header'>🕸 Ecosystem Modeling</div>", unsafe_allow_html=True)

    if "ecosystem" in st.session_state:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🌿 Ecosystem Stability Model")
        st.json(st.session_state["ecosystem"]["parsed"])
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No ecosystem model available yet.")



# =========================================================
# 4) RECOMMENDATIONS TAB
# =========================================================
with tabs[4]:
    st.markdown("<div class='section-header'>🛠 Conservation Recommendations</div>", unsafe_allow_html=True)

    if "recs" in st.session_state:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🌱 Recommended Actions")
        st.json(st.session_state["recs"]["parsed"])
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No recommendations generated yet.")




# =========================================================
# 5) RAW JSON TAB
# =========================================================
with tabs[5]:
    st.header("Debug: Raw Model Output")
    st.subheader("Species Detection Raw Output:")
    st.json(st.session_state.get("analysis"))

    st.subheader("Forecast Raw Output:")
    st.json(st.session_state.get("forecast"))

    st.subheader("Ecosystem Raw Output:")
    st.json(st.session_state.get("ecosystem"))

    st.subheader("Recommendations Raw Output:")
    st.json(st.session_state.get("recs"))
