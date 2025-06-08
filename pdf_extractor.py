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
        dict: OpenAI API response and extracted entities
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
    
    # Extract entities
    entities = extract_entities_from_text(text, client, deployment_name)
    
    return {"summary_response": response, "extracted_entities": entities}

def extract_entities_from_text(text, client, deployment_name):
    """
    Extract specific entities from the document text using Azure OpenAI.
    
    Args:
        text (str): The extracted text from the PDF
        client: The Azure OpenAI client
        deployment_name (str): The name of the Azure OpenAI deployment
        
    Returns:
        dict: Extracted entities
    """
    print("Extracting entities from text...")
    
    # Prepare prompt for entity extraction
    system_message = """
    You are an AI assistant specialized in extracting information from laboratory reports and documents.
    Extract the exact values for the requested entities. If you cannot find a value, respond with "Not found".
    Format your response as a JSON object with the following keys:
    """
    
    user_message = f"""
    Please extract the following entities from this laboratory report text:

    1. our_reference: The "Our Ref" value
    2. date: The "Date" value
    3. subject: The full subject text
    4. sample_reference: The full sample reference description
    5. sampling_date_time: The date and time in brackets in the sample reference section (extract just the date/time)
    6. sample_officer_incharge: The person at the bottom of the document with Chemist as the job title
    7. sampling_catchment: The word in brackets at "Tested For" below "Public Utilities Board"
    8. test_parameters: List of test parameters
    9. units: List of units corresponding to test parameters
    10. test_methods: List of test methods used
    11. results: List of test results corresponding to test parameters
    
    Document text:
    {text}
    
    Return only a valid JSON object with these keys, nothing else.
    """
    
    try:
        # Call Azure OpenAI API for entity extraction
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,  # Low temperature for more deterministic results
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        # Extract content from response
        content = response.choices[0].message.content
        
        # Convert to dictionary if it's a JSON string
        import json
        try:
            entities = json.loads(content)
            
            # Format the date_time entity if present
            if 'sampling_date_time' in entities:
                entities['sampling_date_time'] = format_date_time(entities['sampling_date_time'])
            
            return entities
        except json.JSONDecodeError:
            print("Error: Could not parse JSON response from OpenAI")
            return {"error": "Failed to parse JSON response", "raw_content": content}
        
    except Exception as e:
        print(f"Error extracting entities: {str(e)}")
        return {"error": str(e)}

def format_date_time(date_time_str):
    """
    Format a date-time string to dd/mm/yyyy hh:mm:ss AM/PM format
    
    Args:
        date_time_str (str): The original date-time string from the document
        
    Returns:
        str: Formatted date-time or the original string if formatting fails
    """
    import re
    import datetime
    
    try:
        # Example input: "12/12/07, 1510 hrs"
        # Extract the date and time parts
        match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4}),?\s*(\d{1,4})\s*hrs', date_time_str)
        
        if not match:
            # Return the original if pattern doesn't match
            return date_time_str
        
        date_part = match.group(1)
        time_part = match.group(2)
        
        # Handle 2-digit year and convert to 4-digit year
        if len(date_part.split('/')[-1]) == 2:
            day, month, year_short = date_part.split('/')
            # Assuming 20xx for years less than 50, 19xx for years 50+
            year = f"20{year_short}" if int(year_short) < 50 else f"19{year_short}"
            date_part = f"{day}/{month}/{year}"
        
        # Convert military time to 12-hour format
        if len(time_part) <= 2:  # Hours only
            hour = int(time_part)
            minute = 0
        else:  # Hours and minutes
            if len(time_part) == 3:  # Format like "130" for 1:30
                hour = int(time_part[0])
                minute = int(time_part[1:])
            else:  # Format like "1510" for 15:10
                hour = int(time_part[:-2])
                minute = int(time_part[-2:])
        
        # Determine AM or PM
        am_pm = "AM" if hour < 12 else "PM"
        # Convert 24-hour format to 12-hour format
        if hour > 12:
            hour -= 12
        elif hour == 0:
            hour = 12
        
        # Format the date and time in the required format
        formatted_date_time = f"{date_part} {hour:02d}:{minute:02d}:00 {am_pm}"
        return formatted_date_time
        
    except Exception as e:
        print(f"Error formatting date-time: {str(e)}")
        return date_time_str

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
        print(response['summary_response'].choices[0].message.content)
        
        # Print extracted entities in a readable format
        print("\nExtracted Entities:")
        import json
        entities = response['extracted_entities']
        print(json.dumps(entities, indent=2))
        
        # Save extracted entities to a JSON file
        entities_path = Path(pdf_path).stem + "_entities.json"
        with open(entities_path, "w", encoding="utf-8") as f:
            json.dump(entities, f, indent=2)
            
        print(f"\nExtracted entities saved to: {entities_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
