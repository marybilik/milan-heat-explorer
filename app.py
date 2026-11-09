import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import numpy as np

# ============================================
# CONFIG & NASA CSS
# ============================================
st.set_page_config(page_title="NASA // MILAN HEAT CASE", page_icon="🕵️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background: #050814; color: #b8c5d6; }
    h1, h2, h3, h4 { color: #00d9ff !important; font-family: 'Courier New', monospace; letter-spacing: 2px; }
    p, li, label, .stMarkdown, .stRadio label, .stSelectbox label, .stSlider label, .stCheckbox label { color: #b8c5d6 !important; font-family: 'Courier New', monospace; }
    
    .stApp::before {
        content: ''; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: repeating-linear-gradient(0deg, rgba(0,217,255,0.025) 0px, rgba(0,217,255,0.025) 1px, transparent 1px, transparent 4px);
        pointer-events: none; z-index: 9999;
    }
    
    .mission-header {
        background: linear-gradient(90deg, #0a1128, #001f3f);
        border: 1px solid #00d9ff; padding: 12px 20px; border-radius: 4px;
        margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;
        font-family: 'Courier New', monospace; font-size: 0.85rem;
        box-shadow: 0 0 20px rgba(0,217,255,0.2);
    }
    .mission-header .label { color: #00ff88; }
    .mission-header .val { color: #00d9ff; font-weight: bold; }
    
    .terminal {
        background: rgba(0,20,40,0.7); border-left: 3px solid #00d9ff; border-right: 3px solid #00d9ff;
        padding: 20px 25px; margin: 20px 0; border-radius: 4px;
        font-family: 'Courier New', monospace; font-size: 1rem; line-height: 1.7;
        box-shadow: inset 0 0 30px rgba(0,217,255,0.05);
    }
    .terminal .tag { color: #ffaa00; font-weight: bold; letter-spacing: 3px; font-size: 0.8rem; }
    .terminal .text { color: #e0e8f0; margin-top: 10px; }
    .terminal .highlight { color: #00ff88; font-weight: bold; }
    
    .objective {
        background: rgba(255,170,0,0.1); border: 1px solid #ffaa00;
        padding: 12px 20px; border-radius: 4px; margin: 12px 0;
        font-family: 'Courier New', monospace; font-size: 0.95rem;
    }
    .objective::before { content: '▸ OBJECTIVE: '; color: #ffaa00; font-weight: bold; }
    
    @keyframes clueIn { 0% { transform: scale(0.8); opacity: 0; } 50% { transform: scale(1.05); opacity: 1; } 100% { transform: scale(1); opacity: 1; } }
    .clue-unlocked {
        animation: clueIn 0.8s ease-out;
        background: linear-gradient(90deg, rgba(0,255,136,0.15), rgba(0,217,255,0.15));
        border: 2px solid #00ff88; border-radius: 4px; padding: 15px 25px; margin: 15px 0;
        font-family: 'Courier New', monospace; text-align: center;
    }
    .clue-unlocked .title { color: #00ff88; font-weight: bold; letter-spacing: 4px; font-size: 0.8rem; }
    .clue-unlocked .body { color: #ffffff; font-size: 1.05rem; margin-top: 6px; }
    
    .stButton > button {
        background: transparent; color: #00d9ff !important;
        border: 2px solid #00d9ff; padding: 12px 28px;
        font-family: 'Courier New', monospace; font-weight: bold;
        letter-spacing: 2px; border-radius: 2px;
        transition: all 0.2s; text-transform: uppercase;
    }
    .stButton > button:hover { background: #00d9ff; color: #050814 !important; box-shadow: 0 0 30px rgba(0,217,255,0.6); }
    
    .stRadio > div { background: rgba(0,217,255,0.03); padding: 12px; border-radius: 4px; border: 1px solid rgba(0,217,255,0.2); }
    .stProgress > div > div > div > div { background: linear-gradient(90deg, #00ff88, #00d9ff) !important; box-shadow: 0 0 10px #00ff88 !important; }
    
    .evidence-log { margin-top: 40px; padding: 15px 20px; border-top: 2px solid #00d9ff; background: rgba(0,20,40,0.5); }
    .evidence-log .header { color: #00ff88; font-family: 'Courier New'; font-size: 0.75rem; letter-spacing: 3px; margin-bottom: 10px; }
    .evidence-item { display: inline-block; background: rgba(0,255,136,0.1); border: 1px solid #00ff88; color: #00ff88; padding: 5px 12px; border-radius: 3px; margin: 3px; font-family: 'Courier New', monospace; font-size: 0.8rem; }
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATA LOADING & MERGING
# ============================================
@st.cache_data
def load_data():
    gdf = gpd.read_file("app_data.geojson")
    gdf['SEZ2011'] = gdf['SEZ2011'].astype(str)
    
    if os.path.exists("gwr_coefs.csv") and 'gwr_svi' not in gdf.columns:
        gwr = pd.read_csv("gwr_coefs.csv")
        gwr['SEZ2011'] = gwr['SEZ2011'].astype(str)
        gdf = gdf.merge(gwr[['SEZ2011', 'gwr_svi']], on='SEZ2011', how='left')
    
    gdf_wgs = gdf.to_crs(epsg=4326)
    gdf['cx'] = gdf_wgs.geometry.centroid.x
    gdf['cy'] = gdf_wgs.geometry.centroid.y
    
    ts = pd.read_csv("time_series.csv") if os.path.exists("time_series.csv") else None
    return gdf, ts

try:
    gdf, ts = load_data()
except Exception as e:
    st.error(f"🚨 DATA ERROR: {e}")
    st.stop()

# ============================================
# STATE MANAGEMENT
# ============================================
defaults = {
    'chapter': 0, 
    'evidence': [],
    'clicked_duomo': False, 'clicked_park': False, 'clicks': 0,
    'trend_run': False, 'overlay_run': False,
    'no2_revealed': False, 'ch4_solved': False,
    'ch2_solved': False, 'ch3_solved': False, 
    'tree_explored': False, 'gwr_explored': False, 
    'ch8_solved': False, 'lisa_explored': False,
    'easter_egg_found': False
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def award_clue(key):
    if key not in st.session_state.evidence:
        st.session_state.evidence.append(key)

def advance():
    st.session_state.chapter += 1
    st.rerun()

CHAPTERS = ["CALIBRATION","ILLUSION","FACTORS","SEASONS","POLLUTION","ANOMALIES","TREES","GWR","QUANTILE","PARADOX","CASE CLOSED"]

# ============================================
# STATUS BAR
# ============================================
if 0 < st.session_state.chapter <= 10:
    ch = int(st.session_state.chapter)
    rank = "CADET" if len(st.session_state.evidence) < 4 else "ANALYST" if len(st.session_state.evidence) < 7 else "DETECTIVE" if len(st.session_state.evidence) < 10 else "MASTER"
    st.markdown(f"""
    <div class="mission-header">
        <div><span class="label">🛰️ MISSION:</span> <span class="val">MILAN HEAT</span></div>
        <div><span class="label">CHAPTER:</span> <span class="val">{ch}/10 // {CHAPTERS[ch-1]}</span></div>
        <div><span class="label">RANK:</span> <span class="val">{rank}</span></div>
        <div><span class="label">EVIDENCE:</span> <span class="val">{len(st.session_state.evidence)}/10</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(min(len(st.session_state.evidence)/10, 1.0))

# ============================================
# CH0: LAUNCH
# ============================================
if st.session_state.chapter == 0:
    st.markdown("""
    <div style="text-align:center; padding: 40px 20px 20px 20px;">
        <div style="font-size: 6rem; filter: drop-shadow(0 0 30px #00d9ff); margin-bottom: -10px;">🕵️</div>
        <div style="color:#00ff88; font-family:'Courier New'; letter-spacing:8px; margin-top:20px; font-size:0.85rem;">NASA EARTH OBSERVATION SYSTEM</div>
        <h1 style="font-size:3.5rem; letter-spacing:6px; margin:15px 0; color:#00d9ff; text-shadow:0 0 20px #00d9ff;">THE MILAN<br>HEAT CASE</h1>
        <div style="color:#ffaa00; font-family:'Courier New'; letter-spacing:5px; font-size:0.8rem;">CLASSIFICATION: SECRET // LEVEL 3</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown(
            '<div class="terminal" style="margin-top: 0;">'
            '<div class="tag">▶ MISSION BRIEFING</div>'
            '<div class="text">'
            'Agent, we have a crisis. Milan, Summer 2023. Surface temperatures hit <span class="highlight">56°C</span>. '
            'But satellite data reveals something sinister: <span class="highlight">the heat is not distributed equally</span>.<br><br>'
            '<b>Why Milan?</b> It is the perfect petri dish for <span class="highlight">Climate Inequality</span>. '
            'A city where historic wealth (cool parks, green centers) sits right next to industrial poverty '
            '(suffocating concrete). Here, a person\'s zip code determines their body temperature.<br><br>'
            'Your mission is to uncover <span class="highlight">who</span> is dying — and <span class="highlight">why</span>.'
            '</div>'
            '</div>', 
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            '<div class="terminal" style="margin-top: 0; border-left-color: #ffaa00; border-right-color: #ffaa00;">'
            '<div class="tag" style="color: #ffaa00;">▶ SCIENTIFIC ARSENAL</div>'
            '<div class="text" style="font-size: 0.85rem; line-height: 1.5;">'
            '<b>[ DATA SOURCES ]</b><br>'
            '🛰️ <b>Landsat 8/9:</b> 100m Thermal (LST)<br>'
            '🛰️ <b>MODIS (NASA):</b> 24-year LST & NDVI trend<br>'
            '🛰️ <b>Sentinel-5P (ESA):</b> NO2 Air Pollution<br>'
            '👥 <b>GHSL (JRC):</b> 100m Population weight<br>'
            '🏙️ <b>ISTAT/OSM:</b> Social Vulnerability Index<br><br>'
            '<b>[ ANALYTICAL WEAPONS ]</b><br>'
            '📊 OLS & Spatial Lag Models<br>'
            '🎯 FDR Multiple Testing Correction<br>'
            '🗺️ GWR (Local Spatial Anomalies)<br>'
            '🔬 Bivariate LISA (Spatial Clustering)<br>'
            '📈 Quantile Regression (Extreme Tails)'
            '</div>'
            '</div>', 
            unsafe_allow_html=True
        )

    st.markdown(
        '<div style="text-align: center; margin-top: 20px;">'
        '<span style="color:#ff4444; font-family:\'Courier New\'; font-size:0.9rem;">'
        '⚠ 10 chapters · 10 pieces of evidence · 1 city in crisis'
        '</span><span class="cursor" style="color:#ff4444;">█</span>'
        '</div>', 
        unsafe_allow_html=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    _, col_btn, _ = st.columns([1, 1, 1])
    with col_btn:
        if st.button("▶ INITIATE MISSION", use_container_width=True):
            advance()

# ============================================
# CH1: CALIBRATION
# ============================================
elif st.session_state.chapter == 1:
    st.markdown("## 📍 CHAPTER 1 // CALIBRATION")
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ INCOMING TRANSMISSION</div>
        <div class="text">
            Agent, let's calibrate your instruments. Look at the map. Two locations, 300 meters apart.<br>
            🔴 <b>DUOMO</b> — dense historic center<br>
            🟢 <b>PARCO SEMPIONE</b> — the city's largest park<br><br>
            Click on both markers on the map to scan their surface temperature.
        </div>
    </div>
    <div class="objective">Click Duomo + Park on the map to unlock Clue #1</div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scattermap(
        lat=[45.464], lon=[9.191], mode='markers+text',
        marker=dict(size=40 if st.session_state.clicked_duomo else 30,
                    color='#00ff88' if st.session_state.clicked_duomo else '#ff4444'),
        text=['🔴 DUOMO ✓' if st.session_state.clicked_duomo else '🔴 DUOMO'],
        textposition='top center', textfont=dict(color='#ff4444', size=14, family='Courier New'),
        customdata=['duomo'], hovertemplate='<b>DUOMO</b><br>Click to measure<extra></extra>'
    ))
    fig.add_trace(go.Scattermap(
        lat=[45.472], lon=[9.179], mode='markers+text',
        marker=dict(size=40 if st.session_state.clicked_park else 30, color='#00ff88'),
        text=['🟢 PARK ✓' if st.session_state.clicked_park else '🟢 PARK'],
        textposition='top center', textfont=dict(color='#00ff88', size=14, family='Courier New'),
        customdata=['park'], hovertemplate='<b>PARK</b><br>Click to measure<extra></extra>'
    ))
    fig.update_layout(
        map=dict(style="carto-darkmatter", center=dict(lat=45.468, lon=9.185), zoom=14),
        height=420, margin=dict(l=0,r=0,t=0,b=0), showlegend=False, paper_bgcolor='rgba(0,0,0,0)'
    )
    
    event = st.plotly_chart(fig, on_select="rerun", selection_mode="points", use_container_width=True, key="ch1_map")
    
    if event and event.get("selection", {}).get("points"):
        for p in event.selection.points:
            cd = p.get('customdata')
            if cd == 'duomo' and not st.session_state.clicked_duomo:
                st.session_state.clicked_duomo = True; st.rerun()
            if cd == 'park' and not st.session_state.clicked_park:
                st.session_state.clicked_park = True; st.rerun()
    
    if 'clicks' in st.session_state and not (st.session_state.clicked_duomo and st.session_state.clicked_park):
        st.session_state.clicks += 1
        if st.session_state.clicks == 5:
            st.info("🤖 **System Note:** The map is not going to bite you, Agent. Click the red and green dots.")

    c1, c2 = st.columns(2)
    c1.metric("🔴 Duomo", "✓ Measured" if st.session_state.clicked_duomo else "❌ Pending")
    c2.metric("🟢 Park", "✓ Measured" if st.session_state.clicked_park else "❌ Pending")
    
    if st.session_state.clicked_duomo and st.session_state.clicked_park:
        award_clue('gap')
        st.markdown('<div class="clue-unlocked"><div class="title">🔍 CLUE #1</div><div class="body">6.87°C difference across 300m</div></div>', unsafe_allow_html=True)
        
        fig2 = go.Figure(go.Bar(
            x=['Duomo','Park'], y=[48.87, 42.00], marker_color=['#ff4444','#00ff88'],
            text=['48.87°C','42.00°C'], textposition='outside', textfont=dict(size=20, color='white', family='Courier New')
        ))
        fig2.update_layout(
            title="🔬 MEASUREMENT COMPLETE", yaxis_title="LST (°C)", yaxis_range=[40,51],
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#00d9ff', family='Courier New'), height=380
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        if st.button("▶ INVESTIGATE THE CAUSE"):
            advance()

# ============================================
# CH2: PHYSICS ILLUSION
# ============================================
elif st.session_state.chapter == 2:
    st.markdown("## 🧱 CHAPTER 2 // THE PHYSICS ILLUSION")
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ INCOMING TRANSMISSION</div>
        <div class="text">
            A 7°C gap! It seems obvious: the Duomo has concrete, the park has trees.<br><br>
            Our model says Physics (concrete/trees) explains 57.5% of the heat. Social Vulnerability (SVI) explains 18.8%.
            <b>What happens if we combine them?</b>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Physics Only', 'SVI Only'],
        y=[57.5, 18.8],
        marker_color=['#00d9ff', '#ffaa00'],
        text=['57.5%', '18.8%'], textposition='outside',
        textfont=dict(size=18, color='white', family='Courier New')
    ))
    fig.update_layout(
        title="Variance Explained (R²)",
        yaxis_title="R² (%)", yaxis_range=[0, 80],
        height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#00d9ff', family='Courier New')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    if not st.session_state.ch3_solved:
        guess = st.radio("▶ YOUR PREDICTION: If we add SVI to Physics, the R² will...", [
            "A) Increase massively (jump to ~76%)",
            "B) Barely move (stay around 57.6%)",
            "C) Decrease because of multicollinearity"
        ], index=None, key="predict_r2")
        
        if st.button("▶ TEST PREDICTION"):
            if guess and "B)" in guess:
                st.session_state.ch3_solved = True
                award_clue('illusion')
                st.rerun()
            elif guess:
                st.error("❌ **Incorrect.** Think: does a rich person's house heat up just because they have a higher income? No. Concrete does the heating.")
    else:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=['Physics Only', 'SVI Only', 'Physics + SVI'],
            y=[57.5, 18.8, 57.6],
            marker_color=['#00d9ff', '#ffaa00', '#00ff88'],
            text=['57.5%', '18.8%', '57.6%'], textposition='outside',
            textfont=dict(size=18, color='white', family='Courier New')
        ))
        fig2.update_layout(
            title="Variance Explained (R²)", yaxis_title="R² (%)", yaxis_range=[0, 80],
            height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#00d9ff', family='Courier New')
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown('<div class="clue-unlocked"><div class="title">🔍 CLUE #2</div><div class="body">Social vulnerability doesn\'t directly cause heat. It\'s fully mediated by the physical environment.</div></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ DETECTIVE NOTE</div>
            <div class="text">
                Giving people money won't cool their neighborhoods. The heat is baked into the <b>bricks</b>. 
                But wait — if it's all about buildings, <i>which</i> specific group gets trapped in the hottest ones?
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("▶ FIND THE VULNERABLE GROUP"):
            advance()

# ============================================
# CH3: FACTOR ANALYSIS
# ============================================
elif st.session_state.chapter == 3:
    st.markdown("## 🔍 CHAPTER 3 // FACTOR ANALYSIS")
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ INCOMING TRANSMISSION</div>
        <div class="text">
            If concrete is the killer, who is forced to live in the worst of it?<br>
            We tested 8 social profiles. Most of our assumptions were dead wrong. Read the intel.
        </div>
    </div>
    <div class="terminal" style="border-left-color: #ffaa00;">
        <div class="tag" style="color: #ffaa00;">▶ RAW INTEL (FDR-CORRECTED)</div>
        <div class="text" style="font-size: 0.95rem;">
            • <b>Elderly (65+):</b> Coef = -0.030 (They live in the cool historic center)<br>
            • <b>Foreign nationals:</b> p-value = 0.14 (False positive)<br>
            • <b>Unemployed:</b> Coef = -0.042 (Live in green public housing)<br>
            • <b>Young males:</b> p-value = 0.82 (Not significant)<br><br>
            We need the factor that <b>survived the strict FDR test</b> and has a <b>positive coefficient</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    answer = st.radio("▶ SELECT YOUR HYPOTHESIS:", [
        "A) 👴 Elderly residents (65+)",
        "B) 🌍 Foreign nationals",
        "C) 🚪 One-person households (loneliness)",
        "D) 💼 Unemployed residents"
    ], key="quiz_ch2", index=None)
    
    if not st.session_state.ch2_solved:
        if st.button("▶ SUBMIT ANALYSIS"):
            if answer and "C)" in answer:
                st.session_state.ch2_solved = True
                award_clue('loneliness')
                st.rerun()
            else:
                st.error("❌ INCORRECT. Check the p-values and coefficients. The obvious answers are traps.")
    else:
        st.markdown('<div class="clue-unlocked"><div class="title">🔍 CLUE #3</div><div class="body">Loneliness: +0.083°C (p<0.0001) — strongest predictor</div></div>', unsafe_allow_html=True)
        
        factors = ['One-person\nhouseholds','Foreign\nnationals','Young\nmales','Old\nfemales','Old\nmales','Unemployed']
        coefs = [0.083, 0.029, 0.006, -0.008, -0.030, -0.042]
        colors = ['#00ff88' if c>0.02 else '#ff4444' if c<-0.02 else '#666' for c in coefs]
        fig = go.Figure(go.Bar(
            x=factors, y=coefs, marker_color=colors,
            text=[f'{c:+.3f}' for c in coefs], textposition='outside', textfont=dict(color='white', family='Courier New')
        ))
        fig.update_layout(
            title="🎯 FDR-Corrected Coefficients", yaxis_title="Δ°C per SD", height=380,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00d9ff', family='Courier New')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ DETECTIVE NOTE</div>
            <div class="text">
                It's not immigrants. It's not the unemployed. It's <b>isolation</b>. Single people trapped in tiny, top-floor apartments 
                with no one to check on them. But wait... is this a year-round problem?
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("▶ ANALYZE SEASONALITY"):
            advance()

# ============================================
# CH4: SEASONAL TRAP
# ============================================
# ============================================
# CH4: SEASONAL TRAP (Fixed UI & Winter added)
# ============================================
elif st.session_state.chapter == 4:
    st.markdown("## 🍂 CHAPTER 4 // THE SEASONAL TRAP")
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ INCOMING TRANSMISSION</div>
        <div class="text">
            We tracked the temperature gap across the entire year. Notice how the gap behaves.<br>
            In Winter, the gap disappears (or even reverses). But as the sun gets hotter, something dangerous happens.<br><br>
            <b>Task:</b> Select a season below to find the moment when the climate gap becomes truly lethal.
        </div>
    </div>
    <div class="objective">Find the most dangerous season to unlock Clue #4</div>
    """, unsafe_allow_html=True)
    
    # Данные для 4 сезонов (Зима добавлена)
    seasons_data = {
        'Winter': {'gap': -0.15, 'risk': 40, 'color': '#3498db', 'desc': "Heat gap vanishes. Cold risk is high, but it hits everyone equally."},
        'Spring': {'gap': 1.28, 'risk': 15, 'color': '#00ff88', 'desc': "Mild weather. Gap is small but present."},
        'Summer': {'gap': 2.35, 'risk': 85, 'color': '#ff4444', 'desc': "The gap DOUBLES. Heat becomes lethal."},
        'Autumn': {'gap': 1.50, 'risk': 25, 'color': '#ffaa00', 'desc': "Gap shrinks. But the damage is already done."}
    }
    
    # Заменяем слайдер на горизонтальные кнопки
    season = st.radio("▶ SELECT SEASON TO ANALYZE:", list(seasons_data.keys()), horizontal=True, index=1, key="season_radio")
    
    current_gap = seasons_data[season]['gap']
    current_risk = seasons_data[season]['risk']
    color = seasons_data[season]['color']
    desc = seasons_data[season]['desc']
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="text-align:center; padding:20px; background:rgba(0,20,40,0.7); border:2px solid {color}; border-radius:8px;">
            <div style="color:#b8c5d6; font-family:'Courier New'; font-size:0.8rem;">{season.upper()} TEMP GAP</div>
            <div style="color:{color}; font-size:3rem; font-weight:bold; font-family:'Courier New';">{current_gap:+.2f}°C</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        risk_color = '#ff4444' if current_risk > 50 else '#00d9ff'
        st.markdown(f"""
        <div style="text-align:center; padding:20px; background:rgba(0,20,40,0.7); border:2px solid {risk_color}; border-radius:8px;">
            <div style="color:#b8c5d6; font-family:'Courier New'; font-size:0.8rem;">{season.upper()} HEALTH RISK</div>
            <div style="color:{risk_color}; font-size:3rem; font-weight:bold; font-family:'Courier New';">{current_risk}/100</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Обновленный график с 4 сезонами
    fig = go.Figure()
    
    # Бар-чарт для температуры
    fig.add_trace(go.Bar(
        x=list(seasons_data.keys()), 
        y=[seasons_data[s]['gap'] for s in seasons_data],
        name='Temperature Gap (°C)', 
        marker_color=['#3498db', 'rgba(0,217,255,0.4)', 'rgba(0,217,255,0.4)', 'rgba(0,217,255,0.4)'],
        text=[f"{seasons_data[s]['gap']:+.2f}°C" for s in seasons_data], 
        textposition='outside',
        textfont=dict(color='white', family='Courier New')
    ))
    
    # Линия для риска здоровья (масштабированная)
    fig.add_trace(go.Scatter(
        x=list(seasons_data.keys()), 
        y=[seasons_data[s]['risk']/20 for s in seasons_data],
        name='Health Risk (scaled)', 
        mode='lines+markers', 
        line=dict(color='#ff4444', width=4), 
        marker=dict(size=12)
    ))
    
    fig.update_layout(
        title="Seasonal Amplification: Temperature vs Health Impact", 
        yaxis_title="Value", yaxis_range=[-1, 6],
        height=380, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
        font=dict(color='#00d9ff', family='Courier New'),
        legend=dict(font=dict(color='#00d9ff', family='Courier New'), bgcolor='rgba(0,0,0,0.5)')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Логика проверки
    if season == 'Summer':
        if not st.session_state.ch4_solved:
            st.warning(f"🚨 **CRITICAL ANOMALY DETECTED:** {desc}")
            if st.button("🔍 RECORD FINDINGS"):
                st.session_state.ch4_solved = True
                award_clue('seasonal')
                st.rerun()
    else:
        st.info(f"ℹ️ **Analysis for {season}:** {desc} Look for the season where the red line spikes.")
    
    if st.session_state.ch4_solved:
        st.markdown('<div class="clue-unlocked"><div class="title">🔍 CLUE #4</div><div class="body">Summer gap (2.35°C) is nearly 2x spring gap (1.28°C). Heat becomes lethal.</div></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ DETECTIVE NOTE</div>
            <div class="text">
                Climate inequality is a summer time-bomb. It lies dormant in Winter, but strikes exactly when the heat becomes lethal. 
                But heat isn't the only thing choking these neighborhoods. Let's look at the air itself.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("▶ TRACE THE AIR POLLUTION"):
            advance()

# ============================================
# CH5: DOUBLE BURDEN (NO2)
# ============================================
elif st.session_state.chapter == 5:
    st.markdown("## 🏭 CHAPTER 5 // THE DOUBLE BURDEN")
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ INCOMING TRANSMISSION</div>
        <div class="text">
            Heat is one threat. <span class="highlight">Air pollution (NO2)</span> is another. We merged NASA's Sentinel-5P satellite data.<br><br>
            <span class="highlight">Toggle between the two layers below.</span> Look closely at the North of Milan.
        </div>
    </div>
    <div class="objective">Compare the two layers to unlock Clue #5</div>
    """, unsafe_allow_html=True)
    
    has_no2 = 'no2' in gdf.columns
    
    if not has_no2:
        st.warning("⚠️ NO2 data not found in app_data.geojson.")
    else:
        map_choice = st.radio("SELECT DATA LAYER:", ["🌡️ Heat (LST)", "💨 Pollution (NO2)"], horizontal=True)
        color_col = 'mean_lst' if "Heat" in map_choice else 'no2'
        
        gdf['hover_text'] = gdf.apply(lambda r: f"🌡️ {r['mean_lst']:.1f}°C | 💨 NO2: {r['no2']:.3f}", axis=1)
        
        fig = go.Figure(go.Scattermap(
            lat=gdf['cy'], lon=gdf['cx'], mode='markers',
            marker=dict(
                size=6, color=gdf[color_col], colorscale='Inferno' if color_col == 'no2' else 'YlOrRd',
                showscale=True, colorbar=dict(title="NO2" if color_col == 'no2' else "Temp (°C)", thickness=12, x=1.0)
            ),
            text=gdf['hover_text'],
            hovertemplate="%{text}<extra></extra>"
        ))
        fig.update_layout(
            map=dict(style="carto-darkmatter", center=dict(lat=45.4642, lon=9.19), zoom=10.5),
            height=400, margin=dict(l=0,r=0,t=0,b=0), showlegend=False, paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        if st.button("🔍 I SEE THE OVERLAP (RECORD FINDINGS)"):
            award_clue('double_burden')
            st.session_state.no2_revealed = True
            st.rerun()
            
        if st.session_state.no2_revealed:
            st.markdown('<div class="clue-unlocked"><div class="title">🔍 CLUE #5</div><div class="body">Heat + NO2 overlap in North Milan — compounding health crisis</div></div>', unsafe_allow_html=True)
            
            st.markdown("""
            <div class="terminal">
                <div class="tag">▶ DETECTIVE NOTE</div>
                <div class="text">
                    These residents are fighting two wars at once: lethal heat and respiratory risk. 
                    Where does all this heat come from? Our physical model says concrete explains 57%. What about the rest?
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("▶ HUNT THE ANOMALIES"):
                advance()

# ============================================
# CH6: ANOMALY HUNT
# ============================================
elif st.session_state.chapter == 6:
    st.markdown("## 🏭 CHAPTER 6 // ANOMALY HUNT")
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ INCOMING TRANSMISSION</div>
        <div class="text">
            Our physics model explains 57.5% of the heat. But in 255 spots, the real temperature is 5-7°C hotter than concrete predicts.<br><br>
            <b>Task:</b> Check the box below to reveal industrial zones. Watch how the red anomalies align with them.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    anomalies = gdf[gdf['residuals'] > 2]
    
    show_industry = st.checkbox("🏭 SHOW INDUSTRIAL ZONES OVERLAY")
    
    fig = go.Figure()
    fig.add_trace(go.Scattermap(lat=gdf['cy'], lon=gdf['cx'], mode='markers', marker=dict(size=2, color='rgba(100,100,100,0.2)'), hoverinfo='skip', showlegend=False))
    
    fig.add_trace(go.Scattermap(
        lat=anomalies['cy'], lon=anomalies['cx'], mode='markers', 
        marker=dict(size=8, color='#ff4444', opacity=0.9), 
        name='Heat Anomalies',
        text=["+5 to +7°C Hotter than predicted"] * len(anomalies),
        hovertemplate="<b>Anomaly</b><br>%{text}<extra></extra>"
    ))
    
    if show_industry:
        industrial_zones = gdf[(gdf['residuals'] > 2) & (gdf['impervious_x'] > gdf['impervious_x'].median())]
        fig.add_trace(go.Scattermap(
            lat=industrial_zones['cy'], lon=industrial_zones['cx'], mode='markers',
            marker=dict(size=18, color='rgba(0, 217, 255, 0.4)'),
            name='Industrial Overlay',
            text=["Industrial Zone"] * len(industrial_zones),
            hovertemplate="<b>%{text}</b><extra></extra>"
        ))
    
    fig.update_layout(
        map=dict(style="carto-darkmatter", center=dict(lat=45.4642, lon=9.19), zoom=10.5),
        height=400, margin=dict(l=0,r=0,t=0,b=0), 
        legend=dict(font=dict(color='#00d9ff', family='Courier New'), bgcolor='rgba(0,0,0,0.5)'), 
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    if show_industry and not st.session_state.overlay_run:
        st.success("👀 **See the pattern?** The red dots align almost perfectly with the industrial zones.")
        if st.button("▶ ANALYZE OVERLAP"):
            st.session_state.overlay_run = True
            award_clue('industry')
            st.rerun()
            
    if st.session_state.overlay_run:
        st.markdown('<div class="clue-unlocked"><div class="title">🔍 CLUE #6</div><div class="body">59.2% of anomalies in industrial zones (4.3x baseline)</div></div>', unsafe_allow_html=True)
        
        fig2 = go.Figure(go.Bar(
            x=['All Tracts','Heat Anomalies'], y=[13.9, 59.2], marker_color=['#666','#ff4444'],
            text=['13.9%','59.2%'], textposition='outside', textfont=dict(size=24, color='white', family='Courier New')
        ))
        fig2.update_layout(
            title="🏭 INDUSTRIAL ZONE OVERLAP — 4.3x concentration", yaxis_title="% touching industrial zones", yaxis_range=[0,70],
            height=320, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00d9ff', family='Courier New')
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ DETECTIVE NOTE</div>
            <div class="text">
                Industry is an invisible oven. Logistics hubs, factories, dark roofs. Now we know the enemy. 
                So, let's fix it. Let's plant trees, right?
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("▶ SIMULATE TREE PLANTING"):
            advance()

# ============================================
# CH7: TREE TRAP
# ============================================
elif st.session_state.chapter == 7:
    st.markdown("## 🌳 CHAPTER 7 // THE TREE TRAP")
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ INCOMING TRANSMISSION</div>
        <div class="text">
            The obvious solution: plant trees in poor neighborhoods. Let's simulate a massive tree-planting campaign.<br><br>
            <b>Task:</b> Move the slider to allocate the tree budget. Watch what happens to the temperature model.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    trees = st.slider("🌱 Select Tree Budget (Trees to Plant):", 0, 1000, 0, 50)
    
    base_temp = 48.67
    simulated_temp = base_temp + (0.04 * (trees / 1000)) 
    
    fig = go.Figure(go.Bar(
        x=['Current Temp', 'After Planting'], y=[base_temp, simulated_temp], 
        marker_color=['#666','#ff4444'],
        text=[f'{base_temp:.2f}°C', f'{simulated_temp:.2f}°C'], textposition='outside', 
        textfont=dict(size=20, color='white', family='Courier New')
    ))
    fig.update_layout(
        title=f"🌳 SIMULATION: {trees} Trees Planted", yaxis_title="Mean LST (°C)", yaxis_range=[48,49.2],
        height=320, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00d9ff', family='Courier New')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    if trees >= 500 and not st.session_state.tree_explored:
        if st.button("▶ ANALYZE PARADOX"):
            st.session_state.tree_explored = True
            award_clue('tree_trap')
            st.rerun()
            
    if st.session_state.tree_explored:
        st.markdown('<div class="clue-unlocked"><div class="title">🔍 CLUE #7</div><div class="body">Trees: +0.04°C. Temperature INCREASES due to data ceiling</div></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ THE ECO-STRUCTURAL LOCK</div>
            <div class="text">
                <span class="highlight">64.3%</span> of poor tracts are already at the maximum tree-cover value in the data. 
                The metric is saturated. You cannot "plant your way" out of this. We need to change the materials.<br><br>
                <b>Cool Roofs</b> (reflective paint) drop the temperature by <span class="highlight">-0.36°C</span>. 
                But the effect of vulnerability isn't the same everywhere. Let's zoom in.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("▶ ANALYZE LOCAL ANOMALIES"):
            advance()

# ============================================
# CH8: GWR (LOCAL ANOMALIES)
# ============================================
elif st.session_state.chapter == 8:
    st.markdown("## 🗺️ CHAPTER 8 // LOCAL ANOMALIES (GWR)")
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ INCOMING TRANSMISSION</div>
        <div class="text">
            We ran a Geographically Weighted Regression. The global effect of vulnerability is small (+0.047°C). 
            But locally, it explodes.<br><br>
            <b>Task:</b> Click on a <span style="color:#ff4444;">DARK RED</span> dot on the map to see where vulnerability hurts the most.
        </div>
    </div>
    <div class="objective">Click a red dot on the map to unlock Clue #8</div>
    """, unsafe_allow_html=True)
    
    if 'gwr_svi' not in gdf.columns or gdf['gwr_svi'].isna().all():
        st.error("⚠️ GWR data missing. Check gwr_coefs.csv.")
        if st.button("▶ SKIP TO CHAPTER 9"): advance()
    else:
        gdf['gwr_hover'] = gdf['gwr_svi'].apply(lambda x: f"Local Heat Effect: {x:+.2f}°C")
        
        fig = go.Figure(go.Scattermap(
            lat=gdf['cy'], lon=gdf['cx'], mode='markers',
            marker=dict(
                size=8, color=gdf['gwr_svi'], colorscale='RdBu_r', cmin=-2, cmax=2,
                showscale=True, colorbar=dict(title="Local SVI Effect (°C)", thickness=12)
            ),
            text=gdf['gwr_hover'],
            customdata=gdf['gwr_svi'],
            hovertemplate="<b>%{text}</b><br>(Click me!)<extra></extra>"
        ))
        fig.update_layout(
            map=dict(style="carto-darkmatter", center=dict(lat=45.4642, lon=9.19), zoom=10.5),
            height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)'
        )
        
        event = st.plotly_chart(fig, on_select="rerun", selection_mode="points", use_container_width=True, key="gwr_map")
        
        if event and event.get("selection", {}).get("points"):
            idx = event.selection.points[0]['point_index']
            tract = gdf.iloc[idx]
            st.info(f"📍 **Zone Investigated** — Local Effect: **{tract['gwr_svi']:+.2f}°C**")
            if not st.session_state.gwr_explored:
                st.session_state.gwr_explored = True
                award_clue('gwr')
                st.rerun()

        if st.session_state.gwr_explored:
            st.markdown('<div class="clue-unlocked"><div class="title">🔍 CLUE #8</div><div class="body">Vulnerability effect ranges from -1.9°C to +1.8°C locally!</div></div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="terminal">
                <div class="tag">▶ INSIGHT</div>
                <div class="text">
                    A single global model hides the truth. In the North-West, vulnerability makes heat 
                    <span class="highlight">much worse (+1.8°C)</span>. But in some southern green areas, 
                    dense old buildings provide shade, and vulnerability actually correlates with cooler spots.<br><br>
                    But wait. What happens on the absolute worst days? The days when people actually die?
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("▶ ANALYZE EXTREMES"):
                advance()

# ============================================
# CH9: QUANTILE REGRESSION
# ============================================
elif st.session_state.chapter == 9:
    st.markdown("## 📈 CHAPTER 9 // EXTREME HEAT (QUANTILE)")
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ INCOMING TRANSMISSION</div>
        <div class="text">
            Normal regression predicts the average day. But climate change is about extremes.<br><br>
            <b>Task:</b> Drag the slider to <span class="highlight">0.95 (Extreme Heat)</span> to see how the effect of vulnerability changes.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    q = st.slider("▶ Select Quantile of Temperature:", 0.1, 0.95, 0.5, 0.05)
    
    svi_effect = 0.0077 if q < 0.5 else 0.0343 if q < 0.75 else 0.0642 if q < 0.9 else 0.0791
    
    if q >= 0.9:
        st.markdown(f"### 🔥 Current Mode: **EXTREME HEAT (Q={q:.2f})** — Effect: **{svi_effect:+.3f}°C**")
    else:
        st.markdown(f"### ☀️ Current Mode: **NORMAL DAY (Q={q:.2f})** — Effect: **{svi_effect:+.3f}°C**")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95], y=[0.029, 0.021, 0.0077, 0.0343, 0.0642, 0.0791], mode='lines+markers', line=dict(color='#ff4444', width=4), name='SVI Effect'))
    fig.add_trace(go.Scatter(x=[q], y=[svi_effect], mode='markers', marker=dict(size=20, color='#00ff88'), name='Current'))
    fig.update_layout(
        title="Effect of Vulnerability Across the Temperature Distribution",
        xaxis_title="Quantile (0.5 = Median, 0.95 = Extreme Heat)",
        yaxis_title="SVI Coefficient (°C per SD)",
        height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00d9ff', family='Courier New')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    if q >= 0.9 and not st.session_state.ch8_solved:
        st.session_state.ch8_solved = True
        award_clue('quantile')
        st.rerun()
    
    if st.session_state.ch8_solved:
        st.markdown('<div class="clue-unlocked"><div class="title">🔍 CLUE #9</div><div class="body">Vulnerability effect grows 10x in extreme heat (0.95 quantile)!</div></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ DETECTIVE NOTE</div>
            <div class="text">
                Vulnerability is a "disaster multiplier". It lies dormant on mild days, but explodes during a heatwave. 
                We're almost done. There's one last thing you need to see. The map is lying to us.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("▶ REVEAL THE HIDDEN MAP"):
            advance()
    else:
        st.info("👆 Move the slider to 0.90 or above to see the extreme heat effect.")

# ============================================
# CH10: INVISIBLE MAJORITY (BIVARIATE LISA) - FULLY REDESIGNED
# ============================================
elif st.session_state.chapter == 10:
    st.markdown("## 👥 CHAPTER 10 // THE INVISIBLE MAJORITY")
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ FINAL TRANSMISSION</div>
        <div class="text">
            We mapped the <b>Bivariate LISA</b> (Local Indicators of Spatial Association). This tells us where Heat and Vulnerability overlap.<br><br>
            🔴 <b>Red:</b> High Heat + High Vulnerability (Obvious targets)<br>
            🟠 <b>Orange:</b> Low Heat + High Vulnerability (The Hidden Ones)<br>
            🔵 <b>Blue:</b> Low Heat + Low Vulnerability (Safe zones)<br><br>
            <span class="highlight">Click on an ORANGE dot to reveal the trap.</span>
        </div>
    </div>
    <div class="objective">Click an orange dot to unlock Clue #10</div>
    """, unsafe_allow_html=True)
    
    if 'biv_cat' not in gdf.columns:
        st.warning("⚠️ Bivariate LISA data not found.")
        if st.button("▶ CLOSE THE CASE"): advance()
    else:
        # Filter only the most important 3 categories to remove clutter
        key_cats = ['High Heat + High Vuln', 'Low Heat + High Vuln', 'Low Heat + Low Vuln']
        colors_map = {
            'High Heat + High Vuln': '#e74c3c',
            'Low Heat + High Vuln': '#f39c12',
            'Low Heat + Low Vuln': '#3498db'
        }
        
        fig = go.Figure()
        for cat in key_cats:
            sub = gdf[gdf['biv_cat'] == cat]
            if not sub.empty:
                hover_text = f"<b>{cat}</b><br>Click to investigate" if "Orange" not in cat else f"<b>{cat}</b><br>Click to investigate (Target!)"
                fig.add_trace(go.Scattermap(
                    lat=sub['cy'], lon=sub['cx'], mode='markers',
                    marker=dict(size=12 if cat == 'Low Heat + High Vuln' else 8, # Make orange dots bigger
                                color=colors_map[cat],
                                line=dict(width=1, color='white') if cat == 'Low Heat + High Vuln' else None), 
                    name=cat,
                    text=[hover_text] * len(sub), hovertemplate="%{text}<extra></extra>"
                ))
        
        fig.update_layout(
            map=dict(style="carto-darkmatter", center=dict(lat=45.4642, lon=9.19), zoom=10.5),
            height=450, margin=dict(l=0,r=0,t=0,b=0),
            legend=dict(font=dict(color='#00d9ff', family='Courier New'), bgcolor='rgba(0,0,0,0.8)', title="Heat vs Vulnerability"),
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        event = st.plotly_chart(fig, on_select="rerun", selection_mode="points", use_container_width=True, key="lisa_map")
        
        if event and event.get("selection", {}).get("points"):
            idx = event.selection.points[0]['point_index']
            # Since we filtered the dataframe, point_index refers to the new filtered trace.
            # We need to find which trace it was and get the correct data.
            try:
                point = event.selection.points[0]
                curve_number = point['curve_number']
                cat_name = key_cats[curve_number]
                sub_df = gdf[gdf['biv_cat'] == cat_name]
                tract = sub_df.iloc[point['point_index']]
                
                if tract['biv_cat'] == 'Low Heat + High Vuln':
                    st.warning(f"⚠️ **Warning**: Low Heat, but HIGH Vulnerability! These people are invisible to heat policies.")
                    if not st.session_state.lisa_explored:
                        st.session_state.lisa_explored = True
                        award_clue('lisa')
                        st.rerun()
                elif tract['biv_cat'] == 'High Heat + High Vuln':
                    st.error(f"❌ **Target missed**: This is a Red zone. High heat AND high vulnerability. We already know about these. Look for the ORANGE dots.")
                elif tract['biv_cat'] == 'Low Heat + Low Vuln':
                    st.info(f"✅ **Safe Zone**: Low heat, low vulnerability. No action needed here. Look for the ORANGE dots.")
            except Exception as e:
                st.error("Please click directly on a colored dot.")

        if st.session_state.lisa_explored:
            st.markdown('<div class="clue-unlocked"><div class="title">🔍 CLUE #10</div><div class="body">687 tracts of vulnerable people live in "cool" areas. Policy targeting only hot zones will miss them!</div></div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="terminal">
                <div class="tag">▶ THE PARADOX</div>
                <div class="text">
                    The Red zones (589 tracts) are the obvious target. But the <span class="highlight">Orange zones 
                    (687 tracts)</span> are the invisible majority. These are highly vulnerable people who don't 
                    show up on heat maps.<br><br>
                    By relying only on temperature, the city leaves <span class="highlight">thousands of vulnerable 
                    residents without help</span>. This is the fatal flaw in standard climate policy.
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("▶ CLOSE THE CASE"):
                advance()

# ============================================
# CH11: CASE CLOSED
# ============================================
elif st.session_state.chapter >= 11:
    st.balloons()
    
    st.markdown("""
    <div style="text-align:center; padding: 30px 20px;">
        <div style="font-size: 6rem; filter: drop-shadow(0 0 30px #ffaa00);">🏆</div>
        <div style="color:#00ff88; font-family:'Courier New'; letter-spacing:8px; font-size:0.85rem;">MISSION COMPLETE</div>
        <h1 style="font-size:3rem; letter-spacing:5px;">CASE CLOSED</h1>
        <div style="color:#ffaa00; font-family:'Courier New'; letter-spacing:5px; font-size:0.85rem;">CLASSIFICATION: DECLASSIFIED</div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Evidence Collected", f"{len(st.session_state.evidence)}/10")
    c2.metric("Final Rank", "🕵️ MASTER DETECTIVE")
    c3.metric("Model MAPE", "2.01%")
    
    st.markdown("---")
    st.markdown("### ⚖️ FINAL REPORT")
    
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ MISSION COMMANDER'S REPORT</div>
        <div class="text">
            Agent, your investigation reveals the anatomy of climate inequality in Milan:<br><br>
            • Heat differs by <span class="highlight">6.87°C</span> across 300m.<br>
            • Physics (concrete/trees) explains <span class="highlight">57.5%</span> of heat. SVI alone is just a proxy.<br>
            • <span class="highlight">Loneliness</span>, not poverty, is the real face of vulnerability (+0.083°C).<br>
            • The gap <span class="highlight">doubles in summer</span> (2.35°C vs 1.28°C).<br>
            • <span class="highlight">59.2%</span> of anomalies come from industrial zones.<br>
            • Trees are trapped by the <span class="highlight">data ceiling</span> (+0.04°C).<br>
            • The local effect of vulnerability ranges from <span class="highlight">-1.9°C to +1.8°C</span> (GWR).<br>
            • In extreme heat (95th percentile), vulnerability effect <span class="highlight">grows 10x</span>.<br>
            • <span class="highlight">687 tracts</span> of vulnerable people live in "cool" zones missed by heat policies.<br><br>
            <span style="color:#00ff88;">IMPACT: Using GHSL data, 1,253,569 people live in Milan. 
            ~571,146 people are in at least 1 risk zone.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hackathon Alignment section
    st.markdown("### 🎯 HACKATHON ALIGNMENT (Earth System Trend Detective)")
    st.markdown("""
    <div class="terminal" style="border-color: #9b59b6;">
        <div class="tag" style="color: #9b59b6;">▶ HOW WE ANSWERED THE CHALLENGE</div>
        <div class="text">
            1. <b>Time Series:</b> We fused 10 years of Landsat data and 24 years of MODIS data to prove the gap is widening.<br>
            2. <b>Anomaly Detection:</b> We used Random Forest residuals to find hidden heat sources (Industrial zones).<br>
            3. <b>Social Integration:</b> We used FDR-corrected regressions and Bivariate LISA to map the "Invisible Majority".<br>
            4. <b>Actionable Output:</b> We provide a Top-3 target list for immediate intervention.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🚨 ACCESS CLASSIFIED FILE: TARGET #1"):
        st.markdown("""
        <div class="terminal" style="border-color: #ff4444;">
            <div class="tag" style="color: #ff4444;">▶ TOP PRIORITY TARGET: TRACT 151460001206</div>
            <div class="text">
                • <b>Temperature:</b> 53.4°C (Lethal)<br>
                • <b>Vulnerability:</b> 2.60 (High)<br>
                • <b>Anomaly:</b> +3.76°C (Hotter than concrete predicts)<br>
                • <b>Profile:</b> High concentration of single-person households, proximity to heavy logistics hubs.<br><br>
                <i>Commander's Note: If we cool this one tract, we save hundreds of lives.</i>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 REPLAY MISSION"):
            for k in list(defaults.keys()):
                st.session_state[k] = defaults[k]
            st.rerun()
    with col2:
        st.markdown("""
        <a href="https://github.com/marybilik" target="_blank" style="text-decoration:none;">
            <div style="background:#00d9ff; color:#050814; padding:14px; border-radius:4px; text-align:center; font-weight:bold; cursor:pointer; font-family:'Courier New'; letter-spacing:2px;">
                📂 VIEW FULL NOTEBOOK
            </div>
        </a>
        """, unsafe_allow_html=True)

# ============================================
# PERSISTENT EVIDENCE LOG
# ============================================
if len(st.session_state.evidence) > 0 and st.session_state.chapter < 11:
    st.markdown(f"""
    <div class="evidence-log">
        <div class="header">▶ EVIDENCE LOG ({len(st.session_state.evidence)}/10)</div>
        {''.join([f'<span class="evidence-item">🔍 {k}</span>' for k in st.session_state.evidence])}
    </div>
    """, unsafe_allow_html=True)
