# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 12:57:10 2026

@author: Janit
"""

import streamlit as st
import requests
import pandas as pd
import base64
import os
import math

API_URL = "https://ttc-system-project.azurewebsites.net"

def set_background(image_file):
    with open(image_file, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode()

    page_bg = f"""
    <style>
    .stApp {{
        background:
        linear-gradient(
            rgba(0,0,0,0.45),
            rgba(0,0,0,0.45)
        ),
        url("data:image/jpg;base64,{encoded_string}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """

    st.markdown(page_bg, unsafe_allow_html=True)

set_background("assets/ttc_transit.jpg")


st.title("Welcome to TTC Informative UI")


st.markdown("""
<div style="
    background: rgba(0, 0, 0, 0.55);
    padding: 30px;
    border-radius: 15px;
    backdrop-filter: blur(8px);
    max-width: 800px;
    margin: auto;
    color: white;
">

<h3 style="text-align:center;">🚍 TTC Transit Information System</h3>

<p style="text-align:center;">
This application allows users to explore Toronto Transit Commission (TTC) bus routes using a combination of Natural Language Generation (NLG) and structured transit data.
</p>

<p><strong>🔍 Features:</strong></p>

<ul>
<li>🚉 Find which subway stations are connected to a specific bus route</li>
<li>🚌 Discover which buses serve a particular station</li>
<li>📍 View stop sequences for selected bus routes</li>
</ul>

</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

st.markdown("""
<style>

/* Expander container */
div[data-testid="stExpander"] {
    background: rgba(0, 0, 0, 0.55) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(8px);
    padding: 10px !important;
}

/* Expander header */
div[data-testid="stExpander"] summary {
    color: white !important;
    font-weight: 600;
}

/* Expander content */
div[data-testid="stExpander"] p {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

with st.expander(" How this works"):
    st.markdown("""
                - Data sourced from GTFS transit feeds
                - Cleaned and enriched using rule-basesd transformation
                - FastAPI backend serves processed data
                - Streamlit UI provides interactive exploration
                """)
st.markdown(
    """
    <div style="
        position: relative;
        bottom: 0;
        width: 100%;
        padding: 10px 0;
        text-align: center;
        color: #fff;
        background: rgba(0, 0, 0, 0.4);
        border-radius: 10px;
        font-size: 0.85rem;
        margin-top: 20px;
    ">
        ✔ Supports 150+ validated TTC bus routes with enriched station data
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown("<br>", unsafe_allow_html=True)
st.divider()

st.markdown("🔍Start Exploring🔍")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚌 Bus Number", use_container_width=True):
        st.session_state["option"] = "Bus Number"

with col2:
    if st.button("🚉 Station", use_container_width=True):
        st.session_state["option"] = "Station"

option = st.session_state.get("option", "Bus Number")

if option == "Bus Number":


#  1. Bus → Station (NLG)

    st.markdown("### 🔍 Explore Bus routes w.r.t stations")

    bus_search = st.text_input("Enter Bus Number")

    if st.button("Search Bus", use_container_width=True):

        response = requests.get(API_URL)

        if response.status_code == 200:
            result = response.json()

            st.markdown(f"""
                            <div style="
                                background-color: rgba(255, 255, 255, 0.9);
                                padding: 1.2rem;
                                border-radius: 12px;
                               border-left: 6px solid #DA291C;
                               font-size: 18px;
                               color: #000;
                            ">
                                🚍 {result}
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.error("Bus not found")


#2. Station

if option == "Station":
    st.markdown("### 🔍 Explore stations info")
    station = st.text_input("Enter Station Name")

    if st.button("Search", use_container_width=True):

        response = requests.get(API_URL)

        if response.status_code == 200:
            result = response.json()

            st.markdown(f"""
                            <div style="
                                background-color: rgba(255, 255, 255, 0.9);
                                padding: 1.2rem;
                                border-radius: 12px;
                               border-left: 6px solid #DA291C;
                               font-size: 18px;
                               color: #000;
                            ">
                                🚍 {result}
                            </div>
                            """, unsafe_allow_html=True)
            
# 3. Bus → Stops (Dropdown)
st.markdown("---")

st.subheader("Bus Stops Sequence Search")
st.markdown(
    f"""
    <div style="
        background: rgba(255, 255, 255, 0.15);
        padding: 12px 15px;
        border-radius: 10px;
        backdrop-filter: blur(6px);
        color: #fff;
        font-size: 0.9rem;
        line-height: 1.3;
        margin-bottom: 10px;
    ">
    ⚠️ <strong>Stop Sequence Disclaimer</strong><br>
    • Data reflects available trip records and <strong>may not cover all route variants</strong> (e.g., 24A vs 24B).<br>
    • Some routes show stops from a <strong>representative trip</strong> rather than all possible variations.<br>
    </div>
    """,
    unsafe_allow_html=True
)
# Fetch all buses from API
response = requests.get(API_URL)
if response.status_code == 200:
    bus_numbers_all = response.json().get("buses", [])
else:
    st.error("Could not fetch bus numbers from backend")
    bus_numbers_all = []

# --- Step 1: Ultra-compact horizontal tick boxes ---
first_digits = sorted(set([b[0] for b in bus_numbers_all if b]))
st.write("Select First Digit(s) of Bus Number:")

selected_first_digits = []

# Set maximum columns per row (adjust for compactness)
max_cols = min(len(first_digits), 8)  # more columns = more compact
rows_needed = math.ceil(len(first_digits) / max_cols)

for row in range(rows_needed):
    cols_in_row = st.columns(max_cols, gap="xxsmall")  # very small gap
    for col_index in range(max_cols):
        digit_index = row * max_cols + col_index
        if digit_index < len(first_digits):
            digit = first_digits[digit_index]
            if cols_in_row[col_index].checkbox(digit, key=f"digit_{digit}"):
                selected_first_digits.append(digit)

# Filter buses based on selected digits 
buses_filtered = [b for b in bus_numbers_all if b[0] in selected_first_digits]

#Drop-down menu for actual bus number 
if buses_filtered:
    selected_bus = st.selectbox("Select Bus Number:", buses_filtered)
else:
    st.info("No buses match the selected digit(s).")
    selected_bus = None

# Show stops 
if selected_bus and st.button("Show Stops Table"):
    response_stops = requests.get(API_URL)
    if response_stops.status_code == 200:
        stops_data = response_stops.json().get("stops")
        if stops_data:
            stops_df = pd.DataFrame(stops_data)
            st.subheader(f"Stops Sequence for Bus {selected_bus}")
            st.dataframe(stops_df)
        else:
            st.info("No stops found for this bus.")
    else:
        st.error("Stops API error.")
        

