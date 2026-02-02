import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("Company Registration")

name = st.text_input("Name")
email = st.text_input("Company Email")
password = st.text_input("Password", type="password")

if st.button("Request OTP"):
    res = requests.post(f"{API_URL}/otp-registration", json={
        "name": name,
        "email": email,
        "password": password
    })

    if res.status_code == 200:
        st.success("OTP sent (valid 2 mins)")
        st.session_state.pending_user = {
            "name": name,
            "email": email,
            "password": password
        }
    else:
        st.error(res.json()["detail"])

if st.session_state.pending_user:
    st.divider()
    st.subheader("Enter OTP")

    otp = st.text_input("OTP Code")

    if st.button("Verify OTP and Register"):
        user_data = st.session_state.pending_user

        res = requests.post(f"{API_URL}/verify-otp-register", json={
            "email": user_data["email"],
            "otp": otp
        })

        if res.status_code == 200:
            st.success("Registration Completed!")
            st.session_state.pending_user = None
        else:
            st.error(res.json()["detail"])
