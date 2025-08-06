#!/bin/zsh

# Quick update script for existing Azure Container App deployment
# This rebuilds the image and updates the container app with latest code

# Variables (matching your existing deployment)
RESOURCE_GROUP="pdf-extraction-rg"
ACR_NAME="pdfextractionacr"
CONTAINER_APP_NAME="pdf-extraction-app"
IMAGE_NAME="pdf-extraction-streamlit"
# Use timestamp to force new deployment
IMAGE_TAG="$(date +%Y%m%d-%H%M%S)"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "${GREEN}🚀 PDF Extraction App - Quick Update Deployment${NC}"
echo "================================================="

# Check Azure login
echo "${GREEN}Step 1: Checking Azure login status${NC}"
az account show &>/dev/null
if [ $? -ne 0 ]; then
  echo "${YELLOW}Not logged in to Azure. Initiating login...${NC}"
  az login
  if [ $? -ne 0 ]; then
    echo "${RED}Azure login failed. Please login manually and try again.${NC}"
    exit 1
  fi
else
  echo "${GREEN}✅ Already logged in to Azure.${NC}"
fi

# Check Docker daemon
echo "${GREEN}Step 2: Checking Docker daemon status${NC}"
if ! docker info > /dev/null 2>&1; then
  echo "${RED}❌ Docker daemon is not running. Please start Docker Desktop.${NC}"
  exit 1
else
  echo "${GREEN}✅ Docker daemon is running.${NC}"
fi

# Get ACR credentials
echo "${GREEN}Step 3: Getting ACR credentials${NC}"
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

if [ -z "$ACR_USERNAME" ] || [ -z "$ACR_PASSWORD" ]; then
  echo "${RED}❌ Failed to retrieve ACR credentials.${NC}"
  exit 1
else
  echo "${GREEN}✅ ACR credentials retrieved.${NC}"
fi

# Login to ACR
echo "${GREEN}Step 4: Logging into ACR${NC}"
echo "$ACR_PASSWORD" | docker login "$ACR_NAME.azurecr.io" --username "$ACR_USERNAME" --password-stdin
if [ $? -ne 0 ]; then
  echo "${RED}❌ Failed to login to ACR.${NC}"
  exit 1
else
  echo "${GREEN}✅ Successfully logged into ACR.${NC}"
fi

# Build new image with latest changes
echo "${GREEN}Step 5: Building updated Docker image${NC}"
docker build --platform linux/amd64 -t "$ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG" .
if [ $? -ne 0 ]; then
  echo "${RED}❌ Docker build failed.${NC}"
  exit 1
else
  echo "${GREEN}✅ Docker image built successfully.${NC}"
fi

# Push updated image
echo "${GREEN}Step 6: Pushing updated image to ACR${NC}"
docker push "$ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG"
if [ $? -ne 0 ]; then
  echo "${RED}❌ Failed to push image to ACR.${NC}"
  exit 1
else
  echo "${GREEN}✅ Image pushed successfully.${NC}"
fi

# Update Container App
echo "${GREEN}Step 7: Updating Container App with new image${NC}"
echo "${YELLOW}Using image tag: $IMAGE_TAG${NC}"
echo "${YELLOW}Full image name: $ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG${NC}"

az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --image "$ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG"

if [ $? -ne 0 ]; then
  echo "${RED}❌ Failed to update Container App.${NC}"
  exit 1
else
  echo "${GREEN}✅ Container App updated successfully.${NC}"
  
  # Wait a moment for the update to process
  echo "${YELLOW}⏳ Waiting for deployment to process...${NC}"
  sleep 10
  
  # Check if a new revision was created
  echo "${GREEN}Checking new revision...${NC}"
  az containerapp revision list --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "[?properties.active].{name:name,createdTime:properties.createdTime,image:properties.template.containers[0].image}" --output table
fi

# Get app URL
echo "${GREEN}Step 8: Getting app URL${NC}"
APP_URL=$(az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  -o tsv)

echo ""
echo "${GREEN}🎉 Update completed successfully!${NC}"
echo "${GREEN}📱 Your updated app is available at: https://$APP_URL${NC}"
echo ""
echo "${YELLOW}📋 Changes included in this update:${NC}"
echo "  ✅ Modified 'Results Comply' logic based on test results"
echo "  ✅ Removed names and designations from Streamlit display"
echo "  ✅ Added Pass/Fail column back to test results table"
echo "  ✅ All latest bug fixes and improvements"
echo ""
echo "${GREEN}The app should be available in a few minutes as the new containers start up.${NC}"
