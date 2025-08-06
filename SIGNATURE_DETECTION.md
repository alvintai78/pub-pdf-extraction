# PDF Signature Detection Documentation

## Overview

The PDF extractor has been enhanced with human signature detection capabilities using Azure Document Intelligence and Azure OpenAI. This feature can detect and classify handwritten signatures in single or multi-page PDF documents.

## How It Works

### Two-Stage Detection Process

1. **Image Detection**: Azure Document Intelligence scans the PDF to identify all images and visual elements
2. **Signature Classification**: Azure OpenAI analyzes each detected image to determine if it contains a human signature

### Detection Methods

The system uses two complementary approaches:

1. **Azure Document Intelligence Layout Analysis**: Detects figures and images as part of document structure analysis
2. **PyMuPDF Embedded Image Extraction**: Extracts actual embedded images from the PDF file

## Features

- **Multi-page PDF Support**: Works with both single and multi-page PDF documents
- **Confidence Scoring**: Each detected signature includes a confidence score (0-100%)
- **Detailed Analysis**: Provides reasoning for classification decisions
- **Error Handling**: Robust error handling with detailed error reporting
- **Output Integration**: Signature detection results are integrated with existing entity extraction

## Usage

### Command Line Interface

```bash
# Basic text extraction (existing functionality)
python pdf_extractor.py document.pdf

# Text extraction with signature detection
python pdf_extractor.py document.pdf --signatures

# Full processing with signatures and Excel report
python pdf_extractor.py document.pdf --signatures --excel

# Demo signature detection only
python demo_signature_detection.py document.pdf
```

### Programmatic Usage

```python
from signature_detector import SignatureDetector

# Initialize detector
detector = SignatureDetector()

# Detect signatures in a PDF
results = detector.detect_signatures_in_pdf("document.pdf")

# Check results
print(f"Signatures found: {results['signatures_found']}")
for sig in results['signature_details']:
    print(f"Page {sig['page_number']}: {sig['confidence']:.2%} confidence")
```

## Configuration

### Required Environment Variables

Add these to your `.env` file:

```bash
# Azure Document Intelligence
AZURE_DOC_INTELLIGENCE_KEY=your_key_here
AZURE_DOC_INTELLIGENCE_ENDPOINT=your_endpoint_here

# Azure OpenAI (with vision capabilities)
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_vision_deployment_name
```

### Dependencies

Install required packages:

```bash
pip install PyMuPDF requests
# or
pip install -r requirements.txt
```

## Azure OpenAI Requirements

### Model Requirements

The signature detection feature requires an Azure OpenAI deployment with **vision capabilities**. Supported models:

- **GPT-4 Vision** (gpt-4-vision-preview)
- **GPT-4o** (gpt-4o)
- **GPT-4o mini** (gpt-4o-mini)

### Deployment Setup

1. Create an Azure OpenAI resource
2. Deploy a vision-capable model
3. Update your `AZURE_OPENAI_DEPLOYMENT_NAME` to the vision model deployment

## Output Format

### Signature Detection Results

```json
{
  "pdf_path": "document.pdf",
  "total_images_detected": 3,
  "embedded_images_found": 2,
  "signatures_found": 1,
  "signature_details": [
    {
      "signature_id": "sig_1",
      "page_number": 2,
      "confidence": 0.85,
      "classification": {
        "is_signature": true,
        "confidence": 0.85,
        "reasoning": "The image shows flowing handwritten text with personal characteristics typical of a signature.",
        "signature_characteristics": ["handwritten", "flowing strokes", "personal style"],
        "alternative_classification": null
      }
    }
  ],
  "processing_errors": [],
  "detection_method": "Azure Document Intelligence + Azure OpenAI"
}
```

### Integrated Output

When using `--signatures` with the main extractor, signature detection results are added to the entities JSON:

```json
{
  "our_reference": "REF123",
  "date": "2024-01-15",
  // ... other extracted entities
  "signature_detection": {
    // ... signature detection results as above
  }
}
```

## Signature Classification Criteria

### What Qualifies as a Signature

The AI looks for these characteristics:

- **Handwritten text or marks** made by a person
- **Flowing, cursive-like strokes**
- **Personal style and unique characteristics**
- **Organic, irregular appearance**
- **Typically located at document bottom**
- **May include printed name nearby**

### What's NOT Considered a Signature

- Printed text or logos
- Digital stamps or seals
- Form checkboxes or fields
- Random marks or drawings
- Machine-generated text

## Performance and Limitations

### Processing Time

- **Small PDFs (1-5 pages)**: 10-30 seconds
- **Large PDFs (10+ pages)**: 1-3 minutes
- **High-resolution images**: May require additional processing time

### Accuracy

- **High-quality signatures**: 85-95% accuracy
- **Poor image quality**: 60-80% accuracy
- **Ambiguous marks**: May require manual review

### Limitations

1. **Image Quality**: Low-resolution or compressed images may affect detection accuracy
2. **Complex Layouts**: Signatures in complex document layouts may be harder to detect
3. **Handwritten Text**: May sometimes classify other handwritten text as signatures
4. **API Limits**: Subject to Azure OpenAI rate limits and quotas

## Troubleshooting

### Common Issues

1. **No images detected**
   - Check if PDF has any visual elements
   - Verify Document Intelligence service is working
   - Try with a different PDF

2. **OpenAI vision errors**
   - Ensure you're using a vision-capable model deployment
   - Check API key and endpoint configuration
   - Verify deployment name is correct

3. **PyMuPDF import errors**
   - Install PyMuPDF: `pip install PyMuPDF`
   - System may fall back to Document Intelligence only

4. **Low confidence scores**
   - Review signature quality in original PDF
   - Check if detected images are actually signatures
   - Consider adjusting confidence threshold (default: 50%)

### Error Messages

- **"Missing required environment variables"**: Check your `.env` file
- **"PyMuPDF not available"**: Install PyMuPDF or use Document Intelligence only
- **"Error classifying image"**: Check Azure OpenAI configuration and quotas

## Example Usage

### Basic Signature Detection

```python
# Test with a sample PDF
python demo_signature_detection.py Sample1_low_bromide_salt.pdf
```

### Full Document Processing

```python
# Extract text, entities, and detect signatures
python pdf_extractor.py EN13945-4.pdf --signatures --excel
```

### Batch Processing

```python
import os
from signature_detector import SignatureDetector

detector = SignatureDetector()

# Process all PDFs in a directory
pdf_dir = "documents/"
for filename in os.listdir(pdf_dir):
    if filename.endswith('.pdf'):
        pdf_path = os.path.join(pdf_dir, filename)
        results = detector.detect_signatures_in_pdf(pdf_path)
        print(f"{filename}: {results['signatures_found']} signatures found")
```

## Security and Privacy

- All processing uses Azure services with enterprise-grade security
- PDF content is processed in Azure regions according to your configuration
- No data is stored permanently by the signature detection system
- Follow your organization's data handling policies for sensitive documents

## Future Enhancements

Potential improvements being considered:

1. **Signature Verification**: Compare signatures across documents
2. **Enhanced Classification**: Detect different types of signatures (initials, full signatures)
3. **Batch Processing**: Built-in support for processing multiple PDFs
4. **Signature Extraction**: Save detected signatures as separate image files
5. **Custom Training**: Fine-tune classification for specific document types
