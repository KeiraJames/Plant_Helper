import streamlit as st
import base64

st.set_page_config(page_title="Photo Uploader", layout="wide")

# Initialize session state
if "saved_photos" not in st.session_state:
    st.session_state.saved_photos = {}
if "temp_photo" not in st.session_state:
    st.session_state.temp_photo = None
if "temp_photo_name" not in st.session_state:
    st.session_state.temp_photo_name = ""

# Sidebar Tabs
sidebar_tab = st.sidebar.radio("Choose a tab", ["📤 Upload & Save", "🖼️ View Saved Photos"])

# ===== Tab 1: Upload & Save =====
if sidebar_tab == "📤 Upload & Save":
    st.title("📸 Upload and Save Your Photo")

    # Upload form
    if st.session_state.temp_photo is None:
        uploaded_file = st.file_uploader("Choose a photo...", type=["png", "jpg", "jpeg"], key="uploader")
        photo_name = st.text_input("Name your photo before saving:")

        if uploaded_file and photo_name:
            st.session_state.temp_photo = uploaded_file
            st.session_state.temp_photo_name = photo_name
            st.rerun()  # refresh to enter the preview section

    # Preview and options
    elif st.session_state.temp_photo:
        st.image(st.session_state.temp_photo, caption="Preview", use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Save Photo"):
                encoded = base64.b64encode(st.session_state.temp_photo.getvalue()).decode()
                mime_type = st.session_state.temp_photo.type
                data_url = f"data:{mime_type};base64,{encoded}"
                st.session_state.saved_photos[st.session_state.temp_photo_name] = data_url

                # Clear temporary state
                st.session_state.temp_photo = None
                st.session_state.temp_photo_name = ""
                st.success("Photo saved! ✅")
                st.rerun()

        with col2:
            if st.button("❌ Discard Photo"):
                st.session_state.temp_photo = None
                st.session_state.temp_photo_name = ""
                st.warning("Photo discarded. You can upload another.")
                st.rerun()

# ===== Tab 2: View Saved Photos =====
elif sidebar_tab == "🖼️ View Saved Photos":
    st.title("🖼️ Your Saved Photos")

    st.sidebar.header("Saved Photos")
    selected_photo = st.sidebar.selectbox("Select a saved photo to view:", options=[""] + list(st.session_state.saved_photos.keys()))

    if selected_photo:
        st.subheader(f"📸 Viewing: {selected_photo}")
        st.image(st.session_state.saved_photos[selected_photo], caption=selected_photo, use_container_width=True)
