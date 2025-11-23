import pandas as pd
import requests
import streamlit as st
import plotly.express as px

# =====================================================
# CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Ghana Nutrition & Education Dashboard",
    layout="wide"
)

COUNTRY_GH = "GHA"
COUNTRY_US = "USA"
INDICATORS = {
    "Child Anemia (% of children under 5)": "SH.ANM.CHLD.ZS",
    "Population with Safe Drinking Water (%)": "SH.H2O.SMDW.ZS",
    "Secondary Enrollment (% gross, both genders)": "SE.SEC.ENRR",
    "Educational attainment (Bachelor's or equivalent) (%)": "SE.TER.CUAT.BA.ZS",
    "GDP per Capita (USD)": "NY.GDP.PCAP.CD"
}

indicator_description = {
    "Child Anemia (% of children under 5)": (
        "This shows the prevalence of anemia among young children, often linked to iron and nutrient deficiencies. "
        "For a dietetics partnership, it highlights areas where interventions and research could make a tangible impact "
        "on child nutrition and public health in Ghana."
    ),
    "Population with Safe Drinking Water (%)": (
        "Access to safe drinking water is essential for proper nutrition and health. "
        "This indicator helps the partnership identify opportunities for combined water and nutrition education programs "
        "and community interventions."
    ),
    "Secondary Enrollment (% gross, both genders)": (
        "Secondary enrollment (% gross) shows the total number of students enrolled in secondary education "
        "as a percentage of the population in the official secondary‑school age group. "
        "It allows for fair comparison between Ghana and the USA and indicates the strength of the student pipeline for dietetics programs."
    ),
    "Educational attainment (Bachelor's or equivalent) (%)": (
        "This metric shows the proportion of adults who have completed tertiary education (education beyond high school). "
        "It indicates the pool of potential students and collaborators for research, internships, and joint curriculum development "
        "in dietetics."
    ),
    "GDP per Capita (USD)": (
        "GDP per capita provides economic context that can affect program funding, access to food resources, and sustainability. "
        "Understanding economic conditions helps design realistic and effective nutrition interventions and educational programs."
    )
}


# =====================================================
# FETCH DATA FUNCTION
# =====================================================

def fetch_worldbank_data(country, code):
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{code}?format=json&per_page=2000"
    response = requests.get(url).json()
    if not isinstance(response, list) or len(response) < 2:
        return pd.DataFrame()
    df = pd.DataFrame(response[1])
    df["indicator_code"] = code
    df["country"] = country
    return df

# =====================================================
# DOWNLOAD DATA
# =====================================================

dfs = []
for label, code in INDICATORS.items():
    for country in [COUNTRY_GH, COUNTRY_US]:
        df = fetch_worldbank_data(country, code)
        if not df.empty:
            df["indicator_label"] = label
            dfs.append(df)

data = pd.concat(dfs).reset_index(drop=True)
data["date"] = pd.to_numeric(data["date"], errors="coerce")
data = data.sort_values("date")

ghana = data[data["country"] == COUNTRY_GH]
usa = data[data["country"] == COUNTRY_US]

# =====================================================
# PAGE TITLE
# =====================================================

st.markdown(
    "<h1 style='text-align:center;'>🇬🇭 Ghana Nutrition & Education Dashboard</h1>",
    unsafe_allow_html=True
)
st.write(
    "This dashboard visualizes World Bank development indicators and compares "
    "Ghana with the United States to explore potential academic and dietetics partnerships."
)

# =====================================================
# SELECT INDICATOR
# =====================================================

selected_label = st.selectbox(
    "Select an indicator:",
    list(INDICATORS.keys()),
    key="indicator_select"
)

selected_code = INDICATORS[selected_label]

df_gh_sel = ghana[ghana["indicator_code"] == selected_code]
df_us_sel = usa[usa["indicator_code"] == selected_code]

# Combine for single chart
df_combined = pd.concat([df_gh_sel, df_us_sel])
max_y_combined = df_combined["value"].dropna().max()

# =====================================================
# SINGLE FULL-WIDTH CHART
# =====================================================

if df_combined.empty:
    st.warning("No data available for this indicator.")
else:
    fig = px.line(
        df_combined,
        x="date",
        y="value",
        color="country",
        title=f"{selected_label}: Ghana vs USA",
        labels={
            "date": "Year",
            "value": selected_label,
            "country": "Country"
        }
    )
    fig.update_yaxes(range=[0, max_y_combined])
    st.plotly_chart(fig, use_container_width=True)

    # Display indicator explanation
    st.markdown(f"**About this indicator:** {indicator_description[selected_label]}")
