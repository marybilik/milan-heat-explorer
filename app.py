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
    
    # Drop NaNs for clean maps
    gdf = gdf.dropna(subset=['cx', 'cy'])
    
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
    'ch1_step': 0, 'ch2_step': 0, 'ch3_step': 0, 'ch4_step': 0,
    'clicked_duomo': False, 'clicked_park': False, 
    'ch1_quiz': False, 'ch2_quiz': False, 'ch3_quiz': False,
    'ch4_lisa_solved': False
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

CHAPTERS = ["THE CRIME SCENE","THE TIME BOMB","THE INVISIBLE ENEMY","THE HOTSPOTS","THE INVISIBLE MAJORITY","CASE CLOSED"]

# ============================================
# STATUS BAR
# ============================================
if 0 < st.session_state.chapter <= 5:
    ch = int(st.session_state.chapter)
    rank = "CADET" if len(st.session_state.evidence) < 3 else "ANALYST" if len(st.session_state.evidence) < 6 else "MASTER"
    st.markdown(f"""
    <div class="mission-header">
        <div><span class="label">🛰️ MISSION:</span> <span class="val">MILAN HEAT</span></div>
        <div><span class="label">PHASE:</span> <span class="val">{ch}/5 // {CHAPTERS[ch-1]}</span></div>
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
    
    <div class="terminal" style="max-width:800px; margin:30px auto;">
        <div class="tag">▶ MISSION BRIEFING</div>
        <div class="text">
            Agent, Milan is experiencing a lethal heatwave. Surface temperatures hit <b>56°C</b>. 
            But our satellites show the heat is <span class="highlight">not distributed equally</span>.<br><br>
            We have 5 phases to solve this case. We will use NASA Landsat, MODIS, Sentinel-5P, 
            and machine learning to uncover <span class="highlight">who</span> is dying — and <span class="highlight">why</span>.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    _, col_btn, _ = st.columns([1, 1, 1])
    with col_btn:
        if st.button("▶ INITIATE MISSION", use_container_width=True):
            advance()

# ============================================
# CH1: THE CRIME SCENE (Duomo + R² + Loneliness)
# ============================================
elif st.session_state.chapter == 1:
    st.markdown("## 📍 PHASE 1 // THE CRIME SCENE")
    
    if st.session_state.ch1_step == 0:
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ ACTION REQUIRED</div>
            <div class="text">Click on the <b>DUOMO</b> (concrete) and <b>PARCO SEMPIONE</b> (trees) on the map to measure the gap.</div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure()
        fig.add_trace(go.Scattermap(
            lat=[45.464], lon=[9.191], mode='markers+text',
            marker=dict(size=40 if st.session_state.clicked_duomo else 30, color='#00ff88' if st.session_state.clicked_duomo else '#ff4444'),
            text=['🔴 DUOMO ✓' if st.session_state.clicked_duomo else '🔴 DUOMO'], textposition='top center',
            customdata=['duomo'], hovertemplate='<b>DUOMO</b><br>Click to measure<extra></extra>'
        ))
        fig.add_trace(go.Scattermap(
            lat=[45.472], lon=[9.179], mode='markers+text',
            marker=dict(size=40 if st.session_state.clicked_park else 30, color='#00ff88'),
            text=['🟢 PARK ✓' if st.session_state.clicked_park else '🟢 PARK'], textposition='top center',
            customdata=['park'], hovertemplate='<b>PARK</b><br>Click to measure<extra></extra>'
        ))
        fig.update_layout(map=dict(style="carto-darkmatter", center=dict(lat=45.468, lon=9.185), zoom=14), height=350, margin=dict(l=0,r=0,t=0,b=0), showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
        
        event = st.plotly_chart(fig, on_select="rerun", selection_mode="points", use_container_width=True, key="ch1_map")
        if event and event.get("selection", {}).get("points"):
            for p in event.selection.points:
                cd = p.get('customdata')
                if cd == 'duomo': st.session_state.clicked_duomo = True; st.rerun()
                if cd == 'park': st.session_state.clicked_park = True; st.rerun()
                
        if st.session_state.clicked_duomo and st.session_state.clicked_park:
            award_clue('gap')
            st.session_state.ch1_step = 1
            st.rerun()

    elif st.session_state.ch1_step == 1:
        st.markdown("""
        <div class="terminal" style="border-color: #ffaa00;">
            <div class="tag" style="color: #ffaa00;">▶ CLUE #1: THE 7°C GAP</div>
            <div class="text">
                A 6.87°C difference in 300 meters! Physics (concrete) explains 57.5% of heat. Social Vulnerability (SVI) explains 18.8%.<br><br>
                <b>What happens if we combine them?</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(go.Bar(x=['Physics', 'SVI'], y=[57.5, 18.8], marker_color=['#00d9ff', '#ffaa00'], text=['57.5%', '18.8%'], textposition='outside'))
        fig.update_layout(title="Variance Explained (R²)", yaxis_range=[0, 80], height=250, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00d9ff'))
        st.plotly_chart(fig, use_container_width=True)
        
        guess = st.radio("▶ YOUR PREDICTION: If we add SVI to Physics, the R² will...", [
            "A) Jump to ~76%", "B) Barely move (~57.6%)"
        ], index=None)
        
        if st.button("▶ SUBMIT PREDICTION"):
            if guess and "B)" in guess:
                st.session_state.ch1_quiz = True
                award_clue('illusion')
                st.session_state.ch1_step = 2
                st.rerun()
            else:
                st.error("❌ Incorrect. Money doesn't heat bricks. Concrete does.")

    elif st.session_state.ch1_step == 2:
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ CLUE #2: THE ILLUSION</div>
            <div class="text">
                Correct! Physics is the killer. But if concrete causes the heat, <b>who</b> is forced to live in the worst of it?<br>
                We tested 8 social factors with FDR correction. Read the intel:
            </div>
        </div>
        <div class="terminal" style="border-left-color: #ffaa00;">
            <div class="text" style="font-size: 0.9rem;">
                • Elderly: -0.030 (Cool center)<br>
                • Foreigners: p=0.14 (False positive)<br>
                • Unemployed: -0.042 (Public housing)<br>
                • Young males: p=0.82 (Not significant)<br>
                • <b>One-person households (loneliness): +0.083 (p<0.0001)</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        ans = st.radio("▶ SELECT THE VULNERABLE GROUP:", [
            "A) Elderly", "B) Foreigners", "C) Lonely (One-person households)", "D) Unemployed"
        ], index=None)
        
        if st.button("▶ SUBMIT ANALYSIS"):
            if ans and "C)" in ans:
                award_clue('loneliness')
                st.success("✅ Correct. Loneliness is the hidden face of heat.")
                st.session_state.ch2_step = 1
                st.session_state.ch1_step = 3
                st.rerun()
            else:
                st.error("❌ Check the FDR values. The obvious answers are traps.")
                
    elif st.session_state.ch1_step == 3:
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ CLUE #3: THE LONELY TRAP</div>
            <div class="text">
                Single people are trapped in small, top-floor apartments with no social network. 
                But wait... is this a year-round problem?
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("▶ ANALYZE SEASONALITY"):
            advance()

# ============================================
# CH2: THE TIME BOMB (Seasons + NO2)
# ============================================
elif st.session_state.chapter == 2:
    st.markdown("## 🍂 PHASE 2 // THE TIME BOMB")
    
    if st.session_state.ch2_step == 0:
        st.session_state.ch2_step = 1 # Skip to season
        
    if st.session_state.ch2_step == 1:
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ ACTION REQUIRED</div>
            <div class="text">We tracked the gap across the year. Select the season where the gap becomes lethal.</div>
        </div>
        """, unsafe_allow_html=True)
        
        season = st.radio("▶ SELECT SEASON:", ['Winter', 'Spring', 'Summer', 'Autumn'], horizontal=True, index=1)
        
        gaps = {'Winter': -0.15, 'Spring': 1.28, 'Summer': 2.35, 'Autumn': 1.50}
        risks = {'Winter': 40, 'Spring': 15, 'Summer': 85, 'Autumn': 25}
        
        c1, c2 = st.columns(2)
        c1.metric(f"{season} Temp Gap", f"{gaps[season]:+.2f}°C")
        c2.metric(f"{season} Health Risk", f"{risks[season]}/100")
        
        if season == 'Summer':
            if st.button("🔍 RECORD LETHAL SEASON"):
                award_clue('seasonal')
                st.session_state.ch2_step = 2
                st.rerun()
        else:
            st.info("ℹ️ Look for the season where Health Risk spikes.")
            
    elif st.session_state.ch2_step == 2:
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ CLUE #4: THE SUMMER TRAP</div>
            <div class="text">
                Summer gap (2.35°C) is 2x Spring. Heat becomes lethal exactly when people need help.
                But heat isn't the only thing choking these neighborhoods. Let's look at the air.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        map_choice = st.radio("SELECT DATA LAYER:", ["🌡️ Heat (LST)", "💨 Pollution (NO2)"], horizontal=True)
        color_col = 'mean_lst' if "Heat" in map_choice else 'no2'
        
        plot_df = gdf.dropna(subset=[color_col]) if color_col == 'no2' else gdf
        
        fig = go.Figure(go.Scattermap(
            lat=plot_df['cy'], lon=plot_df['cx'], mode='markers',
            marker=dict(size=5, color=plot_df[color_col], colorscale='Inferno' if color_col == 'no2' else 'YlOrRd', showscale=True),
            hovertemplate="Value: %{marker.color:.2f}<extra></extra>"
        ))
        fig.update_layout(map=dict(style="carto-darkmatter", center=dict(lat=45.4642, lon=9.19), zoom=10.5), height=350, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
        if st.button("🔍 I SEE THE OVERLAP"):
            award_clue('double_burden')
            st.session_state.ch2_step = 3
            st.rerun()
            
    elif st.session_state.ch2_step == 3:
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ CLUE #5: DOUBLE BURDEN</div>
            <div class="text">
                North Milan suffers from both lethal heat and toxic air. 
                Where does all this heat come from? Our physical model says concrete explains 57%. What about the rest?
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("▶ HUNT THE ANOMALIES"):
            advance()

# ============================================
# CH3: THE INVISIBLE ENEMY (Anomalies + Trees)
# ============================================
elif st.session_state.chapter == 3:
    st.markdown("## 🏭 PHASE 3 // THE INVISIBLE ENEMY")
    
    if st.session_state.ch3_step == 0:
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ ACTION REQUIRED</div>
            <div class="text">In 255 spots, the real temperature is 5-7°C hotter than concrete predicts. Check the box to reveal industrial zones.</div>
        </div>
        """, unsafe_allow_html=True)
        
        show_industry = st.checkbox("🏭 SHOW INDUSTRIAL ZONES")
        anomalies = gdf[gdf['residuals'] > 2]
        
        fig = go.Figure()
        fig.add_trace(go.Scattermap(lat=gdf['cy'], lon=gdf['cx'], mode='markers', marker=dict(size=2, color='rgba(100,100,100,0.2)'), hoverinfo='skip', showlegend=False))
        fig.add_trace(go.Scattermap(lat=anomalies['cy'], lon=anomalies['cx'], mode='markers', marker=dict(size=8, color='#ff4444'), name='Anomalies'))
        
        if show_industry:
            ind = gdf[(gdf['residuals'] > 2) & (gdf['impervious_x'] > gdf['impervious_x'].median())]
            fig.add_trace(go.Scattermap(lat=ind['cy'], lon=ind['cx'], mode='markers', marker=dict(size=18, color='rgba(0,217,255,0.4)'), name='Industry'))
            
        fig.update_layout(map=dict(style="carto-darkmatter", center=dict(lat=45.4642, lon=9.19), zoom=10.5), height=350, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', legend=dict(font=dict(color='#00d9ff'), bgcolor='rgba(0,0,0,0.5)'))
        st.plotly_chart(fig, use_container_width=True)
        
        if show_industry:
            if st.button("▶ ANALYZE OVERLAP"):
                award_clue('industry')
                st.session_state.ch3_step = 1
                st.rerun()

    elif st.session_state.ch3_step == 1:
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ CLUE #6: THE INDUSTRIAL OVEN</div>
            <div class="text">
                59.2% of anomalies come from industrial zones. It's an invisible oven.<br>
                So let's fix it. Let's plant trees, right? Move the slider and watch the model.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        trees = st.slider("🌱 Tree Budget:", 0, 1000, 0, 50)
        base_temp = 48.67
        sim_temp = base_temp + (0.04 * (trees / 1000))
        
        fig = go.Figure(go.Bar(x=['Current', 'After Trees'], y=[base_temp, sim_temp], marker_color=['#666','#ff4444'], text=[f'{base_temp:.2f}°C', f'{sim_temp:.2f}°C'], textposition='outside'))
        fig.update_layout(title=f"Simulation: {trees} Trees", yaxis_range=[48, 49.2], height=250, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00d9ff'))
        st.plotly_chart(fig, use_container_width=True)
        
        if trees >= 500:
            if st.button("▶ ANALYZE PARADOX"):
                award_clue('tree_trap')
                st.session_state.ch3_step = 2
                st.rerun()
                
    elif st.session_state.ch3_step == 2:
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ CLUE #7: THE ECO-STRUCTURAL LOCK</div>
            <div class="text">
                64.3% of poor tracts are already at the maximum tree-cover value. You cannot "plant your way" out. 
                We need Cool Roofs (-0.36°C). But the effect isn't the same everywhere.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("▶ ANALYZE LOCAL ANOMALIES"):
            advance()

# ============================================
# CH4: THE HOTSPOTS (GWR + Quantile)
# ============================================
elif st.session_state.chapter == 4:
    st.markdown("## 🗺️ PHASE 4 // THE HOTSPOTS")
    
    if st.session_state.ch4_step == 0:
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ ACTION REQUIRED</div>
            <div class="text">We ran a Geographically Weighted Regression. Click on a DARK RED zone to see where vulnerability hurts most.</div>
        </div>
        """, unsafe_allow_html=True)
        
        plot_df = gdf.dropna(subset=['gwr_svi']).copy()
        fig = go.Figure(go.Scattermap(
            lat=plot_df['cy'], lon=plot_df['cx'], mode='markers',
            marker=dict(size=8, color=plot_df['gwr_svi'], colorscale='RdBu_r', cmin=-2, cmax=2, showscale=True),
            customdata=plot_df.index, hovertemplate="Click to investigate<extra></extra>"
        ))
        fig.update_layout(map=dict(style="carto-darkmatter", center=dict(lat=45.4642, lon=9.19), zoom=10.5), height=350, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)')
        
        event = st.plotly_chart(fig, on_select="rerun", selection_mode="points", use_container_width=True, key="gwr_map")
        
        if event and event.get("selection", {}).get("points"):
            point = event.selection.points[0]
            if 'customdata' in point:
                idx = point['customdata']
                val = gdf.loc[idx, 'gwr_svi']
                st.info(f"📍 Local Effect: **{val:+.2f}°C**")
                award_clue('gwr')
                st.session_state.ch4_step = 1
                st.rerun()

    elif st.session_state.ch4_step == 1:
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ CLUE #8: LOCAL ANOMALIES</div>
            <div class="text">
                The effect of vulnerability ranges from -1.9°C to +1.8°C locally. 
                But what happens on the absolute worst days? Move the slider to find out.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        q = st.slider("▶ Temperature Quantile:", 0.1, 0.95, 0.5, 0.05)
        effect = 0.0077 if q < 0.5 else 0.0343 if q < 0.75 else 0.0642 if q < 0.9 else 0.0791
        
        st.markdown(f"### Current Effect: **{effect:+.3f}°C**")
        if q >= 0.9:
            if st.button("▶ RECORD EXTREME HEAT"):
                award_clue('quantile')
                st.session_state.ch4_step = 2
                st.rerun()
        else:
            st.info("👆 Move slider to 0.90+")
            
    elif st.session_state.ch4_step == 2:
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ CLUE #9: DISASTER MULTIPLIER</div>
            <div class="text">
                In extreme heat (95th percentile), vulnerability effect grows 10x. It lies dormant, then explodes.
                We're almost done. There's one last thing you need to see. The map is lying to us.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("▶ REVEAL THE HIDDEN MAP"):
            advance()

# ============================================
# CH5: THE INVISIBLE MAJORITY (LISA)
# ============================================
elif st.session_state.chapter == 5:
    st.markdown("## 👥 PHASE 5 // THE INVISIBLE MAJORITY")
    
    if not st.session_state.ch4_lisa_solved:
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ ACTION REQUIRED</div>
            <div class="text">
                Bivariate LISA: 🔴 Red = High Heat + High Vuln. 🟠 Orange = Low Heat + High Vuln.<br>
                <b>Find and click on an ORANGE dot to reveal the trap.</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        plot_df = gdf.dropna(subset=['biv_cat']).copy()
        key_cats = ['High Heat + High Vuln', 'Low Heat + High Vuln', 'Low Heat + Low Vuln']
        colors = {'High Heat + High Vuln': '#e74c3c', 'Low Heat + High Vuln': '#f39c12', 'Low Heat + Low Vuln': '#3498db'}
        
        fig = go.Figure()
        for cat in key_cats:
            sub = plot_df[plot_df['biv_cat'] == cat]
            if not sub.empty:
                fig.add_trace(go.Scattermap(
                    lat=sub['cy'], lon=sub['cx'], mode='markers',
                    marker=dict(size=12 if 'Low Heat + High' in cat else 8, color=colors[cat]),
                    name=cat, customdata=sub.index, hovertemplate="Click to investigate<extra></extra>"
                ))
                
        fig.update_layout(map=dict(style="carto-darkmatter", center=dict(lat=45.4642, lon=9.19), zoom=10.5), height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', legend=dict(font=dict(color='#00d9ff'), bgcolor='rgba(0,0,0,0.8)'))
        
        event = st.plotly_chart(fig, on_select="rerun", selection_mode="points", use_container_width=True, key="lisa_map")
        
        if event and event.get("selection", {}).get("points"):
            point = event.selection.points[0]
            if 'customdata' in point:
                idx = point['customdata']
                cat = gdf.loc[idx, 'biv_cat']
                
                if cat == 'Low Heat + High Vuln':
                    award_clue('lisa')
                    st.warning("⚠️ **Correct!** Low Heat, but HIGH Vulnerability! These people are invisible to heat policies.")
                    st.session_state.ch4_lisa_solved = True
                    st.rerun()
                elif cat == 'High Heat + High Vuln':
                    st.error("❌ This is a Red zone. We already know about these. Look for the ORANGE dots.")
                else:
                    st.info("✅ Safe zone. No action needed. Look for the ORANGE dots.")
                    
    else:
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ CLUE #10: THE PARADOX</div>
            <div class="text">
                The Red zones (589 tracts) are the obvious target. But the <span class="highlight">Orange zones (687 tracts)</span> 
                are the invisible majority. These are highly vulnerable people who don't show up on heat maps.<br><br>
                By relying only on temperature, the city leaves thousands without help. This is the fatal flaw in climate policy.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("▶ CLOSE THE CASE"):
            advance()

# ============================================
# CH6: CASE CLOSED
# ============================================
elif st.session_state.chapter >= 6:
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
            • Physics (concrete/trees) explains <span class="highlight">57.5%</span> of heat.<br>
            • <span class="highlight">Loneliness</span>, not poverty, is the real face of vulnerability.<br>
            • The gap <span class="highlight">doubles in summer</span> (2.35°C vs 1.28°C).<br>
            • <span class="highlight">59.2%</span> of anomalies come from industrial zones.<br>
            • Trees are trapped by the <span class="highlight">data ceiling</span> (+0.04°C).<br>
            • Vulnerability effect <span class="highlight">grows 10x</span> in extreme heat.<br>
            • <span class="highlight">687 tracts</span> of vulnerable people live in "cool" zones missed by policies.<br><br>
            <span style="color:#00ff88;">IMPACT: ~571,146 people are in at least 1 risk zone.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 HACKATHON ALIGNMENT (Earth System Trend Detective)")
    st.markdown("""
    <div class="terminal" style="border-color: #9b59b6;">
        <div class="tag" style="color: #9b59b6;">▶ HOW WE ANSWERED THE CHALLENGE</div>
        <div class="text">
            1. <b>Time Series:</b> We fused 10 years of Landsat data (check the expander below).<br>
            2. <b>Anomaly Detection:</b> We used residuals to find hidden industrial ovens.<br>
            3. <b>Social Integration:</b> We used FDR and Bivariate LISA to map the Invisible Majority.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📈 VIEW 10-YEAR LANDSAT TREND (Time Series Requirement)"):
        if ts is not None:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ts['Year'], y=ts['Q1_Rich'], mode='lines+markers', name='Rich (Q1)', line=dict(color='#00ff88', width=4)))
            fig.add_trace(go.Scatter(x=ts['Year'], y=ts['Q4_Poor'], mode='lines+markers', name='Poor (Q4)', line=dict(color='#ff4444', width=4)))
            fig.update_layout(title="Landsat: Rich vs Poor Heat Gap", xaxis_title="Year", yaxis_title="LST (°C)", height=300, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00d9ff'))
            st.plotly_chart(fig, use_container_width=True)
            
    with st.expander("🚨 ACCESS CLASSIFIED FILE: TARGET #1"):
        st.markdown("""
        <div class="terminal" style="border-color: #ff4444;">
            <div class="tag" style="color: #ff4444;">▶ TOP PRIORITY TARGET: TRACT 151460001206</div>
            <div class="text">
                • <b>Temperature:</b> 53.4°C (Lethal)<br>
                • <b>Vulnerability:</b> 2.60 (High)<br>
                • <b>Anomaly:</b> +3.76°C<br>
                • <b>Profile:</b> Single-person households + Heavy logistics hubs.
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
if len(st.session_state.evidence) > 0 and st.session_state.chapter < 6:
    st.markdown(f"""
    <div class="evidence-log">
        <div class="header">▶ EVIDENCE LOG ({len(st.session_state.evidence)}/10)</div>
        {''.join([f'<span class="evidence-item">🔍 {k}</span>' for k in st.session_state.evidence])}
    </div>
    """, unsafe_allow_html=True)
