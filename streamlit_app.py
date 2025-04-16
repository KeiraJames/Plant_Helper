import streamlit as st
import json
import os
import requests
from io import BytesIO
from PIL import Image

# ---------- PlantNet API ----------
class PlantNetAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.PLANTNET_URL = "https://my-api.plantnet.org/v2/identify/all"

    def identify_plant(self, image_path):
        with open(image_path, 'rb') as f:
            files = {'images': f}
            params = {'api-key': self.api_key}
            response = requests.post(self.PLANTNET_URL, files=files, params=params)

        if response.status_code == 200:
            data = response.json()
            if "results" in data and data["results"]:
                plant_name = data["results"][0]["species"]["scientificNameWithoutAuthor"]
                return plant_name
            else:
                return "No plant match found."
        else:
            return f"Error: {response.status_code}"

# ---------- Load Care Info ----------
def load_care_info(plant_name):
    with open("plants_with_personality3_copy.json", "r") as f:
        plant_data = json.load(f)
    for plant in plant_data:
        if plant["Plant Name"].lower() == plant_name.lower():
            return plant
    return None

# ---------- Initialize Session State ----------
if "saved_photos" not in st.session_state:
    st.session_state.saved_photos = {}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = []

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

if "plant_name" not in st.session_state:
    st.session_state.plant_name = None

if "care_info" not in st.session_state:
    st.session_state.care_info = None

# ---------- Sidebar Navigation ----------
page = st.sidebar.radio("Navigation", ["Upload & Identify", "View Saved Photos"])

# ---------- Page 1: Upload and Identify ----------
if page == "Upload & Identify":
    st.header("Upload a Plant Photo")
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        # Store the uploaded image in session state
        st.session_state.uploaded_image = uploaded_file.getvalue()

        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

        # Process identification and display care info
        temp_path = os.path.join("temp_image.jpg")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        api = PlantNetAPI(api_key="2b10X3YLMd8PNAuKOCVPt7MeUe")
        plant_name = api.identify_plant(temp_path)
        st.session_state.plant_name = plant_name
        st.subheader(f"Identified Plant: {plant_name}")

        care_info = load_care_info(plant_name)
        st.session_state.care_info = care_info

        if care_info:
            st.markdown("### 🌿 Plant Care Info")
            for k, v in care_info.items():
                if k != "Personality":
                    st.markdown(f"**{k}:** {v}")
            if "Personality" in care_info:
                st.markdown(f"### 🧠 Personality: {care_info['Personality']['Title']}")
                st.markdown("**Traits:** " + ", ".join(care_info["Personality"]["Traits"]))
                st.markdown("> " + care_info["Personality"]["Prompt"])
        else:
            st.warning("No care info found for this plant.")

        # Chatbot
        st.markdown("### 💬 Talk to your plant!")
        user_input = st.text_input("You:", key="chat_input")
        if user_input:
            response = f"I'm just a plant 🌱, but I hear you: '{user_input}'"
            st.session_state.current_chat.append(("You", user_input))
            st.session_state.current_chat.append(("Plant", response))

        for sender, msg in st.session_state.current_chat:
            st.markdown(f"**{sender}:** {msg}")

        # Save or Discard buttons
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Save"):
                plant_nickname = st.text_input("Give this plant a name to save:", key="nickname")
                if plant_nickname:
                    st.session_state.saved_photos[plant_nickname] = {
                        "image_bytes": st.session_state.uploaded_image,
                        "plant_name": plant_name,
                        "care_info": care_info,
                        "chat": st.session_state.current_chat.copy()
                    }
                    # Clear session state after saving
                    st.session_state.uploaded_image = None
                    st.session_state.plant_name = None
                    st.session_state.care_info = None
                    st.session_state.current_chat = []  # Clear chat history
                    st.success("Saved!")
                else:
                    st.error("Please enter a name to save.")
        
        with col2:
            if st.button("Discard"):
                # Clear only the current session state related to the upload
                st.session_state.uploaded_image = None
                st.session_state.plant_name = None
                st.session_state.care_info = None
                st.session_state.current_chat = []  # Clear chat history
                st.experimental_rerun()  # Refresh to upload a new photo

# ---------- Page 2: View Saved ----------
elif page == "View Saved Photos":
    st.header("📁 Saved Plant Entries")

    if not st.session_state.saved_photos:
        st.info("No saved photos yet.")
    else:
        selected = st.selectbox("Select a saved photo:", list(st.session_state.saved_photos.keys()))
        if selected:
            entry = st.session_state.saved_photos[selected]
            image = Image.open(BytesIO(entry["image_bytes"]))
            st.image(image, caption=f"Saved Photo: {selected}", use_container_width=True)
            st.subheader(f"Identified Plant: {entry['plant_name']}")

            st.markdown("### 🌿 Plant Care Info")
            for k, v in entry["care_info"].items():
                if k != "Personality":
                    st.markdown(f"**{k}:** {v}")
            if "Personality" in entry["care_info"]:
                p = entry["care_info"]["Personality"]
                st.markdown(f"### 🧠 Personality: {p['Title']}")
                st.markdown("**Traits:** " + ", ".join(p["Traits"]))
                st.markdown("> " + p["Prompt"])

            st.markdown("### 💬 Chat History")
            for sender, msg in entry["chat"]:
                st.markdown(f"**{sender}:** {msg}")
