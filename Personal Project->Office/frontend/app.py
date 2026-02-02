import streamlit as st

st.set_page_config(page_title="AI Vision System", layout="wide")

st.title("🚀 AI Vision System")

st.markdown("""
Welcome to the AI Vision Platform

Use the sidebar to navigate:
- Register
- Login
- Image Detection
- Video Detection
- Model Analytics
""")

# Initialize session state globally
if "token" not in st.session_state:
    st.session_state.token = None

if "pending_user" not in st.session_state:
    st.session_state.pending_user = None
