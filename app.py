import streamlit as st
import json
import folium
from streamlit_folium import st_folium

# 1. PAGE SETUP (The "Navbar" and title)
st.set_page_config(page_title="Sarawak Gazette NLP Map", layout="wide")

st.sidebar.title("Navigation & Filters")
st.sidebar.info("This interactive web application displays historical locations extracted from the Sarawak Gazette using BiLSTM-CRF neural networks.")
model_filter = st.sidebar.radio("Compare Models:", ["Show All", "Baseline LSTM", "BiLSTM-CRF"])

st.title("🗺️ Sarawak Gazette: Automated Historical Gazetteer")

# 2. LOAD THE DATA (Automatically updates when Colab pushes new JSON)
@st.cache_data
def load_data():
    with open('sarawak_gazetteer.json', 'r') as file:
        return json.load(file)

data = load_data()

# 3. BUILD THE MAP
# Centered on Sarawak
m = folium.Map(location=[2.5, 113.0], zoom_start=6, tiles="CartoDB positron")

# Loop through the JSON and plot the points
for record in data:
    # Apply sidebar filter logic
    if model_filter != "Show All" and record["model_source"] != model_filter:
        continue
        
    lat, lon = record["coordinates"]
    color = "blue" if record["model_source"] == "LSTM" else "red"
    
    # Same-Sentence Popup HTML
    popup_html = f"""
    <b>Location:</b> {record['historical_name']}<br>
    <b>Source:</b> {record['source_metadata']}<br>
    <hr>
    <i>"{record['snippet_text']}"</i>
    """
    
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color=color, icon="info-sign"),
        tooltip=record['historical_name']
    ).add_to(m)

# 4. RENDER MAP ON THE WEBSITE
st_folium(m, width=1200, height=600)