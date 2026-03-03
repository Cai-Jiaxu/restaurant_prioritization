import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Hungry Hub · CRM",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# Design Tokens — Qiespend Palette
# ─────────────────────────────────────────────
D = dict(
    bg          = "#020617",   # slate-900 deepest
    surface     = "#0f172a",   # slate-800 card bg
    card        = "#27272a",   # zinc-800
    border      = "#3f3f46",   # zinc-700
    text_pri    = "#f1f5f9",   # slate-50
    text_sec    = "#94a3b8",   # slate-400
    lime        = "#d4f03f",   # primary accent
    lime_dim    = "#1a2a00",   # lime background dim
    green       = "#22c55e",   # increase / received
    red         = "#ef4444",   # decrease / failed
    green_dim   = "#052e16",
    red_dim     = "#450a0a",
    purple      = "#a78bfa",   # hidden gem
    slate_mid   = "#64748b",   # stable
)

SEG_COLOR = {
    "Rising":     D["green"],
    "Hidden Gem": D["purple"],
    "Stable":     D["slate_mid"],
    "Declining":  D["red"],
}

SEG_BG = {
    "Rising":     D["green_dim"],
    "Hidden Gem": "#2e1065",
    "Stable":     "#1c1917",
    "Declining":  D["red_dim"],
}

status_css = lambda s: (D["green"], D["green_dim"]) if s in ("Rising","Hidden Gem","Stable") else (D["red"], D["red_dim"])

# ─────────────────────────────────────────────
# CSS — Qiespend Design System
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {D['bg']};
    color: {D['text_pri']};
}}
/* ── Full-width layout: offset below Streamlit's native header ── */
.block-container {{
    padding-top: 3.75rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 100% !important;
}}

/* ── Multiselect tags: black text on lime background ── */
[data-baseweb="tag"] {{
    color: #000 !important;
}}
[data-baseweb="tag"] span,
[data-baseweb="tag"] [data-testid="stMultiSelectDeleteButton"],
[data-baseweb="tag"] svg {{
    color: #000 !important;
    fill: #000 !important;
}}

/* ══ TOP BAR ══ */
.topbar {{
    display: flex; align-items: center; justify-content: space-between;
    background: {D['surface']}; border-bottom: 1px solid {D['border']};
    padding: 14px 32px; position: sticky; top: 0; z-index: 50;
}}
.topbar-logo {{
    font-size: 1.15rem; font-weight: 800; letter-spacing: -0.03em; color: {D['text_pri']};
    display: flex; align-items: center; gap: 10px;
}}
.topbar-logo .dot {{ color: {D['lime']}; }}
.topbar-badge {{
    background: {D['lime_dim']}; color: {D['lime']};
    font-size: 0.7rem; font-weight: 700; padding: 4px 12px; border-radius: 20px;
    border: 1px solid {D['lime']}44; letter-spacing: 0.06em;
}}
.topbar-right {{ display: flex; align-items: center; gap: 12px; }}
.topbar-meta {{ text-align: right; }}
.topbar-val {{ font-size: 1rem; font-weight: 700; color: {D['text_pri']}; }}
.topbar-lbl {{ font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.08em; color: {D['text_sec']}; }}
.topbar-divider {{ width:1px; height:32px; background:{D['border']}; }}

/* ══ PAGE WRAPPER ══ */
.page-wrap {{ padding: 28px 32px; }}

/* ══ SECTION HEADER ══ */
.sec-row {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 20px;
}}
.sec-title {{
    font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em; color: {D['text_pri']};
}}
.sec-sub {{
    font-size: 0.8rem; color: {D['text_sec']}; margin-top: 2px;
}}

/* ══ STAT CARDS ══ */
.stat-grid {{
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 18px; margin-bottom: 24px;
}}
.stat-card {{
    background: {D['card']}; border: 1px solid {D['border']};
    border-radius: 14px; padding: 22px 22px 18px;
    transition: all 0.2s ease; position: relative; overflow: hidden;
}}
.stat-card:hover {{
    border-color: {D['lime']}55; transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(212,240,63,0.08);
}}
.stat-card-top {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 12px;
}}
.stat-icon {{
    width: 36px; height: 36px; border-radius: 10px;
    background: {D['lime_dim']}; color: {D['lime']};
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
}}
.stat-label {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: {D['text_sec']}; font-weight: 600; }}
.stat-value {{ font-size: 2.1rem; font-weight: 800; color: {D['text_pri']}; letter-spacing: -0.04em; line-height: 1; margin: 6px 0 10px; }}
.stat-ctx {{ font-size: 0.75rem; color: {D['text_sec']}; }}
.stat-ctx span {{ color: {D['lime']}; font-weight: 700; }}

/* Progress bars in AI card */
.ai-bar-row {{ display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }}
.ai-bar-lbl {{ font-size: 0.7rem; color: {D['text_sec']}; width: 80px; flex-shrink: 0; }}
.ai-bar-track {{ flex: 1; background: {D['border']}; border-radius: 4px; height: 5px; }}
.ai-bar-fill {{ height: 5px; border-radius: 4px; background: {D['lime']}; }}
.ai-bar-pct {{ font-size: 0.68rem; color: {D['text_sec']}; width: 30px; text-align: right; }}

