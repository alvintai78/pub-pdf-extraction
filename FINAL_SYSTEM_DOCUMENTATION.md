# PDF Extraction System with Signature Detection and Entity Validation

## Overview

This enhanced PDF extraction system combines text extraction, entity identification, signature detection, and validation to provide comprehensive analysis of laboratory reports and certificates of analysis.

## Key Features

### 1. Text Extraction
- Extracts text from PDF files using PyMuPDF
- Handles multi-page documents
- Preserves layout structure where possible

### 2. Entity Extraction
The system extracts the following entities from laboratory reports:

- **Our Ref**: Reference number or file number
- **Company Name**: Laboratory or issuing company
- **Lab Report Creation Date**: Date of report creation
- **Subject**: Product or material being tested
- **Sample Reference**: Batch numbers, sample IDs, etc.
- **Names and Designations**: People who certified/signed the document
- **Test Results**: All test parameters with results, specifications, and pass/fail status

### 3. Signature Detection
- Uses Azure Document Intelligence to detect images in PDFs
- Extracts embedded images using PyMuPDF as backup
- Uses Azure OpenAI (GPT-4V) to classify images as signatures
- Distinguishes between:
  - **Full signatures**: Complete handwritten names with flowing strokes
  - **Initials**: Simple marks or abbreviations
  - **Stamps/logos**: Non-handwritten marks
- Counts only "full signatures" for validation

### 4. Signature Validation
- Compares expected signatures (based on names/designations) with detected signatures
- Automatically infers missing names from signature detection when possible
- Provides validation results:
  - **Is There Signature?**: Yes/No based on actual signature count
  - **Results Comply?**: Yes/No based on signature count matching expectations

## Usage

### Basic Usage
```bash
python3 pdf_extractor.py <pdf_file>
```

### With Signature Detection
```bash
python3 pdf_extractor.py <pdf_file> --signatures
```

## Output Format

The system produces a comprehensive JSON output containing:

```json
{
  "our_ref": "Reference number",
  "company_name": "Company name",
  "lab_report_creation_date": "DD/MM/YYYY",
  "subject": "Product/material",
  "sample_reference": "Sample identifiers",
  "names_and_designations": [
    {"name": "Person Name", "designation": "Role/Title"}
  ],
  "expected_signatures": 2,
  "actual_signatures": 2,
  "is_there_signature": "Yes",
  "results_comply": "Yes",
  "test_results": [
    {
      "parameter": "Test name",
      "unit": "Units",
      "test_method": "Method",
      "result": "Result value",
      "specification": "Requirement",
      "pass_fail": "Pass/Fail"
    }
  ],
  "signature_validation_details": {
    "names_found": ["Name - Role"],
    "signature_count_matches": true,
    "validation_note": "Validation details"
  },
  "signature_detection": {
    "signatures_found": 2,
    "signature_details": [...]
  }
}
```

## Test Results

### Sample2_liquid_oxygen.pdf
- **Signatures Found**: 2 full signatures (LimmyT, Jen Wy)
- **Names Extracted**: Jun wy (QA APPROVED), Limuyt (QC PASSED - inferred)
- **Validation**: ✅ Expected 2, Found 2
- **Results Comply**: Yes

### Sample1_low_bromide_salt.pdf  
- **Signatures Found**: 2 full signatures
- **Names Extracted**: IRENE DI (SENIOR CHEMIST), OOI YEN NEE (MANAGER)
- **Validation**: ✅ Expected 2, Found 2
- **Results Comply**: Yes

## Key Improvements

1. **Intelligent Name Inference**: When signature detection finds more signatures than names extracted from text, the system attempts to infer missing names from signature analysis.

2. **Type-Based Counting**: Only counts "full_signature" types, ignoring initials and stamps for validation.

3. **Robust Error Handling**: Handles JSON serialization, missing fields, and various document formats.

4. **Comprehensive Validation**: Provides detailed validation information including mismatch explanations.

## Technical Stack

- **Text Extraction**: PyMuPDF (fitz)
- **Image Detection**: Azure Document Intelligence, PyMuPDF
- **AI Analysis**: Azure OpenAI (GPT-4 with vision)
- **Output**: JSON format with comprehensive validation details

## Future Enhancements

1. **Date Normalization**: Standardize date formats across documents
2. **Enhanced Name Matching**: Improve correlation between detected and extracted names
3. **Multi-language Support**: Support for documents in different languages
4. **Batch Processing**: Process multiple PDFs simultaneously
5. **Web Interface**: Add a web-based interface for easier usage

## Dependencies

- azure-ai-documentintelligence
- openai
- PyMuPDF
- python-dotenv
- Pillow
- requests

See `requirements.txt` for complete dependency list.
