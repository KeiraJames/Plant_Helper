import streamlit as st
import base64

st.set_page_config(page_title="Photo Uploader", layout="wide")

# Store photos in memory
if "saved_photos" not in st.session_state:
    st.session_state.saved_photos = {}

# ===== Tabs Section =====
tab1, tab2 = st.tabs(["📤 Upload & Save", "🖼️ View Saved Photos"])

# ===== Tab 1: Upload & Save Photo =====
with tab1:
    st.title("📸 Upload and Save Your Photo")

    uploaded_file = st.file_uploader("Choose a photo...", type=["png", "jpg", "jpeg"])
    photo_name = st.text_input("Name your photo before saving:")

    if uploaded_file:
        st.image(uploaded_file, caption="Preview", use_container_width=True)

    # Save button
    if uploaded_file and photo_name:
        if st.button("✅ Save Photo"):
            encoded = base64.b64encode(uploaded_file.getvalue()).decode()
            mime_type = uploaded_file.type
            data_url = f"data:{mime_type};base64,{encoded}"
            st.session_state.saved_photos[photo_name] = data_url
            st.success(f"Saved as '{photo_name}' 🎉")

# ===== Tab 2: View Saved Photos =====
with tab2:
    st.title("Your Saved Photos")

    # Sidebar: List saved photos
    st.sidebar.header("🖼️ Saved Photos")
    selected_photo = st.sidebar.selectbox("Select a saved photo to view:", options=[""] + list(st.session_state.saved_photos.keys()))

    # If a saved photo is selected, display it in the main section
    if selected_photo:
        st.subheader(f"📸 Viewing: {selected_photo}")
        st.image(st.session_state.saved_photos[selected_photo], caption=selected_photo, use_container_width=True)

