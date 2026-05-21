import streamlit as st
import json
import folium
from streamlit_folium import st_folium

# 1. PAGE SETUP
st.set_page_config(page_title="Sarawak Gazette NLP Map", layout="wide")

st.sidebar.title("Navigation & Filters")
st.sidebar.info("This interactive web application displays historical locations extracted from the Sarawak Gazette.")
model_filter = st.sidebar.radio("Compare Models:", ["Show All", "Baseline LSTM", "BiLSTM-CRF"])

st.title("🗺️ Sarawak Gazette: Automated Historical Gazetteer")

# 2. LOAD THE DATA
@st.cache_data
def load_data():
    with open('sarawak_gazetteer.json', 'r') as file:
        return json.load(file)

data = load_data()

# 3. GROUP THE DATA BY LOCATION
# This merges all sentences that share the same historical name into one marker
grouped_locations = {}

for record in data:
    # Apply the sidebar filter first
    if model_filter != "Show All" and record["model_source"] != model_filter:
        continue
        
    loc_name = record["historical_name"]
    
    # If we haven't seen this location yet, create a new entry for it
    if loc_name not in grouped_locations:
        grouped_locations[loc_name] = {
            "coordinates": record["coordinates"],
            "model_source": record["model_source"],
            "mentions": [] # This will hold all the sentences
        }
    
    # Add the sentence and metadata to this location's list
    grouped_locations[loc_name]["mentions"].append({
        "metadata": record["source_metadata"],
        "text": record["snippet_text"]
    })

# 4. BUILD THE MAP
m = folium.Map(location=[2.5, 113.0], zoom_start=6, tiles="CartoDB positron")

# Loop through our newly grouped data
for loc_name, details in grouped_locations.items():
    lat, lon = details["coordinates"]
    color = "blue" if details["model_source"] == "LSTM" else "red"
    total_mentions = len(details["mentions"])
    
    # Start building the HTML for the popup with a SCROLLABLE div box!
    popup_html = f"""
    <div style='width: 280px;'>
        <h4 style='margin-bottom: 2px;'>{loc_name}</h4>
        <p style='color: gray; font-size: 12px; margin-top: 0px;'>Total Mentions: {total_mentions}</p>
        <hr style='margin: 5px 0px;'>
        <div style='max-height: 200px; overflow-y: auto; padding-right: 10px;'>
    """
    
    # Loop through every sentence found for this location and add it to the box
    for i, mention in enumerate(details["mentions"]):
        popup_html += f"""
        <p style='font-size: 11px; margin-bottom: 2px;'><b>Mention {i+1}</b> - <i>{mention['metadata']}</i></p>
        <p style='font-size: 12px; margin-top: 0px;'>"{mention['text']}"</p>
        <br>
        """
        
    # Close the HTML tags
    popup_html += "</div></div>"
    
    # Add the marker to the map
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=320),
        icon=folium.Icon(color=color, icon="info-sign"),
        tooltip=f"{loc_name} ({total_mentions} mentions)"
    ).add_to(m)

# 5. RENDER MAP ON THE WEBSITE
st_folium(m, width=1200, height=600)
