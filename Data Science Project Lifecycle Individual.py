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
        <div class="kpi-value">{land:,.0f} km²</div>
        <div class="kpi-sub">{land_pct:.2f}% of global land</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">👥 Population Exposed</div>
        <div class="kpi-value">{pop:,.0f}</div>
        <div class="kpi-sub">{pop_pct:.2f}% of global population</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">💰 GDP Exposed</div>
        <div class="kpi-value">${gdp:,.0f}</div>
        <div class="kpi-sub">{gdp_pct:.2f}% of global GDP</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────
# GLOBAL TREND
# ─────────────────────────────
st.subheader("📈 Global Trend (% Impact)")

trend = df.groupby(['Scenario','Indicator'])['Percentage'].mean().reset_index()

fig1 = px.line(trend, x='Scenario', y='Percentage', color='Indicator', markers=True)

fig1.update_layout(
    xaxis=dict(showgrid=True),
    yaxis=dict(showgrid=True)
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ─────────────────────────────
# CONTINENT BREAKDOWN
# ─────────────────────────────
st.subheader("🌍 Continent Breakdown (Land %)")

land_df = df[df['Indicator'] == 'Land']

fig2 = px.bar(
    land_df,
    x='Continent',
    y='Percentage',
    color='Scenario',
    barmode='group'
)

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
st.subheader("🔥 Vulnerability Heatmap")

heat_df = df[df['Indicator'] == indicator]

top_countries = (
    heat_df.groupby('Country')['Percentage']
    .max()
    .nlargest(15)
    .index
)

heat_df = heat_df[heat_df['Country'].isin(top_countries)]

pivot = heat_df.pivot_table(
    index='Country',
    columns='Scenario',
    values='Percentage'
)

fig4 = px.imshow(pivot, text_auto=True, color_continuous_scale="RdYlBu_r")

st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ─────────────────────────────
# POP vs GDP
# ─────────────────────────────
st.subheader("📊 Population vs GDP")

pop_df = df[df['Indicator'] == 'Population'].groupby('Scenario')['Impact'].sum().reset_index()
gdp_df = df[df['Indicator'] == 'Gdp'].groupby('Scenario')['Impact'].sum().reset_index()

fig5 = go.Figure()

fig5.add_trace(go.Scatter(
    x=pop_df['Scenario'],
    y=pop_df['Impact']/1e6,
    name="Population (Millions)"
))

fig5.add_trace(go.Scatter(
    x=gdp_df['Scenario'],
    y=gdp_df['Impact']/1e3,
    name="GDP (Billions)"
))

fig5.update_layout(
    yaxis_title="Population (Millions) / GDP (Billions)"
)

st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

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
