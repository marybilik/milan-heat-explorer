import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import time

st.set_page_config(page_title="The Milan Heat Case", page_icon="🕵️", layout="wide", initial_sidebar_state="collapsed")

# ============================================
# NOIR DETECTIVE CSS
# ============================================
st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%); color: #e0e0e0; }
    h1, h2, h3 { color: #f5f5f5 !important; font-family: 'Courier New', monospace; letter-spacing: 1px; }
    p, li, label, .stMarkdown { color: #ccc !important; }
    
    .narration-box {
        background: rgba(20, 25, 40, 0.9);
        border-left: 4px solid #e74c3c;
        padding: 20px 25px;
        border-radius: 8px;
        margin: 20px 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.6);
        font-family: 'Courier New', monospace;
    }
    .narration-box .speaker { color: #e74c3c; font-weight: bold; font-size: 1rem; letter-spacing: 3px; margin-bottom: 10px; }
    .narration-box .text { color: #f5f5f5; font-size: 1.05rem; line-height: 1.7; }
    
    .clue-found {
        background: linear-gradient(90deg, #f39c12, #e74c3c);
        color: white; padding: 18px 25px; border-radius: 8px;
        text-align: center; font-weight: bold; font-size: 1.1rem; margin: 20px 0;
        box-shadow: 0 8px 30px rgba(243, 156, 18, 0.4);
    }
    
    .case-file {
        background: rgba(30, 35, 55, 0.9);
        border: 1px solid #333;
        padding: 15px 20px; border-radius: 8px; margin: 8px 0;
        font-family: 'Courier New', monospace;
    }
    .case-file b { color: #f39c12; }
    
    .stButton > button {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: white !important; border: none; padding: 14px 28px;
        font-weight: bold; border-radius: 8px; font-family: 'Courier New', monospace;
        letter-spacing: 2px; width: 100%; transition: all 0.2s;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(231,76,60,0.5); }
    
    .top-bar {
        background: rgba(0,0,0,0.5); padding: 15px 25px; border-radius: 10px;
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; font-family: 'Courier New', monospace;
    }
    .rank-badge { text-align: center; font-size: 4rem; margin: 20px 0; }
    
    /* Radio/quiz styling */
    .stRadio > div { background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; }
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
    st.error(f"❌ Data error: {e}")
    st.stop()

# ============================================
# SESSION STATE
# ============================================
if 'chapter' not in st.session_state:
    st.session_state.chapter = 0
    st.session_state.evidence = []
    st.session_state.xp = 0
    st.session_state.ch1_ran = False
    st.session_state.ch2_ran = False
    st.session_state.ch3_ran = False
    st.session_state.ch4_ran = False
    st.session_state.ch5_ran = False
    st.session_state.ch6_ran = False

def award(ev_key, ev_text, xp=100):
    if ev_key not in st.session_state.evidence:
        st.session_state.evidence.append(ev_key)
        st.session_state.xp += xp

def go_next():
    st.session_state.chapter += 1
    st.rerun()

def reset():
    for k in ['chapter','evidence','xp','ch1_ran','ch2_ran','ch3_ran','ch4_ran','ch5_ran','ch6_ran']:
        st.session_state.pop(k, None)
    st.rerun()

# ============================================
# TOP STATUS BAR (when investigation started)
# ============================================
if st.session_state.chapter > 0 and st.session_state.chapter < 7:
    st.markdown(f"""
    <div class="top-bar">
        <div>🕵️ <b>DETECTIVE</b> &nbsp;|&nbsp; Chapter {int(st.session_state.chapter)}/6</div>
        <div>🔍 Evidence: <b>{len(st.session_state.evidence)}/6</b></div>
        <div>⚡ XP: <b>{st.session_state.xp}</b></div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(min(len(st.session_state.evidence) / 6, 1.0))

# ============================================
# CHAPTER 0: INTRO
# ============================================
if st.session_state.chapter == 0:
    st.markdown("""
    <div style="text-align:center; padding: 80px 20px;">
        <div style="font-size: 7rem;">🕵️‍♀️</div>
        <h1 style="font-size: 3.5rem; letter-spacing: 8px; margin: 20px 0;">THE MILAN<br>HEAT CASE</h1>
        <p style="font-size: 1.2rem; color: #f39c12; letter-spacing: 4px; margin-top: 30px;">A CLIMATE INEQUALITY INVESTIGATION</p>
        <div style="max-width: 650px; margin: 50px auto; padding: 25px; background: rgba(0,0,0,0.4); border-left: 4px solid #e74c3c; text-align: left;">
            <p style="font-family: 'Courier New', monospace; color: #e0e0e0; line-height: 1.8;">
                <b style="color:#e74c3c;">CLASSIFIED BRIEFING:</b><br><br>
                Milan, Summer 2023. Surface temperatures hit 56°C.<br>
                But the heat is <b>not equal</b>.<br><br>
                Your mission: use NASA satellite data, census records, and 
                machine learning to uncover the hidden geography of climate 
                inequality in one of Europe's richest cities.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔎 ACCEPT THE CASE"):
        go_next()

# ============================================
# CHAPTER 1: THE SCENE
# ============================================
elif st.session_state.chapter == 1:
    st.markdown("## 📍 Chapter 1: The Scene")
    st.markdown("""
    <div class="narration-box">
        <div class="speaker">📡 CASE COMMANDER:</div>
        <div class="text">
            "Detective. Before we dive into 6,000 census tracts, let's start with 
            two locations, just 300 meters apart:<br><br>
            🔴 <b>Duomo</b> — historic center, dense concrete<br>
            🟢 <b>Parco Sempione</b> — the city's largest park<br><br>
            Same city. Same summer. <b>Your mission:</b> measure the temperature gap."
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Map with two points
    fig = go.Figure()
    fig.add_trace(go.Scattermap(
        lat=[45.464], lon=[9.191], mode='markers+text',
        marker=dict(size=35, color='#e74c3c'), text=['🔴 DUOMO'],
        textposition='top center', textfont=dict(color='#e74c3c', size=14),
        name='Duomo', hovertemplate='Duomo — Dense center<extra></extra>'
    ))
    fig.add_trace(go.Scattermap(
        lat=[45.472], lon=[9.179], mode='markers+text',
        marker=dict(size=35, color='#2ecc71'), text=['🟢 PARK'],
        textposition='top center', textfont=dict(color='#2ecc71', size=14),
        name='Park', hovertemplate='Parco Sempione<extra></extra>'
    ))
    fig.update_layout(
        map=dict(style="carto-darkmatter", center=dict(lat=45.468, lon=9.185), zoom=14),
        height=400, margin=dict(l=0, r=0, t=0, b=0), showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    
    if st.button("🌡️ MEASURE BOTH TEMPERATURES"):
        st.session_state.chapter = 1.5
        st.rerun()

# ============================================
# CHAPTER 1.5: REVEAL
# ============================================
elif st.session_state.chapter == 1.5:
    st.markdown("## 🔍 The Evidence")
    
    fig = go.Figure(go.Bar(
        x=['Duomo (Center)', 'Parco Sempione'], y=[48.87, 42.00],
        marker_color=['#e74c3c', '#2ecc71'],
        text=['48.87°C', '42.00°C'], textposition='outside',
        textfont=dict(size=18, color='white')
    ))
    fig.update_layout(
        title="Temperature Difference: 6.87°C in 300 meters",
        yaxis_title="Surface Temperature (°C)", yaxis_range=[40, 50],
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'), height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="clue-found">🔍 CLUE FOUND: A single park cools the area by nearly 7°C</div>', unsafe_allow_html=True)
    award("gap", "6.87°C difference: Duomo vs Park")
    
    st.markdown("""
    <div class="narration-box">
        <div class="speaker">📡 CASE COMMANDER:</div>
        <div class="text">
            "Excellent work. So physics matters — concrete is hot, trees are cool.<br><br>
            But if trees are the answer, why don't we just plant them everywhere? 
            <b>Next mission:</b> investigate WHO actually suffers from the heat. 
            We have NASA Landsat merged with the Social Vulnerability Index for 
            all 6,077 tracts. The answer will surprise you."
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("➡️ PROCEED TO CHAPTER 2"):
        go_next()

# ============================================
# CHAPTER 2: THE SUSPECTS
# ============================================
elif st.session_state.chapter == 2:
    st.markdown("## 🔍 Chapter 2: The Suspects")
    st.markdown("""
    <div class="narration-box">
        <div class="speaker">📡 CASE COMMANDER:</div>
        <div class="text">
            "We ran 8 separate regressions on social vulnerability factors, then 
            applied a strict FDR correction to eliminate false positives.<br><br>
            <b>Your mission:</b> Based on the notebook's output, which group is 
            the TRUE hidden face of heat?"
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    answer = st.radio("🎯 Choose your suspect:", [
        "A) 👴 Elderly residents",
        "B) 🌍 Foreign nationals",
        "C) 🚪 One-person households (loneliness)",
        "D) 💼 Unemployed residents"
    ], key="quiz_ch2")
    
    if st.button("🔍 SUBMIT YOUR VERDICT"):
        if "C)" in answer or "loneliness" in answer.lower():
            st.success("✅ CORRECT, Detective!")
            st.markdown('<div class="clue-found">🔍 CLUE FOUND: Loneliness is the strongest predictor (+0.083°C, p<0.0001)</div>', unsafe_allow_html=True)
            award("loneliness", "Loneliness is strongest predictor (p<0.0001)")
            
            st.markdown("""
            **Why not the others?**
            - ❌ **Elderly:** Live in cooler historic centers (negative coefficient)
            - ❌ **Foreign nationals:** Lost significance after FDR (p=0.14)
            - ❌ **Unemployed:** Live in cooler public housing (negative coefficient)
            - ✅ **Lonely residents:** Trapped in small, top-floor apartments with no social network
            """)
            
            st.markdown("""
            <div class="narration-box">
                <div class="speaker">📡 CASE COMMANDER:</div>
                <div class="text">
                    "The problem is <b>isolation</b>, not poverty. But we're just getting started. 
                    Heat is one thing — but is the gap STATIC or is it getting worse? 
                    <b>Next mission:</b> run a 10-year trend analysis."
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("➡️ PROCEED TO CHAPTER 3"):
                go_next()
        else:
            st.error("❌ Not quite. The FDR correction eliminated the obvious suspects. Try again — the answer is not what you'd expect.")

# ============================================
# CHAPTER 3: THE TREND
# ============================================
elif st.session_state.chapter == 3:
    st.markdown("## 📈 Chapter 3: The Trend")
    st.markdown("""
    <div class="narration-box">
        <div class="speaker">📡 CASE COMMANDER:</div>
        <div class="text">
            "10 years of Landsat data (2014–2023). Is the gap between rich and poor 
            widening, or is it stable?<br><br>
            <b>Your mission:</b> press the button and watch the trend unfold year by year. 
            Pay attention to the <b>slope</b> of the red line."
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if ts is not None:
        if st.button("▶️ RUN 10-YEAR ANALYSIS"):
            ts_s = ts.copy()
            ts_s['Q1_S'] = ts_s['Q1_Rich'].rolling(3).mean()
            ts_s['Q4_S'] = ts_s['Q4_Poor'].rolling(3).mean()
            
            placeholder = st.empty()
            for i in range(3, len(ts_s) + 1):
                with placeholder.container():
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=ts_s['Year'][:i], y=ts_s['Q1_S'][:i],
                                              mode='lines+markers', name='Rich (Q1)',
                                              line=dict(color='#2ecc71', width=4)))
                    fig.add_trace(go.Scatter(x=ts_s['Year'][:i], y=ts_s['Q4_S'][:i],
                                              mode='lines+markers', name='Poor (Q4)',
                                              line=dict(color='#e74c3c', width=4)))
                    fig.update_layout(
                        title=f"⏳ Analyzing... {ts_s['Year'].iloc[i-1]}",
                        xaxis_title="Year", yaxis_title="Mean LST (°C)",
                        yaxis_range=[36, 50], height=400,
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"anim_{i}")
                time.sleep(0.5)
            
            st.markdown('<div class="clue-found">🔍 CLUE FOUND: Poor neighborhoods heat 4% faster. The gap widens.</div>', unsafe_allow_html=True)
            award("trend", "Gap widens by 0.033°C/decade")
            
            st.markdown("""
            **Statistical proof:** 
            - Q1 (Rich) trend: **0.825°C/decade**
            - Q4 (Poor) trend: **0.858°C/decade**
            - Gap: **+0.033°C/decade**
            - After spatial correction (Moran's I = 0.74): **p < 0.0001**
            
            **Seasonal amplification:** The gap nearly doubles in summer — from **1.28°C** (spring) 
            to **2.35°C** (summer). Climate inequality strikes hardest exactly when heat becomes lethal.
            """)
            
            st.markdown("""
            <div class="narration-box">
                <div class="speaker">📡 CASE COMMANDER:</div>
                <div class="text">
                    "The gap is widening, and it peaks in summer. But something doesn't add up: 
                    in some neighborhoods, the actual temperature is MUCH higher than concrete alone 
                    would predict. <b>Next mission:</b> find the hidden heat sources."
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("➡️ PROCEED TO CHAPTER 4"):
                go_next()
        else:
            st.info("👆 Press the button to run the analysis")
    else:
        st.error("⚠️ time_series.csv missing")

# ============================================
# CHAPTER 4: THE HIDDEN CLUE
# ============================================
elif st.session_state.chapter == 4:
    st.markdown("## 🏭 Chapter 4: The Hidden Clue")
    st.markdown("""
    <div class="narration-box">
        <div class="speaker">📡 CASE COMMANDER:</div>
        <div class="text">
            "Our physics-only model explains 57.5% of the heat. But in 255 tracts, 
            it fails completely — the real temperature is far hotter than concrete 
            alone would predict.<br><br>
            <b>Your mission:</b> investigate what's hiding in these anomalies."
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    anomalies = gdf[gdf['residuals'] > 2]
    
    fig = go.Figure()
    fig.add_trace(go.Scattermap(
        lat=gdf['cy'], lon=gdf['cx'], mode='markers',
        marker=dict(size=3, color='rgba(120,120,120,0.4)'),
        hoverinfo='skip', showlegend=False
    ))
    fig.add_trace(go.Scattermap(
        lat=anomalies['cy'], lon=anomalies['cx'], mode='markers',
        marker=dict(size=10, color='#e74c3c'),
        name='Heat Anomalies',
        text=anomalies['SEZ2011'],
        hovertemplate="<b>Tract %{text}</b><br>+7°C above prediction<extra></extra>"
    ))
    fig.update_layout(
        map=dict(style="carto-darkmatter", center=dict(lat=45.4642, lon=9.19), zoom=10.5),
        height=450, margin=dict(l=0, r=0, t=0, b=0), showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)
    
    if st.button("🏭 OVERLAY INDUSTRIAL ZONES"):
        st.markdown('<div class="clue-found">🔍 CLUE FOUND: 59.2% of heat anomalies fall inside industrial zones!</div>', unsafe_allow_html=True)
        award("industry", "59.2% of anomalies in industry (4.3x baseline)")
        
        st.markdown("""
        **The math:**
        - Baseline: only **13.9%** of all tracts touch an industrial zone
        - Among heat anomalies: **59.2%** touch industrial zones
        - **Concentration ratio: 4.3x**
        
        **Why does this matter?** Standard climate models are blind to industry. 
        They see "low residential density" and predict cool. But logistics hubs, 
        railway yards, and factories (dark roofs, asphalt, metal) reach 53-56°C. 
        And the most vulnerable workers live right next to them.
        """)
        
        st.markdown("""
        <div class="narration-box">
            <div class="speaker">📡 CASE COMMANDER:</div>
            <div class="text">
                "Industry is an invisible oven. But now that we know the problem, 
                surely the solution is simple: plant trees? <b>Next mission:</b> 
                test the tree-planting hypothesis. Watch what happens."
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("➡️ PROCEED TO CHAPTER 5"):
            go_next()

# ============================================
# CHAPTER 5: THE TRAP
# ============================================
elif st.session_state.chapter == 5:
    st.markdown("## 🌳 Chapter 5: The Trap")
    st.markdown("""
    <div class="narration-box">
        <div class="speaker">📡 CASE COMMANDER:</div>
        <div class="text">
            "The obvious solution: plant more trees in poor neighborhoods. 
            But Detective, this case has a twist.<br><br>
            <b>Your mission:</b> simulate a mass tree-planting campaign in the 
            poorest district. Watch the model closely."
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🌱 PLANT 100 TREES"):
        st.markdown('<div class="clue-found">🔍 CLUE FOUND: Trees → +0.04°C. Temperature actually INCREASES!</div>', unsafe_allow_html=True)
        award("tree_trap", "64.3% of poor tracts at tree ceiling")
        
        st.markdown("""
        **Why did this fail?** This is the **Eco-Structural Lock**:<br>
        - **64.3%** of poor tracts are already at the maximum tree-cover value (0.614) in the data
        - The metric is saturated — planting more doesn't register
        - By contrast, rich neighborhoods span a wide range (-8 to 0.6)
        
        **The implication:** You cannot "plant your way" out of climate inequality. 
        The physics of dense urban fabric limits what trees can do.
        """)
        
        fig = go.Figure(go.Bar(
            x=['Rich Neighborhoods', 'Poor Neighborhoods'], y=[7.9, 64.3],
            marker_color=['#2ecc71', '#e74c3c'],
            text=['7.9%', '64.3%'], textposition='outside',
            textfont=dict(size=18, color='white')
        ))
        fig.update_layout(
            title="% of tracts at tree-cover ceiling",
            yaxis_title="% of tracts", yaxis_range=[0, 80],
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'), height=350
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        <div class="narration-box">
            <div class="speaker">📡 CASE COMMANDER:</div>
            <div class="text">
                "Trees can't save the poor. But there's another option: <b>cool roofs</b>. 
                <b>Final mission:</b> choose the intervention. The city has one budget. 
                What do you recommend?"
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("➡️ PROCEED TO FINAL CHAPTER"):
            go_next()

# ============================================
# CHAPTER 6: THE SOLUTION
# ============================================
elif st.session_state.chapter == 6:
    st.markdown("## 🏠 Chapter 6: The Solution")
    st.markdown("""
    <div class="narration-box">
        <div class="speaker">📡 CASE COMMANDER:</div>
        <div class="text">
            "Trees failed. But cool roofs — reflective materials that reduce heat 
            absorption — might be the answer.<br><br>
            <b>Your final mission:</b> choose the city's strategy."
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    choice = st.radio("🎯 Submit your policy recommendation:", [
        "🌳 Plant more trees",
        "🏠 Install cool reflective roofs",
        "🔀 Do both simultaneously"
    ], key="ch6_choice")
    
    if st.button("🎯 SUBMIT VERDICT"):
        fig = go.Figure(go.Bar(
            x=['Current', 'Trees Only', 'Cool Roofs', 'Combined'],
            y=[48.67, 48.70, 48.31, 48.32],
            marker_color=['#7f8c8d', '#e74c3c', '#3498db', '#9b59b6'],
            text=['48.67°C', '+0.04°C', '-0.36°C', '-0.35°C'],
            textposition='outside', textfont=dict(size=14, color='white')
        ))
        fig.update_layout(
            title="Intervention Simulation: Poor Neighborhoods",
            yaxis_title="Mean LST (°C)", yaxis_range=[48, 49.5],
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'), height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        if "Cool" in choice or "both" in choice:
            st.success("✅ CORRECT, Detective. Cool roofs are the only effective intervention.")
        else:
            st.warning("⚠️ Trees alone won't work due to the data ceiling. Cool roofs are the answer.")
        
        st.markdown('<div class="clue-found">🔍 CLUE FOUND: Cool Roofs → -0.36°C. Trees → +0.04°C.</div>', unsafe_allow_html=True)
        award("solution", "Cool roofs (-0.36°C) vs trees (+0.04°C)")
        
        if st.button("🏆 CLOSE THE CASE"):
            go_next()

# ============================================
# FINAL: CASE CLOSED
# ============================================
elif st.session_state.chapter >= 7:
    st.balloons()
    
    st.markdown("""
    <div style="text-align:center; padding: 40px 20px;">
        <div style="font-size: 6rem;">🏆</div>
        <h1 style="font-size: 3rem; letter-spacing: 5px;">CASE CLOSED</h1>
        <p style="font-size: 1.3rem; color: #f39c12;">Detective, you have solved the Milan Heat Case.</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Evidence Collected", f"{len(st.session_state.evidence)}/6")
    c2.metric("XP Earned", st.session_state.xp)
    c3.metric("Rank", "🕵️ Climate Detective Master")
    
    st.markdown("---")
    st.markdown("### 📋 Evidence Collected")
    evidence_texts = {
        "gap": "6.87°C difference between Duomo and Park",
        "loneliness": "Loneliness is the strongest predictor of heat (+0.083°C)",
        "trend": "Poor neighborhoods heat 4% faster — gap widens every decade",
        "industry": "59.2% of heat anomalies occur in industrial zones (4.3x baseline)",
        "tree_trap": "64.3% of poor tracts are at the tree-cover ceiling — trees don't work",
        "solution": "Cool roofs (-0.36°C) are the only effective intervention"
    }
    for i, key in enumerate(st.session_state.evidence, 1):
        st.markdown(f'<div class="case-file"><b>CLUE {i}:</b> {evidence_texts.get(key, key)}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ⚖️ Final Verdict")
    st.markdown("""
    <div class="narration-box">
        <div class="speaker">📡 CASE COMMANDER:</div>
        <div class="text">
            "Detective, your investigation reveals:<br><br>
            • Milan's heat differs by <b>6.87°C</b> across 300m<br>
            • Poor neighborhoods heat <b>4% faster</b> every decade<br>
            • <b>59.2%</b> of anomalies come from industry<br>
            • <b>Loneliness</b>, not poverty, is the real face of vulnerability<br>
            • Trees can't fix it — <b>64.3%</b> of poor tracts are at the data ceiling<br>
            • <b>Cool roofs</b> are the only effective intervention (-0.36°C)<br><br>
            <b>571,146 people</b> (40.8% of Milan) live in climate risk zones.<br>
            Your investigation gives them a voice."
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 REPLAY INVESTIGATION"):
            reset()
    with c2:
        st.markdown("""
        <a href="https://github.com/marybilik" target="_blank" style="text-decoration:none;">
            <div style="background:#3498db; color:white; padding:14px; border-radius:8px; text-align:center; font-weight:bold; cursor:pointer;">
                📂 VIEW FULL NOTEBOOK
            </div>
        </a>
        """, unsafe_allow_html=True)
