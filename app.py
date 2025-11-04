import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import io

# --- Page Configuration ---
st.set_page_config(
    page_title="Image to Excel",
    page_icon="📊",
    layout="centered"
)

# --- Function to convert Excel file to a downloadable format ---
@st.cache_data
def to_excel(df):
    """Converts a pandas DataFrame to an Excel file in memory."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

# --- Main App Interface ---
st.title("🖼️ Image to Excel Converter")
st.write("Upload an image of a table, and AI will convert it into a downloadable Excel file.")

# --- API Key Configuration ---
# Use Streamlit's secrets management for the API key
try:
    # This is the correct way for deployed Streamlit apps
    api_key = st.secrets["GOOGLE_API_KEY"]
except (KeyError, FileNotFoundError):
    st.warning("API Key not found in Streamlit secrets. Please add it for the app to work on the cloud.")
    # Fallback for local development if secrets.toml is not used
    api_key = st.text_input("Enter your Google Gemini API Key:", type="password", key="api_key_input")

if not api_key:
    st.error("Please provide your Google Gemini API Key to proceed.")
    st.stop()

# Configure the Generative AI model
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro-vision')

# --- File Uploader ---
uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)

    # "Convert to Excel" button
    if st.button("✨ Convert to Excel"):
        # The prompt for the AI model
        prompt = """
        You are an expert in data extraction. Analyze the image and extract the tabular data.
        Your output must be ONLY the data in CSV format, with a comma (,) as the delimiter.
        Do not include any explanations, introductory text, or markdown formatting like ```csv.
        The first line of your output should be the header row from the table.
        If the image does not contain a table, say 'Error: No table found'.
        """
        
        with st.spinner("AI is working its magic... 🧙‍♂️"):
            try:
                # Call the Gemini API
                response = model.generate_content([prompt, image])
                
                # Clean the response text
                csv_text = response.text.strip()

                # Check for errors from Gemini
                if "Error: No table found" in csv_text:
                    st.error("The AI could not find a table in the image. Please try another one.")
                else:
                    # Remove markdown code fences if they exist
                    if csv_text.startswith("```csv"):
                        csv_text = csv_text[6:]
                    if csv_text.endswith("```"):
                        csv_text = csv_text[:-3]
                    
                    # Convert the CSV text to a pandas DataFrame
                    csv_file_like_object = io.StringIO(csv_text)
                    df = pd.read_csv(csv_file_like_object)

                    st.success("✅ Conversion Successful!")
                    
                    # Display the extracted data
                    st.dataframe(df)

                    # Create the Excel file for download
                    excel_data = to_excel(df)
                    
                    st.download_button(
                        label="📥 Download Excel File",
                        data=excel_data,
                        file_name=f"converted_data_{uploaded_file.name}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.error("This might be due to an invalid API key, network issues, or a problem with the AI response format. Please check your key and try again.")
