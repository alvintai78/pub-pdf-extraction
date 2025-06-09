# PDF Text Extraction with Azure Document Intelligence and OpenAI

This project extracts text from PDF documents using Azure Document Intelligence service, processes the extracted text using Azure OpenAI, and generates formatted Excel reports from the extracted data.

## Prerequisites

- Azure Document Intelligence service account
- Azure OpenAI service account
- Python 3.8 or higher

## Setup

1. Clone or download this repository

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `sample.env` and fill in your Azure API keys and endpoints:
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

Run the script with the path to the PDF file you want to process:

```bash
python pdf_extractor.py path/to/your/pdf_file.pdf [--excel]
```

Options:
- `--excel`: Generate an Excel report from the extracted entities

The script will:
1. Extract text from the PDF using Azure Document Intelligence
2. Save the extracted text to a file (e.g., `filename_extracted_text.txt`)
3. Process the extracted text using Azure OpenAI to extract entities
4. Save the extracted entities to a JSON file (e.g., `filename_entities.json`)
5. Display a summary/analysis of the content
6. If `--excel` is specified, generate a formatted Excel report (e.g., `filename_report.xlsx`)

## Examples

Basic extraction:
```bash
python pdf_extractor.py /Users/alvintai/Downloads/PUB/EN13945-4.pdf
```

Extraction with Excel report generation:
```bash
python pdf_extractor.py /Users/alvintai/Downloads/PUB/EN13945-4.pdf --excel
```

You can also generate an Excel report separately from an existing entities JSON file:
```bash
python generate_excel_report.py filename_entities.json [output_filename.xlsx]
```

## Output Files

- A text file containing the extracted text (e.g., `EN13945-4_extracted_text.txt`)
- A JSON file containing the extracted entities (e.g., `EN13945-4_entities.json`)
- If requested, an Excel report formatted according to the template (e.g., `EN13945-4_report.xlsx`)
- A summary/analysis of the PDF content displayed in the terminal
