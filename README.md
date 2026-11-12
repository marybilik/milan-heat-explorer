# 🕵️ The Milan Heat Case: An Earth System Trend Detective Game

[![NASA Space Apps 2026](https://img.shields.io/badge/NASA%20Space%20Apps-2026-blue.svg)](https://spaceappschallenge.org)
[![Live App](https://img.shields.io/badge/🚀_PLAY_THE_LIVE_GAME-Click_Here-00d9ff?style=for-the-badge)](https://milan-heat-explorer.streamlit.app/)
[![Video Demo](https://img.shields.io/badge/🎥_WATCH_THE_DEMO-YouTube-red?style=for-the-badge)](https://youtu.be/7MqjsmNJB54)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

### 🎥 Project Demo & Links
* **[🚀 Play the Live Interactive Game Here](https://milan-heat-explorer.streamlit.app/)**
* **[🎥 Watch the 3-Minute Video Demo Here](https://youtu.be/7MqjsmNJB54)**
* **[📓 View the Scientific Jupyter Notebook](scientific_analysis.ipynb)** (Contains all spatial regressions, GWR, LISA, and Random Forest models)
* *(Note: Due to the large size of interactive Google Earth Engine maps, the notebook might take a moment to load or require local download).*

---

## 💡 Motivation: Why a Game?

Climate data is complex, intimidating, and often hidden in static, academic papers. The people who need this data the most — policymakers, urban planners, and citizens — rarely have the time to read statistical regressions. 

**We built a detective game because data tells, but stories sell.** By turning the user into a "Climate Detective," we force them to actively uncover the invisible inequalities of Milan. Instead of just showing a red heat map, we challenge the user to measure the 7°C gap between the Duomo and Parco Sempione, discover the "Loneliness Trap," and expose the hidden "Industrial Ovens." Gamification lowers the barrier to entry, making complex spatial statistics accessible, memorable, and actionable.

---

## 🚨 The Problem: The Anatomy of Climate Inequality

Our analysis of Milan reveals a silent crisis:

1. **The Physics Illusion:** Concrete and lack of trees explain **57.5%** of extreme heat. However, social vulnerability (SVI) doesn't directly cause heat; it dictates *who* is forced to live in it.
2. **The Loneliness Trap:** After strict FDR correction, traditional scapegoats (like foreign nationals) were dropped. The strongest social predictor of lethal heat exposure is **loneliness** (one-person households, +0.083°C per SD).
3. **The Industrial Oven:** **59.2%** of extreme heat anomalies occur in industrial and logistics zones — a 4.3x concentration above the city baseline.
4. **The Invisible Majority:** **687 census tracts** have *high vulnerability* but *low heat*, meaning they are currently ignored by heat-targeted climate policies.
5. **The Tree Ceiling:** Planting trees in dense poor areas yields almost no cooling (+0.04°C) due to space limits. **Cool Roofs (-0.36°C) are the only viable physical intervention.**

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

- **Spatial Analysis:** Geographically Weighted Regression (GWR), Bivariate LISA (Local Indicators of Spatial Association), Spatial Lag Models (to correct for spatial autocorrelation).
- **Statistical Modeling:** OLS Regression with Benjamini-Hochberg FDR correction, Quantile Regression (to analyze extreme heat percentiles).
- **Machine Learning:** Random Forest Regressor used for counterfactual simulations (Trees vs. Cool Roofs).
- **Tech Stack:** Python, Streamlit, GeoPandas, Plotly, SciPy, Statsmodels, PySAL, mgwr.

---

## 📊 Data Sources & References (NASA Open Data Rules)

In compliance with the NASA Space Apps Challenge "Cite Everything" rules, all datasets, libraries, and resources are cited below. All Earth observation data was accessed and processed via **Google Earth Engine**.

### 1. NASA & Earth Observation Data
- **Landsat 8 & 9 Collection 2 Level-2:** 30m-resolution Land Surface Temperature (LST) for Summer 2023.
  - *Catalog IDs:* `LANDSAT/LC08/C02/T1_L2`, `LANDSAT/LC09/C02/T1_L2`
  - *Source:* USGS/NASA.
- **MODIS:** 24-year historical trends (2000–2023) of Land Surface Temperature and NDVI.
  - *Catalog IDs:* `MODIS/061/MOD11A2` (LST), `MODIS/061/MOD13A2` (NDVI)
  - *Source:* NASA LP DAAC.
- **GHSL (Global Human Settlement Layer):** Population data for risk exposure calculation (2020, 100m resolution).
  - *Catalog ID:* `JRC/GHSL/P2023A/GHS_POP/2020`
  - *Source:* European Commission Joint Research Centre (JRC).

### 2. ESA & Copernicus Data
- **Sentinel-5P:** Tropospheric NO2 pollution data used for the "Double Burden" analysis (Summer 2023).
  - *Catalog ID:* `COPERNICUS/S5P/OFFL/L3_NO2`
  - *Source:* European Space Agency (ESA) / Copernicus.

### 3. Social & Spatial Data
- **Social Vulnerability Index (SVI) for Milan:** Census tract-level vulnerability scores (2021), including age, income, and household data.
  - *Source:* Zenodo.
  - *Links:* [CSV Data](https://zenodo.org/records/15675828/files/social_vulnerability_index_milan_2021.csv), [GeoJSON Data](https://zenodo.org/api/records/13894260/files/milan_vulnerability_2021.geojson/content).
- **OpenStreetMap (OSM):** Industrial land-use polygons used to detect heat anomalies.
  - *Source:* OpenStreetMap contributors, retrieved via `osmnx` (Geocoding: "Milan, Italy").

### 4. Python Libraries & Tools
- **Earth Engine API (`earthengine-api`)** & **`geemap`** (Apache 2.0)
- **Streamlit** (MIT License)
- **GeoPandas** (BSD-3-Clause)
- **PySAL Ecosystem** (`libpysal`, `esda`, `spreg`, `mgwr`) (BSD-3-Clause)
- **Statsmodels** (BSD-3-Clause)
- **Scikit-Learn** (BSD-3-Clause)
- **PyMannKendall** (MIT License) - Used for time-series trend analysis.
- **Plotly** & **Matplotlib** & **Seaborn** (MIT/BSD-3-Clause)

---

## 📂 Repository Structure

- `app.py` — The Streamlit interactive game.
- `scientific_analysis.ipynb` — The full scientific notebook containing EDA, regressions, GWR, LISA, and simulations.
- `app_data.geojson` — The spatial dataset driving the interactive map.
- `gwr_coefs.csv` — Pre-calculated GWR coefficients for the map.
- `time_series.csv` — 24-year LST trends (MODIS) for Rich vs Poor.
- `ndvi_time_series.csv` — 24-year NDVI trends (MODIS) for Rich vs Poor.
- `packages.txt` & `requirements.txt` — System and Python dependencies.

---

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
This project is licensed under the MIT License. You are free to use, modify, and distribute this code for non-commercial and commercial purposes, provided the original authors are credited.
