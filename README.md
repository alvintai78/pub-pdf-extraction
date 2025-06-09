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

### Command Line Usage

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

### Streamlit Web Application

For a user-friendly interface, you can use the Streamlit web application:

```bash
streamlit run streamlit_app.py
```

This will launch a web interface where you can:
1. Upload PDF files through the browser
2. Preview extracted entities and test results
3. Generate and download Excel reports
4. View raw extracted text and JSON data

The Streamlit app provides an intuitive interface for users without technical knowledge to process PDFs and generate reports.

## Output Files

- A text file containing the extracted text (e.g., `EN13945-4_extracted_text.txt`)
- A JSON file containing the extracted entities (e.g., `EN13945-4_entities.json`)
- If requested, an Excel report formatted according to the template (e.g., `EN13945-4_report.xlsx`)
- A summary/analysis of the PDF content displayed in the terminal

## Azure Deployment

This application can be deployed to Azure Container Apps for production use. For detailed deployment instructions, see [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md).

Quick deployment steps:
1. Update environment variables in `azure.env`
2. Run `./deploy_to_azure.sh`
3. Access your app at the URL provided in the output

### Cross-Architecture Deployment (ARM to x86-64)

If you're developing on an ARM-based machine (like Apple Silicon M1/M2/M3/M4) and deploying to Azure's x86-64 environment, please see our [Cross-Architecture Deployment Guide](CROSS_ARCHITECTURE_DEPLOYMENT.md) for important considerations and best practices.

You can test your application for AMD64 compatibility before deployment:
```bash
./build_test_amd64.sh
```

For more details on Azure Container Apps deployment and troubleshooting, refer to the deployment guide.
