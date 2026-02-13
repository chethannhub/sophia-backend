#!/bin/bash

# Build and Deploy Script for News Teller App

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building and deploying News Teller App to GCP${NC}"

# Check if required environment variables are set
if [ -z "$GCP_PROJECT_ID" ]; then
    echo -e "${RED}Error: GCP_PROJECT_ID environment variable is not set${NC}"
    exit 1
fi

# Set image tag (use current timestamp for versioning)
IMAGE_TAG="v$(date +%Y%m%d-%H%M%S)"
IMAGE_NAME="gcr.io/$GCP_PROJECT_ID/news-teller:$IMAGE_TAG"
LATEST_IMAGE="gcr.io/$GCP_PROJECT_ID/news-teller:latest"

echo -e "${YELLOW}Building Docker image for linux/amd64: $IMAGE_NAME${NC}"

# Ensure buildx is available
docker buildx create --use --name news-teller-builder >/dev/null 2>&1 || true

# Build the Docker image for amd64 to match GKE nodes
docker buildx build --platform linux/amd64 -t $IMAGE_NAME -t $LATEST_IMAGE . --push

echo -e "${YELLOW}Pushing image to Google Container Registry...${NC}"

# Images were pushed by buildx above

echo -e "${YELLOW}Updating Kubernetes deployment files...${NC}"

# Update the deployment.yaml with the correct project ID using a safe placeholder
sed "s/__PROJECT_ID__/$GCP_PROJECT_ID/g" deployment.yaml > deployment-updated.yaml

echo -e "${YELLOW}Deploying to Kubernetes...${NC}"

# Apply Kubernetes configurations
kubectl apply -f deployment-updated.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml

echo -e "${YELLOW}Waiting for deployment to be ready...${NC}"

# Wait for deployment to be ready
kubectl rollout status deployment/news-teller-app --timeout=300s

echo -e "${GREEN}Deployment completed successfully!${NC}"

# Get the external IP
echo -e "${YELLOW}Getting service information...${NC}"
kubectl get services news-teller-service

echo -e "${GREEN}Your application is now deployed!${NC}"
echo -e "${YELLOW}To get the external IP address, run:${NC}"
echo "kubectl get services news-teller-service"
echo ""
echo -e "${YELLOW}To check pod status, run:${NC}"
echo "kubectl get pods -l app=news-teller"
echo ""
echo -e "${YELLOW}To view logs, run:${NC}"
echo "kubectl logs -l app=news-teller --tail=100"

# Clean up temporary file
rm -f deployment-updated.yaml
