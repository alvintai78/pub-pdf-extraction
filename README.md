# PDF Text Extraction with Azure Document Intelligence and OpenAI

This project extracts text from PDF documents using Azure Document Intelligence service and processes the extracted text using Azure OpenAI.

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
python pdf_extractor.py path/to/your/pdf_file.pdf
```

The script will:
1. Extract text from the PDF using Azure Document Intelligence
2. Save the extracted text to a file
3. Process the extracted text using Azure OpenAI
4. Display a summary/analysis of the content

## Example

```bash
python pdf_extractor.py /Users/alvintai/Downloads/PUB/EN13945-4.pdf
```

## Output

- A text file containing the extracted text (e.g., `EN13945-4_extracted_text.txt`)
- A summary/analysis of the PDF content displayed in the terminal
