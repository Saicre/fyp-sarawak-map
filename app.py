import streamlit as st
import json
import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen, LocateControl
from collections import defaultdict

# ── 1. PAGE SETUP ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sarawak Gazette · Historical Gazetteer",
    layout="wide",
    page_icon="🗺️"
)

# ── 2. GLOBAL CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Reset & base ── */
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #0d1117; font-family: 'DM Sans', sans-serif; }

/* ── Remove Streamlit top padding ── */
.block-container { padding-top: 0 !important; }

/* ── NAVBAR ── */
.navbar {
    background: linear-gradient(110deg, #0d1117 0%, #151d2b 60%, #0f1e2e 100%);
    border-bottom: 1px solid rgba(255,255,255,0.07);
    padding: 22px 36px 18px;
    margin-bottom: 0;
    position: relative;
    overflow: hidden;
}
.navbar::before {
    content: '';
    position: absolute;
    top: -40px; right: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(56,189,248,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.navbar-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.75em;
    font-weight: 700;
    color: #f0f6ff;
    letter-spacing: 0.3px;
    line-height: 1.2;
    margin: 0;
}
.navbar-subtitle {
    font-size: 0.82em;
    font-weight: 300;
    color: #64748b;
    margin: 5px 0 0 0;
    letter-spacing: 0.4px;
}
.navbar-badge {
    display: inline-block;
    background: rgba(56,189,248,0.12);
    color: #38bdf8;
    border: 1px solid rgba(56,189,248,0.25);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72em;
    font-weight: 500;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-left: 12px;
    vertical-align: middle;
}

/* ── STAT CARDS ── */
.stat-card {
    background: #151d2b;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 14px 18px;
    text-align: center;
    position: relative;
    overflow: hidden;
    cursor: default;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.stat-card:hover {
    border-color: rgba(56,189,248,0.3);
    box-shadow: 0 0 18px rgba(56,189,248,0.08);
}
.stat-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
}
.stat-number {
    font-family: 'Playfair Display', serif;
    font-size: 2em;
    font-weight: 700;
    color: #f0f6ff;
    line-height: 1;
    display: block;
}
.stat-label {
    font-size: 0.7em;
    font-weight: 500;
    color: #4b5563;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
    display: block;
}
.stat-icon {
    font-size: 1.3em;
    display: block;
    margin-bottom: 4px;
}

/* ── STAT TOOLTIP ── */
.stat-tooltip-wrap {
    position: relative;
    display: block;
}
.stat-tooltip-wrap .stat-tooltip-text {
    visibility: hidden;
    opacity: 0;
    background: #1e293b;
    color: #94a3b8;
    font-size: 0.72em;
    font-family: 'DM Sans', sans-serif;
    text-align: center;
    border-radius: 6px;
    padding: 5px 10px;
    position: absolute;
    bottom: calc(100% + 8px);
    left: 50%;
    transform: translateX(-50%);
    white-space: nowrap;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    transition: opacity 0.18s;
    z-index: 999;
    pointer-events: none;
}
.stat-tooltip-wrap .stat-tooltip-text::after {
    content: '';
    position: absolute;
    top: 100%; left: 50%;
    transform: translateX(-50%);
    border: 5px solid transparent;
    border-top-color: #1e293b;
}
.stat-tooltip-wrap:hover .stat-tooltip-text {
    visibility: visible;
    opacity: 1;
}

/* ── FILTER RADIO — white option text ── */
div[data-testid="stRadio"] label {
    color: #ffffff !important;
    font-size: 0.85em !important;
}
div[data-testid="stRadio"] > label > span {
    color: #ffffff !important;
    font-weight: 500 !important;
}
/* also target the inner span that Streamlit renders for option labels */
div[data-testid="stRadio"] p {
    color: #ffffff !important;
}

/* Framed filter panel */
div[data-testid="stRadio"] {
    background: #1a2333;
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 10px;
    padding: 12px 16px;
}
div[data-testid="stRadio"] > label {
    color: #94a3b8 !important;
    font-size: 0.78em !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
    display: block;
}

/* ── MODEL SUMMARY PILL (fills the empty gap) ── */
.model-summary {
    background: #1a2333;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 10px 16px;
    margin-top: 10px;
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.ms-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.78em;
}
.ms-label {
    color: #64748b;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 6px;
}
.ms-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}
.ms-value {
    color: #cbd5e1;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
    font-size: 0.95em;
}
.ms-bar-wrap {
    height: 3px;
    background: rgba(255,255,255,0.06);
    border-radius: 2px;
    margin-top: 1px;
    overflow: hidden;
}
.ms-bar-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 0.4s ease;
}

