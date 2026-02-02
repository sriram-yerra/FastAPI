import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("🔐 Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    res = requests.post(
        f"{API_URL}/login",
        data={
            "username": email,
            "password": password,
            "grant_type": "password"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if res.status_code == 200:
        token = res.json()["access_token"]
        st.session_state.token = token
        st.success("Logged in!")
        st.balloons()
    else:
        st.error("Invalid credentials")
