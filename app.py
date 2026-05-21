import streamlit as st
import json
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen

# 1. PAGE SETUP
st.set_page_config(page_title="Sarawak Gazette NLP Map", layout="wide")

# CUSTOM CSS FOR TOP NAVBAR
st.markdown("""
    <style>
        .navbar {
            display: flex;
            background-color: #f8f9fa;
            padding: 15px;
            border-bottom: 2px solid #ddd;
            margin-bottom: 20px;
            justify-content: space-between;
        }
        .nav-item { font-weight: bold; font-size: 1.2em; }
        .nav-link { text-decoration: none; color: #007bff; }
    </style>
    <div class="navbar">
        <div class="nav-item">🗺️ Sarawak Gazette Historical Gazetteer</div>
        <div class="nav-item">
            <a class="nav-link" href="https://sarawak-gazette.com/" target="_blank">🔗 Gazette Archive Website</a>
        </div>
    </div>
""", unsafe_allow_html=True)

# 2. FILTERING AREA
model_filter = st.radio("Filter by Model Source:", ["Show All", "LSTM", "BiLSTM-CRF"], horizontal=True)

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
        grouped_locations[loc_name] = {
            "coordinates": record["coordinates"], 
            "model_source": record["model_source"], 
            "mentions": []
        }
    
    grouped_locations[loc_name]["mentions"].append({
        "metadata": record["source_metadata"],
        "text": record["snippet_text"],
        "linked": record["linked_entities"],
        "pdf": record.get("source_pdf", "N/A") # Ensure your JSON has this key
    })

# Helper for empty fields
def fmt(val_list):
    return ", ".join(val_list) if val_list else "None"

# 4. BUILD MAP
m = folium.Map(location=[2.55, 113.0], zoom_start=7, tiles='cartodbpositron')
Fullscreen().add_to(m)
LocateControl(auto_start=False).add_to(m)

for loc_name, details in grouped_locations.items():
    lat, lon = details["coordinates"]
    color = "blue" if details["model_source"] == "LSTM" else "red"
    slides = ""
    
    for i, mnt in enumerate(details["mentions"]):
        display = "block" if i == 0 else "none"
        pdf_url = f"https://github.com/your-username/fyp-sarawak-map/blob/main/pdfs/{mnt['pdf']}"
        
        slides += f"""
        <div class='slide-{loc_name.replace(' ', '_')}' style='display: {display}; padding: 10px;'>
            <p style='font-size: 11px;'><b>Source:</b> {mnt['metadata']} <br>
            <a href='{pdf_url}' target='_blank'>📄 View Original PDF</a></p>
            <p style='font-size: 12px;'><b>People:</b> {fmt(mnt['linked'].get('PERSON', []))}</p>
            <p style='font-size: 12px;'><b>Events:</b> {fmt(mnt['linked'].get('EVENT', []))}</p>
            <p style='font-size: 12px; margin-top: 5px;'><i>"{mnt['text']}"</i></p>
        </div>
        """

    popup_html = f"""
    <div style='width: 300px;'>
        <h3>{loc_name}</h3>
        <div id='slideshow-{loc_name.replace(' ', '_')}'>{slides}</div>
        <div style='text-align: center; margin-top: 10px;'>
            <button onclick="changeSlide(-1, '{loc_name.replace(' ', '_')}')">❮</button>
            <button onclick="changeSlide(1, '{loc_name.replace(' ', '_')}')">❯</button>
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
    
    folium.Marker([lat, lon], popup=folium.Popup(popup_html, max_width=350), 
                  icon=folium.Icon(color=color, icon="info-sign")).add_to(m)

# 5. RENDER
if st.button("📍 Recenter Map"):
    st.rerun()

st_folium(m, width=1200, height=600)
