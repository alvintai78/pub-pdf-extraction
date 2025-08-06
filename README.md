# 🔬 PDF Lab Report Extractor

A comprehensive AI-powered tool for extracting information from PDF laboratory reports and certificates of analysis. Features advanced signature detection, entity extraction, and automated Excel report generation with color-coded status indicators.

## ✨ Features

### 🤖 AI-Powered Extraction
- **Text Extraction**: Advanced PDF text parsing using Azure Document Intelligence
- **Entity Recognition**: Extract key information like company names, dates, test results
- **Structured Output**: Organized JSON format for easy processing

### ✍️ Advanced Signature Detection
- **Computer Vision**: Detect human signatures vs stamps/logos using Azure OpenAI Vision
- **Validation**: Compare expected vs actual signature counts
- **Confidence Scoring**: AI-powered classification with detailed reasoning
- **Type Classification**: Distinguish between full signatures, initials, marks, and stamps

### 📊 Professional Excel Reports
- **Clean Layout**: Professional formatting matching sample templates
- **Color Coding**: Green/red indicators for compliance and signature status
- **Comprehensive Data**: All extracted entities and test results
- **Download Ready**: Formatted for immediate use

### 🌐 Modern Web Interface
- **Streamlit Frontend**: Intuitive, responsive web application
- **Real-time Processing**: Live progress indicators and status updates
- **Multiple Views**: Extracted data, raw text, JSON, and signature details
- **Easy Downloads**: One-click Excel report downloads

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Azure OpenAI API access (with vision-capable models)
- Azure Document Intelligence service

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pdf_extraction
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Azure services**
   ```bash
   cp sample.env azure.env
   # Edit azure.env with your Azure credentials
   ```

### Usage

#### 🌐 Web Interface (Recommended)
```bash
./run_streamlit.sh
# Or manually:
source venv/bin/activate && source azure.env && streamlit run streamlit_app.py
```
**Access at**: http://localhost:8501

#### 💻 Command Line
```bash
# Basic extraction
python pdf_extractor.py sample.pdf

# With signature detection
python pdf_extractor.py sample.pdf --signatures

# Generate Excel report
python pdf_extractor.py sample.pdf --signatures --excel

# Help
python pdf_extractor.py --help
```

## 📁 Project Structure

```
pdf_extraction/
├── 📄 streamlit_app.py          # Modern web interface
├── 🔧 pdf_extractor.py          # Main extraction engine
├── ✍️ signature_detector.py     # AI signature detection
├── 📊 generate_excel_report.py  # Excel generation with colors
├── 🚀 run_streamlit.sh          # Quick start script
├── 📋 requirements.txt          # Python dependencies
├── ⚙️ azure.env                 # Azure service config
├── 📖 README.md                 # This documentation
├── 🎯 sample_output.jpg         # Expected output format
└── 📁 output/                   # Generated reports
```

## 🔧 Configuration

### Environment Variables
Create `azure.env` with your Azure service credentials:

```bash
# Azure OpenAI (Vision-capable model required)
AZURE_OPENAI_API_KEY=your_openai_key
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o  # Must support vision

# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_doc_intel_key
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-doc-intel-resource.cognitiveservices.azure.com/
```

## 📊 Output Formats

### JSON Entities
```json
{
  "our_ref": "CE-8500317108/OYN",
  "company_name": "Setsco Services Pte Ltd",
  "lab_report_creation_date": "18/06/2024",
  "is_there_signature": "Yes",
  "results_comply": "Yes",
  "test_results": [
    {
      "parameter": "pH",
      "unit": "",
      "test_method": "pH meter",
      "result": "4.999",
      "specification": "5 to 9.5",
      "pass_fail": "Fail"
    }
  ],
  "signature_detection": {
    "signatures_found": 2,
    "total_images_detected": 12,
    "signature_details": [...]
  }
}
```

### Excel Report Features
- **Clean Layout**: Professional appearance
- **Color Indicators**: 
  - 🟢 Green: "Yes" status (signatures present, compliance good)
  - 🔴 Red: "No" status (issues detected)
- **Complete Data**: All test results and metadata
- **No Clutter**: Removed unnecessary columns per requirements

## 🎯 Supported Documents

- Laboratory certificates of analysis
- Quality control test reports
- Chemical analysis documents
- Environmental testing reports
- Pharmaceutical testing certificates
- Food safety analysis reports

## 🔍 Signature Detection Capabilities

### Advanced AI Analysis
- **Handwriting Detection**: Identifies flowing, cursive strokes
- **Style Recognition**: Personal signature characteristics
- **Context Validation**: Placement near names/titles
- **Type Classification**: Full signatures vs initials vs stamps