/* ── LEGEND ── */
.legend-bar {
    background: #151d2b;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 18px;
    flex-wrap: wrap;
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 0.82em;
    color: #94a3b8;
}
.legend-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
}
.legend-title {
    font-size: 0.72em;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #4b5563;
}

/* ── BUTTON ── */
.stButton > button {
    background: transparent !important;
    color: #38bdf8 !important;
    border: 1px solid rgba(56,189,248,0.35) !important;
    border-radius: 8px !important;
    padding: 7px 16px !important;
    font-size: 0.82em !important;
    font-weight: 500 !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(56,189,248,0.08) !important;
    border-color: rgba(56,189,248,0.6) !important;
}

/* ── MAP WRAPPER ── */
.map-frame {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.07);
    box-shadow: 0 24px 60px rgba(0,0,0,0.5);
    margin: 0 0 16px 0;
}
.map-frame iframe { display: block; }

/* ── FOOTER ── */
.footer {
    text-align: center;
    padding: 18px;
    font-size: 0.75em;
    color: #2d3748;
    letter-spacing: 0.3px;
    border-top: 1px solid rgba(255,255,255,0.04);
    margin-top: 8px;
}

/* spacing helpers */
.gap-sm { margin-top: 12px; }
.gap-md { margin-top: 20px; }
</style>
""", unsafe_allow_html=True)


# ── 3. NAVBAR ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div style="display:flex; align-items:center; gap:14px;">
        <div style="font-size:2.2em; line-height:1;">🗺️</div>
        <div>
            <p class="navbar-title">
                Sarawak Gazette
                <span class="navbar-badge">NLP · Gazetteer</span>
            </p>
            <p class="navbar-subtitle">Historical location extraction &amp; mapping · LSTM &amp; BiLSTM-CRF models</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Legend row
st.markdown("""
<div style="padding: 10px 4px 0px 4px;">
<div class="legend-bar" style="margin-top:12px;">
    <span class="legend-title">Markers:</span>
    <span class="legend-item">
        <span class="legend-dot" style="background:#3b82f6;"></span>LSTM
    </span>
    <span class="legend-item">
        <span class="legend-dot" style="background:#ef4444;"></span>BiLSTM-CRF
    </span>
    <span style="margin-left:auto; font-size:0.75em; color:#374151;">
        Click any marker to inspect its record(s)
    </span>
</div>
""", unsafe_allow_html=True)
st.markdown("<div class='gap-sm'></div>", unsafe_allow_html=True)

# ── 4. DATA LOADING ────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    with open('sarawak_gazetteer.json', 'r') as f:
        return json.load(f)

data = load_data()


# ── 5. CONTROLS ────────────────────────────────────────────────────────────────
st.markdown("<div class='gap-md'></div>", unsafe_allow_html=True)

col_filter, col_s1, col_s2, col_s3 = st.columns([3, 1.2, 1.2, 1.2])

# Derived stats
filtered   = data if model_filter == "Show All" else [r for r in data if r["model_source"] == model_filter]
n_records  = len(filtered)
n_locations = len(set(r['location_id'] for r in filtered))
n_lstm     = len([r for r in data if r['model_source'] == 'LSTM'])
n_bilstm   = len([r for r in data if r['model_source'] == 'BiLSTM-CRF'])
total_all  = n_lstm + n_bilstm
lstm_pct   = round(n_lstm / total_all * 100) if total_all else 0
bilstm_pct = 100 - lstm_pct

# Model breakdown mini-panel (fills the gap below the radio)
with col_filter:
    st.markdown(f"""
    <div class="model-summary">
        <div class="ms-row">
            <span class="ms-label">
                <span class="ms-dot" style="background:#3b82f6;"></span>LSTM
            </span>
            <span class="ms-value">{n_lstm}</span>
        </div>
        <div class="ms-bar-wrap">
            <div class="ms-bar-fill" style="width:{lstm_pct}%; background:#3b82f6;"></div>
        </div>
        <div class="ms-row">
            <span class="ms-label">
                <span class="ms-dot" style="background:#ef4444;"></span>BiLSTM-CRF
            </span>
            <span class="ms-value">{n_bilstm}</span>
        </div>
        <div class="ms-bar-wrap">
            <div class="ms-bar-fill" style="width:{bilstm_pct}%; background:#ef4444;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_filter:
    model_filter = st.radio(
        "Filter by model:",
        ["Show All", "LSTM", "BiLSTM-CRF"],
        horizontal=True 
    )

