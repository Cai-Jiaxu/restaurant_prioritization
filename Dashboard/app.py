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
    page_title="Hungry Hub · Restaurant Prioritization",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# Custom CSS for premium look
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 8px 0 4px 0;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #8892b0;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 500;
    }
    .metric-delta {
        font-size: 0.8rem;
        color: #64ffda;
        margin-top: 4px;
    }
    .metric-delta.warn { color: #ff6b6b; }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Data Loading
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "Data", "Processed")

REGION_MAP = {
    0: "Unknown", 1: "CBD", 2: "Sukhumvit", 3: "Silom/Sathon",
    4: "Riverside", 5: "North/Ari", 6: "Other", 7: "Provincial",
    8: "Ratchada/Rama9", 9: "Outer Bangkok"
}
CUISINE_MAP = {
    0: "Other", 1: "Thai", 2: "Japanese", 3: "Italian",
    4: "Chinese", 5: "Buffet", 6: "Seafood", 7: "Steak/Grill"
}
SEGMENT_COLORS = {
    "Rising": "#64ffda", "Hidden Gem": "#bb86fc",
    "Stable": "#546e7a", "Declining": "#ff6b6b"
}

@st.cache_data
def load_data():
    predictions = pd.read_csv(os.path.join(DATA_DIR, "Dashboard_Predictions.csv"))
    master = pd.read_csv(os.path.join(DATA_DIR, "master_all_data.csv"))

    # Merge for rich context
    merge_cols = ['restaurant_id', 'restaurant_name_en', 'name', 'primary_cuisine',
                  'total_revenue', 'total_bookings', 'total_guests', 'avg_revenue_per_booking',
                  'no_show_rate', 'internal_score', 'places', 'primary_place']
    merge_cols = [c for c in merge_cols if c in master.columns]
    df = pd.merge(predictions, master[merge_cols], on='restaurant_id', how='left')

    # Decode categorical columns
    df['region'] = df['region_encoded'].map(REGION_MAP).fillna("Unknown")
    df['cuisine'] = df['cuisine_encoded'].map(CUISINE_MAP).fillna("Other")
    df['restaurant_name'] = df['restaurant_name_en'].fillna(df.get('name', 'Unknown'))

    return df

df = load_data()

# ─────────────────────────────────────────────
# Sidebar Filters
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 Filters")
    st.markdown("---")

    segment_filter = st.multiselect(
        "Segment",
        options=sorted(df['ML_Predicted_Segment'].unique()),
        default=sorted(df['ML_Predicted_Segment'].unique()),
        help="Filter by ML-predicted segment"
    )

    region_filter = st.multiselect(
        "Region",
        options=sorted(df['region'].unique()),
        default=sorted(df['region'].unique()),
        help="Filter by Bangkok region"
    )

    cuisine_filter = st.multiselect(
        "Cuisine",
        options=sorted(df['cuisine'].unique()),
        default=sorted(df['cuisine'].unique()),
        help="Filter by cuisine category"
    )

    min_score = st.slider(
        "Min Priority Score",
        min_value=0.0,
        max_value=float(df['ml_priority_score'].max()),
        value=0.0,
        step=1.0,
        help="Only show restaurants above this priority score"
    )

    st.markdown("---")
    st.markdown(f"**Data:** {len(df):,} restaurants")
    st.markdown(f"**Model CV:** 78.7% accuracy")

# Apply filters
mask = (
    df['ML_Predicted_Segment'].isin(segment_filter) &
    df['region'].isin(region_filter) &
    df['cuisine'].isin(cuisine_filter) &
    (df['ml_priority_score'] >= min_score)
)
df_filtered = df[mask]

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("# 🍽️ Hungry Hub · Restaurant Prioritization Dashboard")
st.markdown("*Data-driven marketing resource allocation powered by ML classification*")
st.markdown("")

# ═══════════════════════════════════════════════
# SECTION 1: Executive KPI Cards
# ═══════════════════════════════════════════════
cols = st.columns(6)

total = len(df)
rising = (df['ML_Predicted_Segment'] == 'Rising').sum()
hidden = (df['ML_Predicted_Segment'] == 'Hidden Gem').sum()
declining = (df['ML_Predicted_Segment'] == 'Declining').sum()

# Revenue concentration
if 'total_revenue' in df.columns:
    top20_rev = df.nlargest(int(len(df) * 0.2), 'total_revenue')['total_revenue'].sum()
    total_rev = df['total_revenue'].sum()
    concentration = f"{top20_rev / total_rev * 100:.1f}%" if total_rev > 0 else "N/A"
