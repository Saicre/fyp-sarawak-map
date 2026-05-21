import streamlit as st
import json
import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen

# 1. PAGE SETUP
st.set_page_config(page_title="Sarawak Gazette NLP Map", layout="wide")

# Custom Navbar
st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-bottom: 2px solid #ddd; margin-bottom: 20px;">
        <h2 style="margin:0;">🗺️ Sarawak Gazette Historical Gazetteer</h2>
    </div>
""", unsafe_allow_html=True)

# 2. FILTERING
model_filter = st.radio("Filter by Model Source:", ["Show All", "LSTM", "BiLSTM-CRF"], horizontal=True)

# 3. DATA LOADING
@st.cache_data
def load_data():
    with open('sarawak_gazetteer.json', 'r') as file:
        return json.load(file)

data = load_data()

# 4. MAP STATE MANAGEMENT
# We use a button to reset the center coordinates
if st.button("📍 Recenter Map to Sarawak"):
    st.session_state.center = [2.55, 113.0]
    st.session_state.zoom = 7
    st.rerun()

# Initialize session state if not set
if 'center' not in st.session_state:
    st.session_state.center = [2.55, 113.0]
    st.session_state.zoom = 7

# 5. BUILD MAP
m = folium.Map(location=st.session_state.center, zoom_start=st.session_state.zoom, tiles='cartodbpositron')
Fullscreen().add_to(m)

# Marker Logic (your exact colab logic)
for record in data:
    if model_filter != "Show All" and record["model_source"] != model_filter:
        continue
    
    # Matching your requested popup interface EXACTLY
    linked = record['linked_entities']
    display_hist = record['historical_name'] if record['historical_name'] != record['normalized_name'] else "N/A (Unchanged)"
    
    popup_html = f"""
    <b>ID:</b> {record['location_id']}<br>
    <b>Current Name:</b> {record['normalized_name']}<br>
    <b>Historical Name:</b> {display_hist}<br>
    <b>Model:</b> {record['model_source']}<br>
    <hr>
    <b>People:</b> {', '.join(linked.get('PERSON', [])) if linked.get('PERSON') else 'None'}<br>
    <b>Dates:</b> {', '.join(linked.get('DATE', [])) if linked.get('DATE') else 'None'}<br>
    <b>Orgs:</b> {', '.join(linked.get('ORGANISATION', [])) if linked.get('ORGANISATION') else 'None'}<br>
    <b>Events:</b> {', '.join(linked.get('EVENT', [])) if linked.get('EVENT') else 'None'}<br>
    <hr>
    <i>"{record['snippet_text']}"</i><br><br>
    <small>Source: {record['source_metadata']}</small>
    """

    folium.Marker(
        location=record['coordinates'],
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color="blue" if record['model_source'] == "LSTM" else "red", icon="info-sign")
    ).add_to(m)

# 6. RENDER
st_folium(m, width=1200, height=600, center=st.session_state.center, zoom=st.session_state.zoom)
