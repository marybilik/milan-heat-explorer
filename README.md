# 🕵️ The Milan Heat Case: An Earth System Trend Detective Game

[![NASA Space Apps 2026](https://img.shields.io/badge/NASA%20Space%20Apps-2026-blue.svg)](https://spaceappschallenge.org)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 💡 Motivation: Why a Game?

Climate data is complex, intimidating, and often hidden in static, boring maps. The people who need this data the most — policymakers, urban planners, and citizens — rarely have the time to read statistical regressions or interpret p-values.

**We built a detective game because data tells, but stories sell.** By turning the user into a "Climate Detective," we force them to actively uncover the invisible inequalities of Milan. Instead of just showing a red heat map, we challenge the user to measure the 7°C gap between the Duomo and Parco Sempione, discover the "Loneliness Trap," and expose the "Industrial Ovens." Gamification lowers the barrier to entry, making complex spatial statistics accessible and memorable.

---

## 🚨 The Problem: The Anatomy of Climate Inequality

Our analysis of Milan reveals a silent crisis:

1. **The Physics Illusion:** Concrete and lack of trees explain **57.5%** of extreme heat. However, social vulnerability (SVI) doesn't directly cause heat; it dictates *who* is forced to live in it.
2. **The Loneliness Trap:** After strict FDR correction, traditional scapegoats (like foreign nationals) were dropped. The strongest social predictor of lethal heat exposure is **loneliness** (one-person households, +0.083°C per SD).
3. **The Industrial Oven:** **59.2%** of extreme heat anomalies occur in industrial zones — a 4.3x concentration above the city baseline.
4. **The Invisible Majority:** **687 census tracts** have *high vulnerability* but *low heat*, meaning they are ignored by current climate policies.
5. **The Tree Ceiling:** Planting trees in dense poor areas yields almost no cooling (+0.04°C) due to space limits. **Cool Roofs (-0.36°C) are the only viable intervention.**

---

## 🎮 The Solution: The Game

Built with Streamlit, this interactive experience guides the user through 5 phases:

- **Phase 1: The Crime Scene:** Click on maps to discover the 6.87°C temperature gap in 300 meters.
- **Phase 2: The Time Bomb:** Analyze seasonal data to find when heat becomes lethal (Summer gap is 2x Spring).
- **Phase 3: The Invisible Enemy:** Toggle industrial zones to see the hidden heat sources (59.2% of anomalies).
- **Phase 4: The Hotspots:** Interact with GWR (Geographically Weighted Regression) coefficients locally.
- **Phase 5: The Invisible Majority:** Find the "Orange Zones" (High Vulnerability + Low Heat) missed by policies.

---

## 🔬 Methodology & Tech Stack

The application is the tip of the iceberg. The full scientific methodology is documented in [`scientific_analysis.ipynb`](scientific_analysis.ipynb).

- **Data Fusion:** Landsat 8 & 9 (LST), MODIS (24-year LST & NDVI trends), Sentinel-5P (NO2), ISTAT & Zenodo (Social Vulnerability Index), OpenStreetMap (Industrial zones).
- **Analytics:** Spatial Lag Models, Quantile Regression, Bivariate LISA, GWR (Geographically Weighted Regression), Random Forest counterfactual simulations.
- **App Stack:** Python, Streamlit, GeoPandas, Plotly, SciPy, Statsmodels, PySAL.

---

## 📊 Data Sources & References (NASA Open Data Rules)

In compliance with the NASA Space Apps Challenge rules, all datasets, libraries, and resources are cited below.

### 1. NASA & Earth Observation Data

- **Landsat 8 & 9 Collection 2 Level-2 (Surface Temperature):** Used for 30m-resolution Land Surface Temperature (LST) in Milan.
  - *Source:* USGS/NASA, accessed via Google Earth Engine (`LANDSAT/LC08/C02/T1_L2`, `LANDSAT/LC09/C02/T1_L2`).[reference:0]
  - *Link:* [Landsat 9 Level 2](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2)
- **MODIS (MOD11A2 LST & MOD13A2 NDVI):** Used for 24-year historical trends (2000–2023).
  - *Source:* NASA LP DAAC, accessed via Google Earth Engine (`MODIS/061/MOD11A2`, `MODIS/061/MOD13A2`).
- **Sentinel-5P OFFL NO2:** Used for nitrogen dioxide pollution mapping (Double Burden analysis).
  - *Source:* ESA/Copernicus, accessed via Google Earth Engine (`COPERNICUS/S5P/OFFL/L3_NO2`).[reference:1]

### 2. Social & Spatial Data

- **Social Vulnerability Index (SVI) for Milan:** Used for census tract-level vulnerability scores.
  - *Source:* Zenodo (Characterisation of Social Vulnerability to the environmental hazard of heat in Milan).
  - *Link:* [Zenodo Record 13894260](https://doi.org/10.5281/zenodo.13894260)
- **OpenStreetMap (OSM):** Used for industrial land-use polygons.
  - *Source:* OpenStreetMap contributors, retrieved via `osmnx`.

### 3. Python Libraries & Tools

- **Streamlit** (MIT License)
- **GeoPandas** (BSD-3-Clause)
- **PySAL / Libpysal / Esda / mgwr** (BSD-3-Clause) — Used for Spatial Lag, LISA, and GWR.
- **Statsmodels** (BSD-3-Clause) — Used for OLS, Quantile Regression, and FDR correction.
- **Scikit-Learn** (BSD-3-Clause) — Used for Random Forest simulations.
- **Plotly** (MIT License)

---

## 📂 Repository Structure

- `app.py` — The Streamlit interactive game.
- `scientific_analysis.ipynb` — The full scientific notebook with all spatial analysis (GWR, LISA, Regression, etc.).
- `app_data.geojson` — The spatial dataset driving the map.
- `gwr_coefs.csv` — Pre-calculated GWR coefficients.
- `time_series.csv` — 24-year LST trends (MODIS).
- `ndvi_time_series.csv` — 24-year NDVI trends (MODIS).
- `requirements.txt` — Python dependencies.
- `packages.txt` — System dependencies for Streamlit Cloud (GDAL, PROJ, GEOS).

---

## 🚀 How to Run Locally

Clone the repository:
   ```bash
   git clone https://github.com/marybilik/milan-heat-explorer.git
   ```
Install dependencies:

```bash
pip install -r requirements.txt
```
Run the app:

```bash
streamlit run app.py
```


📄 License

This project is licensed under the MIT License. You are free to use, modify, and distribute this code for non-commercial and commercial purposes, provided the original authors are credited.