/* ══ FEATURED AREA ══ */
.feat-grid {{
    display: grid; grid-template-columns: 8fr 4fr;
    gap: 18px; margin-bottom: 24px;
}}
.feat-chart-card {{
    background: {D['card']}; border: 1px solid {D['border']};
    border-radius: 14px; padding: 26px;
}}
.feat-balance {{ font-size: 2.4rem; font-weight: 800; letter-spacing: -0.04em; color: {D['text_pri']}; margin-bottom: 4px; }}
.feat-bal-lbl {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: {D['text_sec']}; margin-bottom: 16px; }}
.feat-btns {{ display: flex; gap: 10px; margin-bottom: 22px; }}
.btn-outline {{
    border: 1.5px solid {D['border']}; background: transparent;
    color: {D['text_pri']}; font-size: 0.85rem; font-weight: 600;
    padding: 9px 20px; border-radius: 10px; cursor: pointer;
}}
.btn-lime {{
    background: {D['lime']}; color: #000; font-size: 0.85rem; font-weight: 700;
    padding: 9px 20px; border-radius: 10px; border: none; cursor: pointer;
}}
.tab-row {{ display: flex; gap: 6px; margin-bottom: 16px; }}
.tab-chip {{
    font-size: 0.8rem; font-weight: 600; padding: 6px 16px;
    border-radius: 8px; cursor: pointer;
    background: {D['surface']}; color: {D['text_sec']};
    border: 1px solid {D['border']};
}}
.tab-chip.active {{
    background: {D['lime_dim']}; color: {D['lime']};
    border-color: {D['lime']}44;
}}