### Validation Features
- **Count Matching**: Expected vs actual signature comparison
- **Confidence Scoring**: 0.0-1.0 confidence levels
- **Detailed Reasoning**: AI explains classification decisions
- **Error Detection**: Identifies processing issues

### Sample Detection Results
```json
{
  "signature_id": "sig_1",
  "page_number": 3,
  "confidence": 0.95,
  "reasoning": "Elaborate, flowing handwritten mark with cursive-like strokes",
  "signature_type": "full_signature",
  "individual_signature_info": {
    "position": "above printed name 'MANAGER'",
    "description": "Flowing handwritten mark in blue ink"
  }
}
```

## 🛠️ Development

### Adding New Features
1. **Entity Types**: Update AI prompts in `pdf_extractor.py`
2. **Output Formats**: Modify Excel templates in `generate_excel_report.py`
3. **UI Components**: Enhance Streamlit interface in `streamlit_app.py`
4. **Detection Logic**: Improve signature algorithms in `signature_detector.py`

### Testing
```bash
# Test with provided samples
python pdf_extractor.py Sample1_low_bromide_salt.pdf --signatures --excel
python pdf_extractor.py Sample2_liquid_oxygen.pdf --signatures --excel

# Standalone Excel generation
python generate_excel_standalone.py output/Sample1_entities.json
```

## 📈 Performance Metrics

- **Text Extraction**: 2-5 seconds per PDF
- **AI Entity Analysis**: 10-15 seconds per document  
- **Signature Detection**: 5-10 seconds per PDF
- **Excel Generation**: 1-2 seconds
- **Total Processing**: ~20-30 seconds end-to-end

## 🚨 Troubleshooting

### Common Issues

#### Import/Installation Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.8+
```

#### Azure Service Issues
- ✅ Verify credentials in `azure.env`
- ✅ Check service endpoints are correct
- ✅ Ensure sufficient API quotas
- ✅ Test connectivity to Azure services

#### PDF Processing Problems
- ✅ Ensure PDF is not password-protected
- ✅ Check file is not corrupted
- ✅ Verify PDF contains extractable text (not just images)
- ✅ Test with provided sample files first

#### Streamlit Web App Issues
```bash
# Clear cache
streamlit cache clear

# Restart with fresh environment
pkill -f streamlit
./run_streamlit.sh
```

#### Signature Detection Issues
- ✅ Ensure using vision-capable Azure OpenAI model (gpt-4o, gpt-4-vision)
- ✅ Check image extraction is working
- ✅ Verify PDF contains actual signature images

### Debug Steps
1. **Test Environment**: `python -c "import azure.ai.documentintelligence, openai; print('OK')"`
2. **Test Credentials**: Check Azure portal for service status
3. **Test Sample Files**: Use provided samples to verify setup
4. **Check Logs**: Review terminal output for detailed error messages

## 🔒 Security & Compliance

### Data Handling
- PDFs processed temporarily, not stored permanently
- Azure services used for processing only
- Generated reports saved locally
- No data transmitted to third parties

### Best Practices
- Keep Azure credentials secure
- Regular rotation of API keys
- Monitor usage and costs
- Follow organizational data policies

## 🌐 Azure Deployment

Ready for production deployment on Azure Container Apps:

```bash
# Deploy to Azure
./deploy_to_azure.sh

# Test cross-architecture compatibility
./build_test_amd64.sh
```

See deployment guides:
- [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md)
- [CROSS_ARCHITECTURE_DEPLOYMENT.md](CROSS_ARCHITECTURE_DEPLOYMENT.md)

## 📝 License

Internal use only. Follow organizational policies for AI service usage and data handling.

## 🤝 Contributing

1. ✅ Test with sample files first
2. ✅ Update documentation for new features
3. ✅ Follow existing code patterns
4. ✅ Add comprehensive error handling
5. ✅ Include unit tests where possible

## 📞 Support

### Getting Help
1. **First Steps**: Check troubleshooting section above
2. **Logs**: Review terminal output for error details
3. **Test Files**: Verify with provided sample PDFs
4. **Documentation**: Read relevant deployment guides

### Reporting Issues
Include:
- Error messages and logs
- PDF file characteristics (if shareable)
- Environment details (OS, Python version)
- Steps to reproduce

---

**Last Updated**: August 2025  
**Version**: 2.0.0 - Complete Rewrite  
**Status**: Production Ready ✅

### Recent Updates (v2.0.0)
- ✨ Advanced signature detection with AI classification
- 🎨 Color-coded Excel reports (green/red status indicators)
- 🌐 Modern Streamlit web interface with real-time processing
- 📊 Enhanced entity extraction with signature validation
- 🚀 One-click deployment scripts
- 📱 Mobile-responsive web interface
- 🔍 Detailed signature analysis and confidence scoring
