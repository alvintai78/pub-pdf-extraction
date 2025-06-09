#!/bin/zsh

# Script to build and test a Docker image for x86-64 architecture from an ARM Mac
# This is useful for testing before deploying to Azure

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "${GREEN}Setting up Docker Buildx for multi-architecture builds${NC}"
docker buildx create --name mybuilder --use || true
docker buildx inspect --bootstrap

echo "${GREEN}Building Docker image for AMD64 architecture${NC}"
# Build for AMD64 and load it into Docker
docker buildx build --platform linux/amd64 \
  --tag "pdf-extraction-streamlit:test" \
  --load \
  .

echo "${GREEN}Build completed. Testing container...${NC}"
# Run the container with QEMU emulation
docker run --rm -p 8501:8501 pdf-extraction-streamlit:test

echo "${GREEN}Container running at http://localhost:8501${NC}"
echo "Press Ctrl+C to stop the container"
