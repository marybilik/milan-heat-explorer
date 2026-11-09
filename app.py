import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

st.set_page_config(page_title="Milan Heat Detective", page_icon="🕵️", layout="wide", initial_sidebar_state="collapsed")

# ============================================
# CSS (Detective Vibe)
# ============================================
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; max-width: 95%; }
    h1, h2, h3 { font-family: 'Helvetica Neue', sans-serif; }
    .hero-title { font-size: 3rem; font-weight: 900; background: linear-gradient(135deg, #1a1a2e, #e74c3c); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
    
    .dossier-card { background: linear-gradient(135deg, #1a1a2e, #16213e); color: white; padding: 25px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); height: 100%; }
    .dossier-tag { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin: 3px; }
    .tag-danger { background: #e74c3c; }
    .tag-warn { background: #e67e22; }
    .tag-ok { background: #27ae60; }
    
    .story-box { background: #fff; border: 2px solid #e74c3c; border-radius: 10px; padding: 20px; box-shadow: 0 4px 20px rgba(231, 76, 60, 0.15); }
    .story-box h3 { color: #e74c3c; margin-top: 0; }
    
    .metric-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border-left: 4px solid #e74c3c; }
    .stApp { background: #f0f2f6; }
</style>
""", unsafe_allow_html=True)

# ============================================
# ЗАГРУЗКА
# ============================================
@st.cache_data
def load_data():
    gdf = gpd.read_file("app_data.geojson")
    ts = pd.read_csv("time_series.csv") if os.path.exists("time_series.csv") else None
    # Центроиды для карты (clickable)
    gdf['cx'] = gdf.geometry.centroid.x
    gdf['cy'] = gdf.geometry.centroid.y
    return gdf, ts

gdf, ts = load_data()

# State
if 'selected_tract' not in st.session_state:
    st.session_state.selected_tract = None
if 'comparison' not in st.session_state:
    st.session_state.comparison = []

# ============================================
# ХЕДЕР
# ============================================
st.markdown('<div class="hero-title">🕵️ Milan Heat Detective</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#666;font-size:1.1rem;">Investigate climate inequality. Click a neighborhood. Solve the mystery.</p>', unsafe_allow_html=True)
st.markdown("---")

# ============================================
# NAVIGATION
# ============================================
tab1, tab2, tab3 = st.tabs(["🔍 Detective Mode", "⏳ Time Machine", "🎮 Intervention Simulator"])

# ============================================
# TAB 1: DETECTIVE MODE
# ============================================
with tab1:
    col_map, col_info = st.columns([2, 1])
    
    with col_map:
        st.markdown("### 👆 Click any point to investigate")
        
        fig = go.Figure(go.Scattermap(
            lat=gdf['cy'], lon=gdf['cx'],
            mode='markers',
            marker=dict(
                size=gdf['mean_lst'] * 0.3,  # размер = температура
                color=gdf['mean_lst'],
                colorscale=[[0, '#2c3e50'], [0.5, '#e74c3c'], [1, '#ff0000']],
                showscale=True,
                colorbar=dict(title="LST °C", thickness=15),
                opacity=0.85
            ),
            text=gdf['SEZ2011'],
            hovertemplate="<b>Tract %{text}</b><br>Temp: %{marker.color:.1f}°C<extra></extra>",
            customdata=list(range(len(gdf)))
        ))
        fig.update_layout(
            map=dict(style="carto-darkmatter", center=dict(lat=45.4642, lon=9.19), zoom=10.5),
            height=650, margin=dict(l=0, r=0, t=0, b=0), showlegend=False
        )
        
        event = st.plotly_chart(fig, on_select="rerun", selection_mode="points", use_container_width=True, key="detective_map")
        
        # Если кликнули — обновляем session_state
        if event and event.get('selection', {}).get('points'):
            point = event['selection']['points'][0]
            tract_idx = point['customdata']
            st.session_state.selected_tract = gdf.iloc[tract_idx]['SEZ2011']
    
    with col_info:
        if st.session_state.selected_tract is None:
            st.markdown("""
            <div class="story-box">
                <h3>🎯 Your mission</h3>
                <p>Milan is getting hotter. But <strong>not for everyone</strong>. Your task: find the neighborhoods where physical heat meets social vulnerability.</p>
                <p>👈 Click on any point on the map to open its case file.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            tract = gdf[gdf['SEZ2011'] == st.session_state.selected_tract].iloc[0]
            temp = tract['mean_lst']
            svi = tract['social_vulnerability']
            trees = tract['tree_cover_density']
            concrete = tract['impervious_x']
            residual = tract['residuals']
            faces = tract['num_faces'] if 'num_faces' in tract else 0
            
            # Определяем "статус"
            if temp > 52:
                temp_tag = '<span class="dossier-tag tag-danger">🔥 EXTREME HEAT</span>'
            elif temp > 48:
                temp_tag = '<span class="dossier-tag tag-warn">🌡️ HOT</span>'
            else:
                temp_tag = '<span class="dossier-tag tag-ok">✅ MILD</span>'
            
            if residual > 2:
                anom_tag = '<span class="dossier-tag tag-danger">🏭 INDUSTRIAL ANOMALY</span>'
            else:
                anom_tag = ''
            
            if faces >= 2:
                face_tag = f'<span class="dossier-tag tag-danger">⚠️ {faces} OVERLAPPING RISKS</span>'
            elif faces == 1:
                face_tag = '<span class="dossier-tag tag-warn">⚠️ 1 RISK</span>'
            else:
                face_tag = ''
            
            st.markdown(f"""
            <div class="dossier-card">
                <div style="font-size:0.8rem;opacity:0.7;letter-spacing:2px;">CASE FILE</div>
                <h2 style="color:white;margin:5px 0 15px 0;">Tract {tract['SEZ2011']}</h2>
                {temp_tag} {anom_tag} {face_tag}
                <hr style="border-color:rgba(255,255,255,0.2);">
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;margin-top:15px;">
                    <div>
                        <div style="font-size:0.7rem;opacity:0.6;">TEMPERATURE</div>
                        <div style="font-size:1.5rem;font-weight:bold;">{temp:.1f}°C</div>
                    </div>
                    <div>
                        <div style="font-size:0.7rem;opacity:0.6;">VULNERABILITY</div>
                        <div style="font-size:1.5rem;font-weight:bold;">{svi:.2f}</div>
                    </div>
                    <div>
                        <div style="font-size:0.7rem;opacity:0.6;">TREE COVER</div>
                        <div style="font-size:1.2rem;">{trees:.2f}</div>
                    </div>
                    <div>
                        <div style="font-size:0.7rem;opacity:0.6;">CONCRETE</div>
                        <div style="font-size:1.2rem;">{concrete:.2f}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Автоматический "детективный вывод"
            st.markdown("**🔎 Detective note:**")
            notes = []
            if residual > 2:
                notes.append("This area is hotter than concrete alone explains — likely industrial activity.")
            if trees > 0.5:
                notes.append("Already saturated with trees (data ceiling) — planting more won't help.")
            if svi > 1:
                notes.append("High social vulnerability — this is a priority for intervention.")
            if temp > 52:
                notes.append("Extreme heat zone (>52°C) — health risk for elderly and isolated residents.")
            
            for note in notes:
                st.markdown(f"- {note}")
            
            # Кнопка добавления в сравнение
            if st.button("➕ Add to Comparison"):
                if st.session_state.selected_tract not in st.session_state.comparison:
                    st.session_state.comparison.append(st.session_state.selected_tract)
                    st.success(f"Added! Total: {len(st.session_state.comparison)}")
    
    # Comparison panel
    if st.session_state.comparison:
        st.markdown("---")
        st.markdown("### ⚖️ Comparison Mode")
        
        comp_cols = st.columns(len(st.session_state.comparison) + 1)
        
        for i, tract_id in enumerate(st.session_state.comparison[:3]):
            with comp_cols[i]:
                t = gdf[gdf['SEZ2011'] == tract_id].iloc[0]
                st.metric(f"Tract {tract_id[-4:]}", f"{t['mean_lst']:.1f}°C", f"SVI: {t['social_vulnerability']:.2f}")
        
        with comp_cols[-1]:
            if st.button("🗑️ Clear"):
                st.session_state.comparison = []
                st.rerun()

# ============================================
# TAB 2: TIME MACHINE
# ============================================
with tab2:
    st.markdown("### ⏳ Watch the gap widen over time")
    
    if ts is not None:
        ts['Q1_Smooth'] = ts['Q1_Rich'].rolling(3).mean()
        ts['Q4_Smooth'] = ts['Q4_Poor'].rolling(3).mean()
        
        # Range slider
        year_range = st.slider("Select year range:", 2014, 2023, (2014, 2023))
        ts_filtered = ts[(ts['Year'] >= year_range[0]) & (ts['Year'] <= year_range[1])]
        
        # Animated chart with frames
        frames = []
        for i in range(len(ts_filtered)):
            frames.append(go.Frame(
                data=[
                    go.Scatter(x=ts_filtered['Year'].iloc[:i+1], y=ts_filtered['Q1_Smooth'].iloc[:i+1], 
                              mode='lines+markers', line=dict(color='#2ecc71', width=4), name='Rich (Q1)'),
                    go.Scatter(x=ts_filtered['Year'].iloc[:i+1], y=ts_filtered['Q4_Smooth'].iloc[:i+1],
                              mode='lines+markers', line=dict(color='#e74c3c', width=4), name='Poor (Q4)'),
                ],
                name=str(ts_filtered['Year'].iloc[i])
            ))
        
        fig = go.Figure(
            data=[
                go.Scatter(x=[], y=[], mode='lines+markers', line=dict(color='#2ecc71', width=4), name='Rich (Q1)'),
                go.Scatter(x=[], y=[], mode='lines+markers', line=dict(color='#e74c3c', width=4), name='Poor (Q4)'),
            ],
            frames=frames
        )
        
        # Add Play button
        fig.update_layout(
            updatemenus=[dict(
                type="buttons", showactive=False,
                x=0.05, y=1.15, xanchor="left",
                buttons=[
                    dict(label="▶️ Play", method="animate",
                         args=[None, {"frame": {"duration": 800, "redraw": True}, "fromcurrent": True}]),
                    dict(label="⏸️ Pause", method="animate",
                         args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}])
                ]
            )],
            title="The Widening Heat Gap (click Play to animate)",
            xaxis_title="Year", yaxis_title="Mean Summer LST (°C)",
            height=500, plot_bgcolor='white', paper_bgcolor='white',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True, key="time_machine")
        
        # Dynamic insight based on selected range
        st.markdown("---")
        st.markdown("### 📊 Insight for this period")
        
        c1, c2, c3 = st.columns(3)
        gap_start = ts_filtered['Q4_Smooth'].iloc[0] - ts_filtered['Q1_Smooth'].iloc[0]
        gap_end = ts_filtered['Q4_Smooth'].iloc[-1] - ts_filtered['Q1_Smooth'].iloc[-1]
        gap_change = gap_end - gap_start
        
        c1.metric("Starting Gap", f"{gap_start:.2f}°C")
        c2.metric("Ending Gap", f"{gap_end:.2f}°C", f"{gap_change:+.2f}°C")
        c3.metric("Years Analyzed", f"{len(ts_filtered)}")
        
        if gap_change > 0.1:
            st.error(f"🚨 **The gap WIDENED by {gap_change:.2f}°C** over this period. Inequality is accelerating.")
        elif gap_change < -0.1:
            st.success(f"✅ The gap narrowed by {abs(gap_change):.2f}°C. But is this sustainable?")
        else:
            st.info(f"ℹ️ The gap remained stable at ~{gap_end:.2f}°C.")
    
    else:
        st.warning("⚠️ `time_series.csv` не найден.")

# ============================================
# TAB 3: SIMULATOR
# ============================================
with tab3:
    st.markdown("### 🎮 What if we intervene?")
    
    scenario = st.selectbox("Choose intervention:",
        ["🌳 Plant Trees", "🏠 Cool Roofs", "🔀 Combined"])
    
    scenarios_data = {
        "🌳 Plant Trees": {"values": [48.67, 48.70], "color": "#e74c3c", "reason": "Data ceiling — no cooling possible."},
        "🏠 Cool Roofs": {"values": [48.67, 48.31], "color": "#3498db", "reason": "Reflective surfaces reduce temperature by 0.36°C."},
        "🔀 Combined": {"values": [48.67, 48.32], "color": "#9b59b6", "reason": "Slightly less effective than roofs alone."}
    }
    
    data = scenarios_data[scenario]
    
    # Animated bar chart with frames
    frames = [go.Frame(
        data=[go.Bar(x=['Current', 'After'], y=data['values'], marker_color=['#e74c3c', data['color']],
                     text=[f'{v:.2f}°C' for v in data['values']], textposition='auto')],
        name=scenario
    )]
    
    fig = go.Figure(
        data=[go.Bar(x=['Current', 'After'], y=[48.67, 48.67], marker_color=['#e74c3c', '#3498db'])],
        frames=frames
    )
    
    fig.update_layout(
        title=f"Intervention: {scenario}",
        yaxis_title="Mean Surface Temperature (°C)",
        yaxis_range=[48, 49.5], height=450, plot_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True, key="sim_animated")
    
    st.markdown(f'<div class="story-box"><h3>📋 Verdict</h3><p>{data["reason"]}</p></div>', unsafe_allow_html=True)
