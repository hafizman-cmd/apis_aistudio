import streamlit as st
import replicate
import os
import requests
from io import BytesIO

# --- APP SETTINGS ---
st.set_page_config(page_title="Apis Image Studio", page_icon="⚡", layout="centered")

# --- MODERN MINIMALIST STYLING ---
st.markdown("""
<style>
/* moving gradient background */
.stApp {
    background: linear-gradient(-45deg, #0f172a, #1e293b, #020617, #1e1b4b);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}
@keyframes gradientBG {
    0% { background-position: 0% 10%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Main white card container */
.block-container {
    background: rgba(255, 255, 255, 0.97);
    border-radius: 16px;
    padding: 2.5rem 2.5rem;
    margin-top: 3rem;
    margin-bottom: 3rem;
    max-width: 800px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

/* Fix text colors */
h1, h2, h3, p, span, label, div[data-testid="stMarkdownContainer"] > p {
    color: #1e293b !important;
}

/* --- THE BLINKING CURSOR & TEXT INPUTS --- */
.stTextArea textarea,
.stTextInput input {
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    background-color: #ffffff !important;
    color: #0f172a !important; 
    caret-color: #6c63ff !important; 
    padding: 0.8rem !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #6c63ff !important;
    box-shadow: 0 0 0 1px #6c63ff !important;
}

/* --- UNIFIED, USER-FRIENDLY BUTTONS --- */
button[kind="primary"] {
    background-color: #6c63ff !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem !important;
    font-weight: bold !important;
    font-size: 1.1rem !important;
    transition: all 0.2s;
}
button[kind="primary"]:hover {
    background-color: #5a52d4 !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(108,99,255,0.3) !important;
}

.stDownloadButton > button, 
[data-testid="stLinkButton"] > a {
    background-color: #f8fafc !important;
    color: #334155 !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    text-align: center !important;
    display: flex !important;
    justify-content: center !important;
    font-weight: 600 !important;
    width: 100% !important;
    padding: 0.6rem !important;
    transition: all 0.2s;
    text-decoration: none !important;
}
.stDownloadButton > button:hover, 
[data-testid="stLinkButton"] > a:hover {
    background-color: #f1f5f9 !important;
    border-color: #cbd5e1 !important;
    color: #6c63ff !important; 
    transform: translateY(-1px);
}

/* image styling */
.stImage img {
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin-bottom: 1.5rem;
}

/* footer styling */
.footer-text {
    text-align: center;
    color: #94a3b8 !important;
    font-size: 0.85rem;
    margin-top: 3rem;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# --- API KEY LOGIC ---
api_token = st.secrets.get("REPLICATE_API_TOKEN")
if not api_token:
    api_token = st.text_input("🔑 Developer Mode: Enter Replicate Key", type="password")
if api_token:
    os.environ["REPLICATE_API_TOKEN"] = api_token

# --- MAIN UI ---
st.title("⚡ Apis Image Studio")
st.markdown("Create and edit AI images with minimal effort")

tab1, tab2 = st.tabs(["🎨 Generate", "✏️ Edit"])

# ------------------- TAB 1: GENERATE -------------------
with tab1:
    prompt = st.text_area(
        "What do you want to create?",
        placeholder="A futuristic KLCC in 2099, cinematic lighting, ultra detailed..."
    )
    ratio = st.radio("Choose Shape:", ["Square", "Portrait", "Landscape"], horizontal=True)
    dims = {"Square": (1024, 1024), "Portrait": (768, 1024), "Landscape": (1024, 768)}
    w, h = dims[ratio]

    if st.button("Generate Image", type="primary", use_container_width=True):
        if not prompt.strip():
            st.warning("Please type a description first!")
        else:
            with st.spinner("Creating magic..."):
                try:
                    output = replicate.run(
                        "prunaai/p-image",
                        input={"prompt": prompt, "width": w, "height": h}
                    )
                    
                    img_url = str(output)

                    st.image(
                        img_url, 
                        caption="✨ Hover over image and click top-right arrows to expand (Press ESC to close)", 
                        use_container_width=True
                    )

                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        img_data = requests.get(img_url).content
                        st.download_button("💾 Save", data=img_data, file_name="apis_studio.png", mime="image/png", use_container_width=True)
                    with col2:
                        # FIX: Using the direct output object is better for link generation
                        # replicate.com URL format
                        replicate_url = f"https://replicate.com/p/{output.id}" if hasattr(output, 'id') else img_url
                        st.link_button("📋 Link", replicate_url, use_container_width=True)
                    with col3:
                        wa_url = f"https://wa.me/?text=Check out this AI art I made: {img_url}"
                        st.link_button("📱 WhatsApp", wa_url, use_container_width=True)
                    with col4:
                        x_url = f"https://twitter.com/intent/tweet?text=Look at this AI art!&url={img_url}"
                        st.link_button("🐦 X", x_url, use_container_width=True)

                except Exception as e:
                    st.error(f"Error: {e}")

# ------------------- TAB 2: EDIT -------------------
with tab2:
    st.markdown("### Smart Edit")
    uploaded = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    
    if uploaded:
        st.image(uploaded, caption="Original Image", use_container_width=True)

        edit_p = st.text_input(
            "What should we change?",
            placeholder="Make it look like a pencil sketch"
        )
        
        if st.button("Apply Edit", type="primary", use_container_width=True):
            with st.spinner("Processing edit..."):
                try:
                    # UPDATED FIX: We must send the RAW BYTES of the file, not the file object.
                    output = replicate.run(
                        "prunaai/p-image-edit",
                        input={"prompt": edit_p, "image": uploaded.getvalue()} # <--- THIS IS THE FIX
                    )
                    
                    edited_img_url = str(output)
                    
                    st.image(
                        edited_img_url, 
                        caption="✨ Hover over image and click top-right arrows to expand (Press ESC to close)", 
                        use_container_width=True
                    )

                    edited_data = requests.get(edited_img_url).content
                    st.download_button(
                        "💾 Save Edited Image",
                        data=edited_data,
                        file_name="edited_image.png",
                        mime="image/png",
                        use_container_width=True
                    )
                except Exception as e:
                    # Capture specific error messages from the Replicate API
                    if "422" in str(e):
                        st.error("Edit failed: The server rejected the image format. Try converting to a standard JPG/PNG.")
                    else:
                        st.error(f"Edit failed: {e}")

# ------------------- FOOTER -------------------
st.markdown("<p class='footer-text'>© 2026 Apis Image Studio – Modern AI Art Generator</p>", unsafe_allow_html=True)
