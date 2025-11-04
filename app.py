# app.py

import streamlit as st
from google import genai
from PIL import Image
import io

# --- Configuration & Initialization ---

# 1. API Key Handling (Fixes your KeyError)
try:
    # Use the correct key name as defined in .streamlit/secrets.toml
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("🚨 API Key not found!")
    st.warning("Please create a `.streamlit/secrets.toml` file with `GEMINI_API_KEY = 'YOUR_KEY'`")
    st.stop() # Stop the app if the key is missing

# 2. Gemini Client Initialization
# This uses the official and current 'google-genai' SDK
client = genai.Client(api_key=API_KEY)
# We will use the model gemini-2.5-flash which is an excellent multimodal model
MODEL_NAME = "gemini-2.5-flash" 

# --- Streamlit UI and Logic ---

st.title("🖼️ Gemini Image Describer")
st.caption(f"Powered by Google Gemini and {MODEL_NAME}")
st.divider()

# File Uploader
uploaded_file = st.file_uploader(
    "Upload an image (JPG, PNG) to analyze:", 
    type=["png", "jpg", "jpeg"]
)

# Text Input for the prompt
prompt = st.text_input(
    "What question do you have about the image?",
    value="Describe this image in a fun and informative way.",
)

# Execute Button
if uploaded_file is not None:
    # Display the uploaded image
    image_data = uploaded_file.read()
    image = Image.open(io.BytesIO(image_data))
    st.image(image, caption='Image uploaded.', use_column_width=True)

    if st.button("Generate Description", type="primary"):
        if prompt:
            with st.spinner('Analyzing image with Gemini...'):
                try:
                    # 3. Model Call (Uses the current SDK and recommended model)
                    response = client.models.generate_content(
                        model=MODEL_NAME, 
                        contents=[prompt, image] # Multimodal input: text and image
                    )
                    
                    st.subheader("Gemini's Response:")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"An API error occurred: {e}")
                    st.info("Check your API key and model name, or if you've hit a rate limit.")
        else:
            st.warning("Please enter a question about the image.")
