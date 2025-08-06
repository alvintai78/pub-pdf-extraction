#!/bin/zsh

# Script to update environment variables for existing Container App
# This updates the Container App with current azure.env values

# Variables
RESOURCE_GROUP="pdf-extraction-rg"
CONTAINER_APP_NAME="pdf-extraction-app"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "${GREEN}🔧 Updating Container App Environment Variables${NC}"
echo "============================================="

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

# Read environment variables from azure.env
echo "${GREEN}Step 2: Reading environment variables from azure.env${NC}"
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

# Display environment variables that will be updated
echo "${YELLOW}Environment variables to be updated:${NC}"
for var in "${ENV_VARS_ARRAY[@]}"; do
    key=$(echo "$var" | cut -d '=' -f 1)
    echo "  - $key"
done

# Update Container App with new environment variables
echo "${GREEN}Step 3: Updating Container App environment variables${NC}"
if [ ${#ENV_VARS_ARRAY[@]} -gt 0 ]; then
    az containerapp update \
      --name $CONTAINER_APP_NAME \
      --resource-group $RESOURCE_GROUP \
      --set-env-vars "${ENV_VARS_ARRAY[@]}"
    
    if [ $? -ne 0 ]; then
      echo "${RED}❌ Failed to update environment variables.${NC}"
      exit 1
    else
      echo "${GREEN}✅ Environment variables updated successfully.${NC}"
    fi
else
    echo "${YELLOW}No environment variables found in azure.env.${NC}"
    exit 1
fi

# Get app URL
APP_URL=$(az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  -o tsv)

echo ""
echo "${GREEN}🎉 Environment variables updated successfully!${NC}"
echo "${GREEN}📱 Your app: https://$APP_URL${NC}"
echo "${GREEN}The changes will take effect when the app restarts.${NC}"
