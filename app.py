import streamlit as st
import json
import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen
from collections import defaultdict

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
if st.button("📍 Recenter Map to Sarawak"):
    st.session_state.center = [2.55, 113.0]
    st.session_state.zoom = 7
    st.rerun()

if 'center' not in st.session_state:
    st.session_state.center = [2.55, 113.0]
    st.session_state.zoom = 7

# 5. BUILD MAP
m = folium.Map(location=st.session_state.center, zoom_start=st.session_state.zoom, tiles='cartodbpositron')
Fullscreen().add_to(m)

# --- GROUP DATA FOR PAGINATION ---
# Group records by (Location ID, Model) so we can paginate sentences for the same place/model
grouped_data = defaultdict(list)
for record in data:
    if model_filter != "Show All" and record["model_source"] != model_filter:
        continue
    key = (record['location_id'], record['model_source'])
    grouped_data[key].append(record)

# --- MARKER LOGIC WITH HTML/JS CAROUSEL ---
for (loc_id, model_source), records in grouped_data.items():
    # Use the coordinates of the first record in the group
    coords = records[0]['coordinates']
    
    # Matching your visual offset and coloring logic from Colab
    pin_color = "blue" if model_source == "LSTM" else "red"
    lon_offset = 0.05 if pin_color == "red" else 0.0
    actual_location = [coords[0], coords[1] + lon_offset]

    total_slides = len(records)
    
    # Create a safe, unique ID for the Javascript variables to avoid collisions
    html_id = f"{loc_id.replace('-', '_').replace(' ', '_')}_{model_source.replace('-', '_')}"

    # Start the HTML block for the popup
    popup_html = f"""<div id="carousel_{html_id}" style="width: 280px;">"""

    # Generate a "slide" for every sentence related to this location
    for i, rec in enumerate(records):
        display_hist = rec['historical_name'] if rec['historical_name'] != rec['normalized_name'] else "N/A (Unchanged)"
        linked = rec['linked_entities']
        
        # Only display the first slide initially
        display_style = "block" if i == 0 else "none"

        popup_html += f"""
        <div id="slide_{html_id}_{i}" style="display: {display_style};">
            <b>ID:</b> {rec['location_id']}<br>
            <b>Current Name:</b> {rec['normalized_name']}<br>
            <b>Historical Name:</b> {display_hist}<br>
            <b>Model:</b> {rec['model_source']}<br>
            <hr style="margin: 8px 0;">
            <b>People:</b> {', '.join(linked.get('PERSON', [])) if linked.get('PERSON') else 'None'}<br>
            <b>Dates:</b> {', '.join(linked.get('DATE', [])) if linked.get('DATE') else 'None'}<br>
            <b>Orgs:</b> {', '.join(linked.get('ORGANISATION', [])) if linked.get('ORGANISATION') else 'None'}<br>
            <b>Events:</b> {', '.join(linked.get('EVENT', [])) if linked.get('EVENT') else 'None'}<br>
            <hr style="margin: 8px 0;">
            <i>"{rec['snippet_text']}"</i><br><br>
            <small>Source: {rec['source_metadata']}</small>
        """

        # If there is more than 1 sentence, inject the navigation arrows
        if total_slides > 1:
            popup_html += f"""
            <div style="text-align: center; margin-top: 10px; background: #f0f0f0; padding: 5px; border-radius: 5px;">
                <button onclick="changeSlide_{html_id}(-1)" style="cursor:pointer; border:1px solid #ccc; border-radius:3px; padding: 2px 8px;">&larr; Prev</button>
                <span style="margin: 0 10px; font-size: 0.9em;"><b>{i+1}</b> of {total_slides}</span>
                <button onclick="changeSlide_{html_id}(1)" style="cursor:pointer; border:1px solid #ccc; border-radius:3px; padding: 2px 8px;">Next &rarr;</button>
            </div>
            """

        popup_html += "</div>"

    # Inject the Javascript specifically scoped to this marker's popup
    if total_slides > 1:
        popup_html += f"""
        <script>
            var currentSlide_{html_id} = 0;
            function changeSlide_{html_id}(direction) {{
                // Hide current slide
                document.getElementById('slide_{html_id}_' + currentSlide_{html_id}).style.display = 'none';
                
                // Update index
                currentSlide_{html_id} += direction;
                if (currentSlide_{html_id} >= {total_slides}) currentSlide_{html_id} = 0;
                if (currentSlide_{html_id} < 0) currentSlide_{html_id} = {total_slides} - 1;
                
                // Show new slide
                document.getElementById('slide_{html_id}_' + currentSlide_{html_id}).style.display = 'block';
            }}
        </script>
        """

    popup_html += "</div>"

    # Add the marker to the map
    folium.Marker(
        location=actual_location,
        popup=folium.Popup(popup_html, max_width=320),
        icon=folium.Icon(color=pin_color, icon="info-sign")
    ).add_to(m)

# 6. RENDER
st_folium(m, width=1200, height=600, center=st.session_state.center, zoom=st.session_state.zoom)
