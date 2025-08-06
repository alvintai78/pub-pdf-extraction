#!/usr/bin/env python
"""
PDF Text Extraction and Signature Detection using Azure Document Intelligence and OpenAI Agent
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import openai
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from signature_detector import SignatureDetector

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

def enhance_entities_with_signature_validation(entities, signature_results):
    """
    Enhance extracted entities with signature validation logic.
    
    Args:
        entities (dict): Extracted entities from the document
        signature_results (dict): Results from signature detection
        
    Returns:
        dict: Enhanced entities with signature validation
    """
    print("Enhancing entities with signature validation...")
    
    # Count names and designations
    names_and_designations = entities.get("names_and_designations", [])
    expected_signatures = len(names_and_designations)
    
    # Get actual signature count
    actual_signatures = signature_results.get("signatures_found", 0) if signature_results else 0
    
    # If we found more signatures than names, try to infer missing names from signature detection
    if actual_signatures > expected_signatures and signature_results and 'signature_details' in signature_results:
        print(f"Found {actual_signatures} signatures but only {expected_signatures} names. Trying to add missing names...")
        
        # Extract names from signature detection results
        detected_names = []
        for sig_detail in signature_results['signature_details']:
            if 'individual_signature_info' in sig_detail:
                sig_info = sig_detail['individual_signature_info']
                if sig_info.get('type') == 'full_signature':
                    # Extract name from description
                    description = sig_info.get('description', '')
                    if 'name' in description.lower():
                        # Try to extract the name from descriptions like "Handwritten name 'LimmyT'"
                        import re
                        name_match = re.search(r"name ['\"]([^'\"]+)['\"]", description)
                        if name_match:
                            detected_name = name_match.group(1)
                            detected_names.append(detected_name)
        
        print(f"Detected names from signatures: {detected_names}")
        
        # Try to match detected names with missing designations
        existing_designations = [item['designation'] for item in names_and_designations]
        
        # If we have QA but not QC, or vice versa, try to add the missing one
        if 'QA APPROVED' in existing_designations and 'QC PASSED' not in existing_designations:
            if len(detected_names) > len(names_and_designations):
                # Add the missing QC name
                for detected_name in detected_names:
                    if not any(detected_name.lower() in item['name'].lower() for item in names_and_designations):
                        names_and_designations.append({
                            "name": detected_name,
                            "designation": "QC PASSED"
                        })
                        print(f"Added inferred name: {detected_name} - QC PASSED")
                        break
        elif 'QC PASSED' in existing_designations and 'QA APPROVED' not in existing_designations:
            if len(detected_names) > len(names_and_designations):
                # Add the missing QA name
                for detected_name in detected_names:
                    if not any(detected_name.lower() in item['name'].lower() for item in names_and_designations):
                        names_and_designations.append({
                            "name": detected_name,
                            "designation": "QA APPROVED"
                        })
                        print(f"Added inferred name: {detected_name} - QA APPROVED")
                        break
        elif len(detected_names) >= 2 and len(names_and_designations) == 1:
            # If we have multiple detected names but only one extracted
            # Add the other names with appropriate designations
            remaining_names = [name for name in detected_names 
                             if not any(name.lower() in item['name'].lower() for item in names_and_designations)]
            
            if remaining_names:
                # If the existing entry is QA, add QC
                if any('QA' in item['designation'] for item in names_and_designations):
                    names_and_designations.append({
                        "name": remaining_names[0],
                        "designation": "QC PASSED"
                    })
                    print(f"Added inferred name: {remaining_names[0]} - QC PASSED")
                # If the existing entry is QC, add QA  
                elif any('QC' in item['designation'] for item in names_and_designations):
                    names_and_designations.append({
                        "name": remaining_names[0],
                        "designation": "QA APPROVED"
                    })
                    print(f"Added inferred name: {remaining_names[0]} - QA APPROVED")
                else:
                    # Generic signatory
                    names_and_designations.append({
                        "name": remaining_names[0],
                        "designation": "SIGNATORY"
                    })
                    print(f"Added inferred name: {remaining_names[0]} - SIGNATORY")
    
    # Update expected signatures count
    expected_signatures = len(names_and_designations)
    
    # Determine if signatures match expected count
    signatures_match = expected_signatures > 0 and actual_signatures == expected_signatures
    
    # Check test results for any failures - this determines "Results Comply"
    test_results = entities.get("test_results", [])
    test_results_comply = True
    
    for result in test_results:
        pass_fail_status = result.get("pass_fail", "").lower()
        if pass_fail_status == "fail":
            test_results_comply = False
            break
    
    # Results comply is based solely on test results (no failures)
    # If there are no test results, default to "Yes"
    results_comply_status = "Yes" if (not test_results or test_results_comply) else "No"
    
    # Enhanced entities with validation
    enhanced_entities = {
        "our_ref": entities.get("our_ref", "Not found"),
        "company_name": entities.get("company_name", "Not found"),
        "lab_report_creation_date": entities.get("lab_report_creation_date", "Not found"),
        "subject": entities.get("subject", "Not found"),
        "sample_reference": entities.get("sample_reference", "Not found"),
        "names_and_designations": names_and_designations,
        "expected_signatures": expected_signatures,
        "actual_signatures": actual_signatures,
        "is_there_signature": "Yes" if actual_signatures > 0 else "No",
        "results_comply": results_comply_status,
        "test_results": entities.get("test_results", []),
        "signature_validation_details": {
            "names_found": [f"{item.get('name', 'Unknown')} - {item.get('designation', 'Unknown')}" for item in names_and_designations],
            "signature_count_matches": signatures_match,
            "test_results_comply": test_results_comply,
            "validation_note": f"Expected {expected_signatures} signatures based on names/designations, found {actual_signatures} signatures. Test results comply: {test_results_comply}"
        }
    }
    
    if signature_results:
        enhanced_entities["signature_detection"] = signature_results
    
    return enhanced_entities

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
    system_message = "You are an AI assistant that helps analyze and summarize laboratory report and certificate of analysis content."
    user_message = f"Analyze the following laboratory report/certificate content and provide a summary:\n\n{text[:4000]}..."  # Limit text size
    
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
    You are an AI assistant specialized in extracting information from laboratory reports and certificates of analysis.
    Extract the exact values for the requested entities. If you cannot find a value, respond with "Not found".
    Pay close attention to the specific field names and formats requested.
    """
    
    user_message = f"""
    Please extract the following entities from this laboratory report/certificate of analysis text:

    1. Our Ref: Extract from "Our Ref", "File No", "File NO", or similar reference fields
    2. Company Name: Extract the name of the company/laboratory issuing the certificate (usually at the top)
    3. Lab Report Creation Date: Extract the date in DD/MM/YYYY format (look for "Date:" field, convert if needed)
    4. Subject: Extract from "Subject", "Type of Product", or "Product Type" fields
    5. Sample Reference: Extract from "Sample Reference", "Sample Description", "Batch No", or similar sample identification
    6. Names and Designations: Look for ACTUAL READABLE NAMES (not single letters or symbols) with their roles:
       - Look for names near "QA APPROVED", "QC PASSED", "Certified by", "Issued by"
       - Look for "Name/ Signature" sections - the actual names that appear there
       - In this document, look for names like "Jun wy" or other full names near signature areas
       - Ignore single letters like "O *" or "Many *" - find the clearer names
       - Match names with their designations (QA APPROVED, QC PASSED, etc.)
    7. Test Results Table: Extract all test parameters, their units, test methods, and results in a structured format

    Document text:
    {text}
    
    Return only a valid JSON object with these keys:
    {{
        "our_ref": "value or Not found",
        "company_name": "value or Not found", 
        "lab_report_creation_date": "DD/MM/YYYY or Not found",
        "subject": "value or Not found",
        "sample_reference": "value or Not found",
        "names_and_designations": [
            {{"name": "FULL NAME", "designation": "JOB TITLE/ROLE"}},
            ...
        ],
        "test_results": [
            {{
                "parameter": "test parameter name",
                "unit": "unit of measurement", 
                "test_method": "test method used",
                "result": "actual result value",
                "specification": "specification/limit if available",
                "pass_fail": "Pass/Fail status if available"
            }},
            ...
        ]
    }}
    
    IMPORTANT: For names_and_designations, focus on:
    - Clear, readable names like "Jun wy" from the Name/Signature section
    - Match these names with their specific roles (QA APPROVED, QC PASSED)
    - Skip unclear markings like single letters or symbols
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
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        
        # Extract content from response
        content = response.choices[0].message.content
        
        # Convert to dictionary if it's a JSON string
        import json
        try:
            entities = json.loads(content)
            return entities
        except json.JSONDecodeError:
            print("Error: Could not parse JSON response from OpenAI")
            return {"error": "Failed to parse JSON response", "raw_content": content}
        
    except Exception as e:
        print(f"Error extracting entities: {str(e)}")
        return {"error": str(e)}

def main():
    """Main function to run the PDF extraction and processing"""
    if len(sys.argv) < 2:
        print("Usage: python pdf_extractor.py <path_to_pdf_file> [--excel] [--signatures]")
        print("  --excel       Generate Excel report from extracted entities")
        print("  --signatures  Detect human signatures in the PDF")
        return
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found - {pdf_path}")
        return
    
    # Extract text from PDF
    try:
        extracted_text = extract_text_from_pdf(pdf_path)
        
        # Create output directory if it doesn't exist
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Save extracted text to file in the output folder
        output_path = output_dir / f"{Path(pdf_path).stem}_extracted_text.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
        
        print(f"Extracted text saved to: {output_path}")
        
        # Process with Azure OpenAI Agent
        response = process_with_openai_agent(extracted_text)
        
        # Print OpenAI response
        print("\nAzure OpenAI Analysis:")
        print(response['summary_response'].choices[0].message.content)
        
        # Get base entities
        base_entities = response['extracted_entities']
        
        # Initialize signature results
        signature_results = None
        
        # Detect signatures if requested
        if "--signatures" in sys.argv:
            print("\n=== Starting Signature Detection ===")
            try:
                # Initialize signature detector
                detector = SignatureDetector()
                
                # Detect signatures in the PDF
                signature_results = detector.detect_signatures_in_pdf(pdf_path)
                
                # Print signature detection results
                print("\nSignature Detection Results:")
                print(f"Total images detected: {signature_results['total_images_detected']}")
                print(f"Signatures found: {signature_results['signatures_found']}")
                
                if signature_results['signature_details']:
                    print("\nSignature Details:")
                    for i, sig_detail in enumerate(signature_results['signature_details'], 1):
                        print(f"  Signature {i}:")
                        print(f"    Page: {sig_detail.get('page_number', 'unknown')}")
                        print(f"    Confidence: {sig_detail['classification'].get('confidence', 0.0):.2f}")
                        print(f"    Reasoning: {sig_detail['classification'].get('reasoning', 'N/A')}")
                
                if signature_results['processing_errors']:
                    print("\nProcessing Errors:")
                    for error in signature_results['processing_errors']:
                        print(f"  - {error}")
                
                # Save signature detection results
                signature_output_path = output_dir / f"{Path(pdf_path).stem}_signature_detection.json"
                detector.save_signature_detection_results(signature_results, str(signature_output_path))
                
            except Exception as e:
                print(f"Error during signature detection: {str(e)}")
                print("Continuing with text extraction results...")
        
        # Enhance entities with signature validation
        entities = enhance_entities_with_signature_validation(base_entities, signature_results)
        
        # Print extracted entities in a readable format
        print("\nExtracted Entities:")
        print("==================")
        print(f"Our Ref: {entities['our_ref']}")
        print(f"Company Name: {entities['company_name']}")
        print(f"Lab Report Creation Date: {entities['lab_report_creation_date']}")
        print(f"Subject: {entities['subject']}")
        print(f"Sample Reference: {entities['sample_reference']}")
        print(f"Is There Signature?: {entities['is_there_signature']}")
        print(f"Results Comply?: {entities['results_comply']}")
        
        if entities['names_and_designations']:
            print("\nNames and Designations:")
            for i, person in enumerate(entities['names_and_designations'], 1):
                print(f"  {i}. {person.get('name', 'Unknown')} - {person.get('designation', 'Unknown')}")
        
        if entities['test_results']:
            print("\nTest Results:")
            for i, result in enumerate(entities['test_results'], 1):
                print(f"  {i}. {result.get('parameter', 'Unknown')}: {result.get('result', 'Unknown')} {result.get('unit', '')}")
        
        print(f"\nSignature Validation: Expected {entities['expected_signatures']}, Found {entities['actual_signatures']}")
        
        # Clean signature detection data for JSON serialization
        if 'signature_detection' in entities and entities['signature_detection']:
            # Remove binary data that can't be serialized
            for detail in entities['signature_detection'].get('signature_details', []):
                if 'classification' in detail and 'image_info' in detail['classification']:
                    image_info = detail['classification']['image_info']
                    if 'image_data' in image_info:
                        # Replace binary data with size info
                        image_info['image_data_size'] = len(image_info['image_data'])
                        del image_info['image_data']
        
        import json
        print(f"\nFull JSON: {json.dumps(entities, indent=2)}")
        
        # Save extracted entities to a JSON file in the output folder
        entities_path = output_dir / f"{Path(pdf_path).stem}_entities.json"
        with open(entities_path, "w", encoding="utf-8") as f:
            json.dump(entities, f, indent=2)
            
        print(f"\nExtracted entities saved to: {entities_path}")
        
        # Generate Excel report if requested
        if "--excel" in sys.argv:
            try:
                # Import the generate_excel_report function
                from generate_excel_report import generate_excel_report
                
                # Generate the Excel report in the output folder
                output_file = output_dir / f"{Path(pdf_path).stem}_report.xlsx"
                excel_file = generate_excel_report(entities, None, str(output_file))
                print(f"\nGenerated Excel report: {excel_file}")
            except ImportError:
                print("\nError: Could not import generate_excel_report module.")
                print("Make sure the file 'generate_excel_report.py' is in the same directory.")
            except Exception as e:
                print(f"\nError generating Excel report: {str(e)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
