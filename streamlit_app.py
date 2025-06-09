#!/usr/bin/env python
"""
Streamlit Web App for PDF Extraction and Excel Report Generation
"""

import os
import streamlit as st
import pandas as pd
import json
import tempfile
from pathlib import Path
import base64
from io import BytesIO
import logging
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the extraction and excel generation functions
try:
    from pdf_extractor import extract_text_from_pdf, process_with_openai_agent
    from generate_excel_report import generate_excel_report
except Exception as e:
    logger.error(f"Error importing modules: {str(e)}")
    st.error(f"Error importing required modules: {str(e)}")

# Page configuration
st.set_page_config(
    page_title="PDF Lab Report Extractor",
    page_icon="📊",
    layout="wide"
)

# Function to create a download link for a file
def get_download_link(file_path, link_text):
    with open(file_path, "rb") as file:
        contents = file.read()
    
    b64 = base64.b64encode(contents).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{Path(file_path).name}">{link_text}</a>'

# Function to create a download link for an Excel file in memory
def get_excel_download_link(excel_file_path):
    with open(excel_file_path, "rb") as file:
        contents = file.read()
    
    b64 = base64.b64encode(contents).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{Path(excel_file_path).name}">Download Excel Report</a>'
    return href

# Function to display extracted entities in a nice format
def display_entities(entities):
    # Display sample information
    st.subheader("Sample Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Our Reference:**", entities.get('our_reference', 'N/A'))
        st.write("**Date:**", entities.get('date', 'N/A'))
        st.write("**Subject:**", entities.get('subject', 'N/A'))
        st.write("**Sample Reference:**", entities.get('sample_reference', 'N/A'))
    
    with col2:
        st.write("**Sampling Date & Time:**", entities.get('sampling_date_time', 'N/A'))
        st.write("**Sample Officer In-charge:**", entities.get('sample_officer_incharge', 'N/A'))
        st.write("**Sampling Catchment:**", entities.get('sampling_catchment', 'N/A'))
    
    # Display test results
    st.subheader("Test Results")
    
    # Create a DataFrame for test results
    test_data = {
        "Parameter": entities.get('test_parameters', []),
        "Unit": entities.get('units', []),
        "Method": entities.get('test_methods', []),
        "Result": entities.get('results', [])
    }
    
    # Make sure all lists have the same length
    max_len = max(len(test_data[key]) for key in test_data)
    for key in test_data:
        test_data[key] = (test_data[key] + [''] * max_len)[:max_len]
    
    # Create and display the DataFrame if there's data
    if max_len > 0:
        df = pd.DataFrame(test_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No test results found in the document.")

# Main app
def main():
    # Display PUB logo
    try:
        # Use current directory path for logo (handles both local and container environments)
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "publogo.png")
        if os.path.exists(logo_path):
            image = Image.open(logo_path)
            # Get the original image dimensions
            width, height = image.size
            # Resize image to 25% of original size (maintain your current resize level)
            image = image.resize((width // 4, height // 4), Image.LANCZOS)
            
            # Create a column layout specifically for centering
            # The wider side columns will push the image to be perfectly centered
            col1, col2, col3 = st.columns([2, 1, 2])
            
            # Display the image in the middle column
            with col2:
                st.image(image, use_container_width=True)
        else:
            logger.warning(f"Logo file not found at: {logo_path}")
    except Exception as e:
        logger.error(f"Error displaying logo: {str(e)}")
    
    st.title("PDF Lab Report Extractor")
    st.write("Upload a PDF lab report to extract information and generate an Excel report.")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a PDF Lab Report", type=["pdf"])
    
    # Initialize session state for storing extracted data
    if 'extracted_entities' not in st.session_state:
        st.session_state.extracted_entities = None
    
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = None
    
    if 'temp_pdf_path' not in st.session_state:
        st.session_state.temp_pdf_path = None
        
    if 'excel_report_path' not in st.session_state:
        st.session_state.excel_report_path = None
        
    # Process PDF when uploaded
    if uploaded_file is not None:
        with st.spinner("Processing PDF..."):
            # Save the uploaded file to a temporary file
            temp_dir = tempfile.gettempdir()
            temp_pdf_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state.temp_pdf_path = temp_pdf_path
            
            try:
                # Extract text from the PDF
                extracted_text = extract_text_from_pdf(temp_pdf_path)
                st.session_state.extracted_text = extracted_text
                
                # Process with OpenAI
                response = process_with_openai_agent(extracted_text)
                
                # Store the extracted entities
                st.session_state.extracted_entities = response['extracted_entities']
                
                st.success("PDF processed successfully!")
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
    
    # If extraction was successful, display the results
    if st.session_state.extracted_entities:
        # Display tabs for different views
        tab1, tab2, tab3 = st.tabs(["Extracted Data", "Raw Text", "Raw JSON"])
        
        with tab1:
            display_entities(st.session_state.extracted_entities)
            
            # Button to generate Excel report
            if st.button("Generate Excel Report"):
                with st.spinner("Generating Excel report..."):
                    try:
                        # Generate temporary file path for Excel
                        output_file = os.path.join(
                            tempfile.gettempdir(), 
                            f"{Path(st.session_state.temp_pdf_path).stem}_report.xlsx"
                        )
                        
                        # Generate Excel report
                        excel_file = generate_excel_report(
                            st.session_state.extracted_entities, 
                            None, 
                            output_file
                        )
                        
                        st.session_state.excel_report_path = excel_file
                        st.success(f"Excel report generated successfully!")
                        
                        # Provide download link
                        st.markdown(
                            get_excel_download_link(excel_file),
                            unsafe_allow_html=True
                        )
                    except Exception as e:
                        st.error(f"Error generating Excel report: {str(e)}")
        
        with tab2:
            st.text_area("Extracted Text", st.session_state.extracted_text, height=400)
            
        with tab3:
            st.json(st.session_state.extracted_entities)
    else:
        # Show sample image when no file is uploaded
        st.info("Upload a PDF to extract information and generate an Excel report.")
        
        try:
            # Try to display the sample output image if available
            sample_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_output.jpg")
            if os.path.exists(sample_image_path):
                st.image(sample_image_path, caption="Sample Excel Output", use_container_width=True)
        except Exception:
            pass

if __name__ == "__main__":
    main()
