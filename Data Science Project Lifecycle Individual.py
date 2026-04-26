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

st.markdown("""
    <div style="text-align:center;">
        <h1 style="margin-bottom:0;">🌊 Sea-Level Rise Impact Dashboard</h1>
        <p style="color:gray; font-size:16px; margin-top:5px;">
            Interactive analysis of global exposure across sea-level scenarios
        </p>
    </div>
""", unsafe_allow_html=True)


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

scenario_order = ['1 meter','2 meter','3 meter','4 meter','5 meter']

df['Scenario'] = pd.Categorical(
    df['Scenario'],
    categories=scenario_order,
    ordered=True
)

# ─────────────────────────────
# FILTERS
# ─────────────────────────────

scenario = st.selectbox("🌊 Select Scenario", scenario_order)
indicator = st.selectbox("📊 Select Indicator", df['Indicator'].unique())

filtered_df = df[df['Scenario'] == scenario]


# ─────────────────────────────
# KPI FUNCTION
# ─────────────────────────────

def get_kpi(df_subset, name):
    data = df_subset[df_subset['Indicator'] == name]
    impact = data['Impact'].sum()
    total = data['Total'].sum()
    pct = (impact / total * 100) if total > 0 else 0
    return impact, pct

land, land_pct = get_kpi(filtered_df, "Land")
pop, pop_pct = get_kpi(filtered_df, "Population")
gdp, gdp_pct = get_kpi(filtered_df, "Gdp")

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

trend = df.groupby(['Scenario','Indicator']).apply(
    lambda x: x['Impact'].sum() / x['Total'].sum() * 100
).reset_index(name='Percentage')

fig1 = px.line(trend, x='Scenario', y='Percentage', color='Indicator', markers=True)

fig1.update_layout(yaxis_title="Global Exposure (%)")

fig1.update_layout(
    xaxis=dict(showgrid=True),
    yaxis=dict(showgrid=True)
)

fig1.update_layout(
    yaxis_title="Global Exposure (%)",
    xaxis=dict(
        categoryorder='array',
        categoryarray=scenario_order,
        showgrid=True
    ),
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

region = land_df.groupby(['Continent','Scenario']).apply(
    lambda x: x['Impact'].sum() / x['Total'].sum() * 100
).reset_index(name='Percentage')

fig2 = px.bar(
    region,
    x='Continent',
    y='Percentage',
    color='Scenario',
    barmode='group'
)

fig2.update_layout(yaxis_title="Land Exposed (%)")

fig2.update_layout(
    xaxis=dict(categoryorder='array', categoryarray=sorted(df['Continent'].unique())),
    legend=dict(traceorder="normal")
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ─────────────────────────────
# TOP COUNTRIES (DYNAMIC)
# ─────────────────────────────
st.subheader("Country-Level Vulnerability Ranking")
st.caption("Top 15 countries ranked by percentage of impact for the selected indicator and sea-level rise scenario")

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
    color_continuous_scale='Viridis'
)
fig3.update_coloraxes(showscale=False)
fig3.update_layout(xaxis_title="Exposure (%)",xaxis=dict(
        title="Exposure (%)",
        showgrid=True,
        gridcolor="lightgray",
        griddash="dot")
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ─────────────────────────────
# HEATMAP (FIXED)
# ─────────────────────────────
st.subheader("Top Country Vulnerability Heatmap")
st.caption("Top 15 most affected countries showing exposure variations across sea-level rise scenarios (1–5m) for the selected indicator")

heat_df = df[df['Indicator'] == indicator]

# ✅ Get top 15 countries based on MAX exposure across ALL scenarios
top_countries = (
    heat_df.groupby('Country')['Percentage']
    .max()                
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
pivot = pivot.reindex(columns=scenario_order)

# Sort by highest scenario (5 meter usually)
pivot = pivot.sort_values(by=pivot.columns[-1], ascending=False)

# Plot
fig = px.imshow(
    pivot,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="RdYlBu_r"
)

fig.update_coloraxes(colorbar_title="Impact (%)")

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


pop_df = df[df['Indicator'] == 'Population']
gdp_df = df[df['Indicator'] == 'Gdp']

pop_data = pop_df.groupby('Scenario')['Impact'].sum().reindex(scenario_order)
gdp_data = gdp_df.groupby('Scenario')['Impact'].sum().reindex(scenario_order)

fig = go.Figure()

# Population line
fig.add_trace(go.Scatter(
    x=scenario_order,
    y=pop_data.values / 1_000_000,  # convert to millions
    mode='lines+markers+text',
    name='Population (Millions)',
    line=dict(width=3, color="royalblue"),
    marker=dict(size=8, color="royalblue"),
    text=[f"{v/1_000_000:.1f}M" for v in pop_data.values],
    textposition="top center",
    textfont=dict(color="royalblue")
))

# GDP line
fig.add_trace(go.Scatter(
    x=scenario_order,
    y=gdp_data.values / 1_000,  # convert to billions
    mode='lines+markers+text',
    name='GDP (Billions)',
    yaxis='y2',
    line=dict(width=3, dash='dot',color="tomato"),
    marker=dict(size=8, color="tomato"),
    text=[f"{v/1_000:.1f}B" for v in gdp_data.values],
    textposition="bottom center",
    textfont=dict(color="tomato", size=11)
))

fig.update_layout(
    height=500,
    template='plotly_white',
    xaxis=dict(
    title="Scenario",
    showgrid=True,
    gridcolor="lightgray"
),
    
    # LEFT AXIS (Population)
    yaxis=dict(
        title="Population (Millions)",
        tickmode='linear',
        dtick=50,
        showgrid=True,
        gridcolor="lightgray",

    ),

    # RIGHT AXIS (GDP)
    yaxis2=dict(
        title="GDP (Billions)",
        overlaying='y',
        side='right',
        showgrid=False,
        zeroline=False),

    legend=dict(orientation='h', y=-0.2)
)


st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────
# RADAR
# ─────────────────────────────
st.subheader("🕸️ Radar (% Impact)")


# Calculate global exposure across ALL scenarios
overall = df.groupby('Indicator').apply(
    lambda x: x['Impact'].sum() / x['Total'].sum() * 100
).reset_index(name='Percentage')

fig6 = go.Figure()

for sc in scenario_order:
    subset = df[df['Scenario'] == sc]
    vals = subset.groupby('Indicator').apply(
        lambda x: x['Impact'].sum() / x['Total'].sum() * 100
    )

    fig6.add_trace(go.Scatterpolar(
        r=list(vals) + [vals.iloc[0]],
        theta=list(vals.index) + [vals.index[0]],
        fill='toself',
        name=sc
    ))

fig6.update_layout(polar=dict(
        radialaxis=dict(
            title="Exposure (%)",
            range=[0, overall['Percentage'].max() * 1.2]  # 👈 keeps spacing clean
        )
    )
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

def risk(x):
    if x > 10: return "High"
    elif x > 5: return "Medium"
    else: return "Low"

top15['Risk Level'] = top15['Land % at +5m'].apply(risk)

st.dataframe(top15, use_container_width=True)
