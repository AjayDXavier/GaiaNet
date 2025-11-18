import os
import io
import json
from datetime import datetime
from typing import List, Dict

import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt

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
    GEMINI_MODEL = "gemini-1.5-pro"
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
tabs = st.tabs(["Species Detection", "Forecast", "Ecosystem", "Recommendations", "Raw JSON"])



# =========================================================
# 1) SPECIES DETECTION TAB
# =========================================================
with tabs[0]:
    st.header("1. Species Detection")

    uploaded = st.file_uploader("Upload Image", type=["jpg", "png"])
    history_csv = st.file_uploader("Optional Population History CSV", type=["csv"])
    auto_run = st.checkbox("Auto-run all steps", value=True)

    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        st.image(img, width=400)

        img_bytes = image_to_bytes(img)

        st.subheader("Running Species Detection…")

        if HAS_GEMINI and "GEMINI_API_KEY" in os.environ:
            with st.spinner("Gemini analyzing image..."):
                analysis = gemini_species_analysis(img_bytes)
        else:
            st.info("Using CLIP fallback.")
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

        if analysis["parsed"]:
            st.success(analysis["parsed"])
        else:
            st.warning("Could not parse JSON")


        # Load or generate history
        if history_csv:
            df = pd.read_csv(history_csv, parse_dates=["date"])
        else:
            # Synthetic history
            today = datetime.utcnow().date()
            hist = []
            base = 120
            for i in range(6):
                d = today.replace(day=1) - pd.DateOffset(months=i)
                hist.append({"date": d.strftime("%Y-%m-%d"), "count": base - i * 12})
            df = pd.DataFrame(hist[::-1])

        st.session_state["history"] = df


        # Auto-run deeper modules
        if auto_run:
            species = analysis["parsed"]["species_detected"][0]["common_name"]
            history_list = [
                {"date": r["date"].strftime("%Y-%m-%d"), "count": int(r["count"])}
                for _, r in df.iterrows()
            ]

            with st.spinner("Running population forecast…"):
                st.session_state["forecast"] = gemini_population_forecast(species, history_list)

            with st.spinner("Running ecosystem model…"):
                species_list = [s["common_name"] for s in analysis["parsed"]["species_detected"]]
                st.session_state["ecosystem"] = gemini_ecosystem_model(species_list)

            with st.spinner("Generating conservation recommendations…"):
                status = analysis["parsed"]["recommendation_summary"]
                st.session_state["recs"] = gemini_recommendations(
                    species, status, st.session_state["ecosystem"]["parsed"]
                )



# =========================================================
# 2) FORECAST TAB
# =========================================================
with tabs[1]:
    st.header("2. Population Forecast")
    if "forecast" in st.session_state:
        parsed = st.session_state["forecast"]["parsed"]
        st.json(parsed)

        if parsed and "forecast" in parsed:
            dff = pd.DataFrame(parsed["forecast"])
            fig, ax = plt.subplots()
            ax.plot(pd.to_datetime(dff["month"]), dff["population"], marker="o")
            ax.set_title("Predicted Population Trend")
            st.pyplot(fig)
    else:
        st.info("Run detection first.")



# =========================================================
# 3) ECOSYSTEM TAB
# =========================================================
with tabs[2]:
    st.header("3. Ecosystem Modeling")
    if "ecosystem" in st.session_state:
        st.json(st.session_state["ecosystem"]["parsed"])
    else:
        st.info("No ecosystem model yet.")



# =========================================================
# 4) RECOMMENDATIONS TAB
# =========================================================
with tabs[3]:
    st.header("4. Conservation Recommendations")
    if "recs" in st.session_state:
        st.json(st.session_state["recs"]["parsed"])
    else:
        st.info("No recommendations available.")



# =========================================================
# 5) RAW JSON TAB
# =========================================================
with tabs[4]:
    st.header("Debug: Raw Model Output")
    st.subheader("Species Detection Raw Output:")
    st.json(st.session_state.get("analysis"))

    st.subheader("Forecast Raw Output:")
    st.json(st.session_state.get("forecast"))

    st.subheader("Ecosystem Raw Output:")
    st.json(st.session_state.get("ecosystem"))

    st.subheader("Recommendations Raw Output:")
    st.json(st.session_state.get("recs"))
