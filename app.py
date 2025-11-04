import streamlit as st
import base64
import requests
import pandas as pd
from io import BytesIO, StringIO

# ✅ Load Gemini API key from Streamlit secrets
API_KEY = st.secrets["GEMINI_API_KEY"]

# ✅ Correct Gemini Pro Vision endpoint
API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-pro-vision:generateContent"

# ✅ Function to call Gemini API Vision Model with an image
def extract_table_from_image(image_bytes):
    base64_img = base64.b64encode(image_bytes).decode("utf-8")

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [
            {
                "parts": [
                    {"text": "Extract table data from this image and return it as CSV format."},
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": base64_img
                        }
                    }
                ]
            }
        ]
    }

    response = requests.post(f"{API_URL}?key={API_KEY}", headers=headers, json=data)

    if response.status_code == 200:
        try:
            reply = response.json()
            csv_text = reply['candidates'][0]['content']['parts'][0]['text']
            return csv_text
        except Exception as e:
            st.error("✅ API worked but couldn't parse CSV text. Please try a simpler image.")
            return None
    else:
        st.error(f"❌ Gemini API Error: {response.status_code}")
        return None

# ✅ CSV text to Excel file
def csv_text_to_excel(csv_text):
    try:
        df = pd.read_csv(StringIO(csv_text))
        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        return output
    except Exception:
        st.error("❌ Failed to convert CSV to Excel. The format returned by AI may be incorrect.")
        return None

# ---------------------------------
# ✅ Streamlit App UI Starts Here
# ---------------------------------

st.set_page_config(page_title="Image to Excel Converter", layout="centered")

st.title("📸 Image to Excel Converter")
st.markdown("Upload an image of a **table or document** (JPG or PNG). It will be processed by AI to extract data and convert it to Excel. Powered by **Gemini AI**.")

uploaded_file = st.file_uploader("📤 Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    if st.button("🚀 Convert to Excel"):
        with st.spinner("Processing image and extracting data..."):
            image_bytes = uploaded_file.read()

            # Send to Gemini
            csv_text = extract_table_from_image(image_bytes)

            if csv_text:
                st.success("✅ Table extracted from image!")
                st.text_area("📝 Extracted CSV Preview", csv_text, height=250)

                excel_file = csv_text_to_excel(csv_text)

                if excel_file:
                    st.download_button(
                        label="📥 Download Excel File",
                        data=excel_file,
                        file_name="output.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
