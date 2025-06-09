#!/bin/zsh

# Script to validate and test azure.env environment variables

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ENV_FILE="azure.env"

echo "${YELLOW}Validating $ENV_FILE format...${NC}"

if [ ! -f "$ENV_FILE" ]; then
    echo "${RED}Error: File $ENV_FILE not found!${NC}"
    exit 1
fi

# Check for common formatting issues
errors=0

# Check each line
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip comments and empty lines
    [[ "$line" =~ ^#.*$ ]] && continue
    [[ -z "$line" ]] && continue
    
    # Check for spaces around equals sign
    if [[ "$line" == *" ="* || "$line" == *"= "* ]]; then
        echo "${RED}Error: Line contains spaces around equals sign: ${line}${NC}"
        echo "       Should be: ${line// =/=}"
        echo "                  ${line//= /=}"
        errors=$((errors+1))
    fi
    
    # Check if line has equals sign
    if [[ ! "$line" == *"="* ]]; then
        echo "${RED}Error: Line does not contain equals sign: ${line}${NC}"
        errors=$((errors+1))
    fi
    
    # Check for quotes
    if [[ "$line" == *\"* ]]; then
        echo "${YELLOW}Warning: Line contains quotes which may cause issues: ${line}${NC}"
    fi
    
done < "$ENV_FILE"

if [ $errors -gt 0 ]; then
    echo "${RED}Found $errors error(s) in $ENV_FILE. Please fix before deployment.${NC}"
    echo "See ENV_SETUP_GUIDE.md for proper formatting instructions."
else
    echo "${GREEN}No formatting errors found in $ENV_FILE.${NC}"
    
    # Test loading the environment variables
    echo "${YELLOW}Testing environment variables...${NC}"
    
    # Create a temporary script to load and print variable names
    temp_script=$(mktemp)
    echo '#!/bin/zsh' > "$temp_script"
    echo 'set -a' >> "$temp_script"
    echo '. ./azure.env' >> "$temp_script"
    echo 'set +a' >> "$temp_script"
    echo 'echo "Successfully loaded these environment variables:"' >> "$temp_script"
    echo 'env | grep -E "AZURE_(OPENAI|DOC)" | cut -d= -f1' >> "$temp_script"
    
    # Make it executable
    chmod +x "$temp_script"
    
    # Run it
    "$temp_script"
    
    # Clean up
    rm "$temp_script"
    
    echo "${GREEN}Environment variables validation complete.${NC}"
    echo "${YELLOW}Note: This script only checks the format, not if the values are correct.${NC}"
    echo "${YELLOW}Make sure your API keys and endpoints are correct before deployment.${NC}"
fi
