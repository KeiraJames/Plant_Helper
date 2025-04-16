import streamlit as st
import base64

st.set_page_config(page_title="Multi-Photo Viewer", layout="wide")

# Track saved photos in memory
if "saved_photos" not in st.session_state:
    st.session_state.saved_photos = {}

tab1, tab2 = st.tabs(["📤 Upload & Save", "🖼️ Saved Photos"])

with tab1:
    st.header("Upload a Photo")

    uploaded_file = st.file_uploader("Choose a photo...", type=["png", "jpg", "jpeg"])
    photo_name = st.text_input("Enter a name to save this photo:")

    if uploaded_file:
        st.image(uploaded_file, caption="Preview", use_container_width=True)

    # Save button — only active if both image and name are provided
    if uploaded_file and photo_name:
        if st.button("✅ Save Photo"):
            encoded = base64.b64encode(uploaded_file.getvalue()).decode()
            mime_type = uploaded_file.type
            data_url = f"data:{mime_type};base64,{encoded}"
            st.session_state.saved_photos[photo_name] = data_url
            st.success(f"Photo saved as '{photo_name}' ✅")

with tab2:
    st.header("Your Saved Photos")

    if not st.session_state.saved_photos:
        st.info("No photos saved yet.")
    else:
        for name, data_url in st.session_state.saved_photos.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{name}**")
                st.image(data_url, use_container_width=True)
            with col2:
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
                st.markdown(f"""
                    <a href="{viewer_url}" target="_blank">
                        <button style="padding:8px 14px;">📂 Open in New Tab</button>
                    </a>
                """, unsafe_allow_html=True)
