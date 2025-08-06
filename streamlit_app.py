#!/usr/bin/env python
"""
Streamlit Web App for PDF Extraction and Excel Report Generation
"""

import os
import streamlit as st

# Load environment variables from azure.env file if it exists
def load_azure_env():
    """Load environment variables from azure.env file"""
    env_file = os.path.join(os.path.dirname(__file__), 'azure.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load environment variables first
load_azure_env()

# Page configuration must be first
st.set_page_config(
    page_title="PDF Lab Report Extractor",
    page_icon="📊",
    layout="wide"
)

import pandas as pd
import json
import tempfile
from pathlib import Path
import base64
from io import BytesIO
import logging
from PIL import Image
import openai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the extraction and excel generation functions
try:
    from pdf_extractor import extract_text_from_pdf, process_with_openai_agent, extract_entities_from_text, enhance_entities_with_signature_validation
    from signature_detector import SignatureDetector
    from generate_excel_report import generate_excel_report
except Exception as e:
    logger.error(f"Error importing modules: {str(e)}")
    st.error(f"Error importing required modules: {str(e)}")

# Initialize OpenAI client and deployment name
def get_openai_client_and_deployment():
    """Initialize and return Azure OpenAI client and deployment name"""
    try:
        client = openai.AzureOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version="2023-12-01-preview",
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
        )
        deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        return client, deployment_name
    except Exception as e:
        logger.error(f"Error initializing OpenAI client: {str(e)}")
        st.error(f"Error initializing OpenAI client: {str(e)}")
        return None, None

