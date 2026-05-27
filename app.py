import streamlit as st
import json
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

# 1. LOAD DATA
@st.cache_data
def load_data():
    with open('sarawak_gazetteer.json', 'r') as file:
        return json.load(file)

database_records = load_data()

# 2. GROUPING DATA (Crucial for carousel)
grouped_data = {}
for record in database_records:
    loc = record['historical_name']
    if loc not in grouped_data:
        grouped_data[loc] = []
    grouped_data[loc].append(record)

# 3. MAP SETUP
m = folium.Map(location=[2.55, 113.0], zoom_start=6, tiles='cartodbpositron')
lstm_layer = folium.FeatureGroup(name="LSTM Predictions (Blue)")
bilstm_layer = folium.FeatureGroup(name="BiLSTM-CRF Predictions (Red)")

def format_list(lst):
    return ', '.join(lst) if lst else 'None'

# 4. MARKER LOOP
for loc, records in grouped_data.items():
    coords = records[0]['coordinates']
    
    # Bounding Box Filter
    if not (1.0 <= coords[0] <= 5.0 and 109.0 <= coords[1] <= 116.0):
        continue

    # Build Carousel Slides
    slides = ""
    for i, r in enumerate(records):
        display = "block" if i == 0 else "none"
        slides += f"""
        <div class='slide-{loc.replace(' ', '_')}' style='display: {display}; border-top: 1px solid #ccc; padding: 5px;'>
            <i>"{r['snippet_text']}"</i><br>
            <small>Source: {r['source_metadata']}</small>
        </div>
        """

    # Combine Static Colab Info + Carousel
    r = records[0]
    display_hist = r['historical_name'] if r['historical_name'] != r['normalized_name'] else "N/A (Unchanged)"
    
    popup_html = f"""
    <div style='width: 300px;'>
        <b>ID:</b> {r['location_id']}<br>
        <b>Current Name:</b> {r['normalized_name']}<br>
        <b>Historical Name:</b> {display_hist}<br>
        <b>Model:</b> {r['model_source']}<br>
        <hr>
        <b>People:</b> {format_list(r['linked_entities'].get('PERSON', []))}<br>
        <b>Dates:</b> {format_list(r['linked_entities'].get('DATE', []))}<br>
        <b>Orgs:</b> {format_list(r['linked_entities'].get('ORGANISATION', []))}<br>
        <b>Events:</b> {format_list(r['linked_entities'].get('EVENT', []))}<br>
        <div id='ss-{loc.replace(' ', '_')}'>{slides}</div>
        <button onclick="plus(-1, '{loc.replace(' ', '_')}')">❮</button>
        <button onclick="plus(1, '{loc.replace(' ', '_')}')">❯</button>
    </div>
    <script>
    function plus(n, id) {{
        let s = document.getElementsByClassName('slide-'+id);
        let c = 0;
        for(let i=0; i<s.length; i++) {{ if(s[i].style.display === 'block') c = i; s[i].style.display = 'none'; }}
        let next = (c + n + s.length) % s.length;
        s[next].style.display = 'block';
    }}
    </script>
    """

    folium.Marker(
        location=coords,
        popup=folium.Popup(popup_html, max_width=350),
        icon=folium.Icon(color="blue" if r['model_source'] == "LSTM" else "red", icon="info-sign")
    ).add_to(lstm_layer if r['model_source'] == "LSTM" else bilstm_layer)

lstm_layer.add_to(m)
bilstm_layer.add_to(m)
folium.LayerControl().add_to(m)

st_folium(m, width=1200, height=600)
