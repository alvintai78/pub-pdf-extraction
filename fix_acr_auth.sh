#!/bin/zsh

# Script to fix ACR authentication and push Docker image

# Variables - make sure these match your deploy_to_azure.sh values
RESOURCE_GROUP="pdf-extraction-rg"
ACR_NAME="pdfextractionacr"
IMAGE_NAME="pdf-extraction-streamlit"
IMAGE_TAG="latest"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
echo "${GREEN}Checking if Docker is running...${NC}"
if ! docker info > /dev/null 2>&1; then
  echo "${RED}Error: Docker daemon is not running. Please start Docker Desktop.${NC}"
  exit 1
fi

# Ensure logged into Azure
echo "${GREEN}Checking Azure login...${NC}"
if ! az account show > /dev/null 2>&1; then
  echo "${YELLOW}Not logged in to Azure. Logging in...${NC}"
  az login
fi

# Ensure ACR exists
echo "${GREEN}Checking if ACR exists...${NC}"
if ! az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP > /dev/null 2>&1; then
  echo "${RED}Error: ACR $ACR_NAME does not exist in resource group $RESOURCE_GROUP.${NC}"
  echo "${YELLOW}Make sure the ACR name and resource group are correct.${NC}"
  exit 1
fi

# Enable admin on ACR if not already enabled
echo "${GREEN}Ensuring admin is enabled on ACR...${NC}"
az acr update --name $ACR_NAME --admin-enabled true

# Refresh ACR credentials
echo "${GREEN}Getting fresh ACR credentials...${NC}"
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

if [ -z "$ACR_USERNAME" ] || [ -z "$ACR_PASSWORD" ]; then
  echo "${RED}Failed to retrieve ACR credentials.${NC}"
  exit 1
fi

# Force a re-login to ACR
echo "${GREEN}Logging out of ACR (if already logged in)...${NC}"
docker logout "$ACR_NAME.azurecr.io" 2>/dev/null

echo "${GREEN}Logging into ACR with fresh credentials...${NC}"
echo $ACR_PASSWORD | docker login "$ACR_NAME.azurecr.io" --username $ACR_USERNAME --password-stdin

if [ $? -ne 0 ]; then
  echo "${RED}Failed to authenticate with ACR.${NC}"
  echo "${YELLOW}Trying alternative authentication method...${NC}"
  
  # Get Azure subscription ID
  SUBSCRIPTION_ID=$(az account show --query id -o tsv)
  
  # Create a service principal and assign it the AcrPush role
  echo "${GREEN}Creating service principal for ACR access...${NC}"
  ACR_REGISTRY_ID=$(az acr show --name $ACR_NAME --query id -o tsv)
  
  echo "${GREEN}Assigning AcrPush role to your user...${NC}"
  USER_ID=$(az ad signed-in-user show --query id -o tsv)
  az role assignment create --assignee $USER_ID --scope $ACR_REGISTRY_ID --role AcrPush
  
  # Login to ACR using az acr login
  echo "${GREEN}Logging in with az acr login...${NC}"
  az acr login --name $ACR_NAME
fi

# Build and tag the Docker image
echo "${GREEN}Building Docker image...${NC}"
docker build -t "$ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG" .

if [ $? -ne 0 ]; then
  echo "${RED}Docker build failed.${NC}"
  exit 1
fi

# Push the image to ACR
echo "${GREEN}Pushing image to ACR...${NC}"
docker push "$ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG"

if [ $? -ne 0 ]; then
  echo "${RED}Failed to push image to ACR.${NC}"
  echo "${YELLOW}Debugging information:${NC}"
  echo "ACR Username: $ACR_USERNAME"
  echo "Docker images:"
  docker images
  echo "Docker login status:"
  docker info | grep Registry
  exit 1
else
  echo "${GREEN}Successfully pushed image to ACR!${NC}"
  echo "${YELLOW}You can now continue with the Container App deployment:${NC}"
  echo "./deploy_to_azure.sh"
fi
