import streamlit as st
import json
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl

# 1. PAGE SETUP
st.set_page_config(page_title="Sarawak Gazette NLP Map", layout="wide")

# CUSTOM CSS FOR TOP NAVBAR
st.markdown("""
    <style>
        .navbar {
            display: flex;
            background-color: #f8f9fa;
            padding: 10px;
            border-bottom: 1px solid #ddd;
            margin-bottom: 20px;
        }
        .nav-item { margin-right: 20px; font-weight: bold; }
    </style>
    <div class="navbar">
        <div class="nav-item">🗺️ Sarawak Gazetteer</div>
        <div class="nav-item"><a href="https://sarawak-gazette.com/" target="_blank">Gazette Archive Website</a></div>
    </div>
""", unsafe_allow_html=True)

st.title("Automated Historical Map Interface")

# 2. FILTERING AREA (Top section)
col1, col2 = st.columns([1, 4])
with col1:
    model_filter = st.radio("Model View:", ["Show All", "Baseline LSTM", "BiLSTM-CRF"])

# 3. LOAD & GROUP DATA
@st.cache_data
def load_data():
    with open('sarawak_gazetteer.json', 'r') as file:
        return json.load(file)

data = load_data()

grouped_locations = {}
for record in data:
    if model_filter != "Show All" and record["model_source"] != model_filter:
        continue
    loc_name = record["historical_name"]
    if loc_name not in grouped_locations:
        grouped_locations[loc_name] = {"coordinates": record["coordinates"], "model_source": record["model_source"], "mentions": []}
    grouped_locations[loc_name]["mentions"].append({"metadata": record["source_metadata"], "text": record["snippet_text"]})

# 4. BUILD MAP WITH PLUGINS
m = folium.Map(location=[2.5, 113.0], zoom_start=7, tiles="CartoDB positron")

# Add "Recenter" button
LocateControl(auto_start=False).add_to(m)

# Add Marker Layer
fg = folium.FeatureGroup(name="Gazette Locations")
for loc_name, details in grouped_locations.items():
    lat, lon = details["coordinates"]
    color = "blue" if details["model_source"] == "LSTM" else "red"
    
    # [Insert HTML logic for popup here - use the carousel code from previous step]
    # (Abbreviated for brevity, paste the popup loop here!)
    
    folium.Marker([lat, lon], tooltip=loc_name).add_to(fg)

fg.add_to(m)
folium.LayerControl().add_to(m) # Add Layer Toggle

# 5. DISPLAY MAP
st_folium(m, width=1200, height=600)