# Check for required environment variables
def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        'AZURE_OPENAI_API_KEY',
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_DOC_INTELLIGENCE_KEY',
        'AZURE_DOC_INTELLIGENCE_ENDPOINT'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    # AZURE_OPENAI_DEPLOYMENT_NAME is optional, it defaults to "gpt-4o"
    if not os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'):
        st.info("ℹ️ AZURE_OPENAI_DEPLOYMENT_NAME not set, using default: gpt-4o")
    
    if missing_vars:
        st.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        st.info("Please ensure all Azure service credentials are properly configured.")
        st.info("Check your azure.env file and make sure it contains all required variables.")
        return False
    return True

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
    st.subheader("📋 Sample Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Our Ref:**", entities.get('our_ref', 'N/A'))
        st.write("**Company Name:**", entities.get('company_name', 'N/A'))
        st.write("**Lab Report Creation Date:**", entities.get('lab_report_creation_date', 'N/A'))
        st.write("**Subject:**", entities.get('subject', 'N/A'))
    
    with col2:
        st.write("**Sample Reference:**", entities.get('sample_reference', 'N/A'))
        
        # Display signature and compliance status with color coding
        is_signature = entities.get('is_there_signature', 'N/A')
        results_comply = entities.get('results_comply', 'N/A')
        
        if is_signature.lower() == 'yes':
            st.markdown("**Is There Signature?:** :green[✅ Yes]")
        elif is_signature.lower() == 'no':
            st.markdown("**Is There Signature?:** :red[❌ No]")
        else:
            st.write("**Is There Signature?:**", is_signature)
            
        if results_comply.lower() == 'yes':
            st.markdown("**Results Comply?:** :green[✅ Yes]")
        elif results_comply.lower() == 'no':
            st.markdown("**Results Comply?:** :red[❌ No]")
        else:
            st.write("**Results Comply?:**", results_comply)
    
    # Display signature detection results if available
    signature_detection = entities.get('signature_detection', {})
    if signature_detection:
        st.subheader("✍️ Signature Detection Results")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Images Analyzed", signature_detection.get('total_images_detected', 0))
        with col2:
            st.metric("Signatures Found", signature_detection.get('signatures_found', 0))
        with col3:
            expected_sigs = entities.get('expected_signatures', 0)
            actual_sigs = entities.get('actual_signatures', 0)
            match_status = "✅ Match" if expected_sigs == actual_sigs else "⚠️ Mismatch"
            st.metric("Signature Validation", f"{actual_sigs}/{expected_sigs}", delta=match_status)
    
    # Display test results
    st.subheader("🧪 Test Results")
    
    test_results = entities.get('test_results', [])
    if test_results:
        # Create DataFrame for test results
        df_data = []
        for result in test_results:
            df_data.append({
                'Parameter': result.get('parameter', ''),
                'Unit': result.get('unit', ''),
                'Test Method': result.get('test_method', ''),
                'Result': result.get('result', ''),
                'Specification': result.get('specification', ''),
                'Pass/Fail': result.get('pass_fail', '')
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            
            # Style the dataframe to highlight Pass/Fail
            def highlight_pass_fail(val):
                if val == 'Pass':
                    return 'background-color: #d4edda; color: #155724;'
                elif val == 'Fail':
                    return 'background-color: #f8d7da; color: #721c24;'
                return ''
            
            styled_df = df.style.applymap(highlight_pass_fail, subset=['Pass/Fail'])
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.info("No test results found in the document.")
    else:
        st.info("No test results found in the document.")

# Main app
def main():
    # Check environment first
    if not check_environment():
        st.stop()
    
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
    
    st.title("🔬 PDF Lab Report Extractor")
    st.write("Upload a PDF lab report to extract information, detect signatures, and generate a formatted Excel report.")
    
    # Add some helpful information
    with st.expander("ℹ️ How it works"):
        st.markdown("""
        This application uses advanced AI to:
        
        1. **📄 Extract Text**: Parse and extract text content from PDF lab reports
        2. **🤖 AI Analysis**: Use Azure OpenAI to identify and structure key information
        3. **✍️ Signature Detection**: Detect and validate human signatures using computer vision
        4. **📊 Excel Generation**: Create formatted Excel reports with color-coded status indicators
        
        **Supported Features:**
        - Laboratory certificate analysis
        - Test result extraction
        - Signature presence validation
        - Compliance status checking
        - Professional Excel report generation
        """)
    
    # File uploader
    uploaded_file = st.file_uploader("📎 Upload a PDF Lab Report", type=["pdf"], help="Select a PDF laboratory report or certificate of analysis")
    
    # Initialize session state for storing extracted data
    if 'extracted_entities' not in st.session_state:
        st.session_state.extracted_entities = None
    
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = None
    
    if 'temp_pdf_path' not in st.session_state:
        st.session_state.temp_pdf_path = None
        
    if 'excel_report_path' not in st.session_state:
        st.session_state.excel_report_path = None
        
    if 'signature_detection_results' not in st.session_state:
        st.session_state.signature_detection_results = None
        
    # Process PDF when uploaded
    if uploaded_file is not None:
        # Add options for processing
        st.subheader("Processing Options")
        col1, col2 = st.columns(2)
        
        with col1:
            detect_signatures = st.checkbox("🖋️ Detect Signatures", value=True, help="Use AI to detect and validate signatures in the PDF")
        
        with col2:
            generate_excel = st.checkbox("📊 Generate Excel Report", value=True, help="Automatically generate Excel report after extraction")
        
        if st.button("🚀 Process PDF", type="primary"):
            with st.spinner("Processing PDF..."):
                # Save the uploaded file to a temporary file
                temp_dir = tempfile.gettempdir()
                temp_pdf_path = os.path.join(temp_dir, uploaded_file.name)
                
                with open(temp_pdf_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.session_state.temp_pdf_path = temp_pdf_path
                
                try:
                    # Extract text from the PDF
                    progress_bar = st.progress(0)
                    st.write("📄 Extracting text from PDF...")
                    extracted_text = extract_text_from_pdf(temp_pdf_path)
                    st.session_state.extracted_text = extracted_text
                    progress_bar.progress(25)
                    
                    # Extract entities
                    st.write("🤖 Extracting entities with AI...")
                    
                    # Get OpenAI client and deployment name
                    client, deployment_name = get_openai_client_and_deployment()
                    if client is None or deployment_name is None:
                        st.error("❌ Failed to initialize OpenAI client")
                        return
                    
                    entities = extract_entities_from_text(extracted_text, client, deployment_name)
                    progress_bar.progress(50)
                    
                    # Detect signatures if requested
                    if detect_signatures:
                        st.write("✍️ Detecting signatures...")
                        signature_detector = SignatureDetector()
                        signature_results = signature_detector.detect_signatures_in_pdf(temp_pdf_path)
                        st.session_state.signature_detection_results = signature_results
                        
                        # Enhance entities with signature validation
                        entities = enhance_entities_with_signature_validation(entities, signature_results)
                        progress_bar.progress(75)
                    
                    # Store the extracted entities
                    st.session_state.extracted_entities = entities
                    progress_bar.progress(100)
                    
                    st.success("✅ PDF processed successfully!")
                    
                    # Auto-generate Excel if requested
                    if generate_excel:
                        with st.spinner("📊 Generating Excel report..."):
                            try:
                                output_file = os.path.join(
                                    tempfile.gettempdir(), 
                                    f"{Path(temp_pdf_path).stem}_report.xlsx"
                                )
                                
                                excel_file = generate_excel_report(entities, None, output_file)
                                st.session_state.excel_report_path = excel_file
                                st.success("📊 Excel report generated automatically!")
                                
                            except Exception as e:
                                st.error(f"Error generating Excel report: {str(e)}")
                    
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {str(e)}")
                    logger.error(f"Error processing PDF: {str(e)}")
    
    # If extraction was successful, display the results
    if st.session_state.extracted_entities:
        # Display tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Extracted Data", "📄 Raw Text", "🔧 Raw JSON", "✍️ Signature Details"])
        
        with tab1:
            display_entities(st.session_state.extracted_entities)
            
            # Excel report section
            st.subheader("📊 Excel Report")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Button to generate/regenerate Excel report
                if st.button("🔄 Generate Excel Report", help="Generate a formatted Excel report"):
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
                            st.success(f"📊 Excel report generated successfully!")
                            
                        except Exception as e:
                            st.error(f"❌ Error generating Excel report: {str(e)}")
            
            with col2:
                # Download link for Excel report
                if st.session_state.excel_report_path and os.path.exists(st.session_state.excel_report_path):
                    st.markdown(
                        f"**📥 Download:** {get_excel_download_link(st.session_state.excel_report_path)}",
                        unsafe_allow_html=True
                    )
                else:
                    st.info("Generate Excel report to enable download")
        
        with tab2:
            st.subheader("📄 Extracted Text")
            st.text_area("Raw extracted text from PDF", st.session_state.extracted_text, height=400)
            
        with tab3:
            st.subheader("🔧 Raw JSON Data")
            st.json(st.session_state.extracted_entities)
            
        with tab4:
            st.subheader("✍️ Signature Detection Details")
            if st.session_state.signature_detection_results:
                signature_data = st.session_state.signature_detection_results
                
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Images Analyzed", signature_data.get('total_images_detected', 0))
                with col2:
                    st.metric("Signatures Found", signature_data.get('signatures_found', 0))
                with col3:
                    st.metric("Processing Errors", len(signature_data.get('processing_errors', [])))
                
                # Detailed signature information
                signature_details = signature_data.get('signature_details', [])
                if signature_details:
                    st.subheader("Signature Details")
                    for i, sig in enumerate(signature_details, 1):
                        with st.expander(f"Signature {i} - Page {sig.get('page_number', 'N/A')} (Confidence: {sig.get('confidence', 0):.2f})"):
                            st.write("**Reasoning:**", sig.get('classification', {}).get('reasoning', 'N/A'))
                            st.write("**Characteristics:**", ', '.join(sig.get('classification', {}).get('signature_characteristics', [])))
                            
                            # Individual signature info
                            individual_info = sig.get('individual_signature_info', {})
                            if individual_info:
                                st.write("**Position:**", individual_info.get('position', 'N/A'))
                                st.write("**Type:**", individual_info.get('type', 'N/A'))
                                st.write("**Description:**", individual_info.get('description', 'N/A'))
                else:
                    st.info("No signatures detected in the document")
            else:
                st.info("No signature detection performed. Enable signature detection when processing the PDF.")
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