else:
    concentration = "N/A"

kpi_data = [
    ("Total Portfolio", f"{total:,}", "restaurants", False),
    ("Revenue Risk", concentration, "from top 20%", True),
    ("Rising Stars", f"{rising}", "high-growth partners", False),
    ("Hidden Gems", f"{hidden}", "underexploited quality", False),
    ("At-Risk", f"{declining}", "declining partners", True),
    ("Actionable", f"{rising + hidden}", "marketing targets", False),
]

for col, (label, value, sublabel, is_warn) in zip(cols, kpi_data):
    delta_class = "warn" if is_warn else ""
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-delta {delta_class}">{sublabel}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# ═══════════════════════════════════════════════
# SECTION 2 & 3: Tabs for Priority List and Portfolio Map
# ═══════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Priority Marketing List",
    "🗺️ Portfolio Map",
    "📊 Segment Analysis",
    "🔍 Restaurant Explorer"
])

# ─────────────────────────────────────────────
# TAB 1: Priority Marketing List
# ─────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-header">Prioritized Marketing Targets</div>', unsafe_allow_html=True)
    st.markdown("Partners ranked by ML priority score — higher = greater marketing opportunity.")

    # Show only actionable segments by default
    actionable = df_filtered[df_filtered['ML_Predicted_Segment'].isin(['Rising', 'Hidden Gem'])].copy()
    show_all = st.toggle("Show all segments (including Stable & Declining)", value=False)
    display_df = df_filtered if show_all else actionable

    if not display_df.empty:
        display_df = display_df.sort_values('ml_priority_score', ascending=False).reset_index(drop=True)
        display_df.index += 1
        display_df.index.name = 'Rank'

        show_cols = ['restaurant_name', 'ML_Predicted_Segment', 'ml_priority_score',
                     'cuisine', 'region', 'prob_rising', 'prob_hidden_gem']
        if 'gmaps_rating' in display_df.columns:
            show_cols.append('gmaps_rating')
        if 'momentum_score' in display_df.columns:
            show_cols.append('momentum_score')

        show_cols = [c for c in show_cols if c in display_df.columns]

        st.dataframe(
            display_df[show_cols].style.format({
                'ml_priority_score': '{:.1f}',
                'prob_rising': '{:.3f}',
                'prob_hidden_gem': '{:.3f}',
                'gmaps_rating': '{:.1f}',
                'momentum_score': '{:.1f}'
            }).background_gradient(
                subset=['ml_priority_score'], cmap='viridis', vmin=0
            ),
            use_container_width=True,
            height=500,
            column_config={
                "restaurant_name": st.column_config.TextColumn("Restaurant", width="medium"),
                "ML_Predicted_Segment": st.column_config.TextColumn("Segment", width="small"),
                "ml_priority_score": st.column_config.NumberColumn("Priority Score", format="%.1f"),
                "cuisine": st.column_config.TextColumn("Cuisine", width="small"),
                "region": st.column_config.TextColumn("Region", width="small"),
                "prob_rising": st.column_config.ProgressColumn("P(Rising)", min_value=0, max_value=1, format="%.2f"),
                "prob_hidden_gem": st.column_config.ProgressColumn("P(Hidden Gem)", min_value=0, max_value=1, format="%.2f"),
                "gmaps_rating": st.column_config.NumberColumn("GMaps ★", format="%.1f"),
                "momentum_score": st.column_config.NumberColumn("Momentum", format="%.1f"),
            }
        )

        # Download button
        csv = display_df[show_cols].to_csv(index=True)
        st.download_button(
            "📥 Download as CSV",
            csv,
            "priority_marketing_list.csv",
            "text/csv",
            use_container_width=False
        )

        # Summary stats
        c1, c2, c3 = st.columns(3)
        c1.metric("Partners Shown", len(display_df))
        c2.metric("Avg Priority Score", f"{display_df['ml_priority_score'].mean():.1f}")
        c3.metric("Top Score", f"{display_df['ml_priority_score'].max():.1f}")
    else:
        st.info("No restaurants match your current filters.")


