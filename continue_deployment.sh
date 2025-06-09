#!/bin/zsh

# Script to continue deployment after successful image push
# This picks up where fix_acr_auth.sh left off

# Variables (you'll need to customize these)
RESOURCE_GROUP="pdf-extraction-rg"
LOCATION="australiaeast"
ACR_NAME="pdfextractionacr"
CONTAINER_APP_NAME="pdf-extraction-app"
CONTAINER_APP_ENV="pdf-extraction-env"
IMAGE_NAME="pdf-extraction-streamlit"
IMAGE_TAG="latest"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "${GREEN}Checking Azure login status${NC}"
# Check if already logged in
az account show &>/dev/null
if [ $? -ne 0 ]; then
  echo "${YELLOW}Not logged in to Azure. Initiating login...${NC}"
  az login
  # Check if login was successful
  if [ $? -ne 0 ]; then
    echo "${RED}Azure login failed. Please login manually and try again.${NC}"
    exit 1
  fi
else
  echo "${GREEN}Already logged in to Azure.${NC}"
fi

# Verify image exists in ACR
echo "${GREEN}Verifying image exists in ACR...${NC}"
az acr repository show --name $ACR_NAME --repository $IMAGE_NAME > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "${RED}Error: Image $IMAGE_NAME not found in ACR $ACR_NAME.${NC}"
  echo "${YELLOW}Please run ./fix_acr_auth.sh first to build and push the image.${NC}"
  exit 1
fi

# Get ACR credentials
echo "${GREEN}Getting ACR credentials${NC}"
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# Create Container App Environment
echo "${GREEN}Creating Container App Environment${NC}"
az containerapp env create \
  --name $CONTAINER_APP_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Read environment variables from file
echo "${YELLOW}Parsing environment variables from azure.env...${NC}"
ENV_VARS_ARRAY=()
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip comments and empty lines
    [[ "$line" =~ ^#.*$ ]] && continue
    [[ -z "$line" ]] && continue
    
    # Split into key and value
    if [[ $line == *"="* ]]; then
        key=$(echo "$line" | cut -d '=' -f 1)
        value=$(echo "$line" | cut -d '=' -f 2-)
        
        # Add to array in the correct format for --env-vars
        ENV_VARS_ARRAY+=("$key=$value")
    fi
done < azure.env

# Make sure Azure has access to ACR
echo "${GREEN}Ensuring ACR access for Container Apps...${NC}"
az acr update --name $ACR_NAME --admin-enabled true

# Display environment variables that will be used (safe for display without actual values)
echo "${YELLOW}Environment variables to be set:${NC}"
for var in "${ENV_VARS_ARRAY[@]}"; do
    key=$(echo "$var" | cut -d '=' -f 1)
    echo "  - $key"
done

# Create the container app
if [ ${#ENV_VARS_ARRAY[@]} -gt 0 ]; then
    echo "${GREEN}Creating Container App with ${#ENV_VARS_ARRAY[@]} environment variables...${NC}"
    az containerapp create \
      --name $CONTAINER_APP_NAME \
      --resource-group $RESOURCE_GROUP \
      --environment $CONTAINER_APP_ENV \
      --image "$ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG" \
      --registry-server "$ACR_NAME.azurecr.io" \
      --registry-username $ACR_USERNAME \
      --registry-password "$ACR_PASSWORD" \
      --env-vars "${ENV_VARS_ARRAY[@]}" \
      --target-port 8501 \
      --ingress external \
      --min-replicas 1 \
      --max-replicas 3 \
      --cpu 1.0 \
      --memory 2.0Gi
else
    echo "${YELLOW}No environment variables found in azure.env. Creating Container App without environment variables...${NC}"
    az containerapp create \
      --name $CONTAINER_APP_NAME \
      --resource-group $RESOURCE_GROUP \
      --environment $CONTAINER_APP_ENV \
      --image "$ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG" \
      --registry-server "$ACR_NAME.azurecr.io" \
      --registry-username $ACR_USERNAME \
      --registry-password "$ACR_PASSWORD" \
      --target-port 8501 \
      --ingress external \
      --min-replicas 1 \
      --max-replicas 3 \
      --cpu 1.0 \
      --memory 2.0Gi
fi

# Get the Container App URL
echo "${GREEN}Getting Container App URL...${NC}"
APP_URL=$(az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  -o tsv)

# Output final results
echo "${GREEN}Deployment completed.${NC}"
if [ -n "$APP_URL" ]; then
  echo "${GREEN}Your Streamlit app is available at: https://$APP_URL ${NC}"
else
  echo "${YELLOW}Container App created, but couldn't retrieve URL automatically.${NC}"
  echo "${YELLOW}Check your Azure portal to find the URL for your Container App.${NC}"
fi
