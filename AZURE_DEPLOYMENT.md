# Deploying to Azure Container Apps

This guide explains how to deploy the PDF Extraction Streamlit application to Azure Container Apps.

## Prerequisites

1. [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed
2. [Docker](https://docs.docker.com/get-docker/) installed
3. Active Azure subscription
4. Azure OpenAI and Azure Document Intelligence services already set up

## Step-by-Step Deployment Process

### 1. Update Azure Environment Variables

Edit the `azure.env` file with your actual Azure service credentials:

```
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=your_azure_openai_deployment_name

# Azure Document Intelligence Configuration
AZURE_DOC_INTELLIGENCE_KEY=your_azure_document_intelligence_key
AZURE_DOC_INTELLIGENCE_ENDPOINT=your_azure_document_intelligence_endpoint
```

### 2. Customize Deployment Settings (Optional)

Open `deploy_to_azure.sh` and customize the following variables if needed:

```bash
RESOURCE_GROUP="pdf-extraction-rg"
LOCATION="eastus"
ACR_NAME="pdfextractionacr"
CONTAINER_APP_NAME="pdf-extraction-app"
CONTAINER_APP_ENV="pdf-extraction-env"
IMAGE_NAME="pdf-extraction-streamlit"
IMAGE_TAG="latest"
```

- `RESOURCE_GROUP`: Name for your Azure resource group
- `LOCATION`: Azure region where resources will be created
- `ACR_NAME`: Name for your Azure Container Registry (must be globally unique)
- `CONTAINER_APP_NAME`: Name for your Container App
- `CONTAINER_APP_ENV`: Name for your Container App Environment
- `IMAGE_NAME`: Name for your Docker image
- `IMAGE_TAG`: Tag for your Docker image version

### 3. Run the Deployment Script

Execute the deployment script:

```bash
./deploy_to_azure.sh
```

This script will:
1. Log you into Azure
2. Create a resource group
3. Create an Azure Container Registry
4. Build and push your Docker image
5. Create a Container Apps environment
6. Deploy your application
7. Output the URL where your app is accessible

### 4. Access Your Application

After deployment completes, you'll see a URL where your application is accessible. Open this URL in your web browser to access your Streamlit app.

## Troubleshooting

### Common Issues

1. **Authentication errors**: Make sure you're logged into Azure CLI with `az login`
2. **ACR name already exists**: Choose a different name for your ACR in the script
3. **Environment variable issues**: Check if your environment variables in azure.env are set correctly
4. **Deployment failures**: Check Azure portal for more detailed error messages

### Viewing Logs

To view logs from your Container App:

```bash
az containerapp logs show --name pdf-extraction-app --resource-group pdf-extraction-rg
```

## Updating the Application

To update your application after making changes:

1. Make your code changes
2. Run the deployment script again:
   ```bash
   ./deploy_to_azure.sh
   ```

## Cost Management

Remember that Azure Container Apps incurs costs. Consider:
- Setting minimum replicas to 0 if you don't need constant availability
- Deleting resources when not needed with:
  ```bash
  az group delete --name pdf-extraction-rg --yes --no-wait
  ```

## Additional Resources

- [Azure Container Apps Documentation](https://docs.microsoft.com/en-us/azure/container-apps/)
- [Streamlit Deployment](https://docs.streamlit.io/knowledge-base/deploy/)
- [Docker Documentation](https://docs.docker.com/)
