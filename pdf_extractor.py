#!/usr/bin/env python
"""
PDF Text Extraction using Azure Document Intelligence and OpenAI Agent
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import openai
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

# Load environment variables
load_dotenv()

# Azure Document Intelligence setup
doc_intelligence_key = os.environ.get("AZURE_DOC_INTELLIGENCE_KEY")
doc_intelligence_endpoint = os.environ.get("AZURE_DOC_INTELLIGENCE_ENDPOINT")

# Azure OpenAI setup
openai.api_key = os.environ.get("AZURE_OPENAI_API_KEY")
openai.api_base = os.environ.get("AZURE_OPENAI_ENDPOINT")
openai.api_type = "azure"
openai.api_version = "2023-12-01-preview"  # Update this if needed
deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF using Azure Document Intelligence service.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    print(f"Processing file: {pdf_path}")
    
    # Initialize Document Intelligence client
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=doc_intelligence_endpoint,
        credential=AzureKeyCredential(doc_intelligence_key)
    )
    
    # Read PDF file
    with open(pdf_path, "rb") as f:
        document_bytes = f.read()
    
    # Analyze the document
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-layout",  # Using the layout model
        body=document_bytes,
        content_type="application/pdf"
    )
    
    # Get results
    result = poller.result()
    
    # Extract text from the result
    extracted_text = ""
    for page in result.pages:
        for line in page.lines:
            extracted_text += line.content + "\n"
    
    return extracted_text

def process_with_openai_agent(text):
    """
    Process the extracted text using Azure OpenAI.
    
    Args:
        text (str): Extracted text from the PDF
        
    Returns:
        dict: OpenAI API response
    """
    print("Processing extracted text with Azure OpenAI...")
    
    # Prepare prompt
    system_message = "You are an AI assistant that helps analyze and summarize document content."
    user_message = f"Analyze the following document content and provide a summary:\n\n{text[:4000]}..."  # Limit text size
    
    # Initialize the Azure OpenAI client
    client = openai.AzureOpenAI(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        api_version="2023-12-01-preview",
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
    )
    
    # Call Azure OpenAI API with the deployment name as the model
    print(f"Using deployment name: {deployment_name}")
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    return response

def main():
    """Main function to run the PDF extraction and processing"""
    if len(sys.argv) < 2:
        print("Usage: python pdf_extractor.py <path_to_pdf_file>")
        return
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found - {pdf_path}")
        return
    
    # Extract text from PDF
    try:
        extracted_text = extract_text_from_pdf(pdf_path)
        
        # Save extracted text to file
        output_path = Path(pdf_path).stem + "_extracted_text.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
        
        print(f"Extracted text saved to: {output_path}")
        
        # Process with Azure OpenAI Agent
        response = process_with_openai_agent(extracted_text)
        
        # Print OpenAI response
        print("\nAzure OpenAI Analysis:")
        print(response.choices[0].message.content)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
