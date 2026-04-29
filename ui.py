# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 12:57:10 2026

@author: Janit
"""

import streamlit as st
import requests
import pandas as pd
import base64
import math
import os

API_URL = "https://ttc-system-project-e5cdf5aub6fzdabg.canadacentral-01.azurewebsites.net"


# ---------------- HELPER ----------------
def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=10)
        return response.json()
    except:
        return {}


# ---------------- BACKGROUND ----------------
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


BASE_DIR = os.path.dirname(__file__)
image_path = os.path.join(BASE_DIR, "..", "assets", "ttc_transit.jpg")

set_background(image_path)

st.title("🚍 TTC Transit Information System")


# ---------------- DESCRIPTION ----------------
st.markdown("""
<div style="
    background: rgba(0, 0, 0, 0.55);
    padding: 25px;
    border-radius: 15px;
    backdrop-filter: blur(8px);
    color: white;
">

### Explore Toronto Transit Data

• Find which subway stations a bus connects to  
• Discover buses serving a station  
• View stop sequences for routes  

</div>
""", unsafe_allow_html=True)

st.divider()

with st.expander("📘 How it Works & Data Disclaimer"):

    st.markdown("""
    <div style="
        background: rgba(0, 0, 0, 0.55);
        padding: 20px;
        border-radius: 12px;
        backdrop-filter: blur(6px);
        color: white;
    ">

    ### ⚙️ How This System Works

    • Built using **FastAPI (backend)** and **Streamlit (frontend)**  
    • Data is processed from GTFS transit datasets and stored in a structured SQLite database  
    • SQL queries are used to dynamically retrieve:
      - Bus → Station relationships  
      - Station → Bus mappings  
      - Stop sequences for routes  

    • A lightweight Natural Language Generation (NLG) layer converts raw results into readable responses  

    <br>

    ### ⚠️ Data Disclaimer

    • Stop sequences are derived from the **most complete available trip** for each route  
    • Some bus routes have multiple variants (e.g., 24A, 24B)  
    • Due to dataset limitations:
      - Variant-specific routes may not be fully distinguishable  
      - A representative route is shown instead  

    • Minor inconsistencies may exist due to:
      - Missing trip-level data  
      - Incomplete variant mappings  

    </div>
    """, unsafe_allow_html=True)

st.markdown("### 🔍 Start Exploring")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚌 Bus Number", use_container_width=True):
        st.session_state["option"] = "Bus Number"

with col2:
    if st.button("🚉 Station", use_container_width=True):
        st.session_state["option"] = "Station"

option = st.session_state.get("option", "Bus Number")


# ---------------- BUS → STATION ----------------
if option == "Bus Number":

    st.markdown("### 🔍 Explore Bus routes w.r.t stations")
    bus_search = st.text_input("Enter Bus Number")

    if st.button("Search Bus", use_container_width=True):

        with st.spinner("Fetching data..."):
            data = fetch_data(f"/bus/{bus_search}")

        result = data.get("data")

        if not result:
            st.warning("No data found.")
        else:
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


# ---------------- STATION → BUS ----------------
if option == "Station":

    st.markdown("### 🔍 Explore stations info")
    station = st.text_input("Enter Station Name")

    if st.button("Search", use_container_width=True):

        with st.spinner("Fetching data..."):
            data = fetch_data(f"/station/{station}")

        result = data.get("data")

        if not result:
            st.warning("No data found.")
        else:
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


# ---------------- BUS STOP SEQUENCE ----------------
st.markdown("---")

st.subheader("🛑 Bus Stops Sequence Search")

# Fetch buses
data = fetch_data("/bus_numbers")
bus_numbers_all = data.get("data", [])

if not bus_numbers_all:
    st.warning("No bus data available. Check backend connection.")
    st.stop()

# First digit filter
first_digits = sorted(set([str(b)[0] for b in bus_numbers_all if b]))

st.write("Select First Digit(s) of Bus Number:")

selected_first_digits = []

max_cols = min(len(first_digits), 8)
rows_needed = math.ceil(len(first_digits) / max_cols)

for row in range(rows_needed):
    cols = st.columns(max_cols, gap="xxsmall")
    for col_index in range(max_cols):
        digit_index = row * max_cols + col_index
        if digit_index < len(first_digits):
            digit = first_digits[digit_index]
            if cols[col_index].checkbox(digit, key=f"digit_{digit}"):
                selected_first_digits.append(digit)

# Filter buses
buses_filtered = [b for b in bus_numbers_all if str(b)[0] in selected_first_digits]

if buses_filtered:
    selected_bus = st.selectbox("Select Bus Number:", buses_filtered)
else:
    st.info("No buses match the selected digit(s).")
    selected_bus = None


# ---------------- SHOW STOPS ----------------
if selected_bus and st.button("Show Stops Table"):

    with st.spinner("Loading stops..."):
        data = fetch_data(f"/bus/{selected_bus}/stops")

    stops = data.get("data")

    if not stops:
        st.warning("No stops found for this bus.")
    else:
        stops_df = pd.DataFrame(stops)

        st.subheader(f"Stops Sequence for Bus {selected_bus} (Representative Route)")

        st.info(
            "ℹ️ Stop sequence is based on the most complete available trip. "
            "Variant-specific routes may not be fully distinguished due to dataset limitations."
        )

        st.dataframe(stops_df)