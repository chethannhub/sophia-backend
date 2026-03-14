#!/bin/bash

# Script to create Kubernetes secrets for News Teller App

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Creating Kubernetes secrets for News Teller App${NC}"

# Check if required environment variables are set
if [ -z "$GCP_PROJECT_ID" ]; then
    echo -e "${RED}Error: GCP_PROJECT_ID environment variable is not set${NC}"
    exit 1
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    echo -e "${RED}Error: GOOGLE_API_KEY environment variable is not set${NC}"
    exit 1
fi

if [ -z "$GOOGLE_CSE_ID" ]; then
    echo -e "${RED}Error: GOOGLE_CSE_ID environment variable is not set${NC}"
    exit 1
fi

if [ -z "$NEWS_API_KEY" ]; then
    echo -e "${RED}Error: NEWS_API_KEY environment variable is not set${NC}"
    exit 1
fi

if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo -e "${RED}Error: GOOGLE_APPLICATION_CREDENTIALS environment variable is not set${NC}"
    echo "Please set it to the path of your service account JSON file"
    exit 1
fi

if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo -e "${RED}Error: Service account file not found at $GOOGLE_APPLICATION_CREDENTIALS${NC}"
    exit 1
fi

# Create app secrets
echo -e "${YELLOW}Creating application secrets...${NC}"
kubectl create secret generic app-secrets \
  --from-literal=GCP_PROJECT_ID="$GCP_PROJECT_ID" \
  --from-literal=GOOGLE_API_KEY="$GOOGLE_API_KEY" \
  --from-literal=GOOGLE_CSE_ID="$GOOGLE_CSE_ID" \
    --from-literal=NEWS_API_KEY="$NEWS_API_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -

# Create Google Cloud service account secret
echo -e "${YELLOW}Creating Google Cloud service account secret...${NC}"
kubectl create secret generic google-cloud-key \
  --from-file=service-account.json="$GOOGLE_APPLICATION_CREDENTIALS" \
  --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}Secrets created successfully!${NC}"

# Verify secrets
echo -e "${YELLOW}Verifying secrets...${NC}"
kubectl get secrets app-secrets google-cloud-key

echo -e "${GREEN}All secrets are ready for deployment!${NC}"
