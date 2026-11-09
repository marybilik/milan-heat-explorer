import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# ============================================
# КОНФИГУРАЦИЯ И СТИЛИ (Премиум вид)
# ============================================
st.set_page_config(
    page_title="Milan Heat Inequality",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="collapsed" # Убираем сайдбар
)

# Кастомный CSS для премиального вида
st.markdown("""
<style>
    /* Убираем лишние отступы сверху */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    
    /* Стили для заголовков */
    h1, h2, h3 { font-family: 'Helvetica Neue', sans-serif; color: #1a1a2e; }
    .main-title { font-size: 2.8rem; font-weight: 800; text-align: center; margin-bottom: 0; }
    .sub-title { font-size: 1.1rem; color: #666; text-align: center; margin-bottom: 2rem; }
    
    /* Стили для KPI карточек */
    .metric-card {
        background: white; border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid #e74c3c;
        text-align: center; height: 100%;
    }
    .metric-value { font-size: 2rem; font-weight: bold; color: #1a1a2e; margin: 0; }
    .metric-label { font-size: 0.9rem; color: #666; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Стили для текстовых блоков */
    .insight-box {
        background: #f8f9fa; border-left: 5px solid #e74c3c; padding: 1.5rem;
        border-radius: 0 8px 8px 0; margin: 1rem 0;
    }
    
    /* Убираем стандартный фон Streamlit */
    .stApp { background-color: #f4f6f9; }
</style>
""", unsafe_allow_html=True)

# ============================================
# ЗАГРУЗКА ДАННЫХ
# ============================================
@st.cache_data
def load_data():
    try: gdf = gpd.read_file("app_data.geojson")
    except: gdf = None
    try: df = pd.read_csv("app_data.csv")
    except: df = None
    try: ts = pd.read_csv("time_series.csv")
    except: ts = None
    return gdf, df, ts

gdf, df, ts = load_data()

if gdf is None:
    st.error("❌ `app_data.geojson` не найден. Загрузите файл в репозиторий.")
    st.stop()

# ============================================
# ХЕДЕР
# ============================================
st.markdown('<div class="main-title">🌡️ Milan Heat Inequality Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">NASA Space Apps Challenge 2026 | Earth System Trend Detective</div>', unsafe_allow_html=True)

# ============================================
# НАВИГАЦИЯ (Горизонтальная, без сайдбара)
# ============================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard", 
    "🗺️ Interactive Map", 
    "📈 Trends & Analytics", 
    "🏭 Deep Dive", 
    "🛠️ Policy Simulator"
])

