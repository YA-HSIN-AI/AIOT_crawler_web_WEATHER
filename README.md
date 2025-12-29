# AIOT_crawler_web_WEATHER
Lecture 13 demo: Python web crawler for CWA Open Data (weather API), using SQLite and Streamlit
# 🌤️ One-Week Agro Weather Forecast + Growing Degree Analysis (Streamlit Demo)

A lightweight Streamlit demo that **fetches Taiwan CWA (Central Weather Administration) open data**, stores the latest forecast JSON, and provides a simple **agricultural interpretation** (crop-friendly temperature range + weekly trend visualization).

✅ Designed for **Streamlit Community Cloud deployment**  
✅ Includes an in-app button to **Fetch Latest Data** (no need to run crawler manually)

---

## 🔗 Demo
- Streamlit App: **(https://aiotcrawlerwebweather-ghr3kf78nbiqnksni5voyk.streamlit.app/)**  
  

---

## 📌 Features
- **Fetch Latest Forecast** from CWA Open Data (in-app button)
- Save JSON locally to `weather_data/`
- Crop scenario selection (Rice/Corn/Cabbage/Tomato)
- Weekly temperature trend chart
- Raw JSON expander for technical verification

---

# CRISP-DM (Project Methodology)

## 1) Business Understanding
### Goal
Provide a simple web demo that helps users interpret **one-week weather forecasts** for agriculture-related decisions.

### Target Users
- Students / demo viewers
- People interested in agriculture-weather interpretation
- Anyone who wants a quick forecast summary

### Success Criteria
- App can run on Streamlit Cloud
- Users can fetch the latest forecast inside the app
- App shows summary + chart + raw JSON evidence

---

## 2) Data Understanding
### Data Source
- **CWA Open Data API** (One-week forecast dataset)

### Data Type
- JSON response (raw forecast information)

### Key Challenge (Cloud)
- Streamlit Cloud may encounter SSL verification issues with some endpoints.
- This project includes a workaround in `crawler.py` to ensure the demo remains functional for coursework/demo purposes.

---

## 3) Data Preparation
### Storage
- Forecast JSON files are saved to:
  - `weather_data/weather_YYYYMMDD_HHMMSS.json`

### Loader Logic
- App loads the latest JSON file (sorted by filename timestamp).
- If no JSON exists, user can click **Fetch Latest Data** to create one.

---

## 4) Modeling (Simple Rule-Based Interpretation)
This project uses a simplified rule-based model (not ML training):

- Define crop temperature comfort ranges (example):
  - Rice: 20–30°C
  - Corn: 18–30°C
  - Cabbage: 15–25°C
  - Tomato: 18–28°C

- Compare weekly average temperature vs range:
  - Below range → “Too Cold”
  - Above range → “Too Hot”
  - Within range → “Suitable”

---

## 5) Evaluation
### What we evaluate
- Can the app fetch and store forecast data successfully?
- Does the UI produce a readable interpretation and visualization?
- Does it run consistently on Streamlit Cloud?

### Limitations
- Demo uses simplified temperature samples / rule-based explanation.
- Not intended for real agricultural decision-making.
- Data accuracy depends on CWA source availability.

---

## 6) Deployment
### Deployed on Streamlit Community Cloud
- App entry: `app.py`
- Data fetch module: `crawler.py`

### Secrets (Required on Streamlit Cloud)
Set the API key in:
**Manage app → Settings → Secrets**

```toml
CWA_API_KEY = "YOUR_CWA_API_KEY"
