#!/bin/zsh

# Azure deployment script for Streamlit PDF Extraction app

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

echo "${GREEN}Step 1: Checking Azure login status${NC}"
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

# Create Resource Group
echo "${GREEN}Step 2: Creating Resource Group${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo "${GREEN}Step 3: Creating Azure Container Registry${NC}"
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# Ensure admin is enabled on ACR
echo "${GREEN}Step 4: Enabling admin on ACR${NC}"
az acr update --name $ACR_NAME --admin-enabled true

# Get fresh ACR credentials
echo "${GREEN}Step 5: Getting fresh ACR credentials${NC}"
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# Verify credentials were retrieved successfully
if [ -z "$ACR_USERNAME" ] || [ -z "$ACR_PASSWORD" ]; then
  echo "${RED}Failed to retrieve ACR credentials. Trying alternative approach...${NC}"
  
  # Get Azure subscription ID
  SUBSCRIPTION_ID=$(az account show --query id -o tsv)
  
  # Get ACR registry ID
  ACR_REGISTRY_ID=$(az acr show --name $ACR_NAME --query id -o tsv)
  
  # Assign AcrPush role to the current user
  echo "${GREEN}Assigning AcrPush role to your user...${NC}"
  USER_ID=$(az ad signed-in-user show --query id -o tsv)
  az role assignment create --assignee $USER_ID --scope $ACR_REGISTRY_ID --role AcrPush
  
  # Try to get credentials again
  ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
  ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)
  
  if [ -z "$ACR_USERNAME" ] || [ -z "$ACR_PASSWORD" ]; then
    echo "${RED}Still unable to retrieve ACR credentials. Please check your Azure permissions.${NC}"
    exit 1
  fi
fi

# Force logout from ACR if already logged in
echo "${GREEN}Step 6: Ensuring clean Docker login state${NC}"
docker logout "$ACR_NAME.azurecr.io" 2>/dev/null

# Login to ACR with fresh credentials
echo "${GREEN}Step 7: Logging into ACR with fresh credentials${NC}"
echo $ACR_PASSWORD | docker login "$ACR_NAME.azurecr.io" --username $ACR_USERNAME --password-stdin

# Check if login was successful
if [ $? -ne 0 ]; then
  echo "${YELLOW}Standard Docker login failed. Trying alternative authentication method...${NC}"
  az acr login --name $ACR_NAME
  
  if [ $? -ne 0 ]; then
    echo "${RED}All ACR authentication methods failed. Please check your network and permissions.${NC}"
    exit 1
  fi
fi

# Check Docker daemon status
echo "${GREEN}Step 6: Checking Docker daemon status${NC}"
if ! docker info > /dev/null 2>&1; then
  echo "${RED}Error: Docker daemon is not running. Please start Docker Desktop or Docker service.${NC}"
  echo "You can start Docker Desktop from the Applications folder or run 'open -a Docker' in Terminal."
  echo "Exiting deployment script."
  exit 1
fi

# Build and push Docker image using standard Docker commands
echo "${GREEN}Step 7: Building and pushing Docker image${NC}"
# Using standard Docker build since buildx might not be available on all systems
docker build --platform linux/amd64 -t "$ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG" .
if [ $? -ne 0 ]; then
  echo "${RED}Docker build failed. Trying alternative build method...${NC}"
  # Fallback to standard build without platform specification
  docker build -t "$ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG" .
fi

# Push the image to ACR
echo "${GREEN}Pushing image to ACR${NC}"
docker push "$ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG"

# Create Container App Environment
echo "${GREEN}Step 8: Creating Container App Environment${NC}"
az containerapp env create \
  --name $CONTAINER_APP_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Create Container App
echo "${GREEN}Step 9: Creating Container App${NC}"
echo "${GREEN}Reading environment variables from azure.env${NC}"

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

# Format env vars properly
ENV_VARS_PARAM=""
if [ ${#ENV_VARS_ARRAY[@]} -gt 0 ]; then
    ENV_VARS_PARAM="--env-vars"
fi

# Make sure Azure has access to ACR
echo "${GREEN}Ensuring ACR access for Container Apps...${NC}"
az acr update --name $ACR_NAME --admin-enabled true

# Get updated ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# Create the container app with proper authentication
echo "${GREEN}Creating Container App with authenticated ACR access...${NC}"
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

echo "${GREEN}Deployment completed.${NC}"
if [ -n "$APP_URL" ]; then
  echo "${GREEN}Your Streamlit app is available at: https://$APP_URL ${NC}"
else
  echo "${YELLOW}Container App created, but couldn't retrieve URL automatically.${NC}"
  echo "${YELLOW}Check your Azure portal to find the URL for your Container App.${NC}"
fi