# ─────────────────────────────────────────────
# TAB 2: Portfolio Risk & Opportunity Map
# ─────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">Portfolio Risk & Opportunity Map</div>', unsafe_allow_html=True)
    st.markdown("Each bubble is a restaurant. **Hidden Gems** = high quality, low internal performance. **Declining** = high performance but deteriorating signals.")

    if 'internal_score' in df_filtered.columns:
        scatter_df = df_filtered.copy()
        # Use weighted_rating_score (48% coverage) as quality proxy instead of external_quality_score (10%)
        y_col = 'weighted_rating_score' if 'weighted_rating_score' in scatter_df.columns else 'external_quality_score'
        scatter_df[y_col] = scatter_df[y_col].fillna(0)

        fig_scatter = px.scatter(
            scatter_df,
            x='internal_score',
            y=y_col,
            color='ML_Predicted_Segment',
            size='ml_priority_score',
            size_max=20,
            hover_name='restaurant_name',
            hover_data={
                'internal_score': ':.1f',
                y_col: ':.2f',
                'ml_priority_score': ':.1f',
                'cuisine': True,
                'region': True
            },
            color_discrete_map=SEGMENT_COLORS,
            labels={
                'internal_score': 'Internal Performance Score',
                y_col: 'Weighted Rating Score',
                'ML_Predicted_Segment': 'Segment'
            },
            opacity=0.7
        )
        fig_scatter.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=550,
            font=dict(family="Inter"),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02,
                xanchor="right", x=1, font=dict(size=12)
            )
        )
        fig_scatter.update_xaxes(gridcolor='rgba(255,255,255,0.05)')
        fig_scatter.update_yaxes(gridcolor='rgba(255,255,255,0.05)')
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Quadrant annotations
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown("🟢 **Top-Right**: High performance + High quality → *Cash Cows*")
        c2.markdown("🟣 **Bottom-Right**: High quality + Low performance → *Hidden Gems*")
        c3.markdown("🔴 **Top-Left**: High performance + Low quality → *At Risk*")
        c4.markdown("⚪ **Bottom-Left**: Low both → *Stable / Growth Needed*")
    else:
        st.info("Internal score data not available for this visualization.")


