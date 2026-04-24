import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# ===============================
# LOAD DATA
# ===============================
@st.cache_data
def load_data():
    df = pd.read_excel("Data Science Project Lifecycle.xlsx")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# ===============================
# CLEANING (FIX YOUR OLD BUGS HERE)
# ===============================

# Normalize Scenario names (VERY IMPORTANT)
df["Scenario"] = df["Scenario"].str.replace(" ", "")
# "1 meter" → "1meter"

# Sort scenarios properly
scenario_order = ["1meter","2meter","3meter","4meter","5meter"]

df["Scenario"] = pd.Categorical(df["Scenario"], categories=scenario_order, ordered=True)

# ===============================
# SIDEBAR
# ===============================
st.sidebar.title("🌊 Filters")

selected_scenario = st.sidebar.selectbox(
    "Select Scenario",
    scenario_order
)

selected_indicator = st.sidebar.selectbox(
    "Select Indicator",
    df["Indicator"].unique()
)

# ===============================
# TITLE
# ===============================
st.title("🌊 Sea-Level Rise Impact Dashboard")

# ===============================
# KPI SECTION (USING IMPACT)
# ===============================
st.subheader(f"📊 Global Impact — {selected_scenario}")

kpi_df = df[df["Scenario"] == selected_scenario]

col1, col2, col3 = st.columns(3)

def get_total(ind):
    return kpi_df[kpi_df["Indicator"] == ind]["Impact"].sum()

col1.metric("🌍 Land at Risk", f"{get_total('Land'):,.0f}")
col2.metric("👥 Population Exposed", f"{get_total('Population'):,.0f}")
col3.metric("💰 GDP Exposed", f"{get_total('GDP'):,.0f}")

st.markdown("---")

# ===============================
# GLOBAL TREND (PERCENTAGE)
# ===============================
st.subheader("📈 Global Trend (% Impact)")

trend_df = df.groupby(["Scenario","Indicator"])["Percentage"].mean().reset_index()

fig_line = px.line(
    trend_df,
    x="Scenario",
    y="Percentage",
    color="Indicator",
    markers=True
)

st.plotly_chart(fig_line, use_container_width=True)

# ===============================
# REGIONAL BREAKDOWN
# ===============================
st.subheader("🌍 Continent Breakdown")

region_df = df[
    (df["Indicator"] == selected_indicator)
]

region_group = region_df.groupby(["Continent","Scenario"])["Impact"].sum().reset_index()

fig_region = px.bar(
    region_group,
    x="Continent",
    y="Impact",
    color="Scenario",
    barmode="group"
)

st.plotly_chart(fig_region, use_container_width=True)

# ===============================
# TOP COUNTRIES
# ===============================
st.subheader(f"🏆 Top 15 Countries — {selected_indicator}")

top_df = df[
    (df["Scenario"] == selected_scenario) &
    (df["Indicator"] == selected_indicator)
]

top_df = top_df.sort_values(by="Percentage", ascending=False).head(15)

fig_top = px.bar(
    top_df,
    x="Percentage",
    y="Country",
    orientation="h",
    color="Percentage",
    color_continuous_scale="Reds"
)

st.plotly_chart(fig_top, use_container_width=True)

# ===============================
# HEATMAP (FIXED PERFECTLY)
# ===============================
st.subheader("🔥 Vulnerability Heatmap")

heat_df = df[df["Indicator"] == selected_indicator]

heat_pivot = heat_df.pivot_table(
    index="Country",
    columns="Scenario",
    values="Percentage"
)

# Top 15 based on selected scenario
heat_pivot = heat_pivot.sort_values(by=selected_scenario, ascending=False).head(15)

fig_heat = px.imshow(
    heat_pivot,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="Reds"
)

st.plotly_chart(fig_heat, use_container_width=True)

# ===============================
# DUAL AXIS (POP vs GDP)
# ===============================
st.subheader("📊 Population vs GDP")

pop_df = df[df["Indicator"] == "Population"].groupby("Scenario")["Impact"].sum()
gdp_df = df[df["Indicator"] == "GDP"].groupby("Scenario")["Impact"].sum()

fig_dual = go.Figure()

fig_dual.add_trace(go.Scatter(
    x=pop_df.index,
    y=pop_df.values,
    name="Population",
    mode="lines+markers"
))

fig_dual.add_trace(go.Scatter(
    x=gdp_df.index,
    y=gdp_df.values,
    name="GDP",
    mode="lines+markers",
    yaxis="y2"
))

fig_dual.update_layout(
    yaxis=dict(title="Population"),
    yaxis2=dict(title="GDP", overlaying="y", side="right")
)

st.plotly_chart(fig_dual, use_container_width=True)

# ===============================
# RADAR CHART
# ===============================
st.subheader("🧭 Impact Profile")

radar_df = df[df["Scenario"] == selected_scenario]

radar_group = radar_df.groupby("Indicator")["Percentage"].mean().reset_index()

fig_radar = go.Figure()

fig_radar.add_trace(go.Scatterpolar(
    r=radar_group["Percentage"],
    theta=radar_group["Indicator"],
    fill='toself'
))

st.plotly_chart(fig_radar, use_container_width=True)

# ===============================
# TABLE
# ===============================
st.subheader("📋 Top Countries Table")

st.dataframe(top_df)
