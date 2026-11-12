# 🕵️ The Milan Heat Case: An Earth System Trend Detective Game

[![NASA Space Apps 2026](https://img.shields.io/badge/NASA%20Space%20Apps-2026-blue.svg)](https://spaceappschallenge.org)
[![Streamlit App]([https://static.streamlit.io/badges/streamlit_badge_black_white.svg](https://milan-heat-explorer.streamlit.app/))](https://share.streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

### 🎥 Project Demo
*[Добавь сюда ссылку на YouTube видео, когда запишешь: 👉 Watch the gameplay demo here](ССЫЛКА_НА_ВИДЕО)*
*(Note: The interactive game is playable via Streamlit. The full scientific methodology, including spatial regressions and Random Forest simulations, is detailed in the `scientific_analysis.ipynb` notebook).*



## 💡 Motivation: Why a Game?

Climate data is complex, intimidating, and often hidden in static, academic papers. The people who need this data the most — policymakers, urban planners, and citizens — rarely have the time to read statistical regressions. 

**We built a detective game because data tells, but stories sell.** By turning the user into a "Climate Detective," we force them to actively uncover the invisible inequalities of Milan. Instead of just showing a red heat map, we challenge the user to measure the 7°C gap between the Duomo and Parco Sempione, discover the "Loneliness Trap," and expose the hidden "Industrial Ovens." Gamification lowers the barrier to entry, making complex spatial statistics accessible, memorable, and actionable.


## 🚨 The Problem: The Anatomy of Climate Inequality

Our analysis of Milan reveals a silent crisis:

1. **The Physics Illusion:** Concrete and lack of trees explain **57.5%** of extreme heat. However, social vulnerability (SVI) doesn't directly cause heat; it dictates *who* is forced to live in it.
2. **The Loneliness Trap:** After strict FDR correction, traditional scapegoats (like foreign nationals) were dropped. The strongest social predictor of lethal heat exposure is **loneliness** (one-person households, +0.083°C per SD).
3. **The Industrial Oven:** **59.2%** of extreme heat anomalies occur in industrial and logistics zones — a 4.3x concentration above the city baseline (see `screenshot_logistics.png`).
4. **The Invisible Majority:** **687 census tracts** have *high vulnerability* but *low heat*, meaning they are currently ignored by heat-targeted climate policies.
5. **The Tree Ceiling:** Planting trees in dense poor areas yields almost no cooling (+0.04°C) due to space limits. **Cool Roofs (-0.36°C) are the only viable physical intervention.**



## 🎮 The Solution: The Game

Built with Streamlit, this interactive experience guides the user through 5 phases:

- **Phase 1: The Crime Scene:** Click on maps to discover the 6.87°C temperature gap in 300 meters.
- **Phase 2: The Time Bomb:** Analyze seasonal data to find when heat becomes lethal (Summer gap is 2x Spring).
- **Phase 3: The Invisible Enemy:** Toggle industrial zones to see the hidden heat sources (59.2% of anomalies).
- **Phase 4: The Hotspots:** Interact with GWR (Geographically Weighted Regression) coefficients locally.
- **Phase 5: The Invisible Majority:** Find the "Orange Zones" (High Vulnerability + Low Heat) missed by policies.



## 🔬 Methodology & Tech Stack

The application is the tip of the iceberg. The full scientific methodology is documented in [`scientific_analysis.ipynb`](scientific_analysis.ipynb).

- **Spatial Analysis:** Geographically Weighted Regression (GWR), Bivariate LISA (Local Indicators of Spatial Association), Spatial Lag Models (to correct for spatial autocorrelation).
- **Statistical Modeling:** OLS Regression with Benjamini-Hochberg FDR correction, Quantile Regression (to analyze extreme heat percentiles).
- **Machine Learning:** Random Forest Regressor used for counterfactual simulations (Trees vs. Cool Roofs).
- **Tech Stack:** Python, Streamlit, GeoPandas, Plotly, SciPy, Statsmodels, PySAL, mgwr.


## 📂 Repository Structure

- `app.py` — The Streamlit interactive game.
- `scientific_analysis.ipynb` — The full scientific notebook containing the EDA, regressions, and model training.
- `app_data.geojson` — The spatial dataset driving the interactive map.
- `app_data.csv` — Processed tabular data.
- `gwr_coefs.csv` — Pre-calculated local GWR coefficients for the map.
- `time_series.csv` — 24-year LST trends (MODIS) for Rich (Q1) vs Poor (Q4).
- `ndvi_time_series.csv` — 24-year NDVI trends (MODIS) for Rich (Q1) vs Poor (Q4).
- `screenshot_logistics.png` & `screenshot_railway.png` — Visual evidence of industrial heat anomalies.
- `requirements.txt` — Python dependencies.
- `packages.txt` — System dependencies for Streamlit Cloud (GDAL, PROJ, GEOS).


## 📊 Data Sources & References (NASA Open Data Rules)

All datasets, libraries, and resources are cited below.

### 1. NASA & Earth Observation Data (Accessed via Google Earth Engine)
- **Landsat 8 & 9 Collection 2 Level-2:** 30m-resolution Land Surface Temperature (LST) used for the base heat map. (`LANDSAT/LC08/C02/T1_L2`, `LANDSAT/LC09/C02/T1_L2`).
- **MODIS:** Used for 24-year historical trends (2000–2023) of LST and NDVI. (`MODIS/061/MOD11A2`, `MODIS/061/MOD13A2`).
- **NASA GHSL (Global Human Settlement Layer):** Population data for risk exposure calculation. (`JRC/GHSL/P2023A/GHS_POP/2020`).
- **ESA Sentinel-5P:** Tropospheric NO2 pollution data used for the "Double Burden" analysis. (`COPERNICUS/S5P/OFFL/L3_NO2`).

### 2. Social & Spatial Data
- **Social Vulnerability Index (SVI) for Milan:** Census tract-level vulnerability scores (2021).
  - *Source:* Zenodo. 
  - *Link:* [Zenodo Record 13894260](https://doi.org/10.5281/zenodo.13894260)
- **OpenStreetMap (OSM):** Industrial land-use polygons used to detect heat anomalies.
  - *Source:* OpenStreetMap contributors, retrieved via `osmnx`.

### 3. Python Libraries & Tools
- **Streamlit** (MIT License)
- **GeoPandas** (BSD-3-Clause)
- **PySAL / Libpysal / Esda / mgwr** (BSD-3-Clause)
- **Statsmodels** (BSD-3-Clause)
- **Scikit-Learn** (BSD-3-Clause)
- **Plotly** (MIT License)
- **PyMannKendall** (MIT License) — Used for time-series trend analysis.



## 🚀 How to Run Locally

Clone the repository:
```bash
   git clone https://github.com/marybilik/milan-heat-explorer.git
```


Install Python dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

📄 License
This project is licensed under the MIT License. You are free to use, modify, and distribute this code for non-commercial and commercial purposes, provided the original authors are credited
