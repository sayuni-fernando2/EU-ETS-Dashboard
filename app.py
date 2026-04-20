import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration

st.set_page_config(
    page_title="EU ETS Emissions Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load data

@st.cache_data
def load_data():
    df = pd.read_csv("ets_clean.csv")
    return df

df = load_data()

# Sidebar

st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/320px-Flag_of_Europe.svg.png",
    width=100,
)
st.sidebar.title("EU ETS Dashboard")
st.sidebar.markdown("Use the filters below to explore the data.")
st.sidebar.markdown("---")

# Country filter
all_countries = sorted(df["COUNTRY"].unique())
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=all_countries,
    default=["Germany", "France", "Poland", "Italy", "Spain"],
)

# Sector filter
all_sectors = sorted(df["SECTOR"].unique())
selected_sectors = st.sidebar.multiselect(
    "Select Sectors",
    options=all_sectors,
    default=all_sectors,
)

# Year range filter
min_year = int(df["YEAR"].min())
max_year = int(df["YEAR"].max())
selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Data Source:** European Environment Agency (EEA)")
st.sidebar.markdown("**Coverage:** 2005 - 2024")
st.sidebar.markdown("**Unit:** Tonnes of CO2 equivalent")

# Filter data

if not selected_countries:
    selected_countries = all_countries
if not selected_sectors:
    selected_sectors = all_sectors

filtered_df = df[
    (df["COUNTRY"].isin(selected_countries))
    & (df["SECTOR"].isin(selected_sectors))
    & (df["YEAR"] >= selected_years[0])
    & (df["YEAR"] <= selected_years[1])
]

# Header

st.title("EU Emissions Trading System Dashboard")
st.markdown(
    """
    This dashboard analyses greenhouse gas emissions from industrial installations
    across Europe, as reported under the **EU Emissions Trading System (EU ETS)**.
    Use the sidebar filters to explore emissions by country, sector, and year.
    """
)
st.markdown("---")

# KPI summary cards

st.subheader("Key Summary Statistics")

total_emissions = filtered_df["VERIFIED_EMISSIONS"].sum()
avg_annual = filtered_df.groupby("YEAR")["VERIFIED_EMISSIONS"].sum().mean()
top_country = (
    filtered_df.groupby("COUNTRY")["VERIFIED_EMISSIONS"]
    .sum()
    .idxmax()
    if not filtered_df.empty else "N/A"
)
top_sector = (
    filtered_df.groupby("SECTOR")["VERIFIED_EMISSIONS"]
    .sum()
    .idxmax()
    if not filtered_df.empty else "N/A"
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Emissions",
        value=f"{total_emissions / 1e9:.2f} Gt CO2",
        help="Total verified emissions for selected filters",
    )
with col2:
    st.metric(
        label="Avg Annual Emissions",
        value=f"{avg_annual / 1e6:.1f} Mt CO2",
        help="Average annual emissions across selected years",
    )
with col3:
    st.metric(
        label="Top Emitting Country",
        value=top_country,
        help="Country with the highest total emissions",
    )
with col4:
    st.metric(
        label="Top Emitting Sector",
        value=top_sector[:25] + "..." if len(top_sector) > 25 else top_sector,
        help="Sector with the highest total emissions",
    )

st.markdown("---")

# Section 1: Emissions Trend Over Time

st.subheader("Emissions Trend Over Time")
st.markdown("Track how emissions have changed year by year for each selected country.")

trend_df = (
    filtered_df.groupby(["YEAR", "COUNTRY"])["VERIFIED_EMISSIONS"]
    .sum()
    .reset_index()
)
trend_df["VERIFIED_EMISSIONS_MT"] = trend_df["VERIFIED_EMISSIONS"] / 1e6

fig_trend = px.line(
    trend_df,
    x="YEAR",
    y="VERIFIED_EMISSIONS_MT",
    color="COUNTRY",
    markers=True,
    title="Annual Verified Emissions by Country (Million Tonnes CO2)",
    labels={
        "YEAR": "Year",
        "VERIFIED_EMISSIONS_MT": "Emissions (Mt CO2)",
        "COUNTRY": "Country",
    },
    template="plotly_white",
)
fig_trend.update_layout(
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
    height=450,
)
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# Section 2: Emissions by Country

st.subheader("Total Emissions by Country")
st.markdown("Compare total verified emissions across selected countries for the chosen time period.")

country_df = (
    filtered_df.groupby("COUNTRY")["VERIFIED_EMISSIONS"]
    .sum()
    .reset_index()
    .sort_values("VERIFIED_EMISSIONS", ascending=False)
)
country_df["VERIFIED_EMISSIONS_MT"] = country_df["VERIFIED_EMISSIONS"] / 1e6

