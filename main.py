import requests
import json
from datetime import datetime

# import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
from pandas import Series, DataFrame
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="OkumaDB Dashboard",
                   page_icon=":chart_with_upwards_trend:",
                   layout="wide"
                   )

# ----------------------------------------------------------------------------


@st.cache
def get_data_from_api():
    url = f"http://127.0.0.1:8000/okumaDb/cCurrentAlarm/toolBreakage"
    data = requests.get(url)

    dfs = pd.DataFrame(data.json())

    dfs["TimeLostToolBreakage"] = pd.to_datetime(
        dfs["OBrudConfirmedTimestamp"]
    ) - pd.to_datetime(dfs["TimeStamp"])

    dfs["TimeLostToolBreakage"] = (pd.to_numeric(
        dfs["TimeLostToolBreakage"].dt.total_seconds())/60).round(1)

    return dfs

    # ------------------------------------------------------------------------------


dfs = get_data_from_api()
print(dfs[:5])

# ---- SIDEBAR ----
st.sidebar.image("./static/graf.png", use_column_width=True, width=275)

st.sidebar.header("Please Filter Here:")
alarmNumber = st.sidebar.multiselect(
    "Select AlarmNumber:",
    options=dfs["AlarmNumber"].unique(),
    default=dfs["AlarmNumber"].unique()
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
st.title(":computer: OKUMA DB ToolBreakage")
st. markdown("##")


# Toolbreakage count per tool
number_of_tool_broken_per_tool = (dfs['GetToolName'].value_counts())

fig_tool_broken = px.bar(
    number_of_tool_broken_per_tool,
    x="GetToolName",
    y=number_of_tool_broken_per_tool.index,
    orientation="h",
    title="<b> Top ToolBreakage tool </b>",
    template="plotly_white",
)

# Remove lines and background color from fig;
fig_tool_broken.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)
st.plotly_chart(fig_tool_broken)

# Show data
st.text("Raw Data Table, from MSSQL Database:")
st.dataframe(dfs)


# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