# ============================================
# ВКЛАДКА 1: DASHBOARD
# ============================================
with tab1:
    # KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="metric-card"><div class="metric-value">571k</div><div class="metric-label">People at Risk</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card" style="border-top-color: #e67e22;"><div class="metric-value">59.2%</div><div class="metric-label">Anomalies in Industry</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card" style="border-top-color: #8e44ad;"><div class="metric-value">+0.858°C</div><div class="metric-label">Heating Rate / Decade</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-card" style="border-top-color: #27ae60;"><div class="metric-value">2.01%</div><div class="metric-label">Model Error (MAPE)</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick Map
    st.subheader("Quick Map Preview")
    geojson = json.loads(gdf.to_json())
    
    # ИСПОЛЬЗУЕМ НОВЫЙ МЕТОД (fix для AttributeError)
    fig = px.choropleth_mapbox(
        gdf, geojson=geojson, locations='SEZ2011', featureidkey='properties.SEZ2011',
        color='mean_lst', color_continuous_scale='YlOrRd', range_color=(35, 55),
        mapbox_style="carto-positron", zoom=10.5, center={"lat": 45.4642, "lon": 9.1900},
        opacity=0.7, labels={'mean_lst': 'Temperature (°C)'}
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# ВКЛАДКА 2: INTERACTIVE MAP
# ============================================
with tab2:
    st.subheader("Explore Spatial Distribution")
    
    c1, c2 = st.columns([1, 1])
    with c1:
        metric = st.selectbox("Select Metric:", 
            ["Surface Temperature", "Social Vulnerability", "Priority Score", "Industrial Anomaly"])
    with c2:
        quartile = st.multiselect("Filter by SVI Quartile:", 
            ["Q1 (Rich)", "Q2", "Q3", "Q4 (Poor)"], default=["Q1 (Rich)", "Q4 (Poor)"])

    col_map = {
        'Surface Temperature': 'mean_lst',
        'Social Vulnerability': 'social_vulnerability',
        'Priority Score': 'priority_score',
        'Industrial Anomaly': 'residuals'
    }
    selected = col_map[metric]
    
    filtered = gdf.copy()
    if 'svi_quartile' in filtered.columns:
        filtered = filtered[filtered['svi_quartile'].isin(quartile)]

    filtered_geojson = json.loads(filtered.to_json())
    
    fig = px.choropleth_mapbox(
        filtered, geojson=filtered_geojson, locations='SEZ2011', featureidkey='properties.SEZ2011',
        color=selected, color_continuous_scale='Viridis',
        mapbox_style="carto-darkmatter", # Темная карта выглядит премиально
        zoom=10.5, center={"lat": 45.4642, "lon": 9.1900}, opacity=0.8,
        labels={selected: metric}
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=600)
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# ВКЛАДКА 3: TRENDS
# ============================================
with tab3:
    st.subheader("10-Year Heating Trend (2014-2023)")
    
    if ts is not None:
        ts['Q1_Smooth'] = ts['Q1_Rich'].rolling(3).mean()
        ts['Q4_Smooth'] = ts['Q4_Poor'].rolling(3).mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ts['Year'], y=ts['Q1_Smooth'], mode='lines+markers',
                                  line=dict(color='#2ecc71', width=4), name='Rich Neighborhoods (Q1)'))
        fig.add_trace(go.Scatter(x=ts['Year'], y=ts['Q4_Smooth'], mode='lines+markers',
                                  line=dict(color='#e74c3c', width=4), name='Poor Neighborhoods (Q4)'))
        
        fig.update_layout(
            title='The Widening Gap: Rich vs Poor',
            xaxis_title='Year', yaxis_title='Mean LST (°C)',
            height=500, plot_bgcolor='white', paper_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('<div class="insight-box">💡 <b>Key Insight:</b> Poor neighborhoods are heating 4% faster than rich ones. The gap is highly significant (p < 0.0001).</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ `time_series.csv` не найден.")

# ============================================
# ВКЛАДКА 4: DEEP DIVE
# ============================================
with tab4:
    st.subheader("Case Studies: Hidden Heat Islands")
    
    c1, c2 = st.columns(2)
    with c1:
        if os.path.exists("screenshot_logistics.png"):
            st.image("screenshot_logistics.png", use_column_width=True)
        st.markdown('<div class="insight-box"><b>Logistics Heat Trap:</b> Dark roofs and asphalt reach 53°C+.</div>', unsafe_allow_html=True)
    
    with c2:
        if os.path.exists("screenshot_railway.png"):
            st.image("screenshot_railway.png", use_column_width=True)
        st.markdown('<div class="insight-box"><b>Steel Desert:</b> Railway yards act as massive heat sinks.</div>', unsafe_allow_html=True)

# ============================================
# ВКЛАДКА 5: POLICY SIMULATOR
# ============================================
with tab5:
    st.subheader("Intervention Simulator")
    
    current_temp = 48.67
    
    intervention = st.radio("Select Intervention Strategy:", 
        ["🌳 Plant Trees", "🏠 Cool Roofs (Reflective)", "🔀 Combined Approach"], horizontal=True)
    
    if intervention == "🌳 Plant Trees":
        effect, color = 0.04, "#e74c3c"
        reason = "Data ceiling reached. Marginal cooling effect."
    elif intervention == "🏠 Cool Roofs (Reflective)":
        effect, color = -0.36, "#3498db"
        reason = "Highly effective. Reduces surface temperature significantly."
    else:
        effect, color = -0.32, "#9b59b6"
        reason = "Slightly less effective than cool roofs alone."

    c1, c2 = st.columns(2)
    c1.metric("Current Temperature", f"{current_temp:.2f}°C")
    c2.metric("After Intervention", f"{current_temp + effect:.2f}°C", f"{effect:+.2f}°C")

    fig = go.Figure(go.Bar(
        x=['Current Reality', 'After Intervention'], y=[current_temp, current_temp + effect],
        marker_color=['#e74c3c', color], text=[f'{current_temp:.2f}°C', f'{current_temp + effect:.2f}°C'], textposition='auto'
    ))
    fig.update_layout(height=400, yaxis_range=[48, 49.5], plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f'<div class="insight-box">{reason}</div>', unsafe_allow_html=True)
