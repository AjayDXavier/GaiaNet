# 🌍 GaiaNet — Biodiversity Intelligence Platform (Hackathon Edition)

**AI-Powered Ecosystem Monitoring using Google Gemini 2.5 Pro**

---

## 🧠 Overview

GaiaNet is an intelligent biodiversity monitoring and conservation decision-support system built for the **SEED Hackathon 2025**.  
It uses **Google Gemini 2.5 Pro**, **Streamlit**, and smart ecological modeling to generate real-time insights about wildlife and ecosystems.

### 🔎 What GaiaNet Does
- Detects wildlife species from images  
- Forecasts population decline or recovery  
- Models ecosystem stability and species interactions  
- Generates conservation actions prioritized by impact & urgency  
- Provides a clean, modern dashboard UI with dark mode  

This project showcases how **multimodal AI** can transform conservation and ecological research when combined with structured workflows and intuitive visualization.

---

## 🏗️ Tech Stack

| Component | Technology |
|----------|------------|
| **Frontend / Dashboard** | Streamlit (Dark Mode Custom UI) |
| **AI Engine** | Google Gemini 2.5 Pro |
| **Fallback Model** | CLIP zero-shot (HuggingFace Transformers) |
| **Data Handling** | pandas, matplotlib |
| **PDF Export** | fpdf2 |
| **Audio Processing** | librosa, soundfile |
| **Map Visualization** | pydeck |
| **Satellite/Drone Analysis** | numpy (mock NDVI) |

---

## 🚀 Key Features (Current Version)

### 🦜 1. Species Detection
- Upload an image  
- Gemini identifies:
  - common name  
  - scientific name  
  - habitat type  
  - confidence score  
  - observations  
- Automatic fallback to CLIP if API is missing

---

### 📈 2. Population Forecasting
- Upload or auto-generate population history  
- Gemini uses ecological reasoning to produce:
  - next 6 months population forecast  
  - confidence intervals  
  - decline/recovery assessment  
  - textual explanations  
- Clean visualization of forecasted trends  

---

### 🕸️ 3. Ecosystem Interaction Modeling
- Gemini models species interactions and food webs  
- Detects keystone species  
- Estimates ecosystem collapse risk  
- Runs “what-if” simulations  

---

### 🌱 4. Conservation Recommendations
- Gemini suggests prioritized actions:
  - habitat restoration  
  - anti-poaching  
  - invasive species control  
  - corridor rebuilding  
- Provides impact scores, urgency levels, and rationale  

---

### 🧪 5. Clean Dark-Themed Dashboard
- Fully redesigned UI  
- Card layout  
- Modern typography  
- Compact charts  
- Clean tab structure  
- Consistent dark mode  

---

## ⚙️ Installation & Run

### **1. Install Requirements**


```bash
pip install -r requirements.txt
```
### **2. Set Gemini API Key


You can provide the key in one of two ways:

### **Via environment variable**
```
```bash
export GEMINI_API_KEY="YOUR_KEY"
```
### Or enter it directly in the Streamlit sidebar
The sidebar includes a secure **password field** where you can manually enter your Gemini API key.

---

## 3. Run the App
```
streamlit run app.py
```
# 🚧 WORK IN PROGRESS — Upcoming Features

GaiaNet is actively being expanded.  
The following features are **in development** and partially implemented in prototype form:

---

## 📊 1. Beautiful KPI Cards
Upcoming visually appealing KPI-style metrics:

- **Ecosystem health score**  
- **Population risk score**  
- **Habitat quality metric**  
- **NDVI (vegetation index)**  

These will appear after species detection, forecasting, or ecosystem modeling.

---

## 📄 2. PDF Report Export
A one-click **Download Report** button will generate a full conservation report containing:

- Detected species  
- Forecast graphs  
- Ecological reasoning  
- Intervention recommendations  
- Metadata  
- Images / spectrograms  

Built using **fpdf2** for lightweight PDF creation.

---

## 🖼️ 3. Multi-Image Batch Detection
Allows users to:

- Upload **5–20 images at once**  
- Run species detection on each image  
- Display results in a **gallery-style layout**  
- Optionally extract & display **GPS coordinates (EXIF)** on a map  

---

## 🎧 4. Audio Species Detection
Support for analyzing wildlife audio such as:

- Bird calls  
- Frog croaks  
- Mammal sounds  
- Insect signals  

### Pipeline:
1. Convert audio → **spectrogram**  
2. Send spectrogram → **Gemini** for species inference  
3. *(Optional)* Use **YAMNet** for pre-filtering the sound category  

---

## 🛰️ 5. Satellite Image Analysis
Two upcoming satellite/drone modules:

- **NDVI vegetation health estimation** (mock or real NDVI)  
- **Habitat quality scoring**  
- **Deforestation / disturbance analysis**  

Will support drone imagery and geospatial raster data.

---

## 🗺️ 6. Map Visualizations (pydeck)
A map dashboard layer is in development to:

- Plot species sightings on a map  
- Cluster multiple detections  
- Visualize ecosystem risk by region  
- Use **GPS EXIF data** when available  
- Fallback to synthetic coordinates for demo images  

---

## 🧭 7. Literature Extraction (Planned)
Using Gemini to extract structured ecological insights from research papers:

- Species references  
- Threats  
- Policy recommendations  
- Geographic mentions  

This will help tie scientific literature to real-time species detection and forecasting.

---
