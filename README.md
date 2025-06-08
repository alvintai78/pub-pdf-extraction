# PDF Text Extraction with Azure Document Intelligence and OpenAI

This project extracts text from PDF documents using Azure Document Intelligence service and processes the extracted text using Azure OpenAI. It also extracts specific entities from laboratory reports.

## Prerequisites

- Azure Document Intelligence service account
- Azure OpenAI service account
- Python 3.8 or higher

## Setup

1. Clone or download this repository

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `sample.env` and fill in your Azure API keys and endpoints:
   ```
   # Azure OpenAI Configuration
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
   AZURE_OPENAI_DEPLOYMENT_NAME=your_azure_openai_deployment_name

   # Azure Document Intelligence Configuration
   AZURE_DOC_INTELLIGENCE_KEY=your_azure_document_intelligence_key
   AZURE_DOC_INTELLIGENCE_ENDPOINT=your_azure_document_intelligence_endpoint
   ```

## Usage

### Basic Text Extraction

Run the script with the path to the PDF file you want to process:

```bash
python pdf_extractor.py path/to/your/pdf_file.pdf
```

The script will:
1. Extract text from the PDF using Azure Document Intelligence
2. Save the extracted text to a file (e.g., `filename_extracted_text.txt`)
3. Process the extracted text using Azure OpenAI
4. Extract specific entities from the document
5. Display a summary/analysis of the content
6. Save extracted entities to a JSON file (e.g., `filename_entities.json`)

### Using Extracted Entities

The `use_entities.py` utility script provides a way to display the extracted entities in a formatted report:

```bash
python use_entities.py filename_entities.json
```

## Example

```bash
python pdf_extractor.py /Users/alvintai/Downloads/PUB/EN13945-4.pdf
python use_entities.py EN13945-4_entities.json
```

## Output Files

- A text file containing the extracted text (e.g., `EN13945-4_extracted_text.txt`)
- A JSON file containing the extracted entities (e.g., `EN13945-4_entities.json`)
- A summary/analysis of the PDF content displayed in the terminal

## Extracted Entities

The following entities are extracted from laboratory reports:

1. **our_reference**: The "Our Ref" value
2. **date**: The "Date" value
3. **subject**: The full subject text
4. **sample_reference**: The full sample reference description
5. **sampling_date_time**: The date and time in brackets in the sample reference
6. **sample_officer_incharge**: The person with Chemist job title
7. **sampling_catchment**: The word in brackets at "Tested For" section
8. **test_parameters**: List of test parameters
9. **units**: List of units corresponding to test parameters
10. **test_methods**: List of test methods used
11. **results**: List of test results
