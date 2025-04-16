import streamlit as st
import base64
import json
import requests
from io import BytesIO

# ===== API Setup =====
API_KEY = "2b10X3YLMd8PNAuKOCVPt7MeUe"
PLANTNET_URL = "https://my-api.plantnet.org/v2/identify/all"

def identify_plant(image_bytes):
    files = {'images': ('image.jpg', image_bytes)}
    params = {'api-key': API_KEY}
    response = requests.post(PLANTNET_URL, files=files, params=params)
    if response.status_code == 200:
        data = response.json()
        if "results" in data and data["results"]:
            return data["results"][0]["species"]["scientificNameWithoutAuthor"]
        else:
            return None
    else:
        return None

def get_care_info(plant_name, care_data):
    for plant in care_data:
        if plant["Plant Name"].lower() == plant_name.lower():
            return plant
    return None

# ===== Load Plant Care JSON =====
with open("plants_with_personality3_copy.json", "r") as f:
    care_data = json.load(f)

# ===== Streamlit Setup =====
st.set_page_config(page_title="Plant Buddy", layout="wide")

# ===== Session State Setup =====
if "saved_photos" not in st.session_state:
    st.session_state.saved_photos = {}  # {name: {"image": url, "info": ..., "chat": ...}}
if "temp_photo" not in st.session_state:
    st.session_state.temp_photo = None
if "saving_mode" not in st.session_state:
    st.session_state.saving_mode = False
if "temp_plant_name" not in st.session_state:
    st.session_state.temp_plant_name = ""
if "temp_care_info" not in st.session_state:
    st.session_state.temp_care_info = None
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# ===== Sidebar Navigation =====
tab = st.sidebar.radio("📚 Navigation", ["📤 Upload & Identify", "🪴 View Saved Plants"])

# ===== Upload & Identify Tab =====
if tab == "📤 Upload & Identify":
    st.title("📤 Upload a Plant Photo")

    if st.session_state.temp_photo is None:
        uploaded_file = st.file_uploader("Upload a plant photo", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            st.session_state.temp_photo = uploaded_file
            st.session_state.chat_log = []
            st.rerun()

    elif st.session_state.temp_photo and not st.session_state.saving_mode:
        image_bytes = st.session_state.temp_photo.getvalue()
        st.image(image_bytes, caption="Uploaded Plant", use_container_width=True)

        with st.spinner("Identifying plant..."):
            plant_name = identify_plant(image_bytes)

        if plant_name:
            st.session_state.temp_plant_name = plant_name
            care_info = get_care_info(plant_name, care_data)
            st.session_state.temp_care_info = care_info

            st.subheader(f"🌿 Plant Identified: {plant_name}")
            if care_info:
                st.markdown(f"**Light:** {care_info['Light Requirements']}")
                st.markdown(f"**Watering:** {care_info['Watering']}")
                st.markdown(f"**Humidity:** {care_info['Humidity Preferences']}")
                st.markdown(f"**Temperature:** {care_info['Temperature Range']}")
                st.markdown(f"**Feeding:** {care_info['Feeding Schedule']}")
                st.markdown(f"**Toxicity:** {care_info['Toxicity']}")
                st.markdown(f"**Additional Care:** {care_info['Additional Care']}")
                st.markdown(f"**Personality:** *{care_info['Personality']['Title']}* - {', '.join(care_info['Personality']['Traits'])}")
                st.markdown(f"*{care_info['Personality']['Prompt']}*")
            else:
                st.warning("No care info found for this plant.")

            st.divider()
            st.subheader("🧠 Chat with your plant:")
            prompt = st.text_input("Say something to your plant:")
            if prompt:
                plant_response = f"{st.session_state.temp_plant_name} says: 🌱 I'm listening! You said: '{prompt}'"
                st.session_state.chat_log.append(("You", prompt))
                st.session_state.chat_log.append((st.session_state.temp_plant_name, plant_response))

            for speaker, msg in st.session_state.chat_log:
                st.markdown(f"**{speaker}:** {msg}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save"):
                    st.session_state.saving_mode = True
                    st.rerun()
            with col2:
                if st.button("🗑️ Discard"):
                    st.session_state.temp_photo = None
                    st.session_state.temp_plant_name = ""
                    st.session_state.temp_care_info = None
                    st.session_state.chat_log = []
                    st.success("Photo discarded. Upload another plant.")
                    st.rerun()

        else:
            st.error("❌ Could not identify the plant. Try another photo.")
            st.session_state.temp_photo = None

    elif st.session_state.saving_mode:
        st.image(st.session_state.temp_photo, caption="Confirm Save", use_container_width=True)
        name_input = st.text_input("Enter a name to save this plant")

        if name_input and st.button("✅ Confirm Save"):
            encoded = base64.b64encode(st.session_state.temp_photo.getvalue()).decode()
            mime_type = st.session_state.temp_photo.type
            data_url = f"data:{mime_type};base64,{encoded}"

            st.session_state.saved_photos[name_input] = {
                "image": data_url,
                "plant_name": st.session_state.temp_plant_name,
                "care_info": st.session_state.temp_care_info,
                "chat_log": st.session_state.chat_log
            }

            # Clear temp states
            st.session_state.temp_photo = None
            st.session_state.temp_plant_name = ""
            st.session_state.temp_care_info = None
            st.session_state.chat_log = []
            st.session_state.saving_mode = False

            st.success(f"🌟 Saved as '{name_input}'!")
            st.rerun()

# ===== View Saved Plants Tab =====
elif tab == "🪴 View Saved Plants":
    st.title("🪴 Your Saved Plants")

    options = list(st.session_state.saved_photos.keys())
    selected = st.sidebar.selectbox("Choose a saved plant:", [""] + options)

    if selected:
        entry = st.session_state.saved_photos[selected]
        st.subheader(f"📸 {selected}")
        st.image(entry["image"], use_container_width=True)

        if "plant_name" in entry:
            st.markdown(f"**Plant Identified:** {entry['plant_name']}")
        if "care_info" in entry and entry["care_info"]:
            care = entry["care_info"]
            st.markdown(f"**Light:** {care['Light Requirements']}")
            st.markdown(f"**Watering:** {care['Watering']}")
            st.markdown(f"**Humidity:** {care['Humidity Preferences']}")
            st.markdown(f"**Temperature:** {care['Temperature Range']}")
            st.markdown(f"**Feeding:** {care['Feeding Schedule']}")
            st.markdown(f"**Toxicity:** {care['Toxicity']}")
            st.markdown(f"**Additional Care:** {care['Additional Care']}")
            st.markdown(f"**Personality:** *{care['Personality']['Title']}* - {', '.join(care['Personality']['Traits'])}")
            st.markdown(f"*{care['Personality']['Prompt']}*")

        if "chat_log" in entry:
            st.subheader("🧠 Chat History")
            for speaker, msg in entry["chat_log"]:
                st.markdown(f"**{speaker}:** {msg}")
