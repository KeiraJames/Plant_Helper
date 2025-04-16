import streamlit as st
import base64

st.set_page_config(page_title="Photo Uploader", layout="centered")

# Store photos in memory
if "saved_photos" not in st.session_state:
    st.session_state.saved_photos = {}

# ===== Sidebar Section =====
st.sidebar.header("🖼️ Saved Photos")
if st.session_state.saved_photos:
    for name, data_url in st.session_state.saved_photos.items():
        html_viewer = f"""
        <html>
          <head><title>{name}</title></head>
          <body style="text-align:center; padding:2em;">
            <h2>{name}</h2>
            <img src="{data_url}" style="max-width:90%; border:1px solid #ccc;" />
            <p><i>This is your saved photo.</i></p>
          </body>
        </html>
        """
        html_encoded = base64.b64encode(html_viewer.encode()).decode()
        viewer_url = f"data:text/html;base64,{html_encoded}"
        st.sidebar.markdown(f"**{name}**", unsafe_allow_html=True)
        st.sidebar.markdown(f"""
            <a href="{viewer_url}" target="_blank">
                <button style="padding:4px 8px;">📂 View</button>
            </a>
        """, unsafe_allow_html=True)
else:
    st.sidebar.info("No saved photos yet.")

# ===== Main Area =====
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
