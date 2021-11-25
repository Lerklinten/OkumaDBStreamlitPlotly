import requests
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_lottie import st_lottie


st.set_page_config(page_title="OkumaDB Dashboard",
                   page_icon=":chart_with_upwards_trend:",
                   layout="wide"
                   )

# ----------------------------------------------------------------------------


@st.cache
def get_data_from_api(url: str, *tool: str):
    data = requests.get(url)
    dfs = pd.DataFrame(data.json())
    if tool:
        dfs["TimeLostToolBreakage"] = pd.to_datetime(
            dfs["OBrudConfirmedTimestamp"]
        ) - pd.to_datetime(dfs["TimeStamp"])

        dfs["TimeLostToolBreakage"] = (pd.to_numeric(
            dfs["TimeLostToolBreakage"].dt.total_seconds())/60).round(1)

    return dfs

    # ------------------------------------------------------------------------------


# Get data from API
dfs = get_data_from_api(
    "https://fastapi-okumadb.azurewebsites.net/okumaDb/cCurrentAlarm/toolBreakage/", "tool")
print(dfs[:5])

df = get_data_from_api(
    "https://fastapi-okumadb.azurewebsites.net/okumaDb/cCurrentAlarm/")
print(df[:5])

# Hyperlink tilbage til "/redoc"
st.markdown( "Okuma [API](https://fastapi-okumadb.azurewebsites.net/docs "Comment after hyperlink")", unsafe_allow_html=False)


# ---- SIDEBAR ----
st.sidebar.image("./static/okuma.png", use_column_width=False, width=275)
# Lottie function


def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


lottie_bigData = load_lottiefile("static/bigData.json")
lottie_bell = load_lottiefile("static/bell.json")
lottie_tool = load_lottiefile("static/tool.json")

#  Image
#st.sidebar.image("./static/graf.png", width=275)

with st.sidebar:
    st_lottie(lottie_bigData,
              speed=.3,
              reverse=False,
              loop=False,
              quality="low",
              renderer="svg",
              height=None,
              width=275,
              key=None,
              )

# Header
st.sidebar.header("Please Filter Here:")

with st.sidebar:
    st_lottie(lottie_bell,
              speed=1,
              reverse=False,
              loop=True,
              quality="high",
              width=25,
              )

alarmNumber = st.sidebar.multiselect(
    "Select AlarmNumber:",
    options=dfs["AlarmNumber"].unique(),
    default=dfs["AlarmNumber"].unique()
)
with st.sidebar:
    st_lottie(lottie_tool,
              speed=1,
              reverse=False,
              loop=True,
              quality="high",
              width=25,
              )

toolName = st.sidebar.multiselect(
    "Select Tool Number:",
    options=dfs["GetToolName"].unique(),
    default=dfs["GetToolName"].unique()
)
# Use filter for querry, @alarmNumber = variable alarmNumber
dfs = dfs.query(
    "AlarmNumber==@alarmNumber & GetToolName==@toolName")


# ---------------MAIN PAGE-----------

st.title("ToolBreakage")
st. markdown("##")


# Toolbreakage count per tool
number_of_tool_broken_per_tool = (dfs['GetToolName'].value_counts())

fig_tool_broken = px.bar(
    number_of_tool_broken_per_tool,
    x="GetToolName",
    y=number_of_tool_broken_per_tool.index,
    orientation="h",
    title="<b> Top ToolBreakage tool </b>",
    template="plotly_dark",


)
number_of_OBrud_checked = dfs['TimeLostToolBreakage'].value_counts()

fig_OBrud_Checked = px.bar(
    number_of_OBrud_checked,
    x="TimeLostToolBreakage",
    y=number_of_OBrud_checked.index,
    orientation="v",
    title="<b> Toolbreakage checked by operator </b>",
    template="plotly_dark",


)


# Remove lines and background color from fig;
fig_tool_broken.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)
fig_OBrud_Checked.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# Insert to columms for figs:
left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_tool_broken, use_container_width=True)
right_column.plotly_chart(fig_OBrud_Checked, use_container_width=True)


# Show data
st.text("Raw Data Table, from MSSQL Database:")
st.dataframe(dfs)

st.text("Number of OBrud checked")
st.dataframe(number_of_OBrud_checked)
# print(number_of_OBrud_checked)

# Print all alarms
st.text("All alarm sorted by datetime")
st.dataframe(df)


# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
