import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# ============================================
# КОНФИГУРАЦИЯ
# ============================================
st.set_page_config(
    page_title="Milan Heat Inequality Explorer",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2.8rem; font-weight: 800; color: #1a1a2e; text-align: center; }
    .sub-header { font-size: 1.1rem; color: #666; text-align: center; margin-bottom: 2rem; }
    .insight-box { background-color: #f8f9fa; border-left: 5px solid #e74c3c; padding: 1rem 1.5rem; margin: 1rem 0; border-radius: 0 8px 8px 0; }
    .insight-box h4 { margin-top: 0; color: #e74c3c; }
    .trend-answer { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ============================================
# ЗАГРУЗКА ДАННЫХ (КЭШ)
# ============================================
@st.cache_data
def load_all_data():
    try:
        gdf = gpd.read_file("app_data.geojson")
    except:
        gdf = None
    
    try:
        df = pd.read_csv("app_data.csv")
    except:
        df = None
    
    try:
        ts = pd.read_csv("time_series.csv")
    except:
        ts = None
    
    return gdf, df, ts

gdf, df, ts = load_all_data()

if gdf is None:
    st.error("❌ Файл `app_data.geojson` не найден. Пожалуйста, загрузите его в папку с приложением.")
    st.stop()

# ============================================
# ХЕДЕР
# ============================================
st.markdown('<div class="main-header">🌡️ Milan Heat Inequality Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">NASA Space Apps Challenge 2026 | Earth System Trend Detective</div>', unsafe_allow_html=True)

# ============================================
# БОКОВАЯ ПАНЕЛЬ
# ============================================
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to:", [
    "📊 Executive Dashboard",
    "🗺️ Interactive Heat Map",
    "📈 Time Series Analysis",
    "🏭 Deep Dive Case Studies",
    "🔬 Research Findings",
    "🛠️ Policy Simulator",
    "📋 Data Explorer"
])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Key Stats")
st.sidebar.metric("Census Tracts", f"{len(gdf):,}")
st.sidebar.metric("Mean LST", f"{gdf['mean_lst'].mean():.1f}°C")
st.sidebar.metric("Moran's I", "0.74")
st.sidebar.markdown("---")
st.sidebar.markdown("**Data Sources:**")
st.sidebar.markdown("- NASA Landsat 8/9\n- Zenodo SVI\n- OpenStreetMap")

# ============================================
# 1. EXECUTIVE DASHBOARD
# ============================================
if page == "📊 Executive Dashboard":
    st.header("Executive Summary")
    
    # KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("People in Risk Zones", "571,146", "40.8% of population")
    c2.metric("Heat Anomalies in Industry", "59.2%", "4.3x baseline")
    c3.metric("Heating Rate (Poor)", "+0.858°C/decade", "vs +0.825°C (Rich)")
    c4.metric("Model Accuracy (MAPE)", "2.01%", "Very high")
    
    st.markdown("---")
    st.subheader("🔑 Three Key Findings")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div class="insight-box"><h4>🌡️ The Gap</h4><p>Surface temperatures differ by <strong>6.87°C</strong> across 300m. Poor neighborhoods heat <strong>4% faster</strong> than rich ones (p < 0.0001 after spatial correction).</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="insight-box"><h4>🏭 The Hidden Source</h4><p><strong>59.2%</strong> of extreme heat anomalies occur in industrial zones — a <strong>4.3x concentration</strong> above baseline.</p></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="insight-box"><h4>🛠️ The Solution</h4><p>Planting trees: <strong>+0.04°C</strong> (data ceiling). <strong>Cool Roofs: -0.36°C</strong> — the only viable intervention.</p></div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🗺️ Quick Map Preview")
    geojson = json.loads(gdf.to_json())
    
    fig = px.choropleth_mapbox(
        gdf, geojson=geojson, locations='SEZ2011', featureidkey='properties.SEZ2011',
        color='mean_lst', color_continuous_scale='YlOrRd', range_color=(35, 55),
        mapbox_style="carto-positron", zoom=10.5, center={"lat": 45.4642, "lon": 9.1900},
        opacity=0.7, labels={'mean_lst': 'LST (°C)'}
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# 2. INTERACTIVE HEAT MAP
# ============================================
elif page == "🗺️ Interactive Heat Map":
    st.header("Spatial Distribution Explorer")
    st.markdown("Explore the city interactively. Use filters below to customize the view.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        metric = st.selectbox("🎨 Color by:", [
            "Surface Temperature (LST)", "Social Vulnerability (SVI)", 
            "Priority Score", "Heat Anomaly (Residual)", "NO2 Pollution"
        ])
    with c2:
        quartile_filter = st.multiselect("📊 SVI Quartile:", 
            ["Q1 (Rich)", "Q2", "Q3", "Q4 (Poor)"],
            default=["Q1 (Rich)", "Q2", "Q3", "Q4 (Poor)"])
    with c3:
        show_lisa = st.checkbox("🔍 Highlight Hot Spots (LISA)", value=False)
    
    col_map = {
        'Surface Temperature (LST)': 'mean_lst',
        'Social Vulnerability (SVI)': 'social_vulnerability',
        'Priority Score': 'priority_score',
        'Heat Anomaly (Residual)': 'residuals',
        'NO2 Pollution': 'no2'
    }
    selected_col = col_map[metric]
    
    filtered = gdf.copy()
    if 'svi_quartile' in filtered.columns:
        filtered = filtered[filtered['svi_quartile'].isin(quartile_filter)]
    
    filtered_geojson = json.loads(filtered.to_json())
    
    hover_data = {'SEZ2011': True}
    if 'mean_lst' in filtered.columns:
        hover_data['mean_lst'] = ':.1f'
    if 'social_vulnerability' in filtered.columns:
        hover_data['social_vulnerability'] = ':.2f'
    
    fig = px.choropleth_mapbox(
        filtered, geojson=filtered_geojson, 
        locations='SEZ2011', featureidkey='properties.SEZ2011',
        color=selected_col, color_continuous_scale='YlOrRd',
        mapbox_style="carto-positron", zoom=10.5,
        center={"lat": 45.4642, "lon": 9.1900}, opacity=0.7,
        hover_data=hover_data, labels={selected_col: metric}
    )
    
    if show_lisa and 'lisa_cat' in filtered.columns:
        colors = {'Hot Spot (HH)': '#d73027', 'Cold Spot (LL)': '#4575b4'}
        for cat, color in colors.items():
            sub = filtered[filtered['lisa_cat'] == cat]
            if not sub.empty:
                fig.add_trace(go.Scattermapbox(
                    lat=sub.geometry.centroid.y, lon=sub.geometry.centroid.x,
                    mode='markers', marker=dict(size=10, color=color),
                    name=cat
                ))
    
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=650)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Tracts Shown", len(filtered))
    c2.metric("Mean Value", f"{filtered[selected_col].mean():.2f}")
    c3.metric("Max Value", f"{filtered[selected_col].max():.2f}")

# ============================================
# 3. TIME SERIES ANALYSIS
# ============================================
elif page == "📈 Time Series Analysis":
    st.header("10-Year Heating Trend (2014-2023)")
    
    if ts is not None:
        # Smoothing
        ts['Q1_Smooth'] = ts['Q1_Rich'].rolling(3).mean()
        ts['Q4_Smooth'] = ts['Q4_Poor'].rolling(3).mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ts['Year'], y=ts['Q1_Rich'], mode='lines+markers', 
                                  opacity=0.3, name='Q1 Raw', line=dict(color='#2ecc71')))
        fig.add_trace(go.Scatter(x=ts['Year'], y=ts['Q4_Poor'], mode='lines+markers', 
                                  opacity=0.3, name='Q4 Raw', line=dict(color='#e74c3c')))
        fig.add_trace(go.Scatter(x=ts['Year'], y=ts['Q1_Smooth'], mode='lines+markers',
                                  line=dict(color='#2ecc71', width=4), name='Q1 (Rich) - Smoothed'))
        fig.add_trace(go.Scatter(x=ts['Year'], y=ts['Q4_Smooth'], mode='lines+markers',
                                  line=dict(color='#e74c3c', width=4), name='Q4 (Poor) - Smoothed'))
        
        fig.update_layout(
            title='The Widening Heat Gap: Rich vs Poor',
            xaxis_title='Year', yaxis_title='Mean Summer LST (°C)',
            height=500, hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("💡 **Note:** Thick lines show 3-year moving average. Thin lines show raw annual data.")
        
        st.markdown("---")
        st.subheader("Seasonal Amplification: The Summer Trap")
        
        seasonal = pd.DataFrame({
            'Season': ['Spring', 'Summer', 'Autumn'],
            'Q1 (Rich)': [19.29, 46.30, 31.77],
            'Q4 (Poor)': [20.57, 48.66, 33.33]
        })
        
        fig2 = px.bar(seasonal, x='Season', y=['Q1 (Rich)', 'Q4 (Poor)'], barmode='group',
                      color_discrete_map={'Q1 (Rich)': '#2ecc71', 'Q4 (Poor)': '#e74c3c'},
                      title='Seasonal Temperature Gap: Rich vs Poor')
        fig2.update_layout(yaxis_title='Mean Temperature (°C)', height=400)
        st.plotly_chart(fig2, use_container_width=True)
        
        st.success("📌 **Key Insight:** The gap nearly doubles in Summer (2.35°C vs 1.28°C in Spring). Climate inequality is seasonally activated.")
    else:
        st.warning("⚠️ `time_series.csv` не найден.")

# ============================================
# 4. DEEP DIVE CASE STUDIES
# ============================================
elif page == "🏭 Deep Dive Case Studies":
    st.header("Case Studies: Hidden Heat Islands")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🚛 Logistics Heat Trap")
        if os.path.exists("screenshot_logistics.png"):
            st.image("screenshot_logistics.png", caption="Priority Tract 151460001206")
        else:
            st.warning("📸 Загрузите `screenshot_logistics.png`")
        st.markdown("""
        **Analysis:** Large dark roofs and asphalt absorb heat, reaching **53°C+**.
        This is a hidden heat source that standard climate models miss.
        """)
    
    with c2:
        st.subheader("🚂 Steel Desert")
        if os.path.exists("screenshot_railway.png"):
            st.image("screenshot_railway.png", caption="Railway Yard — High Temperature")
        else:
            st.warning("📸 Загрузите `screenshot_railway.png`")
        st.markdown("""
        **Analysis:** Metal and gravel surfaces create extreme heat islands.
        Railway yards reach **55°C+** — a 4.3x concentration of heat anomalies.
        """)
    
    st.markdown("---")
    st.subheader("📍 Top Priority Tracts")
    if 'priority_score' in gdf.columns:
        top_20 = gdf.nlargest(20, 'priority_score')
        st.dataframe(top_20[['SEZ2011', 'mean_lst', 'social_vulnerability', 'residuals']].head(10), use_container_width=True)

# ============================================
# 5. RESEARCH FINDINGS
# ============================================
elif page == "🔬 Research Findings":
    st.header("Full Research Methodology")
    
    t1, t2, t3, t4 = st.tabs(["📊 The Gap", "🏭 Hidden Heat", "🌳 Eco-Lock", "🧍 Faces of Heat"])
    
    with t1:
        st.markdown("### Physics vs Social Vulnerability")
        st.markdown("""
        **R² Decomposition:**
        - Physics (concrete + trees): **57.5%**
        - SVI only: 18.8%
        - Physics + SVI: **57.5%** (SVI adds 0.1%)
        """)
    
    with t2:
        st.markdown("### Industrial Heat Anomalies")
        c1, c2 = st.columns(2)
        c1.metric("Baseline (all tracts)", "13.9%")
        c2.metric("Anomalies in Industrial", "59.2%")
        st.metric("Concentration Ratio", "4.3x")
    
    with t3:
        st.markdown("### The Eco-Structural Lock")
        c1, c2 = st.columns(2)
        c1.metric("Poor at Ceiling", "64.3%")
        c2.metric("Rich at Ceiling", "7.9%")
    
    with t4:
        st.markdown("### Who Suffers? FDR-Corrected")
        st.table(pd.DataFrame({
            'Factor': ['One-person households', 'Foreign nationals', 'Unemployed'],
            'Coefficient': ['+0.083°C', '+0.029°C', '-0.042°C'],
            'p-value (FDR)': ['<0.0001', '0.14', '0.04'],
            'Significant': ['✅', '❌', '✅']
        }))
    
    st.markdown("---")
    st.markdown("""
    <div class="trend-answer">
    <h3>🎯 Answer to the NASA "Trend Detective" Challenge</h3>
    <p>Our local trend — a <strong>0.033°C/decade gap</strong> between rich and poor — 
    confirms that urban inequality amplifies the global warming baseline, creating a 
    compounding climate crisis for vulnerable populations.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# 6. POLICY SIMULATOR
# ============================================
elif page == "🛠️ Policy Simulator":
    st.header("Intervention Simulator")
    st.markdown("Select an intervention and see the simulated impact.")
    
    current_temp = 48.67
    
    intervention = st.radio("Select intervention:", 
        ["🌳 Plant Trees", "🏠 Cool Roofs", "🔀 Combined"], horizontal=True)
    
    if intervention == "🌳 Plant Trees":
        effect, explanation = 0.04, "Trees yield almost no cooling due to the data ceiling (64.3% at maximum)."
    elif intervention == "🏠 Cool Roofs":
        effect, explanation = -0.36, "Cool roofs reduce temperature by -0.36°C. The only viable intervention."
    else:
        effect, explanation = -0.32, "Combined approach yields slightly less than cool roofs alone."
    
    new_temp = current_temp + effect
    
    c1, c2 = st.columns(2)
    c1.metric("Current Temperature", f"{current_temp:.2f}°C")
    c2.metric("After Intervention", f"{new_temp:.2f}°C", f"{effect:+.2f}°C")
    
    fig = go.Figure(go.Bar(x=['Current', 'After'], y=[current_temp, new_temp],
                           marker_color=['#e74c3c', '#3498db'],
                           text=[f'{current_temp:.2f}', f'{new_temp:.2f}'], textposition='auto'))
    fig.update_layout(title=f'Intervention: {intervention}', yaxis_title='Temperature (°C)', height=400, yaxis_range=[48, 49.5])
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"**Analysis:** {explanation}")
    
    st.markdown("---")
    st.subheader("🎯 Priority Zones Map")
    top_20 = gdf.nlargest(20, 'priority_score')
    top_geojson = json.loads(top_20.to_json())
    
    fig2 = px.choropleth_mapbox(top_20, geojson=top_geojson, locations='SEZ2011',
                                featureidkey='properties.SEZ2011', color='priority_score',
                                color_continuous_scale='Reds', mapbox_style="carto-positron",
                                zoom=10.5, center={"lat": 45.4642, "lon": 9.1900}, opacity=0.8)
    fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)
    st.plotly_chart(fig2, use_container_width=True)

# ============================================
# 7. DATA EXPLORER
# ============================================
elif page == "📋 Data Explorer":
    st.header("Data Explorer")
    st.markdown("Filter and explore the full dataset.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        lst_range = st.slider("Temperature (°C):", float(gdf['mean_lst'].min()), float(gdf['mean_lst'].max()),
                              (float(gdf['mean_lst'].min()), float(gdf['mean_lst'].max())))
    with c2:
        svi_range = st.slider("SVI:", float(gdf['social_vulnerability'].min()), float(gdf['social_vulnerability'].max()),
                              (float(gdf['social_vulnerability'].min()), float(gdf['social_vulnerability'].max())))
    with c3:
        if 'lisa_cat' in gdf.columns:
            lisa_filter = st.multiselect("LISA:", gdf['lisa_cat'].unique(), default=gdf['lisa_cat'].unique())
    
    filtered = gdf[(gdf['mean_lst'] >= lst_range[0]) & (gdf['mean_lst'] <= lst_range[1]) &
                   (gdf['social_vulnerability'] >= svi_range[0]) & (gdf['social_vulnerability'] <= svi_range[1])]
    if 'lisa_cat' in gdf.columns and lisa_filter:
        filtered = filtered[filtered['lisa_cat'].isin(lisa_filter)]
    
    st.dataframe(filtered[['SEZ2011', 'mean_lst', 'social_vulnerability', 'impervious_x', 'tree_cover_density', 'priority_score']].head(100), use_container_width=True)
    st.metric("Matching Tracts", len(filtered))

# ============================================
# FOOTER
# ============================================
st.sidebar.markdown("---")
st.sidebar.info("🌡️ **Milan Heat Explorer**\n\nBuilt with Streamlit, Plotly & NASA Landsat data.")