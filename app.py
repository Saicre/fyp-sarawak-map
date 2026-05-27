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

# 4. DATA GROUPING (Fixed: Grouping logic added here)
grouped_locations = {}
for record in data:
    if model_filter != "Show All" and record["model_source"] != model_filter:
        continue
    
    loc_name = record["historical_name"]
    if loc_name not in grouped_locations:
        grouped_locations[loc_name] = {
            "coordinates": record["coordinates"], 
            "model_source": record["model_source"], 
            "mentions": []
        }
    
    grouped_locations[loc_name]["mentions"].append({
        "metadata": record["source_metadata"],
        "text": record["snippet_text"],
        "linked": record["linked_entities"]
    })

# 5. MAP STATE MANAGEMENT
if 'map_key' not in st.session_state:
    st.session_state.map_key = 0

if st.button("📍 Recenter Map to Sarawak"):
    st.session_state.center = [2.55, 113.0]
    st.session_state.zoom = 7
    st.session_state.map_key += 1
    st.rerun()

if 'center' not in st.session_state:
    st.session_state.center = [2.55, 113.0]
    st.session_state.zoom = 7

# 6. BUILD MAP
m = folium.Map(location=st.session_state.center, zoom_start=st.session_state.zoom, tiles='cartodbpositron')
Fullscreen().add_to(m)

# Marker Logic
for loc_name, details in grouped_locations.items():
    lat, lon = details["coordinates"]
    
    # Bounding Box Filter
    if not (1.0 <= lat <= 5.0 and 109.0 <= lon <= 116.0):
        continue

    # Carousel Logic
    slides = ""
    for i, mnt in enumerate(details["mentions"]):
        display = "block" if i == 0 else "none"
        linked = mnt['linked']
        slides += f"""
        <div class='slide-{loc_name.replace(' ', '_')}' style='display: {display}; padding: 5px;'>
            <p style='font-size: 11px;'><b>Source:</b> {mnt['metadata']}</p>
            <p style='font-size: 12px;'><i>"{mnt['text']}"</i></p>
            <p style='font-size: 10px;'>Slide {i+1} / {len(details['mentions'])}</p>
        </div>
        """

    popup_html = f"""
    <div style='width: 300px; font-family: sans-serif;'>
        <b>Historical Name:</b> {loc_name}<br>
        <hr style="margin: 5px 0;">
        <div id='slideshow-{loc_name.replace(' ', '_')}'>{slides}</div>
        <div style='text-align: center; margin-top: 5px;'>
            <button onclick="changeSlide(-1, '{loc_name.replace(' ', '_')}')">❮ Prev</button>
            <button onclick="changeSlide(1, '{loc_name.replace(' ', '_')}')">Next ❯</button>
        </div>
    </div>
    <script>
    function changeSlide(n, id) {{
        let slides = document.getElementsByClassName('slide-'+id);
        let current = 0;
        for(let i=0; i<slides.length; i++) {{
            if(slides[i].style.display === 'block') current = i;
            slides[i].style.display = 'none';
        }}
        let next = (current + n + slides.length) % slides.length;
        slides[next].style.display = 'block';
    }}
    </script>
    """

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=350),
        icon=folium.Icon(color="blue" if details['model_source'] == "LSTM" else "red", icon="info-sign")
    ).add_to(m)

# 7. RENDER
st_folium(
    m, 
    width=1200, 
    height=600, 
    center=st.session_state.center, 
    zoom=st.session_state.zoom,
    key=f"map_{st.session_state.map_key}"
)
