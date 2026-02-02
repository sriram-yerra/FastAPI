import streamlit as st
import requests
from PIL import Image
from io import BytesIO

st.markdown("""
<style>
.center-col {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Detection History", layout="wide")
st.title("Detection History")

# Optional Login Protection
if not st.session_state.get("token"):
    st.warning("Login required")
    st.stop()

# Table Layout
col1, col2, col3 = st.columns([2,2,1])

with col1:
    st.markdown('<div class="center-col"><b>Image</b></div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="center-col"><b>Filename</b></div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="center-col"><b># Detections</b></div>', unsafe_allow_html=True)

st.divider()

# Fetch detections from backend
res = requests.get(f"{API_URL}/detections-history")

if res.status_code != 200:
    st.error("Failed to load detections")
    st.stop()

data = res.json()

if not data:
    st.info("No detections found")
    st.stop()

# Loop through detections
for item in data:
    col1, col2, col3 = st.columns([2,2,1])

    # Image column
    with col1:
        st.markdown('<div class="center-col">', unsafe_allow_html=True)
        st.image(item["filepath"], width=250)
        st.markdown('</div>', unsafe_allow_html=True)

    # Filename column
    with col2:
        st.markdown(f'<div class="center-col">{item["filename"]}</div>', unsafe_allow_html=True)

    # Detection count column
    with col3:
        st.markdown(f'<div class="center-col"><span style="background:#0f5132;color:#d1e7dd;padding:6px 12px;border-radius:10px;">{item["num_detections"]}</span></div>', unsafe_allow_html=True)

    st.divider()
