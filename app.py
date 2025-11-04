import streamlit as st
import requests
from PIL import Image
import pandas as pd
import io
import base64

st.set_page_config(page_title="Image to Excel", page_icon="📊")
st.title("📊 Image to Excel Converter")

api_key = st.secrets["OPENROUTER_API_KEY"]

uploaded_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)
    
    if st.button("🔄 Convert to Excel", type="primary"):
        with st.spinner("Processing..."):
            try:
                # Convert image to base64
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                # Call OpenRouter API
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                    },
                    json={
                        "model": "google/gemini-flash-1.5",
                        "messages": [{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Extract table data as CSV only:"},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                            ]
                        }]
                    }
                )
                
                csv_data = response.json()['choices'][0]['message']['content']
                df = pd.read_csv(io.StringIO(csv_data))
                
                st.dataframe(df, use_container_width=True)
                
                excel_buffer = io.BytesIO()
                df.to_excel(excel_buffer, index=False, engine='openpyxl')
                excel_buffer.seek(0)
                
                st.download_button(
                    "⬇️ Download Excel",
                    excel_buffer,
                    "data.xlsx",
                    mime="application/vnd.ms-excel"
                )
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
