import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Auth System")

# Session state for token
if "token" not in st.session_state:
    st.session_state.token = None

if "pending_user" not in st.session_state:
    st.session_state.pending_user = None

menu = st.sidebar.selectbox("Menu", ["Register", "Login", "Profile"])

if menu == "Register":
    st.header("Company Registration")

    name = st.text_input("Name")
    email = st.text_input("Company Email")
    password = st.text_input("Password", type="password")

    if st.button("Send OTP"):
        res = requests.post(f"{API_URL}/request-otp", json={
            "name": name,
            "email": email,
            "password": password
        })

        if res.status_code == 200:
            st.success("OTP sent to your email (valid 2 mins)")
            st.session_state.pending_user = {
                "name": name,
                "email": email,
                "password": password
            }
        else:
            st.error(res.json()["detail"])

    if st.session_state.pending_user:
        st.subheader("Enter OTP")

        otp = st.text_input("OTP Code")

        if st.button("Verify OTP"):
            user_data = st.session_state.pending_user

            res = requests.post(f"{API_URL}/verify-otp", json={
                "email": user_data["email"],
                "otp": otp
            })

            if res.status_code == 200:
                st.success("Registration Completed!")
                st.session_state.pending_user = None
            else:
                st.error(res.json()["detail"])



elif menu == "Login":
    st.header("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post( # HTTP request is created (http://127.0.0.1:8000/login)
            f"{API_URL}/login",
            data={      # Data is Sent as FORM (Not JSON)
                "username": email,
                "password": password,
                "grant_type": "password" # (grant_type=password&username=ram@example.com&password=ram)
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        st.write(res.status_code)
        st.write(res.text)

        if res.status_code == 200:
            token = res.json()["access_token"]
            st.session_state.token = token
            st.success("Logged in!")
        else:
            st.error("Invalid credentials")


elif menu == "Profile":
    st.header("My Profile")

    if not st.session_state.token:
        st.warning("Login first")
    else:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        res = requests.get(f"{API_URL}/profile", headers=headers)

        if res.status_code == 200:
            data = res.json()
            st.write("Name:", data["name"])
            st.write("Email:", data["email"])
        else:
            st.error("Session expired. Login again.")
