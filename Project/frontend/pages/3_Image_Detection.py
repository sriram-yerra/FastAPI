import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("🖼 Image Detection")

if not st.session_state.token:
    st.warning("Please login first")
    st.stop()

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    if st.button("Detect"):
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }

        headers = {"Authorization": f"Bearer {st.session_state.token}"}

        res = requests.post(
            f"{API_URL}/detect-image",
            files=files,
            headers=headers
        )

        if res.status_code == 200:
            data = res.json()
            st.success("Detection Completed")

            result_path = data["download_url"]

            result_image = requests.get(
                f"{API_URL}/view-image",
                params={"path": result_path}
            )

            if result_image.status_code == 200:
                st.image(result_image.content, caption="Detection Result", use_container_width=True)

            st.write("Total Detections:", data["Total Detections"])
        else:
            st.error(res.text)