fig_country = px.bar(
    country_df,
    x="COUNTRY",
    y="VERIFIED_EMISSIONS_MT",
    title="Total Verified Emissions by Country (Million Tonnes CO2)",
    labels={
        "COUNTRY": "Country",
        "VERIFIED_EMISSIONS_MT": "Emissions (Mt CO2)",
    },
    color="VERIFIED_EMISSIONS_MT",
    color_continuous_scale="Reds",
    template="plotly_white",
)
fig_country.update_layout(
    xaxis_tickangle=-45,
    coloraxis_showscale=False,
    height=450,
)
st.plotly_chart(fig_country, use_container_width=True)

st.markdown("---")

# Section 3: Emissions by Sector

st.subheader("Emissions by Sector")
st.markdown("Understand which industry sectors contribute most to total emissions.")

col_left, col_right = st.columns(2)

sector_df = (
    filtered_df.groupby("SECTOR")["VERIFIED_EMISSIONS"]
    .sum()
    .reset_index()
    .sort_values("VERIFIED_EMISSIONS", ascending=False)
)
sector_df["VERIFIED_EMISSIONS_MT"] = sector_df["VERIFIED_EMISSIONS"] / 1e6

with col_left:
    fig_sector_bar = px.bar(
        sector_df,
        x="VERIFIED_EMISSIONS_MT",
        y="SECTOR",
        orientation="h",
        title="Emissions by Sector (Mt CO2)",
        labels={
            "SECTOR": "Sector",
            "VERIFIED_EMISSIONS_MT": "Emissions (Mt CO2)",
        },
        color="VERIFIED_EMISSIONS_MT",
        color_continuous_scale="Blues",
        template="plotly_white",
    )
    fig_sector_bar.update_layout(
        coloraxis_showscale=False,
        height=500,
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig_sector_bar, use_container_width=True)

with col_right:
    fig_pie = px.pie(
        sector_df.head(8),
        values="VERIFIED_EMISSIONS_MT",
        names="SECTOR",
        title="Sector Share of Total Emissions (Top 8)",
        template="plotly_white",
        hole=0.3,
    )
    fig_pie.update_layout(height=500)
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# Section 4: Country vs Sector Heatmap

st.subheader("Country vs Sector Emissions Heatmap")
st.markdown("Identify which sectors are the biggest emitters in each country.")

top_sectors = (
    filtered_df.groupby("SECTOR")["VERIFIED_EMISSIONS"]
    .sum()
    .nlargest(6)
    .index.tolist()
)

heatmap_df = (
    filtered_df[filtered_df["SECTOR"].isin(top_sectors)]
    .groupby(["COUNTRY", "SECTOR"])["VERIFIED_EMISSIONS"]
    .sum()
    .reset_index()
)
heatmap_pivot = heatmap_df.pivot(
    index="COUNTRY", columns="SECTOR", values="VERIFIED_EMISSIONS"
).fillna(0) / 1e6

fig_heatmap = px.imshow(
    heatmap_pivot,
    title="Emissions by Country and Sector (Mt CO2) - Top 6 Sectors",
    labels=dict(x="Sector", y="Country", color="Mt CO2"),
    color_continuous_scale="YlOrRd",
    aspect="auto",
    template="plotly_white",
)
fig_heatmap.update_layout(
    height=500,
    xaxis_tickangle=-30,
)
st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("---")

# Section 5: Raw Data Table

st.subheader("Explore the Raw Data")
st.markdown("Browse the filtered dataset directly.")

show_data = st.checkbox("Show raw data table")
if show_data:
    display_df = (
        filtered_df.groupby(["COUNTRY", "SECTOR", "YEAR"])["VERIFIED_EMISSIONS"]
        .sum()
        .reset_index()
        .sort_values(["COUNTRY", "YEAR"])
    )
    display_df["VERIFIED_EMISSIONS"] = display_df["VERIFIED_EMISSIONS"].apply(
        lambda x: f"{x:,.0f}"
    )
    display_df.columns = ["Country", "Sector", "Year", "Verified Emissions (Tonnes CO2)"]
    st.dataframe(display_df, use_container_width=True)

# Footer

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: grey; font-size: 13px;'>
    EU ETS Emissions Dashboard | 5DATA004C Data Science Project Lifecycle<br>
    Data Source: European Environment Agency (EEA) |
    <a href='https://www.eea.europa.eu/en/datahub/datahubitem-view/98f04097-26de-4fca-86c4-63834818c0c0' target='_blank'>Dataset Link</a>
    </div>
    """,
    unsafe_allow_html=True,
)