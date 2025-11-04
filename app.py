import streamlit as st
import base64
import requests
import pandas as pd
from io import BytesIO

# Load Gemini API Key from secrets (never push in repo)
API_KEY = st.secrets.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")

# URL for Gemini Pro Vision
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent"

# Function to encode image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode("utf-8")

# Function to call Gemini API
def extract_table_from_image(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Extract table data from this image and return CSV:"
                    },
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": base64_image
                        }
                    }
                ]
            }
        ]
    }

    response = requests.post(
        f"{API_URL}?key={API_KEY}",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        try:
            content = response.json()['candidates'][0]['content']['parts'][0]['text']
            return content
        except Exception as e:
            st.error("Failed to parse Gemini response")
            return ""
    else:
        st.error(f"Gemini API Error: {response.status_code}")
        return ""

# Convert CSV text to Excel file
def csv_text_to_excel(csv_text):
    from io import StringIO
    try:
        df = pd.read_csv(StringIO(csv_text))
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return output
    except Exception as e:
        st.error("Unable to convert CSV to Excel. Check format.")
        return None

# Streamlit UI
st.set_page_config(page_title="Image to Excel App", layout="centered")
st.title("📊 Image to Excel Converter")

st.markdown("Upload an image of a table or document. The AI will extract data and convert it to Excel format.")

uploaded_file = st.file_uploader("Upload Image (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    if st.button("Convert to Excel"):
        with st.spinner("Processing... Please wait ⏳"):
            image_bytes = uploaded_file.read()

            csv_output = extract_table_from_image(image_bytes)

            if csv_output:
                st.success("✅ Table data extracted.")
                st.text_area("Extracted CSV Preview", csv_output, height=250)

                excel_file = csv_text_to_excel(csv_output)

                if excel_file:
                    st.download_button(
                        label="📥 Download Excel File",
                        data=excel_file,
                        file_name="output.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
