import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────
# PAGE CONFIG
# ─────────────────────────────
st.set_page_config(page_title="Sea Level Dashboard", layout="wide")

# ─────────────────────────────
# CUSTOM CSS (PREMIUM LOOK)
# ─────────────────────────────
st.markdown("""
<style>
.main {background-color: #f5f7fa;}
.block-container {padding-top: 2rem;}

.kpi-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
    text-align: center;
}

.kpi-title {font-size: 14px; color: gray;}
.kpi-value {font-size: 28px; font-weight: bold;}
.kpi-sub {font-size: 13px; color: #555;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────
# TITLE
# ─────────────────────────────
st.title("🌊 Sea-Level Rise Impact Dashboard")
st.caption("Interactive analysis of global exposure across sea-level scenarios")
st.markdown("---")

# ─────────────────────────────
# LOAD DATA
# ─────────────────────────────
df = pd.read_excel("Data Science Project Lifecycle.xlsx")

# CLEAN COLUMN NAMES (CRITICAL FIX)
df.columns = df.columns.str.strip()

# CLEAN VALUES
df['Indicator'] = df['Indicator'].str.strip().str.title()
df['Scenario'] = df['Scenario'].str.strip().str.lower()
df['Continent'] = df['Continent'].str.strip()

# ─────────────────────────────
# FILTERS
# ─────────────────────────────
col1, col2 = st.columns(2)

with col1:
    scenario = st.selectbox("🌊 Select Scenario", sorted(df['Scenario'].unique()))

with col2:
    indicator = st.selectbox("📊 Select Indicator", df['Indicator'].unique())

filtered_df = df[df['Scenario'] == scenario]

# ─────────────────────────────
# KPI FUNCTION
# ─────────────────────────────
def get_kpi(name):
    data = filtered_df[filtered_df['Indicator'] == name]
    impact = data['Impact'].sum()
    total = data['Total'].sum()
    pct = (impact / total * 100) if total > 0 else 0
    return impact, pct

land, land_pct = get_kpi("Land")
pop, pop_pct = get_kpi("Population")
gdp, gdp_pct = get_kpi("Gdp")

# ─────────────────────────────
# KPI CARDS (PREMIUM STYLE)
# ─────────────────────────────
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🌍 Land at Risk</div>
        <div class="kpi-value">{land/1_000:.0f}k km²</div>
        <div class="kpi-sub">{land_pct:.2f}% of global land</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">👥 Population Exposed</div>
        <div class="kpi-value">{pop/1_000_000:.1f}M</div>
        <div class="kpi-sub">{pop_pct:.2f}% of global population</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">💰 GDP Exposed</div>
        <div class="kpi-value">${gdp/1000:.1f}B</div>
        <div class="kpi-sub">{gdp_pct:.2f}% of global GDP</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────
# GLOBAL TREND
# ─────────────────────────────
st.subheader("Global Percentage Impact by Scenario — All Indicators")
st.caption("How each indicator's exposure grows from +1m to +5m sea-level rise (% of global total)")

trend = df.groupby(['Scenario','Indicator'])['Percentage'].mean().reset_index()

fig1 = px.line(trend, x='Scenario', y='Percentage', color='Indicator', markers=True)

fig1.update_layout(yaxis_title="Global Exposure (%)")

fig1.update_layout(
    xaxis=dict(showgrid=True),
    yaxis=dict(showgrid=True)
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ─────────────────────────────
# CONTINENT BREAKDOWN
# ─────────────────────────────
st.subheader("🌍 Regional Land Exposure by Scenario(Land %)")
st.caption("Percentage of land at risk per region across sea-level rise scenarios")

land_df = df[df['Indicator'] == 'Land']

fig2 = px.bar(
    land_df,
    x='Continent',
    y='Percentage',
    color='Scenario',
    barmode='group'
)
fig2.update_traces(opacity=1)
fig2.update_layout(yaxis_title="Land Exposed (%)",bargroupgap=0)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ─────────────────────────────
# TOP COUNTRIES (DYNAMIC)
# ─────────────────────────────
st.subheader("🏆 Top 15 Countries")

top_df = df[
    (df['Scenario'] == scenario) &
    (df['Indicator'] == indicator)
].nlargest(15, 'Percentage')

fig3 = px.bar(
    top_df.sort_values('Percentage'),
    x='Percentage',
    y='Country',
    orientation='h',
    color='Percentage',
    color_continuous_scale='Blues'
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ─────────────────────────────
# HEATMAP (FIXED)
# ─────────────────────────────
st.subheader("🔥 Vulnerability Heatmap (Top 15 Across All Scenarios)")

heat_df = df[df['Indicator'] == indicator]

# ✅ Get top 15 countries based on MAX exposure across ALL scenarios
top_countries = (
    heat_df.groupby('Country')['Percentage']
    .max()                      # you can also use .mean() if needed
    .nlargest(15)
    .index
)

# Filter only those countries
heat_df = heat_df[heat_df['Country'].isin(top_countries)]

# Pivot table
pivot = heat_df.pivot_table(
    index='Country',
    columns='Scenario',
    values='Percentage'
)

# Sort by highest scenario (5 meter usually)
pivot = pivot.sort_values(by=pivot.columns[-1], ascending=False)

# Plot
fig = px.imshow(
    pivot,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="RdYlBu_r"
)

fig.update_layout(
    height=600
)

st.plotly_chart(fig, use_container_width=True)
# ─────────────────────────────
# POP and GPD
# ─────────────────────────────
st.subheader("Global Absolute Impact Growth — Population & GDP")
st.caption("Cumulative increase in people and GDP value exposed as sea levels rise")

import plotly.graph_objects as go

scenario_order = ['1 meter', '2 meter', '3 meter', '4 meter', '5 meter']

pop_df = df[df['Indicator'] == 'Population']
gdp_df = df[df['Indicator'] == 'Gdp']

pop_data = pop_df.groupby('Scenario')['Impact'].sum().reindex(scenario_order)
gdp_data = gdp_df.groupby('Scenario')['Impact'].sum().reindex(scenario_order)

fig = go.Figure()

# Population line
fig.add_trace(go.Scatter(
    x=scenario_order,
    y=pop_data.values / 1_000_000,  # convert to millions
    mode='lines+markers',
    name='Population (Millions)',
    line=dict(width=3)
))

# GDP line
fig.add_trace(go.Scatter(
    x=scenario_order,
    y=gdp_data.values / 1_000,  # convert to billions
    mode='lines+markers',
    name='GDP (Billions)',
    yaxis='y2',
    line=dict(width=3, dash='dot')
))

fig.update_layout(
    height=500,
    template='plotly_white',
    xaxis_title="Scenario",
    
    # LEFT AXIS (Population)
    yaxis=dict(
        title="Population (Millions)",
        tickmode='linear',
        dtick=50  # 0, 50, 100, 150...
    ),

    # RIGHT AXIS (GDP)
    yaxis2=dict(
        title="GDP (Billions)",
        overlaying='y',
        side='right'
    ),

    legend=dict(orientation='h', y=-0.2)
)

st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────
# RADAR
# ─────────────────────────────
st.subheader("🕸️ Radar (% Impact)")

radar_df = df[df['Scenario'] == scenario]

radar = radar_df.groupby('Indicator')['Percentage'].mean().reset_index()

fig6 = go.Figure()

fig6.add_trace(go.Scatterpolar(
    r=radar['Percentage'],
    theta=radar['Indicator'],
    fill='toself'
))

fig6.update_layout(
    polar=dict(radialaxis=dict(title="Percentage (%)"))
)

st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# ─────────────────────────────
# TABLE
# ─────────────────────────────
st.subheader("📋 Top 15 Most Vulnerable Countries")

land_df = df[df['Indicator'] == 'Land']

t1 = land_df[land_df['Scenario'] == '1 meter'][['Country','Percentage']]
t3 = land_df[land_df['Scenario'] == '3 meter'][['Country','Percentage']]
t5 = land_df[land_df['Scenario'] == '5 meter'][['Country','Percentage']]

merged = t1.merge(t3, on='Country', suffixes=(' 1m',' 3m'))
merged = merged.merge(t5, on='Country')

merged.columns = ['Country','Land % at +1m','Land % at +3m','Land % at +5m']

top15 = merged.sort_values('Land % at +5m', ascending=False).head(15)

st.dataframe(top15, use_container_width=True)
