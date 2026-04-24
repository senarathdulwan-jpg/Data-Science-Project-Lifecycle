import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Sea Level Dashboard", layout="wide")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_excel("Data Science Project Lifecycle.xlsx")
# -----------------------------
# TITLE
# -----------------------------
st.title("🌊 Sea Level Rise Impact Dashboard")

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")

indicator = st.sidebar.selectbox("Indicator", sorted(df["Indicator"].unique()))
scenario = st.sidebar.selectbox("Scenario", sorted(df["Scenario"].unique()))

filtered_df = df[
    (df["Indicator"] == indicator) &
    (df["Scenario"] == scenario)
]

# -----------------------------
# KPI CARDS
# -----------------------------
st.subheader("Key Metrics")

col1, col2, col3 = st.columns(3)

total_sum = filtered_df["Total"].sum()
impact_sum = filtered_df["Impact"].sum()
avg_percent = filtered_df["Percentage"].mean()

col1.metric("Total", f"{total_sum:,.0f}")
col2.metric("Total Impact", f"{impact_sum:,.0f}")
col3.metric("Avg Impact %", f"{avg_percent:.2f}%")

# -----------------------------
# ROW 1 — BAR + HEATMAP
# -----------------------------
col4, col5 = st.columns(2)

# 🔹 BAR CHART
with col4:
    st.subheader("Top 10 Countries by Impact")

    top_df = filtered_df.sort_values(by="Impact", ascending=False).head(10)

    fig, ax = plt.subplots()
    ax.barh(top_df["Country"], top_df["Impact"])
    ax.invert_yaxis()
    st.pyplot(fig)

# 🔹 HEATMAP
with col5:
    st.subheader("Heatmap (Top 10 Countries)")

    pivot = df[df["Indicator"] == indicator].pivot_table(
        index="Scenario",
        columns="Country",
        values="Percentage"
    )

    pivot = pivot[top_df["Country"]]

    fig2, ax2 = plt.subplots()
    cax = ax2.imshow(pivot, aspect='auto')
    ax2.set_xticks(range(len(pivot.columns)))
    ax2.set_xticklabels(pivot.columns, rotation=90)
    ax2.set_yticks(range(len(pivot.index)))
    ax2.set_yticklabels(pivot.index)

    fig2.colorbar(cax)
    st.pyplot(fig2)

# -----------------------------
# ROW 2 — SCATTER
# -----------------------------
st.subheader("Total vs Impact Relationship")

fig3, ax3 = plt.subplots()
ax3.scatter(filtered_df["Total"], filtered_df["Impact"])
ax3.set_xlabel("Total")
ax3.set_ylabel("Impact")
st.pyplot(fig3)

# -----------------------------
# TABLE — TOP 15
# -----------------------------
st.subheader("Top 15 Most Vulnerable Countries")

table_df = filtered_df.sort_values(by="Percentage", ascending=False).head(15)

st.dataframe(table_df)

# -----------------------------
# INSIGHTS
# -----------------------------
st.subheader("Key Insights")

st.markdown("""
- 🌍 Higher sea-level scenarios significantly increase impact across all indicators.
- 📈 Countries with smaller land areas often show higher percentage exposure.
- ⚠️ Coastal and island nations dominate the high-risk category.
- 💰 Economic (GDP) exposure rises sharply in higher scenarios.
""")