/* ML Model Card */
.model-card {{
    background: linear-gradient(135deg, #1a2a00 0%, #0f172a 60%, {D['card']} 100%);
    border: 1px solid {D['lime']}33;
    border-radius: 14px; padding: 26px;
    position: relative; overflow: hidden;
}}
.model-card::before {{
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 160px; height: 160px; border-radius: 50%;
    background: radial-gradient({D['lime']}22, transparent 70%);
}}
.model-card-icon {{ font-size: 2rem; margin-bottom: 14px; }}
.model-card-title {{ font-size: 1.1rem; font-weight: 800; color: {D['text_pri']}; margin-bottom: 6px; }}
.model-card-desc {{ font-size: 0.82rem; color: {D['text_sec']}; line-height: 1.6; margin-bottom: 20px; }}
.model-stat-row {{ display: flex; justify-content: space-between; margin-bottom: 12px; }}
.model-stat-val {{ font-size: 1.6rem; font-weight: 800; color: {D['lime']}; letter-spacing: -0.03em; }}
.model-stat-lbl {{ font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em; color: {D['text_sec']}; margin-top: 2px; }}
.model-btn {{
    display: block; width: 100%;
    background: {D['lime']}; color: #000; font-weight: 700; font-size: 0.85rem;
    padding: 10px; border-radius: 10px; text-align: center; border: none; cursor: pointer;
    margin-top: 16px;
}}

/* ══ RESTAURANT TABLE ══ */
.tbl-wrap {{
    background: {D['card']}; border: 1px solid {D['border']};
    border-radius: 14px; overflow: hidden; margin-bottom: 24px;
}}
.tbl-header {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 22px; border-bottom: 1px solid {D['border']};
    flex-wrap: wrap; gap: 10px;
}}
.tbl-search {{
    background: {D['surface']}; border: 1px solid {D['border']};
    border-radius: 8px; padding: 8px 14px; color: {D['text_pri']};
    font-size: 0.85rem; min-width: 240px; font-family: inherit;
}}
.tbl {{
    width: 100%; border-collapse: collapse;
}}
.tbl th {{
    background: {D['surface']}; font-size: 0.7rem; text-transform: uppercase;
    letter-spacing: 0.08em; color: {D['text_sec']}; font-weight: 700;
    padding: 12px 18px; text-align: left; border-bottom: 1px solid {D['border']};
}}
.tbl td {{
    padding: 13px 18px; font-size: 0.875rem; color: {D['text_pri']};
    border-bottom: 1px solid {D['border']}66;
}}
.tbl tr:last-child td {{ border-bottom: none; }}
.tbl tr:hover td {{ background: {D['surface']}88; }}
.badge {{
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 0.72rem; font-weight: 700; padding: 3px 10px;
    border-radius: 20px; letter-spacing: 0.04em; white-space: nowrap;
}}
.badge-green {{ background: {D['green_dim']}; color: {D['green']}; border: 1px solid {D['green']}33; }}
.badge-red   {{ background: {D['red_dim']};   color: {D['red']};   border: 1px solid {D['red']}33; }}
.badge-lime  {{ background: {D['lime_dim']};  color: {D['lime']};  border: 1px solid {D['lime']}33; }}
.badge-grey  {{ background: #1c1917; color: {D['slate_mid']}; border: 1px solid {D['slate_mid']}33; }}
.tbl-foot {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 22px; border-top: 1px solid {D['border']};
    font-size: 0.8rem; color: {D['text_sec']};
}}
.page-btn {{
    background: {D['surface']}; border: 1px solid {D['border']};
    color: {D['text_pri']}; font-size: 0.8rem; padding: 5px 12px;
    border-radius: 6px; cursor: pointer;
}}
.page-btn.active {{
    background: {D['lime_dim']}; border-color: {D['lime']}44; color: {D['lime']};
}}

/* ══ SIDEBAR ══ */
[data-testid="stSidebar"] {{
    background: {D['surface']} !important;
    border-right: 1px solid {D['border']} !important;
}}

/* ══ TAB OVERRIDE ══ */
.stTabs [data-baseweb="tab-list"] {{
    background: {D['surface']}; border-radius: 10px; padding: 5px;
    border: 1px solid {D['border']}; gap: 3px; margin-bottom: 18px;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 7px; padding: 8px 20px;
    font-size: 0.875rem; font-weight: 600; color: {D['text_sec']};
}}
.stTabs [data-baseweb="tab"][aria-selected="true"] {{
    background: {D['lime_dim']} !important;
    color: {D['lime']} !important;
    border: 1px solid {D['lime']}44 !important;
}}

/* DataFrame */
div[data-testid="stDataFrame"] {{
    border: 1px solid {D['border']}; border-radius: 12px; overflow: hidden;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Data
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(BASE_DIR, "..", "Data", "Processed")

REGION_MAP = {
    0:"Unknown",1:"CBD",2:"Sukhumvit",3:"Silom/Sathon",
    4:"Riverside",5:"North/Ari",6:"Other",7:"Provincial",
    8:"Ratchada/Rama9",9:"Outer Bangkok"
}
CUISINE_MAP = {
    0:"Other",1:"Thai",2:"Japanese",3:"Italian",
    4:"Chinese",5:"Buffet",6:"Seafood",7:"Steak/Grill"
}

@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(DATA_DIR, "Dashboard_Predictions.csv"))
    master = pd.read_csv(os.path.join(DATA_DIR, "master_all_data.csv"))
    cols = ['restaurant_id','restaurant_name_en','name','primary_cuisine',
            'total_revenue','total_bookings','total_guests','avg_revenue_per_booking',
            'no_show_rate','internal_score','places','primary_place']
    cols = [c for c in cols if c in master.columns]
    df = pd.merge(df, master[cols], on='restaurant_id', how='left')
    df['region']          = df['region_encoded'].map(REGION_MAP).fillna("Unknown")
    df['cuisine']         = df['cuisine_encoded'].map(CUISINE_MAP).fillna("Other")
    df['restaurant_name'] = df['restaurant_name_en'].fillna(df.get('name','Unknown'))
    return df

df = load_data()

# ─────────────────────────────────────────────
# Sidebar Filters
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:6px 0 10px;">
        <div style="font-size:1.05rem;font-weight:800;color:{D['text_pri']};letter-spacing:-0.02em;">
            🍽️ HungryHub<span style="color:{D['lime']};">.</span>
        </div>
        <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.1em;color:{D['text_sec']};">
            Partner CRM
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Segment counts
    st.markdown(f"<div style='font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;color:{D['text_sec']};font-weight:700;margin-bottom:5px;'>Active Segments</div>", unsafe_allow_html=True)
    for seg, col in SEG_COLOR.items():
        cnt = (df['ML_Predicted_Segment'] == seg).sum()
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
             padding:5px 8px;border-radius:6px;margin-bottom:3px;
             background:{SEG_BG.get(seg,'#1c1917')};">
            <span style="font-size:0.8rem;color:{col};font-weight:600;">{seg}</span>
            <span style="background:{col}22;color:{col};font-size:0.66rem;
                  font-weight:700;padding:2px 7px;border-radius:10px;">{cnt}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"<div style='border-top:1px solid {D['border']};margin:8px 0 6px;'></div>", unsafe_allow_html=True)

    # Filters
    st.markdown(f"<div style='font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;color:{D['text_sec']};font-weight:700;margin-bottom:4px;'>Filters</div>", unsafe_allow_html=True)
    seg_f     = st.multiselect("Segment", sorted(df['ML_Predicted_Segment'].unique()), default=sorted(df['ML_Predicted_Segment'].unique()), label_visibility="collapsed")
    region_f  = st.multiselect("Region",  sorted(df['region'].unique()),               default=sorted(df['region'].unique()),               label_visibility="collapsed")
    cuisine_f = st.multiselect("Cuisine", sorted(df['cuisine'].unique()),               default=sorted(df['cuisine'].unique()),               label_visibility="collapsed")
    _score_max = int(df['ml_priority_score'].max()) + 1
    _steps = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, min(_score_max, 55), _score_max]
    _steps = sorted(set(_steps))  # dedupe and sort
    st.markdown(f"<div style='font-size:0.72rem;color:{D['text_sec']};margin-bottom:4px;'>Min Priority Score</div>", unsafe_allow_html=True)
    min_score = st.select_slider(
        "Min Priority Score",
        options=_steps,
        value=0,
        label_visibility="collapsed"
    )
    st.markdown(f"<div style='font-size:0.7rem;color:{D['text_sec']};margin-top:2px;'>Showing scores ≥ <b style='color:{D['lime']};'>{min_score}</b></div>", unsafe_allow_html=True)

# Filter data
if not seg_f:     seg_f     = sorted(df['ML_Predicted_Segment'].unique())
if not region_f:  region_f  = sorted(df['region'].unique())
if not cuisine_f: cuisine_f = sorted(df['cuisine'].unique())

mask = (df['ML_Predicted_Segment'].isin(seg_f) & df['region'].isin(region_f) &
        df['cuisine'].isin(cuisine_f) & (df['ml_priority_score'] >= min_score))
dff = df[mask]

# ─────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────
total    = len(dff)
rising   = int((dff['ML_Predicted_Segment'] == 'Rising').sum())
hidden   = int((dff['ML_Predicted_Segment'] == 'Hidden Gem').sum())
declining= int((dff['ML_Predicted_Segment'] == 'Declining').sum())
stable   = int((dff['ML_Predicted_Segment'] == 'Stable').sum())
actionable = rising + hidden

total_rev = 0.0
concentration = "N/A"
avg_score = dff['ml_priority_score'].mean() if len(dff) > 0 else 0.0

if 'total_revenue' in dff.columns and len(dff) > 0:
    total_rev = float(dff['total_revenue'].sum())
    top20 = dff.nlargest(max(1, int(len(dff)*0.2)), 'total_revenue')['total_revenue'].sum()
    concentration = f"{top20/total_rev*100:.1f}%" if total_rev > 0 else "N/A"

seg_pcts = {s: int((dff['ML_Predicted_Segment']==s).sum()/max(total,1)*100) for s in SEG_COLOR}

# ─────────────────────────────────────────────
# TOP BAR
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
  <div style="display:flex;align-items:center;gap:14px;">
    <div class="topbar-logo">🍽️ HungryHub<span class="dot">.</span></div>
    <div class="topbar-badge">ML Engine v3 Active</div>
  </div>
  <div class="topbar-right">
    <div class="topbar-meta">
      <div class="topbar-val">{total:,}</div>
      <div class="topbar-lbl">Partners in view</div>
    </div>
    <div class="topbar-divider"></div>
    <div class="topbar-meta">
      <div class="topbar-val" style="color:{D['lime']};">{actionable}</div>
      <div class="topbar-lbl">Actionable</div>
    </div>
    <div class="topbar-divider"></div>
    <div class="topbar-meta">
      <div class="topbar-val" style="color:{D['red']};">{declining}</div>
      <div class="topbar-lbl">At-Risk</div>
    </div>
    <div class="topbar-divider"></div>
    <div style="font-size:0.75rem;color:{D['text_sec']};text-align:right;">
      <div style="font-weight:700;color:{D['text_pri']};">78.7%</div>
      <div>Model CV</div>
    </div>
  </div>
</div>
<div class="page-wrap">
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Section header
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="sec-row">
  <div>
    <div class="sec-title">Dashboard</div>
    <div class="sec-sub">Marketing resource allocation · Powered by ML classification</div>
  </div>
  <div style="display:flex;gap:10px;">
    <button class="btn-outline">📊 Generate Report</button>
    <button class="btn-lime">⬇️ Export</button>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# STAT CARDS ROW (4-column like Qiespend)
# ─────────────────────────────────────────────
rev_str = f"฿{total_rev:,.0f}" if total_rev > 0 else "N/A"
avg_bk  = float(dff['avg_revenue_per_booking'].mean()) if 'avg_revenue_per_booking' in dff.columns and len(dff)>0 else 0

st.markdown(f"""
<div class="stat-grid">

  <div class="stat-card">
    <div class="stat-card-top">
      <div class="stat-label">Rising Stars</div>
      <div class="stat-icon">⚡</div>
    </div>
    <div class="stat-value">{rising}</div>
    <div class="stat-ctx"><span>+{seg_pcts['Rising']}%</span> of portfolio</div>
  </div>

  <div class="stat-card">
    <div class="stat-card-top">
      <div class="stat-label">Hidden Gems</div>
      <div class="stat-icon" style="background:#2e1065;color:{D['purple']};">◆</div>
    </div>
    <div class="stat-value" style="color:{D['purple']};">{hidden}</div>
    <div class="stat-ctx"><span style="color:{D['purple']};">+{seg_pcts['Hidden Gem']}%</span> of portfolio</div>
  </div>

  <div class="stat-card">
    <div class="stat-card-top">
      <div class="stat-label">At-Risk (Declining)</div>
      <div class="stat-icon" style="background:{D['red_dim']};color:{D['red']};">⚠️</div>
    </div>
    <div class="stat-value" style="color:{D['red']};">{declining}</div>
    <div class="stat-ctx"><span style="color:{D['red']};">{seg_pcts['Declining']}%</span> of portfolio  · needs action</div>
  </div>

  <div class="stat-card">
    <div class="stat-card-top">
      <div class="stat-label">ML Segment Distribution</div>
      <div class="stat-icon">🧠</div>
    </div>
    <div class="stat-value">{actionable}</div>
    <div style="margin-top:4px;">
      <div class="ai-bar-row">
        <div class="ai-bar-lbl">Rising</div>
        <div class="ai-bar-track"><div class="ai-bar-fill" style="width:{seg_pcts['Rising']}%;"></div></div>
        <div class="ai-bar-pct">{seg_pcts['Rising']}%</div>
      </div>
      <div class="ai-bar-row">
        <div class="ai-bar-lbl">Hidden Gem</div>
        <div class="ai-bar-track"><div class="ai-bar-fill" style="width:{seg_pcts['Hidden Gem']}%;background:{D['purple']};"></div></div>
        <div class="ai-bar-pct">{seg_pcts['Hidden Gem']}%</div>
      </div>
      <div class="ai-bar-row">
        <div class="ai-bar-lbl">Stable</div>
        <div class="ai-bar-track"><div class="ai-bar-fill" style="width:{seg_pcts['Stable']}%;background:{D['slate_mid']};"></div></div>
        <div class="ai-bar-pct">{seg_pcts['Stable']}%</div>
      </div>
      <div class="ai-bar-row">
        <div class="ai-bar-lbl">Declining</div>
        <div class="ai-bar-track"><div class="ai-bar-fill" style="width:{seg_pcts['Declining']}%;background:{D['red']};"></div></div>
        <div class="ai-bar-pct">{seg_pcts['Declining']}%</div>
      </div>
    </div>
  </div>

</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FEATURED AREA: Bar Chart + Model Card
# ─────────────────────────────────────────────
# Prepare cuisine breakdown
cuisine_scores = dff.groupby('cuisine')['ml_priority_score'].mean().sort_values(ascending=False).reset_index()
top_cuisine    = cuisine_scores.iloc[0]['cuisine'] if len(cuisine_scores) > 0 else ""
bar_colors     = [D['lime'] if c == top_cuisine else D['border'] for c in cuisine_scores['cuisine']]

fig_bar = go.Figure(go.Bar(
    x=cuisine_scores['cuisine'], y=cuisine_scores['ml_priority_score'],
    marker=dict(color=bar_colors, line=dict(width=0)),
    text=[f"{v:.0f}" for v in cuisine_scores['ml_priority_score']],
    textposition='inside', insidetextanchor='end',
    textfont=dict(size=11, color='#000000')
))
fig_bar.update_layout(
    template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    height=250, margin=dict(l=0, r=0, t=30, b=0), showlegend=False,
    xaxis=dict(showgrid=False, tickfont=dict(size=11, color=D['text_sec'])),
    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)', zeroline=False,
               tickfont=dict(size=10, color=D['text_sec'])),
    font=dict(family='Inter')
)

no_show_avg = float(dff['no_show_rate'].mean()) if 'no_show_rate' in dff.columns and len(dff)>0 else 0
total_bk    = int(dff['total_bookings'].sum()) if 'total_bookings' in dff.columns else 0

st.markdown(f"""
<div class="feat-chart-card">
  <div style="text-align:center;">
    <div class="feat-bal-lbl">Total Actionable Partners</div>
    <div class="feat-balance">{actionable} <span style="font-size:1.2rem;color:{D['text_sec']};font-weight:500;">targets</span></div>
    <div class="feat-btns" style="justify-content:center;">
      <button class="btn-outline">🔍 Explore Partners</button>
      <button class="btn-lime">⚡ Action Queue</button>
    </div>
  </div>
  <div class="tab-row" style="justify-content:center;margin-top:16px;">
    <div class="tab-chip active">Bar view — Avg Score by Cuisine</div>
    <div class="tab-chip">Line view — Segment Trend</div>
  </div>
</div>""", unsafe_allow_html=True)
st.plotly_chart(fig_bar, use_container_width=True)
st.markdown(f"<div style='font-size:0.75rem;color:{D['text_sec']};text-align:center;margin-top:-8px;padding-bottom:4px;'>Highlighted: <b style='color:{D['lime']};'>{top_cuisine}</b> (highest avg. priority score)</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RESTAURANT TABLE (Qiespend transaction style)
# ─────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;margin-top:8px;">
  <div>
    <div class="sec-title">Priority Marketing List</div>
    <div class="sec-sub">Restaurants ranked by ML priority score — the action queue for marketing allocation</div>
  </div>
</div>""", unsafe_allow_html=True)

tbl_top   = dff.sort_values('ml_priority_score', ascending=False).reset_index(drop=True)
tbl_top.index += 1
actionable_only = tbl_top[tbl_top['ML_Predicted_Segment'].isin(['Rising','Hidden Gem'])].copy()

tab_a, tab_b, tab_c, tab_d = st.tabs([
    "⚡ Priority List", "🗺️ Portfolio Map", "📊 Segment Analysis", "🔍 Partner Explorer"
])

# ─── Tab 1: Restaurant Table
with tab_a:
    show_all = st.toggle("Show all segments", value=False)
    view_df  = tbl_top if show_all else actionable_only

    PAGE_SIZE = 8
    if 'tbl_page' not in st.session_state: st.session_state.tbl_page = 1
    total_pages = max(1, (len(view_df) + PAGE_SIZE - 1) // PAGE_SIZE)
    page = st.session_state.tbl_page
    start = (page-1)*PAGE_SIZE; end = start+PAGE_SIZE
    page_df = view_df.iloc[start:end]

    def seg_badge(seg):
        if seg in ("Rising","Hidden Gem"): return f'<span class="badge badge-green">{seg}</span>'
        if seg == "Declining":             return f'<span class="badge badge-red">{seg}</span>'
        return f'<span class="badge badge-grey">{seg}</span>'

    rows_html = ""
    for rank, (_, r) in enumerate(page_df.iterrows(), start=start+1):
        name = str(r['restaurant_name'])[:32]
        seg  = r['ML_Predicted_Segment']
        sc   = f"{r['ml_priority_score']:.1f}"
        gmap = f"{r['gmaps_rating']:.1f} ⭐" if 'gmaps_rating' in r and float(r.get('gmaps_rating',0)) > 0 else "—"
        mom  = f"{r['momentum_score']:.1f}" if 'momentum_score' in r and pd.notna(r.get('momentum_score')) else "—"
        p_r  = f"{float(r.get('prob_rising',0)):.0%}"
        p_h  = f"{float(r.get('prob_hidden_gem',0)):.0%}"
        sc_color = D['lime'] if float(r['ml_priority_score']) > 70 else (D['green'] if float(r['ml_priority_score']) > 40 else D['text_sec'])
        rows_html += f"""
        <tr>
          <td style="color:{D['text_sec']};font-size:0.75rem;">#{rank}</td>
          <td><div style="font-weight:600;color:{D['text_pri']};">{name}</div>
              <div style="font-size:0.72rem;color:{D['text_sec']};">{r['cuisine']} · {r['region']}</div></td>
          <td>{seg_badge(seg)}</td>
          <td style="font-size:1rem;font-weight:800;color:{sc_color};">{sc}</td>
          <td><div style="display:flex;align-items:center;gap:6px;">
                <span style="color:{D['text_pri']};font-size:0.82rem;">{p_r}</span>
                <div style="background:{D['border']};border-radius:3px;height:4px;width:48px;">
                  <div style="background:{D['green']};height:4px;border-radius:3px;width:{int(float(r.get('prob_rising',0))*100)}%;"></div>
                </div>
              </div></td>
          <td><div style="display:flex;align-items:center;gap:6px;">
                <span style="color:{D['text_pri']};font-size:0.82rem;">{p_h}</span>
                <div style="background:{D['border']};border-radius:3px;height:4px;width:48px;">
                  <div style="background:{D['purple']};height:4px;border-radius:3px;width:{int(float(r.get('prob_hidden_gem',0))*100)}%;"></div>
                </div>
              </div></td>
          <td>{gmap}</td>
          <td>{mom}</td>
        </tr>"""

    # ── Render table ──
    export_df = view_df[['restaurant_name','ML_Predicted_Segment','ml_priority_score','cuisine','region']].to_csv(index=False)

    st.markdown(f"""
    <div class="tbl-wrap">
      <div class="tbl-header">
        <div style="font-size:0.9rem;font-weight:700;color:{D['text_pri']};">
          Prioritized Partners <span style="color:{D['text_sec']};font-weight:400;font-size:0.8rem;">({len(view_df)} results)</span>
        </div>
        <div style="display:flex;gap:8px;align-items:center;">
          <button class="btn-outline" style="font-size:0.78rem;padding:6px 14px;">⬇️ Export</button>
        </div>
      </div>
      <table class="tbl">
        <thead>
          <tr>
            <th>Rank</th><th>Restaurant</th><th>Segment</th>
            <th>Priority Score</th><th>P(Rising)</th><th>P(Hidden Gem)</th>
            <th>GMaps ★</th><th>Momentum</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
      <div class="tbl-foot">
        <div>Showing {start+1}–{min(end,len(view_df))} of {len(view_df)} partners</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Pagination: compact centred buttons ──
    def get_page_range(cur, total, wing=2):
        if total <= 7:
            return list(range(1, total + 1))
        pages = [1]
        lo = max(2, cur - wing)
        hi = min(total - 1, cur + wing)
        if lo > 2:   pages.append('…')
        pages.extend(range(lo, hi + 1))
        if hi < total - 1: pages.append('…')
        pages.append(total)
        return pages

    page_range = get_page_range(page, total_pages)

    st.markdown(f"""
    <style>
    /* Compact pagination buttons */
    div.pg-row div[data-testid="stColumns"] div[data-testid="stColumn"] {{
        min-width: 0 !important;
        flex: 0 0 auto !important;
    }}
    div.pg-row button {{
        padding: 2px 10px !important;
        min-height: 32px !important;
        font-size: 0.8rem !important;
        min-width: 36px !important;
        width: auto !important;
    }}
    div.pg-row button[disabled] {{
        background: {D['lime']} !important;
        color: #000 !important;
        opacity: 1 !important;
        border-color: {D['lime']} !important;
        font-weight: 700 !important;
    }}
    </style>
    <div class="pg-row">""", unsafe_allow_html=True)

    _, pg_centre, _ = st.columns([2, 4, 2])
    with pg_centre:
        slots = ['‹'] + page_range + ['›']
        pg_cols = st.columns(len(slots))
        for i, p in enumerate(slots):
            with pg_cols[i]:
                if p == '‹':
                    if st.button("‹", key="pg_prev", disabled=(page <= 1)):
                        st.session_state.tbl_page = page - 1; st.rerun()
                elif p == '›':
                    if st.button("›", key="pg_next", disabled=(page >= total_pages)):
                        st.session_state.tbl_page = page + 1; st.rerun()
                elif p == '…':
                    st.markdown("<div style='text-align:center;padding-top:6px;color:#64748b;'>…</div>",
                                unsafe_allow_html=True)
                elif p == page:
                    st.button(str(p), key=f"pg_{p}", disabled=True)
                else:
                    if st.button(str(p), key=f"pg_{p}"):
                        st.session_state.tbl_page = p; st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.72rem;color:{D['text_sec']};text-align:center;margin-top:2px;'>Page {page} of {total_pages}</div>",
                unsafe_allow_html=True)

    st.download_button("📥 Download CSV", export_df, "hungry_hub_priority_list.csv", "text/csv")

# ─── Tab 2: Portfolio Map
with tab_b:
    if 'internal_score' in dff.columns:
        y_col = 'weighted_rating_score' if 'weighted_rating_score' in dff.columns else 'external_quality_score'
        sdf   = dff.copy(); sdf[y_col] = sdf[y_col].fillna(0)
        fig_s = px.scatter(sdf, x='internal_score', y=y_col, color='ML_Predicted_Segment',
                           size='ml_priority_score', size_max=20, hover_name='restaurant_name',
                           color_discrete_map=SEG_COLOR, opacity=0.75,
                           labels={'internal_score':'Internal Performance','ML_Predicted_Segment':'Segment'})
        fig_s.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)', height=520, font=dict(family='Inter'),
                            margin=dict(l=0,r=0,t=20,b=0),
                            legend=dict(orientation="h", y=1.06, x=0, font=dict(size=11)))
        fig_s.update_xaxes(gridcolor='rgba(255,255,255,0.04)', zeroline=False)
        fig_s.update_yaxes(gridcolor='rgba(255,255,255,0.04)', zeroline=False)
        st.plotly_chart(fig_s, use_container_width=True)
        c1,c2,c3,c4 = st.columns(4)
        c1.markdown(f"<span style='color:{D['lime']};font-weight:700;'>Top-Right:</span> High performance + quality", unsafe_allow_html=True)
        c2.markdown(f"<span style='color:{D['purple']};font-weight:700;'>Bottom-Right:</span> High quality, low performance", unsafe_allow_html=True)
        c3.markdown(f"<span style='color:{D['red']};font-weight:700;'>Top-Left:</span> Deteriorating signals", unsafe_allow_html=True)
        c4.markdown(f"<span style='color:{D['slate_mid']};font-weight:700;'>Bottom-Left:</span> Stable / average", unsafe_allow_html=True)
    else: st.info("Internal score not available.")

# ─── Tab 3: Segment Analysis
with tab_c:
    l, r = st.columns(2)
    with l:
        sc = dff['ML_Predicted_Segment'].value_counts()
        fd = go.Figure(data=[go.Pie(labels=sc.index, values=sc.values, hole=0.6,
                                    marker=dict(colors=[SEG_COLOR.get(s,'#888') for s in sc.index]),
                                    textinfo='percent', textfont=dict(size=12, color='#fff'))])
        fd.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', height=360,
                         showlegend=True, legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
                         annotations=[dict(text=f"<b>{len(dff):,}</b><br><span style='font-size:10px'>total</span>",
                                          x=0.5, y=0.5, showarrow=False, font=dict(size=18, color=D['text_pri']))])
        st.plotly_chart(fd, use_container_width=True)
    with r:
        cg = dff.groupby(['cuisine','ML_Predicted_Segment']).size().reset_index(name='n')
        fb = px.bar(cg, x='cuisine', y='n', color='ML_Predicted_Segment',
                    color_discrete_map=SEG_COLOR, barmode='stack',
                    labels={'n':'Restaurants','cuisine':'Cuisine','ML_Predicted_Segment':'Segment'})
        fb.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                         plot_bgcolor='rgba(0,0,0,0)', height=360, font=dict(family='Inter'),
                         legend=dict(orientation="h", y=1.05, x=1, xanchor="right"))
        fb.update_xaxes(gridcolor='rgba(255,255,255,0.04)')
        fb.update_yaxes(gridcolor='rgba(255,255,255,0.04)')
        st.plotly_chart(fb, use_container_width=True)

    rg = dff.groupby(['region','ML_Predicted_Segment']).size().reset_index(name='n')
    fr = px.bar(rg, x='region', y='n', color='ML_Predicted_Segment',
                color_discrete_map=SEG_COLOR, barmode='stack',
                labels={'n':'Restaurants','region':'Region','ML_Predicted_Segment':'Segment'})
    fr.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                     plot_bgcolor='rgba(0,0,0,0)', height=380, font=dict(family='Inter'),
                     legend=dict(orientation="h", y=1.05, x=1, xanchor="right"))
    st.plotly_chart(fr, use_container_width=True)

# ─── Tab 4: Partner Explorer
with tab_d:
    names    = sorted(df['restaurant_name'].dropna().unique().tolist())
    selected = st.selectbox("Search partner", [""]+names, index=0, label_visibility="collapsed",
                            placeholder="Type a restaurant name...")
    if selected:
        row = df[df['restaurant_name']==selected].iloc[0]
        seg = row['ML_Predicted_Segment']; sc = SEG_COLOR.get(seg, D['text_sec']); bg = SEG_BG.get(seg, D['surface'])

        st.markdown(f"""
        <div style="background:{D['card']};border:1px solid {D['border']};border-left:4px solid {sc};
             border-radius:14px;padding:24px;margin-bottom:18px;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
            <div>
              <div style="font-size:1.6rem;font-weight:800;letter-spacing:-0.03em;color:{D['text_pri']};margin-bottom:8px;">{selected}</div>
              <span style="background:{bg};color:{sc};font-size:0.78rem;font-weight:700;
                    padding:4px 12px;border-radius:20px;border:1px solid {sc}44;">{seg}</span>&nbsp;
              <span style="background:{D['surface']};color:{D['text_sec']};font-size:0.78rem;
                    padding:4px 10px;border-radius:20px;">{row['cuisine']}</span>&nbsp;
              <span style="background:{D['surface']};color:{D['text_sec']};font-size:0.78rem;
                    padding:4px 10px;border-radius:20px;">📍 {row['region']}</span>
            </div>
            <div style="text-align:right;">
              <div style="font-size:3.2rem;font-weight:800;letter-spacing:-0.05em;color:{D['text_pri']};line-height:1;">{row['ml_priority_score']:.1f}</div>
              <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.08em;color:{D['text_sec']};">Priority Score</div>
              <div style="font-size:0.82rem;color:{D['lime']};margin-top:4px;">Network Rank #{int(row['overall_rank'])}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        # Telemetry
        tele = []
        if 'internal_score' in row and pd.notna(row.get('internal_score')): tele.append(("Internal Performance", f"{row['internal_score']:.1f}", D['lime']))
        if 'weighted_rating_score' in row and pd.notna(row.get('weighted_rating_score')): tele.append(("Weighted Rating", f"{row['weighted_rating_score']:.2f}", D['purple']))
        if 'momentum_score' in row and pd.notna(row.get('momentum_score')): tele.append(("Momentum Score", f"{row['momentum_score']:.1f}", D['green'] if row['momentum_score']>0 else D['red']))
        if 'prob_rising' in row: tele.append(("P(Rising)", f"{float(row['prob_rising']):.1%}", D['lime']))

        if tele:
            cols_t = st.columns(len(tele))
            for c, (lbl, val, col) in zip(cols_t, tele):
                c.markdown(f"""
                <div style="background:{D['surface']};border:1px solid {D['border']};border-radius:12px;padding:16px;">
                  <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.06em;color:{D['text_sec']};font-weight:700;margin-bottom:6px;">{lbl}</div>
                  <div style="font-size:1.7rem;font-weight:800;color:{col};letter-spacing:-0.03em;">{val}</div>
                </div>""", unsafe_allow_html=True)

        ca, cb = st.columns([1, 1.4])
        with ca:
            st.markdown(f"<div style='font-size:0.78rem;font-weight:700;color:{D['text_sec']};text-transform:uppercase;letter-spacing:0.06em;margin:16px 0 10px;'>Prediction Confidence</div>", unsafe_allow_html=True)
            prob_map = {'Declining':'prob_declining','Stable':'prob_stable','Rising':'prob_rising','Hidden Gem':'prob_hidden_gem'}
            for s, pk in prob_map.items():
                p = float(row.get(pk, 0)); pct = int(p*100); col = SEG_COLOR.get(s, D['text_sec'])
                st.markdown(f"""
                <div style="margin-bottom:10px;">
                  <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                    <span style="font-size:0.8rem;font-weight:600;color:{col};">{s}</span>
                    <span style="font-size:0.78rem;color:{D['text_sec']};">{p:.1%}</span>
                  </div>
                  <div style="background:{D['border']};border-radius:4px;height:6px;">
                    <div style="background:{col};width:{pct}%;height:6px;border-radius:4px;"></div>
                  </div>
                </div>""", unsafe_allow_html=True)

        with cb:
            metrics = {}
            for cn, lb in [('internal_score','Internal'),('momentum_score','Momentum'),('ml_priority_score','ML Priority')]:
                if cn in row and pd.notna(row.get(cn)): metrics[lb] = float(row[cn])
            if 'weighted_rating_score' in row and pd.notna(row.get('weighted_rating_score')):
                metrics['Rating×20'] = float(row['weighted_rating_score'])*20
            if metrics:
                fig_m = go.Figure(go.Bar(
                    x=list(metrics.keys()), y=list(metrics.values()),
                    marker=dict(color=[D['lime'],D['green'],D['purple'],D['text_sec']][:len(metrics)], line=dict(width=0)),
                    text=[f"{v:.1f}" for v in metrics.values()], textposition='outside',
                    textfont=dict(size=11, color=D['text_sec'])
                ))
                fig_m.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)', height=280, showlegend=False,
                                    margin=dict(l=0,r=0,t=30,b=0), font=dict(family='Inter'),
                                    yaxis=dict(range=[0,115],gridcolor='rgba(255,255,255,0.04)'),
                                    xaxis=dict(showgrid=False))
                st.plotly_chart(fig_m, use_container_width=True)

        if 'total_revenue' in row:
            rev=f"฿{float(row.get('total_revenue',0)):,.0f}"; bk=f"{int(row.get('total_bookings',0)):,}"
            ns=f"{float(row.get('no_show_rate',0)):.2%}"; web=f"{int(row.get('web_views',0)):,}" if 'web_views' in row else "—"
            st.markdown(f"""
            <div style="background:{D['card']};border:1px solid {D['border']};border-radius:14px;padding:20px;margin-top:12px;">
              <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.08em;color:{D['text_sec']};font-weight:700;margin-bottom:16px;">Core Business Telemetry</div>
              <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:20px;">
                <div><div style="font-size:0.65rem;color:{D['text_sec']};text-transform:uppercase;letter-spacing:0.06em;font-weight:600;">Revenue</div><div style="font-size:1.3rem;font-weight:800;color:{D['text_pri']};margin-top:4px;">{rev}</div></div>
                <div><div style="font-size:0.65rem;color:{D['text_sec']};text-transform:uppercase;letter-spacing:0.06em;font-weight:600;">Bookings</div><div style="font-size:1.3rem;font-weight:800;color:{D['text_pri']};margin-top:4px;">{bk}</div></div>
                <div><div style="font-size:0.65rem;color:{D['text_sec']};text-transform:uppercase;letter-spacing:0.06em;font-weight:600;">Web Views</div><div style="font-size:1.3rem;font-weight:800;color:{D['text_pri']};margin-top:4px;">{web}</div></div>
                <div><div style="font-size:0.65rem;color:{D['text_sec']};text-transform:uppercase;letter-spacing:0.06em;font-weight:600;">No-Show Rate</div><div style="font-size:1.3rem;font-weight:800;color:{D['red']};margin-top:4px;">{ns}</div></div>
              </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:{D['card']};border:2px dashed {D['border']};border-radius:14px;padding:48px;text-align:center;margin-top:8px;">
          <div style="font-size:2rem;margin-bottom:10px;">🔍</div>
          <div style="font-size:1rem;font-weight:700;color:{D['text_pri']};margin-bottom:6px;">Search for a partner</div>
          <div style="font-size:0.85rem;color:{D['text_sec']};">Use the search box above to view a restaurant's full intelligence profile.</div>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:24px 0 16px;margin-top:28px;
     border-top:1px solid {D['border']};color:{D['text_sec']};font-size:0.75rem;">
  Hungry Hub Partner CRM &nbsp;·&nbsp; ML Pipeline v3 &nbsp;·&nbsp;
  Built with Streamlit & LightGBM
</div>
</div>
""", unsafe_allow_html=True)
