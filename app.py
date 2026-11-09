import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

st.set_page_config(page_title="NASA :: MILAN HEAT CASE", page_icon="🛰️", layout="wide", initial_sidebar_state="collapsed")

# ============================================
# NASA MISSION CONTROL CSS
# ============================================
st.markdown("""
<style>
    /* Global - Deep Space */
    .stApp { background: #050814; color: #b8c5d6; }
    h1, h2, h3, h4 { color: #00d9ff !important; font-family: 'Courier New', monospace; letter-spacing: 2px; }
    p, li, label, .stMarkdown, .stRadio label, .stSelectbox label { color: #b8c5d6 !important; font-family: 'Courier New', monospace; }
    
    /* Terminal Scan Line */
    .stApp::before {
        content: '';
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: repeating-linear-gradient(0deg, rgba(0, 217, 255, 0.03) 0px, rgba(0, 217, 255, 0.03) 1px, transparent 1px, transparent 4px);
        pointer-events: none; z-index: 9999;
    }
    
    /* Blinking cursor */
    @keyframes blink { 0%, 50% { opacity: 1; } 51%, 100% { opacity: 0; } }
    .cursor { animation: blink 1s infinite; color: #00ff88; }
    
    /* Typewriter effect */
    @keyframes typing {
        from { max-width: 0; }
        to { max-width: 100%; }
    }
    .typed { display: inline-block; overflow: hidden; white-space: nowrap; animation: typing 2s steps(60) forwards; vertical-align: bottom; }
    
    /* Mission header */
    .mission-header {
        background: linear-gradient(90deg, #0a1128, #001f3f);
        border: 1px solid #00d9ff;
        padding: 12px 20px; border-radius: 4px; margin-bottom: 20px;
        display: flex; justify-content: space-between; align-items: center;
        font-family: 'Courier New', monospace; font-size: 0.9rem;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.2);
    }
    .mission-header .label { color: #00ff88; }
    .mission-header .val { color: #00d9ff; font-weight: bold; }
    
    /* Terminal box */
    .terminal {
        background: rgba(0, 20, 40, 0.7);
        border-left: 3px solid #00d9ff;
        border-right: 3px solid #00d9ff;
        padding: 20px 25px; margin: 20px 0; border-radius: 4px;
        font-family: 'Courier New', monospace; font-size: 1rem; line-height: 1.7;
        box-shadow: inset 0 0 30px rgba(0, 217, 255, 0.05);
    }
    .terminal .tag { color: #ffaa00; font-weight: bold; letter-spacing: 3px; font-size: 0.85rem; }
    .terminal .text { color: #e0e8f0; margin-top: 10px; }
    .terminal .highlight { color: #00ff88; font-weight: bold; }
    
    /* Objective box */
    .objective {
        background: rgba(255, 170, 0, 0.1); border: 1px solid #ffaa00;
        padding: 15px 20px; border-radius: 4px; margin: 15px 0;
        font-family: 'Courier New', monospace;
    }
    .objective::before { content: '▸ OBJECTIVE: '; color: #ffaa00; font-weight: bold; }
    
    /* Clue found animation */
    @keyframes clueIn {
        0% { transform: scale(0.8); opacity: 0; box-shadow: 0 0 0 rgba(0,255,136,0); }
        50% { transform: scale(1.05); opacity: 1; box-shadow: 0 0 40px rgba(0,255,136,0.8); }
        100% { transform: scale(1); opacity: 1; box-shadow: 0 0 20px rgba(0,255,136,0.4); }
    }
    .clue-unlocked {
        animation: clueIn 0.8s ease-out;
        background: linear-gradient(90deg, rgba(0,255,136,0.15), rgba(0,217,255,0.15));
        border: 2px solid #00ff88; border-radius: 4px;
        padding: 18px 25px; margin: 20px 0;
        font-family: 'Courier New', monospace; text-align: center;
    }
    .clue-unlocked .title { color: #00ff88; font-weight: bold; letter-spacing: 4px; font-size: 0.85rem; }
    .clue-unlocked .body { color: #ffffff; font-size: 1.1rem; margin-top: 8px; }
    
    /* XP bar glow */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00ff88, #00d9ff) !important;
        box-shadow: 0 0 10px #00ff88 !important;
    }
    
    /* Buttons - NASA style */
    .stButton > button {
        background: transparent; color: #00d9ff !important;
        border: 2px solid #00d9ff; padding: 12px 30px;
        font-family: 'Courier New', monospace; font-weight: bold;
        letter-spacing: 3px; border-radius: 2px;
        transition: all 0.2s; text-transform: uppercase;
    }
    .stButton > button:hover {
        background: #00d9ff; color: #050814 !important;
        box-shadow: 0 0 30px rgba(0, 217, 255, 0.6);
    }
    
    /* Radio buttons */
    .stRadio > div { background: rgba(0,217,255,0.03); padding: 15px; border-radius: 4px; border: 1px solid rgba(0,217,255,0.2); }
    
    /* Big NASA logo/rank */
    .rank-badge { font-size: 5rem; text-align: center; filter: drop-shadow(0 0 20px #00d9ff); }
    
    /* Pulsing marker */
    @keyframes pulse { 0% { r: 20; opacity: 1; } 100% { r: 40; opacity: 0; } }
    
    /* Hide header/footer */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATA
# ============================================
@st.cache_data
def load_data():
    gdf = gpd.read_file("app_data.geojson")
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
# SESSION STATE
# ============================================
defaults = {
    'chapter': 0,
    'xp': 0,
    'evidence': [],
    'clicked_duomo': False,
    'clicked_park': False,
    'trend_run': False,
    'overlay_run': False,
    'intervention_done': False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def award_clue(key, xp):
    if key not in st.session_state.evidence:
        st.session_state.evidence.append(key)
        st.session_state.xp += xp

def advance():
    st.session_state.chapter += 1
    st.rerun()

# ============================================
# STATUS BAR (chapters 1-6)
# ============================================
if 0 < st.session_state.chapter <= 6:
    rank = "CADET" if st.session_state.xp < 200 else "ANALYST" if st.session_state.xp < 400 else "DETECTIVE"
    st.markdown(f"""
    <div class="mission-header">
        <div><span class="label">🛰️ NASA MISSION:</span> <span class="val">MILAN HEAT CASE</span></div>
        <div><span class="label">CHAPTER:</span> <span class="val">{int(st.session_state.chapter)}/6</span></div>
        <div><span class="label">RANK:</span> <span class="val">{rank}</span></div>
        <div><span class="label">EVIDENCE:</span> <span class="val">{len(st.session_state.evidence)}/6</span></div>
        <div><span class="label">XP:</span> <span class="val">{st.session_state.xp}</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(min(len(st.session_state.evidence)/6, 1.0))

# ============================================
# CHAPTER 0: LAUNCH SCREEN
# ============================================
if st.session_state.chapter == 0:
    st.markdown("""
    <div style="text-align:center; padding: 60px 20px;">
        <div style="font-size: 7rem; filter: drop-shadow(0 0 30px #00d9ff);">🛰️</div>
        <div style="color: #00ff88; font-family: 'Courier New'; letter-spacing: 8px; margin-top: 20px; font-size: 0.9rem;">NASA EARTH OBSERVATION SYSTEM</div>
        <h1 style="font-size: 3.5rem; letter-spacing: 6px; margin: 15px 0; color: #00d9ff; text-shadow: 0 0 20px #00d9ff;">THE MILAN<br>HEAT CASE</h1>
        <div style="color: #ffaa00; font-family: 'Courier New'; letter-spacing: 5px; font-size: 0.85rem;">CLASSIFICATION: SECRET // LEVEL 3</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="terminal" style="max-width: 700px; margin: 40px auto;">
        <div class="tag">▶ MISSION BRIEFING</div>
        <div class="text">
            <span class="typed">Agent, we have detected an anomaly.</span><span class="cursor">█</span><br><br>
            Milan, Summer 2023. Surface temperatures reached <span class="highlight">56°C</span>.<br>
            But satellite data reveals a disturbing pattern:<br>
            <span class="highlight">The heat is not distributed equally.</span><br><br>
            Your mission: use NASA Landsat imagery, social vulnerability data, 
            and machine learning to uncover <span class="highlight">who</span> is dying 
            from heat in one of Europe's richest cities — and <span class="highlight">why</span>.<br><br>
            <span style="color: #ff4444;">⚠ This is a 6-chapter investigation. You must complete each objective.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("▶ INITIATE MISSION"):
        advance()

# ============================================
# CHAPTER 1: CALIBRATION (click to measure)
# ============================================
elif st.session_state.chapter == 1:
    st.markdown("## 📍 CHAPTER 1 :: CALIBRATION")
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ INCOMING TRANSMISSION</div>
        <div class="text">
            "Agent, first we calibrate your instruments. We have flagged two locations 
            exactly <span class="highlight">300 meters apart</span>:<br>
            🔴 <b>DUOMO</b> — historic city center, dense concrete<br>
            🟢 <b>PARCO SEMPIONE</b> — the city's largest park<br><br>
            <span class="highlight">Click on BOTH markers on the map</span> to measure 
            their surface temperature."
        </div>
    </div>
    <div class="objective">Measure both points to unlock the first clue</div>
    """, unsafe_allow_html=True)
    
    # Build map with 2 clickable points
    fig = go.Figure()
    
    duomo_color = '#00ff88' if st.session_state.clicked_duomo else '#ff4444'
    park_color = '#00ff88' if st.session_state.clicked_park else '#00ff88'
    
    duomo_size = 40 if st.session_state.clicked_duomo else 30
    park_size = 40 if st.session_state.clicked_park else 30
    
    fig.add_trace(go.Scattermap(
        lat=[45.464], lon=[9.191], mode='markers+text',
        marker=dict(size=duomo_size, color=duomo_color, allowoverlap=True),
        text=['🔴 DUOMO ✓' if st.session_state.clicked_duomo else '🔴 DUOMO'],
        textposition='top center',
        textfont=dict(color='#ff4444', size=14, family='Courier New'),
        name='Duomo',
        customdata=['duomo'] * 1,
        hovertemplate='<b>DUOMO</b><br>Click to measure<extra></extra>'
    ))
    fig.add_trace(go.Scattermap(
        lat=[45.472], lon=[9.179], mode='markers+text',
        marker=dict(size=park_size, color=park_color, allowoverlap=True),
        text=['🟢 PARK ✓' if st.session_state.clicked_park else '🟢 PARK'],
        textposition='top center',
        textfont=dict(color='#00ff88', size=14, family='Courier New'),
        name='Park',
        customdata=['park'] * 1,
        hovertemplate='<b>PARK</b><br>Click to measure<extra></extra>'
    ))
    
    fig.update_layout(
        map=dict(style="carto-darkmatter", center=dict(lat=45.468, lon=9.185), zoom=14),
        height=450, margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    
    event = st.plotly_chart(fig, on_select="rerun", selection_mode="points", 
                             use_container_width=True, key="ch1_map")
    
    if event and event.get("selection", {}).get("points"):
        for point in event.selection.points:
            cd = point.get('customdata')
            if cd == 'duomo' and not st.session_state.clicked_duomo:
                st.session_state.clicked_duomo = True
                st.rerun()
            if cd == 'park' and not st.session_state.clicked_park:
                st.session_state.clicked_park = True
                st.rerun()
    
    # Show progress
    c1, c2 = st.columns(2)
    c1.metric("🔴 Duomo Measured", "✓" if st.session_state.clicked_duomo else "❌ Pending")
    c2.metric("🟢 Park Measured", "✓" if st.session_state.clicked_park else "❌ Pending")
    
    # When both clicked → reveal
    if st.session_state.clicked_duomo and st.session_state.clicked_park:
        award_clue('gap', 100)
        st.markdown('<div class="clue-unlocked"><div class="title">🔍 CLUE #1 UNLOCKED</div><div class="body">6.87°C difference across 300 meters</div></div>', unsafe_allow_html=True)
        
        fig2 = go.Figure(go.Bar(
            x=['Duomo', 'Park'], y=[48.87, 42.00],
            marker_color=['#ff4444', '#00ff88'],
            text=['48.87°C', '42.00°C'], textposition='outside',
            textfont=dict(size=20, color='white', family='Courier New')
        ))
        fig2.update_layout(
            title="🔬 MEASUREMENT COMPLETE",
            yaxis_title="LST (°C)", yaxis_range=[40, 51],
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#00d9ff', family='Courier New'), height=400
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ ANALYSIS</div>
            <div class="text">
                "Confirmed. A single park cools its surroundings by nearly <span class="highlight">7°C</span>.<br><br>
                If physics alone drove heat, we could just plant trees everywhere. 
                But this case is more complicated. Next, we investigate 
                <span class="highlight">who actually suffers</span> — and it's not who you think."
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("▶ PROCEED TO CHAPTER 2"):
            advance()

# ============================================
# CHAPTER 2: FACTOR ANALYSIS
# ============================================
elif st.session_state.chapter == 2:
    st.markdown("## 🔍 CHAPTER 2 :: FACTOR ANALYSIS")
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ INCOMING TRANSMISSION</div>
        <div class="text">
            "We ran <span class="highlight">8 regression models</span> on social vulnerability 
            factors, all controlling for concrete and trees. Then we applied 
            <span class="highlight">Benjamini-Hochberg FDR correction</span> to eliminate false positives.<br><br>
            The results are... surprising.<br><br>
            <span class="highlight">Based on the data, which group is the TRUE hidden face of heat?</span>"
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    answer = st.radio("▶ SELECT YOUR HYPOTHESIS:", [
        "A) 👴 Elderly residents (65+)",
        "B) 🌍 Foreign nationals",
        "C) 🚪 One-person households (loneliness)",
        "D) 💼 Unemployed residents"
    ], key="quiz_ch2")
    
    if st.button("▶ SUBMIT ANALYSIS"):
        if "C)" in answer:
            award_clue('loneliness', 100)
            st.markdown('<div class="clue-unlocked"><div class="title">🔍 CLUE #2 UNLOCKED</div><div class="body">Loneliness is the strongest predictor (+0.083°C, p<0.0001)</div></div>', unsafe_allow_html=True)
            
            # Animation-like coefficient chart
            factors = ['One-person\nhouseholds', 'Foreign\nnationals', 'Young\nmales', 'Old\nfemales', 'Old\nmales', 'Unemployed']
            coefs = [0.083, 0.029, 0.006, -0.008, -0.030, -0.042]
            colors = ['#00ff88' if c > 0.02 else '#ff4444' if c < -0.02 else '#666' for c in coefs]
            
            fig = go.Figure(go.Bar(
                x=factors, y=coefs, marker_color=colors,
                text=[f'{c:+.3f}' for c in coefs], textposition='outside',
                textfont=dict(color='white', family='Courier New')
            ))
            fig.update_layout(
                title="🎯 FDR-Corrected Coefficients (controlling for concrete + trees)",
                yaxis_title="Δ°C per SD", height=400,
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#00d9ff', family='Courier New')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <div class="terminal">
                <div class="tag">▶ INTERPRETATION</div>
                <div class="text">
                    "The FDR correction <span class="highlight">eliminated foreign nationals</span> 
                    as a false positive (p=0.14). The true face of heat is 
                    <span class="highlight">LONELINESS</span>.<br><br>
                    <b>Why not elderly?</b> They live in cooler historic centers.<br>
                    <b>Why not unemployed?</b> They live in cooler public housing.<br>
                    <b>Why lonely?</b> They're trapped in small, top-floor apartments 
                    with no social network to escape heat waves."
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("▶ PROCEED TO CHAPTER 3"):
                advance()
        else:
            st.error("❌ INCORRECT. The FDR correction eliminated the obvious suspects. Check the coefficients again.")

# ============================================
# CHAPTER 3: TREND
# ============================================
elif st.session_state.chapter == 3:
    st.markdown("## 📈 CHAPTER 3 :: 10-YEAR TREND")
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ INCOMING TRANSMISSION</div>
        <div class="text">
            "We retrieved <span class="highlight">10 years of Landsat data</span> (2014-2023).<br><br>
            <span class="highlight">Is the gap between rich and poor widening, or is it stable?</span><br><br>
            Run the analysis and watch what happens."
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if ts is not None:
        ts_s = ts.copy()
        ts_s['Q1_S'] = ts_s['Q1_Rich'].rolling(3).mean()
        ts_s['Q4_S'] = ts_s['Q4_Poor'].rolling(3).mean()
        
        if not st.session_state.trend_run:
            if st.button("▶ RUN 10-YEAR SIMULATION"):
                st.session_state.trend_run = True
                st.rerun()
        else:
            # Plotly native animation - NO freeze, browser-side
            frames = []
            for i in range(3, len(ts_s) + 1):
                frames.append(go.Frame(
                    data=[
                        go.Scatter(x=ts_s['Year'][:i], y=ts_s['Q1_S'][:i],
                                   mode='lines+markers', name='Rich (Q1)',
                                   line=dict(color='#00ff88', width=4)),
                        go.Scatter(x=ts_s['Year'][:i], y=ts_s['Q4_S'][:i],
                                   mode='lines+markers', name='Poor (Q4)',
                                   line=dict(color='#ff4444', width=4)),
                    ],
                    name=str(int(ts_s['Year'].iloc[i-1]))
                ))
            
            fig = go.Figure(
                data=[
                    go.Scatter(x=[], y=[], mode='lines+markers', name='Rich (Q1)',
                               line=dict(color='#00ff88', width=4)),
                    go.Scatter(x=[], y=[], mode='lines+markers', name='Poor (Q4)',
                               line=dict(color='#ff4444', width=4)),
                ],
                frames=frames
            )
            
            fig.update_layout(
                updatemenus=[dict(
                    type="buttons", showactive=False,
                    x=0.02, y=1.15, xanchor="left",
                    bgcolor='#00d9ff', bordercolor='#00d9ff',
                    font=dict(color='#050814'),
                    buttons=[
                        dict(label="▶ PLAY", method="animate",
                             args=[None, {"frame": {"duration": 600, "redraw": True},
                                          "fromcurrent": True, "transition": {"duration": 300}}]),
                        dict(label="⏸ PAUSE", method="animate",
                             args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}]),
                    ]
                )],
                title="🔬 CLIMATE TREND ANALYSIS (2014-2023)",
                xaxis_title="Year", yaxis_title="Mean Summer LST (°C)",
                yaxis_range=[36, 50], height=450,
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#00d9ff', family='Courier New'),
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            award_clue('trend', 100)
            st.markdown('<div class="clue-unlocked"><div class="title">🔍 CLUE #3 UNLOCKED</div><div class="body">Poor neighborhoods heat 4% faster — gap widens every decade</div></div>', unsafe_allow_html=True)
            
            st.markdown("""
            <div class="terminal">
                <div class="tag">▶ STATISTICAL PROOF</div>
                <div class="text">
                    • Rich (Q1) trend: <span class="highlight">0.825°C/decade</span><br>
                    • Poor (Q4) trend: <span class="highlight">0.858°C/decade</span><br>
                    • Gap: <span class="highlight">+0.033°C/decade</span><br>
                    • After spatial correction (Moran's I = 0.74): <span class="highlight">p < 0.0001</span><br><br>
                    <span style="color: #ffaa00;">⚠ SEASONAL AMPLIFICATION:</span> The gap nearly doubles in summer — 
                    from 1.28°C (spring) to 2.35°C (summer). Climate inequality strikes 
                    hardest exactly when heat becomes lethal.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("▶ PROCEED TO CHAPTER 4"):
                advance()

# ============================================
# CHAPTER 4: ANOMALIES
# ============================================
elif st.session_state.chapter == 4:
    st.markdown("## 🏭 CHAPTER 4 :: ANOMALY HUNT")
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ INCOMING TRANSMISSION</div>
        <div class="text">
            "Our physics-only model explains 57.5% of the heat. But in 
            <span class="highlight">255 tracts</span>, it fails completely — the real 
            temperature is 5-7°C hotter than concrete alone would predict.<br><br>
            <span class="highlight">Where are these hidden heat sources?</span>"
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    anomalies = gdf[gdf['residuals'] > 2]
    
    fig = go.Figure()
    fig.add_trace(go.Scattermap(
        lat=gdf['cy'], lon=gdf['cx'], mode='markers',
        marker=dict(size=2, color='rgba(100,100,100,0.3)'),
        hoverinfo='skip', showlegend=False
    ))
    fig.add_trace(go.Scattermap(
        lat=anomalies['cy'], lon=anomalies['cx'], mode='markers',
        marker=dict(size=10, color='#ff4444', opacity=0.9),
        name='Heat Anomalies (>2°C above prediction)',
        text=anomalies['SEZ2011'],
        hovertemplate="<b>Tract %{text}</b><br>Anomaly: +5 to +7°C<extra></extra>"
    ))
    fig.update_layout(
        map=dict(style="carto-darkmatter", center=dict(lat=45.4642, lon=9.19), zoom=10.5),
        height=450, margin=dict(l=0, r=0, t=0, b=0), showlegend=True,
        legend=dict(font=dict(color='#00d9ff', family='Courier New'), bgcolor='rgba(0,0,0,0.5)')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    if not st.session_state.overlay_run:
        if st.button("▶ OVERLAY INDUSTRIAL ZONES"):
            st.session_state.overlay_run = True
            st.rerun()
    else:
        award_clue('industry', 100)
        st.markdown('<div class="clue-unlocked"><div class="title">🔍 CLUE #4 UNLOCKED</div><div class="body">59.2% of heat anomalies fall inside industrial zones!</div></div>', unsafe_allow_html=True)
        
        # Animated bar comparison
        fig2 = go.Figure(go.Bar(
            x=['All Tracts (baseline)', 'Heat Anomalies'],
            y=[13.9, 59.2],
            marker_color=['#666', '#ff4444'],
            text=['13.9%', '59.2%'], textposition='outside',
            textfont=dict(size=24, color='white', family='Courier New')
        ))
        fig2.update_layout(
            title="🏭 INDUSTRIAL ZONE OVERLAP — 4.3x concentration",
            yaxis_title="% touching industrial zones", yaxis_range=[0, 70],
            height=350,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#00d9ff', family='Courier New')
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ REVELATION</div>
            <div class="text">
                "The math is undeniable:<br>
                • Baseline: only <span class="highlight">13.9%</span> of tracts touch industrial zones<br>
                • Among heat anomalies: <span class="highlight">59.2%</span> touch industrial zones<br>
                • <span class="highlight">4.3x concentration ratio</span><br><br>
                Standard climate models are blind to industry. They see 'low residential density' 
                and predict cool. But logistics hubs, railway yards, and factories reach 53-56°C. 
                And the most vulnerable workers live right next to them."
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("▶ PROCEED TO CHAPTER 5"):
            advance()

# ============================================
# CHAPTER 5: THE TRAP
# ============================================
elif st.session_state.chapter == 5:
    st.markdown("## 🌳 CHAPTER 5 :: THE TRAP")
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ INCOMING TRANSMISSION</div>
        <div class="text">
            "Industry is an invisible oven. But surely the solution is simple: 
            <span class="highlight">plant trees in poor neighborhoods</span>?<br><br>
            Run the tree-planting simulation. Watch the result closely."
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("▶ SIMULATE MASS TREE PLANTING"):
        st.session_state.intervention_done = True
        
        award_clue('tree_trap', 100)
        st.markdown('<div class="clue-unlocked"><div class="title">🔍 CLUE #5 UNLOCKED</div><div class="body">Trees → +0.04°C. Temperature actually INCREASES!</div></div>', unsafe_allow_html=True)
        
        fig = go.Figure(go.Bar(
            x=['Current', 'After Trees'],
            y=[48.67, 48.70],
            marker_color=['#666', '#ff4444'],
            text=['48.67°C', '+0.04°C ↑'], textposition='outside',
            textfont=dict(size=20, color='white', family='Courier New')
        ))
        fig.update_layout(
            title="🌳 TREE INTERVENTION: THE PARADOX",
            yaxis_title="Mean LST (°C)", yaxis_range=[48, 49.2],
            height=350,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#00d9ff', family='Courier New')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ THE ECO-STRUCTURAL LOCK</div>
            <div class="text">
                "Why did this fail?<br><br>
                • <span class="highlight">64.3%</span> of poor tracts are already at the 
                  maximum tree-cover value (0.614) in the data<br>
                • The metric is saturated — planting more doesn't register<br>
                • By contrast, rich neighborhoods span a wide range (-8 to 0.6)<br><br>
                <span style="color:#ff4444;">You cannot 'plant your way' out of climate inequality.</span><br>
                The physics of dense urban fabric limits what trees can do."
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Comparison chart
        fig2 = go.Figure(go.Bar(
            x=['Rich Neighborhoods', 'Poor Neighborhoods'],
            y=[7.9, 64.3],
            marker_color=['#00ff88', '#ff4444'],
            text=['7.9%', '64.3%'], textposition='outside',
            textfont=dict(size=20, color='white', family='Courier New')
        ))
        fig2.update_layout(
            title="% of tracts at tree-cover ceiling",
            yaxis_title="% of tracts", yaxis_range=[0, 80],
            height=350,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#00d9ff', family='Courier New')
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        if st.button("▶ PROCEED TO FINAL CHAPTER"):
            advance()

# ============================================
# CHAPTER 6: THE SOLUTION
# ============================================
elif st.session_state.chapter == 6:
    st.markdown("## 🏠 CHAPTER 6 :: THE SOLUTION")
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ FINAL TRANSMISSION</div>
        <div class="text">
            "Trees failed. But there's another option: <span class="highlight">cool roofs</span> — 
            reflective materials that reduce heat absorption.<br><br>
            <span class="highlight">Choose the city's strategy. The budget will be deployed based on your recommendation.</span>"
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    choice = st.radio("▶ FINAL RECOMMENDATION:", [
        "🌳 Plant more trees",
        "🏠 Install cool reflective roofs",
        "🔀 Do both simultaneously"
    ], key="ch6_choice")
    
    if st.button("▶ SUBMIT FINAL VERDICT"):
        award_clue('solution', 150)
        st.markdown('<div class="clue-unlocked"><div class="title">🔍 CLUE #6 UNLOCKED</div><div class="body">Cool Roofs (-0.36°C) >> Trees (+0.04°C)</div></div>', unsafe_allow_html=True)
        
        fig = go.Figure(go.Bar(
            x=['Current', 'Trees Only', 'Cool Roofs', 'Combined'],
            y=[48.67, 48.70, 48.31, 48.32],
            marker_color=['#666', '#ff4444', '#00ff88', '#00d9ff'],
            text=['48.67°C', '+0.04°C', '-0.36°C', '-0.35°C'],
            textposition='outside',
            textfont=dict(size=18, color='white', family='Courier New')
        ))
        fig.update_layout(
            title="🔬 INTERVENTION SIMULATION — POOR NEIGHBORHOODS",
            yaxis_title="Mean LST (°C)", yaxis_range=[48, 49.5],
            height=400,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#00d9ff', family='Courier New')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        <div class="terminal">
            <div class="tag">▶ VERDICT</div>
            <div class="text">
                <span style="color:#00ff88;">✅ Cool Roofs</span> reduce temperature by <span class="highlight">-0.36°C</span>.<br>
                <span style="color:#ff4444;">❌ Trees</span> produce almost no cooling (<span class="highlight">+0.04°C</span>) due to the data ceiling.<br><br>
                <span class="highlight">Policy Recommendation:</span><br>
                Redirect tree-planting budgets in dense areas to cool roofs, 
                reflective pavements, and green walls.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🏆 CLOSE THE CASE"):
            advance()

# ============================================
# FINAL: CASE CLOSED
# ============================================
elif st.session_state.chapter >= 7:
    st.balloons()
    
    st.markdown("""
    <div style="text-align:center; padding: 30px 20px;">
        <div class="rank-badge">🏆</div>
        <div style="color: #00ff88; font-family: 'Courier New'; letter-spacing: 8px; font-size: 0.9rem;">MISSION COMPLETE</div>
        <h1 style="font-size: 3rem; letter-spacing: 5px;">CASE CLOSED</h1>
        <div style="color: #ffaa00; font-family: 'Courier New'; letter-spacing: 5px; font-size: 0.85rem;">CLASSIFICATION: DECLASSIFIED</div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Evidence Collected", f"{len(st.session_state.evidence)}/6")
    c2.metric("Total XP", st.session_state.xp)
    c3.metric("Final Rank", "🕵️ MASTER DETECTIVE")
    
    st.markdown("---")
    st.markdown("### 📋 CASE EVIDENCE SUMMARY")
    
    evidence_texts = {
        "gap": ("CLUE #1", "6.87°C difference across 300m — Duomo vs Park"),
        "loneliness": ("CLUE #2", "Loneliness (+0.083°C, p<0.0001) is the strongest predictor"),
        "trend": ("CLUE #3", "Poor neighborhoods heat 4% faster — gap widens every decade"),
        "industry": ("CLUE #4", "59.2% of heat anomalies occur in industrial zones (4.3x baseline)"),
        "tree_trap": ("CLUE #5", "64.3% of poor tracts are at the tree-cover ceiling — trees don't work"),
        "solution": ("CLUE #6", "Cool roofs (-0.36°C) are the only effective intervention"),
    }
    for key in st.session_state.evidence:
        num, text = evidence_texts.get(key, ("CLUE", key))
        st.markdown(f"""
        <div style="background:rgba(0,255,136,0.05); border:1px solid #00ff88; 
                    padding:12px 20px; border-radius:4px; margin:8px 0;
                    font-family:'Courier New';">
            <span style="color:#00ff88; font-weight:bold; letter-spacing:2px;">{num}</span>
            <span style="color:#e0e8f0; margin-left:15px;">{text}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ⚖️ FINAL REPORT")
    st.markdown("""
    <div class="terminal">
        <div class="tag">▶ MISSION COMMANDER'S REPORT</div>
        <div class="text">
            "Agent, your investigation reveals the anatomy of climate inequality in Milan:<br><br>
            • Heat differs by <span class="highlight">6.87°C</span> across 300m<br>
            • Poor neighborhoods heat <span class="highlight">4% faster</span> every decade<br>
            • <span class="highlight">59.2%</span> of anomalies come from industrial zones<br>
            • <span class="highlight">Loneliness</span>, not poverty, is the real face of vulnerability<br>
            • <span class="highlight">64.3%</span> of poor tracts are at the tree-cover ceiling<br>
            • <span class="highlight">Cool roofs</span> are the only effective intervention (-0.36°C)<br><br>
            <span style="color:#00ff88;">IMPACT: 571,146 people (40.8% of Milan) live in climate risk zones.</span><br>
            Your investigation gives them a voice — and a policy roadmap."
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
            <div style="background:#00d9ff; color:#050814; padding:14px; border-radius:4px; 
                        text-align:center; font-weight:bold; cursor:pointer;
                        font-family:'Courier New'; letter-spacing:2px;">
                📂 VIEW FULL NOTEBOOK
            </div>
        </a>
        """, unsafe_allow_html=True)