with col_s1:
    st.markdown(f"""
    <div class="stat-tooltip-wrap">
        <span class="stat-tooltip-text">Extracted records of the selected model</span>
        <div class="stat-card">
            <span class="stat-icon">📄</span>
            <span class="stat-number">{n_records}</span>
            <span class="stat-label">Records</span>
        </div>
    </div>""", unsafe_allow_html=True)

with col_s2:
    st.markdown(f"""
    <div class="stat-tooltip-wrap">
        <span class="stat-tooltip-text">Unique locations marked on the map</span>
        <div class="stat-card">
            <span class="stat-icon">📍</span>
            <span class="stat-number">{n_locations}</span>
            <span class="stat-label">Locations</span>
        </div>
    </div>""", unsafe_allow_html=True)

with col_s3:
    st.markdown(f"""
    <div class="stat-tooltip-wrap">
        <span class="stat-tooltip-text">Total records across all models</span>
        <div class="stat-card">
            <span class="stat-icon">🔬</span>
            <span class="stat-number">{n_lstm + n_bilstm}</span>
            <span class="stat-label">Total</span>
        </div>
    </div>""", unsafe_allow_html=True)


# ── 6. MAP STATE ───────────────────────────────────────────────────────────────
if 'center' not in st.session_state:
    st.session_state.center = [2.55, 113.0]
    st.session_state.zoom = 7

INIT_LAT = 2.55
INIT_LNG = 113.0
INIT_ZOOM = 7

# ── 7. BUILD MAP ───────────────────────────────────────────────────────────────
m = folium.Map(
    location=st.session_state.center,
    zoom_start=st.session_state.zoom,
    tiles='cartodbpositron'
)
Fullscreen().add_to(m)

# ── Recenter button injected as a proper Leaflet control ──────────────────────
recenter_js = f"""
<script>
(function waitForLeaflet() {{
    if (typeof L === 'undefined') {{ setTimeout(waitForLeaflet, 200); return; }}
    var maps = Object.values(window).filter(function(v) {{ return v && v instanceof L.Map; }});
    if (maps.length === 0) {{ setTimeout(waitForLeaflet, 200); return; }}
    var map = maps[0];

    var ResetControl = L.Control.extend({{
        options: {{ position: 'topleft' }},
        onAdd: function(map) {{
            var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-recenter');
            container.title = 'Recenter to Sarawak';
            container.style.cssText = [
                'width:26px', 'height:26px',
                'background:white', 'cursor:pointer',
                'display:flex', 'align-items:center', 'justify-content:center',
                'font-size:15px', 'user-select:none',
                'border-radius:2px'
            ].join(';');
            container.innerHTML = '⌂';
            L.DomEvent.on(container, 'click', function(e) {{
                L.DomEvent.stopPropagation(e);
                map.setView([{INIT_LAT}, {INIT_LNG}], {INIT_ZOOM});
            }});
            L.DomEvent.disableClickPropagation(container);
            return container;
        }}
    }});
    new ResetControl().addTo(map);
}})();
</script>
"""
m.get_root().html.add_child(folium.Element(recenter_js))

# ── Inject popup stylesheet ────────────────────────────────────────────────────
POPUP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400&display=swap');
.leaflet-popup-content-wrapper {
    border-radius: 14px !important;
    box-shadow: 0 12px 40px rgba(0,0,0,0.45) !important;
    padding: 0 !important;
    overflow: hidden;
    border: none !important;
}
.leaflet-popup-content {
    margin: 0 !important;
    font-family: 'DM Sans', system-ui, -apple-system, sans-serif !important;
    font-size: 13px !important;
}
.leaflet-popup-tip-container { margin-top: -1px; }

