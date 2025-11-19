🌍 GaiaNet — Biodiversity Intelligence Platform (Hackathon Edition)

AI-Powered Ecosystem Monitoring using Google Gemini 2.5 Pro

🧠 Overview

GaiaNet is an intelligent biodiversity monitoring and conservation decision-support system built for the SEED Hackathon 2025.
It uses Google Gemini 2.5 Pro, Streamlit, and smart ecological modeling to generate real-time insights about wildlife and ecosystems.

🔎 What GaiaNet Does

Detects wildlife species from images

Forecasts population decline or recovery

Models ecosystem stability and species interactions

Generates conservation actions prioritized by impact & urgency

Provides a clean, modern dashboard UI with dark mode

This project showcases how multimodal AI can transform conservation and ecological research when combined with structured workflows and intuitive visualization.

🏗️ Tech Stack
Component	Technology
Frontend / Dashboard	Streamlit (Dark Mode Custom UI)
AI Engine	Google Gemini 2.5 Pro
Fallback Model	CLIP zero-shot from HuggingFace
Data Handling	pandas, matplotlib
PDF Export	fpdf2
Audio Processing	librosa, soundfile
Map Visualization	pydeck
Satellite/Drone Analysis	numpy (mock NDVI)
🚀 Key Features (Current Version)
🦜 1. Species Detection

Upload an image

Gemini identifies:

common name

scientific name

habitat type

confidence score

observations

Automatic fallback to CLIP if API is missing

📈 2. Population Forecasting

Upload or auto-generate population history

Gemini uses ecological reasoning to produce:

next 6 months population forecast

confidence intervals

decline/recovery assessment

textual explanations

Clean visualization of forecasted trends

🕸️ 3. Ecosystem Interaction Modeling

Gemini models species interactions and food webs

Detects keystone species

Estimates ecosystem collapse risk

Runs “what-if” simulations (e.g., species declines)

🌱 4. Conservation Recommendations

Gemini gives prioritized actions:

habitat restoration

anti-poaching

invasive species control

corridor rebuilding

Includes urgency, impact, cost estimates, and rationale

🧪 5. Clean Dark-Themed Dashboard

Fully redesigned UI

Card layout

Modern typography

Compact charts

Clean tab structure

Consistent dark mode

⚙️ Installation & Run
1. Install Requirements
pip install -r requirements.txt

2. Set Gemini API Key

Either via environment variable:

export GEMINI_API_KEY="YOUR_KEY"


Or enter it in the Streamlit sidebar.

3. Run App
streamlit run app.py
🚧 WORK IN PROGRESS — Upcoming Features

GaiaNet is actively being expanded. The following features are in development and partially implemented in prototype form:


📊 1. Beautiful KPI Cards

Upcoming cards:

Ecosystem health score

Population risk score

Habitat quality metric

NDVI (vegetation index)

These will appear after each module finishes processing.

📄 2. PDF Report Export

A single-click Download Report button will generate:

detected species

graphs

ecological reasoning

intervention recommendations

metadata

images/spectrograms

Using fpdf2 for lightweight PDF creation.

🖼️ 3. Multi-Image Batch Detection

Feature enables:

Uploading 5–20 images at once

Running detection on each

Summaries displayed in a gallery-like layout

Optional GPS-based mapping via EXIF

🎧 4. Audio Species Detection

Supports:

Bird calls

Frog croaks

Mammal sounds

Insect pulses

Pipeline:

Convert audio → spectrogram

Send spectrogram to Gemini for species inference

(Optional) add YAMNet classifier as a pre-filter

🛰️ 5. Satellite Image Analysis

Two planned modes:

NDVI vegetation health inference (mock or real)

Habitat quality scoring

Deforestation / disturbance estimation

Drone and satellite integration will allow ecosystem-wide assessments.

🗺️ 6. Map Visualizations (pydeck)

Upcoming map dashboard layer:

Plot species sightings on a map

Cluster multiple locations

Visualize ecosystem risk by region

Use EXIF GPS when available

Fallback to synthetic coordinates during demo

🧭 7. Literature Extraction (Planned)

Using Gemini to extract:

species references

threats

policy recommendations

geospatial mentions

from uploaded PDFs or journal abstracts.
