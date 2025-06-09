# Setting Up Environment Variables for Azure Deployment

This document explains how to properly set up your `azure.env` file for deployment to Azure Container Apps.

## Understanding the `azure.env` File

The `azure.env` file contains environment variables that will be passed to your container in Azure Container Apps. These variables include API keys and endpoints required for your application to connect to Azure services.

## Proper Format

Each environment variable should be set on a separate line in the format:

```
KEY_NAME=value
```

- No spaces before or after the equals sign
- No quotes around values unless they're part of the value itself
- No spaces or special characters in the key name
- Comments start with `#` and are ignored

## Example of a Correctly Formatted `azure.env` File

```
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=abc123def456ghi789jkl
AZURE_OPENAI_ENDPOINT=https://your-openai-instance.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=your-model-deployment

# Azure Document Intelligence Configuration
AZURE_DOC_INTELLIGENCE_KEY=xyz987abc654def321ghi
AZURE_DOC_INTELLIGENCE_ENDPOINT=https://your-doc-instance.cognitiveservices.azure.com
```

## Steps to Set Up Your Environment Variables

1. **Get Your API Keys and Endpoints**
   - Azure OpenAI: From Azure Portal → Your OpenAI resource → Keys and Endpoint
   - Document Intelligence: From Azure Portal → Your Document Intelligence resource → Keys and Endpoint

2. **Update the `azure.env` File**
   - Replace the placeholder values with your actual keys and endpoints
   - Make sure there are no extra spaces or quotes
   - Save the file

3. **Test Locally (Optional)**
   - You can test these environment variables locally by running:
     ```
     export $(grep -v '^#' azure.env | xargs)
     python streamlit_app.py
     ```

## Troubleshooting

If you encounter errors related to environment variables:

1. **Check Format**: Ensure each line follows the KEY=value format without spaces
2. **Check for Special Characters**: Remove any quotes, spaces, or special characters
3. **Verify Keys**: Double-check that your API keys and endpoints are correct
4. **File Encoding**: Ensure the file is saved with UTF-8 encoding without BOM

## Security Note

The `azure.env` file contains sensitive information. Make sure to:

1. **Never commit it to public repositories**
2. **Add it to your `.gitignore` file**
3. **Consider using Azure Key Vault for production deployments**

For more information on securing your environment variables in Azure Container Apps, see the [official documentation](https://learn.microsoft.com/en-us/azure/container-apps/secure-your-app).