/* Header */
.ph { padding: 13px 16px 11px; color: white; }
.ph.lstm   { background: linear-gradient(125deg, #1d4ed8 0%, #2563eb 100%); }
.ph.bilstm { background: linear-gradient(125deg, #b91c1c 0%, #dc2626 100%); }
.ph-name  { font-size: 1.05em; font-weight: 600; color: #fff; line-height: 1.3; }
.ph-model { font-size: 0.72em; font-weight: 400; opacity: 0.80;
            letter-spacing: 0.5px; text-transform: uppercase; margin-top: 2px; }

/* Body */
.pb { padding: 12px 16px 14px; background: #ffffff; }

/* Fields */
.pf-label { font-size: 0.65em; font-weight: 600; text-transform: uppercase;
            letter-spacing: 0.8px; color: #9ca3af; margin-bottom: 1px; }
.pf-value { color: #1f2937; font-size: 0.85em; }

/* Two-col grid */
.pgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 12px; margin-bottom: 9px; }

/* Divider */
.pdiv { border: none; border-top: 1px solid #f1f5f9; margin: 9px 0; }

/* Tags */
.ptag { display: inline-block; border-radius: 4px;
        padding: 1px 7px; font-size: 0.73em; font-weight: 500;
        margin: 1px 2px 1px 0; line-height: 1.6; }
.ptag-none { color: #d1d5db; font-style: italic; font-size: 0.78em; }
.t-person { background: #fef9c3; color: #854d0e; }
.t-date   { background: #dcfce7; color: #166534; }
.t-org    { background: #ede9fe; color: #5b21b6; }
.t-event  { background: #fee2e2; color: #991b1b; }

/* Coordinates */
.pcoords { font-family: 'DM Mono', 'Courier New', monospace;
           background: #f1f5f9; padding: 4px 9px; border-radius: 5px;
           font-size: 0.78em; color: #475569; display: inline-block; margin-top: 2px; }

/* Snippet */
.psnippet { background: #f8fafc; border-left: 3px solid #3b82f6;
            padding: 8px 11px; border-radius: 0 7px 7px 0;
            font-style: italic; color: #374151; font-size: 0.82em;
            line-height: 1.55; margin: 4px 0 6px; }
.psnippet.bilstm { border-left-color: #ef4444; }

/* Source */
.psource { font-size: 0.72em; color: #9ca3af; }

/* Nav */
.pnav { display: flex; justify-content: space-between; align-items: center;
        background: #f8fafc; padding: 7px 12px;
        border-top: 1px solid #e2e8f0; }
.pnav-btn { cursor: pointer; background: white; border: 1px solid #e2e8f0;
            border-radius: 5px; padding: 3px 11px; font-size: 0.78em; color: #374151;
            font-family: 'DM Sans', sans-serif; }
.pnav-btn:hover { background: #e0e7ff; border-color: #c7d2fe; }
.pnav-counter { font-size: 0.78em; color: #6b7280; font-weight: 500; }
</style>
"""
m.get_root().html.add_child(folium.Element(POPUP_CSS))


# ── Helpers ────────────────────────────────────────────────────────────────────
def fmt_tags(items, css_class):
    if not items:
        return '<span class="ptag-none">None</span>'
    return " ".join(f'<span class="ptag {css_class}">{item}</span>' for item in items)


# ── Group records ──────────────────────────────────────────────────────────────
grouped = defaultdict(list)
for rec in data:
    if model_filter != "Show All" and rec["model_source"] != model_filter:
        continue
    grouped[(rec['location_id'], rec['model_source'])].append(rec)


# ── Build markers ──────────────────────────────────────────────────────────────
for (loc_id, model_src), records in grouped.items():
    coords     = records[0]['coordinates']
    is_lstm    = model_src == "LSTM"
    pin_color  = "blue" if is_lstm else "red"
    hdr_class  = "lstm" if is_lstm else "bilstm"
    lon_offset = 0.0 if is_lstm else 0.05
    pin_loc    = [coords[0], coords[1] + lon_offset]
    total      = len(records)
    uid        = f"{loc_id.replace('-','_').replace(' ','_')}_{model_src.replace('-','_')}"

    html = f'<div id="car_{uid}" style="width:295px;">'

    for i, r in enumerate(records):
        hist     = r['historical_name'] if r['historical_name'] != r['normalized_name'] else "N/A (Unchanged)"
        resolved = r.get('resolved_name', 'N/A')
        linked   = r['linked_entities']
        rc       = r['coordinates']
        vis      = "block" if i == 0 else "none"

        html += f"""
<div id="sl_{uid}_{i}" style="display:{vis};">
  <div class="ph {hdr_class}">
    <div class="ph-name">{r['normalized_name']}</div>
    <div class="ph-model">{model_src}</div>
  </div>
  <div class="pb">
    <div class="pgrid">
      <div>
        <div class="pf-label">ID</div>
        <div class="pf-value">{r['location_id']}</div>
      </div>
      <div>
        <div class="pf-label">Model</div>
        <div class="pf-value">{model_src}</div>
      </div>
    </div>
    <hr class="pdiv">
    <div style="margin-bottom:6px;">
      <div class="pf-label">Normalized Name</div>
      <div class="pf-value">{r['normalized_name']}</div>
    </div>
    <div style="margin-bottom:6px;">
      <div class="pf-label">Historical Name</div>
      <div class="pf-value">{hist}</div>
    </div>
    <div style="margin-bottom:6px;">
      <div class="pf-label">Resolved Name</div>
      <div class="pf-value">{resolved}</div>
    </div>
    <hr class="pdiv">
    <div style="margin-bottom:5px;">
      <div class="pf-label">People</div>
      <div>{fmt_tags(linked.get('PERSON', []), 't-person')}</div>
    </div>
    <div style="margin-bottom:5px;">
      <div class="pf-label">Dates</div>
      <div>{fmt_tags(linked.get('DATE', []), 't-date')}</div>
    </div>
    <div style="margin-bottom:5px;">
      <div class="pf-label">Organisations</div>
      <div>{fmt_tags(linked.get('ORGANISATION', []), 't-org')}</div>
    </div>
    <div style="margin-bottom:8px;">
      <div class="pf-label">Events</div>
      <div>{fmt_tags(linked.get('EVENT', []), 't-event')}</div>
    </div>
    <hr class="pdiv">
    <div style="margin-bottom:8px;">
      <div class="pf-label">Coordinates</div>
      <span class="pcoords">{rc[0]:.6f}, {rc[1]:.6f}</span>
    </div>
    <hr class="pdiv">
    <div class="psnippet {hdr_class}">"{r['snippet_text']}"</div>
    <div class="psource">📄 {r['source_metadata']}</div>
  </div>
"""
        if total > 1:
            html += f"""
  <div class="pnav">
    <button class="pnav-btn" onclick="chg_{uid}(-1)">&#8592; Prev</button>
    <span class="pnav-counter">{i+1} / {total}</span>
    <button class="pnav-btn" onclick="chg_{uid}(1)">Next &#8594;</button>
  </div>"""

        html += "\n</div>\n"

    if total > 1:
        html += f"""
<script>
var _c_{uid} = 0;
function chg_{uid}(d) {{
  document.getElementById('sl_{uid}_' + _c_{uid}).style.display = 'none';
  _c_{uid} = (_c_{uid} + d + {total}) % {total};
  document.getElementById('sl_{uid}_' + _c_{uid}).style.display = 'block';
}}
</script>"""

    html += "</div>"

    folium.Marker(
        location=pin_loc,
        popup=folium.Popup(html, max_width=320),
        icon=folium.Icon(color=pin_color, icon="info-sign")
    ).add_to(m)


# ── 8. RENDER ──────────────────────────────────────────────────────────────────
st.markdown('<div class="map-frame">', unsafe_allow_html=True)
st_folium(
    m,
    width=None,
    height=640,
    center=st.session_state.center,
    zoom=st.session_state.zoom,
    returned_objects=[]
)
st.markdown('</div>', unsafe_allow_html=True)


# ── 9. FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Sarawak Gazette Historical Gazetteer &nbsp;·&nbsp;
    NLP Location Extraction &nbsp;·&nbsp;
    LSTM &amp; BiLSTM-CRF &nbsp;·&nbsp;
    Built with Streamlit &amp; Folium
</div>
""", unsafe_allow_html=True)