# ─────────────────────────────────────────────
# TAB 3: Segment Analysis
# ─────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">Segment Distribution & Breakdown</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        # Donut chart of segments
        seg_counts = df_filtered['ML_Predicted_Segment'].value_counts()
        fig_donut = go.Figure(data=[go.Pie(
            labels=seg_counts.index,
            values=seg_counts.values,
            hole=0.55,
            marker=dict(colors=[SEGMENT_COLORS.get(s, '#888') for s in seg_counts.index]),
            textinfo='label+value',
            textfont=dict(size=13, family="Inter"),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>'
        )])
        fig_donut.update_layout(
            title=dict(text="ML Predicted Segments", font=dict(size=16, family="Inter")),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400,
            showlegend=False,
            annotations=[dict(text=f"{len(df_filtered):,}<br>total", x=0.5, y=0.5,
                             font_size=18, showarrow=False, font_color="#8892b0")]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_right:
        # Segment by cuisine
        cuisine_seg = df_filtered.groupby(['cuisine', 'ML_Predicted_Segment']).size().reset_index(name='count')
        fig_cuisine = px.bar(
            cuisine_seg,
            x='cuisine', y='count', color='ML_Predicted_Segment',
            color_discrete_map=SEGMENT_COLORS,
            labels={'count': 'Restaurants', 'cuisine': 'Cuisine', 'ML_Predicted_Segment': 'Segment'},
            title="Segments by Cuisine"
        )
        fig_cuisine.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400,
            font=dict(family="Inter"),
            barmode='stack',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_cuisine.update_xaxes(gridcolor='rgba(255,255,255,0.05)')
        fig_cuisine.update_yaxes(gridcolor='rgba(255,255,255,0.05)')
        st.plotly_chart(fig_cuisine, use_container_width=True)

    # Segment by region
    region_seg = df_filtered.groupby(['region', 'ML_Predicted_Segment']).size().reset_index(name='count')
    fig_region = px.bar(
        region_seg,
        x='region', y='count', color='ML_Predicted_Segment',
        color_discrete_map=SEGMENT_COLORS,
        labels={'count': 'Restaurants', 'region': 'Region', 'ML_Predicted_Segment': 'Segment'},
        title="Segments by Region"
    )
    fig_region.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        font=dict(family="Inter"),
        barmode='stack',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_region.update_xaxes(gridcolor='rgba(255,255,255,0.05)')
    fig_region.update_yaxes(gridcolor='rgba(255,255,255,0.05)')
    st.plotly_chart(fig_region, use_container_width=True)


# ─────────────────────────────────────────────
# TAB 4: Restaurant Explorer
# ─────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-header">Restaurant Deep Dive</div>', unsafe_allow_html=True)

    # Search
    restaurant_names = sorted(df['restaurant_name'].dropna().unique().tolist())
    selected = st.selectbox("Search restaurant", [""] + restaurant_names, index=0,
                           placeholder="Type to search...")

    if selected:
        row = df[df['restaurant_name'] == selected].iloc[0]

        c1, c2 = st.columns([1, 2])

        with c1:
            st.markdown(f"### {selected}")
            st.markdown(f"**Segment:** `{row['ML_Predicted_Segment']}`")
            st.markdown(f"**Cuisine:** {row['cuisine']}")
            st.markdown(f"**Region:** {row['region']}")
            st.markdown(f"**Priority Score:** `{row['ml_priority_score']:.1f}`")
            st.markdown(f"**Overall Rank:** #{int(row['overall_rank'])}")
            if 'gmaps_rating' in row and row['gmaps_rating'] > 0:
                st.markdown(f"**GMaps Rating:** {'⭐' * int(row['gmaps_rating'])} ({row['gmaps_rating']:.1f})")

            st.markdown("---")
            st.markdown("#### Class Probabilities")
            prob_data = {
                'Declining': row.get('prob_declining', 0),
                'Stable': row.get('prob_stable', 0),
                'Rising': row.get('prob_rising', 0),
                'Hidden Gem': row.get('prob_hidden_gem', 0)
            }
            for label, prob in prob_data.items():
                color = SEGMENT_COLORS.get(label, '#888')
                st.markdown(f"**{label}**")
                st.progress(min(prob, 1.0))

        with c2:
            # Performance metrics as bar chart
            metrics = {}
            if 'internal_score' in row and pd.notna(row.get('internal_score')):
                metrics['Internal\nPerformance'] = row['internal_score']
            if 'external_quality_score' in row and pd.notna(row.get('external_quality_score')):
                metrics['External\nQuality'] = row['external_quality_score']
            if 'momentum_score' in row and pd.notna(row.get('momentum_score')):
                metrics['Momentum'] = row['momentum_score']
            if 'ml_priority_score' in row and pd.notna(row.get('ml_priority_score')):
                metrics['ML Priority'] = row['ml_priority_score']
            if 'weighted_rating_score' in row and pd.notna(row.get('weighted_rating_score')):
                metrics['Weighted\nRating'] = row['weighted_rating_score'] * 20  # Scale 0-5 to 0-100

            if metrics:
                fig_bar = go.Figure(data=[
                    go.Bar(
                        x=list(metrics.keys()),
                        y=list(metrics.values()),
                        marker=dict(
                            color=list(metrics.values()),
                            colorscale='Viridis',
                            line=dict(width=0)
                        ),
                        text=[f"{v:.1f}" for v in metrics.values()],
                        textposition='outside',
                        textfont=dict(size=14, family="Inter", color="white")
                    )
                ])
                fig_bar.update_layout(
                    title=dict(text="Performance Profile (0-100 scale)", font=dict(size=14, family="Inter")),
                    template='plotly_dark',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=350,
                    yaxis=dict(range=[0, 105], gridcolor='rgba(255,255,255,0.05)'),
                    xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                    font=dict(family="Inter"),
                    showlegend=False
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            # Business metrics table
            if 'total_revenue' in row:
                st.markdown("#### Business Metrics")
                biz_metrics = {
                    'Total Revenue': f"฿{row.get('total_revenue', 0):,.0f}",
                    'Total Bookings': f"{row.get('total_bookings', 0):,.0f}",
                    'Avg Rev/Booking': f"฿{row.get('avg_revenue_per_booking', 0):,.0f}",
                    'No-Show Rate': f"{row.get('no_show_rate', 0):.2%}",
                    'Web Views': f"{row.get('web_views', 0):,.0f}",
                    'GMaps Reviews': f"{row.get('gmaps_reviews', 0):,.0f}",
                }
                biz_df = pd.DataFrame(list(biz_metrics.items()), columns=['Metric', 'Value'])
                st.dataframe(biz_df, use_container_width=True, hide_index=True)
    else:
        st.info("👆 Select a restaurant from the dropdown to see its detailed profile.")


# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #546e7a; font-size: 0.8rem;'>"
    "Hungry Hub Restaurant Prioritization System · ML Pipeline v3 · "
    "Built with Streamlit & LightGBM"
    "</div>",
    unsafe_allow_html=True
)
