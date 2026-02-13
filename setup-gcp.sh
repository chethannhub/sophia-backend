#!/bin/bash

# GCP Setup Script for News Teller App
# This script sets up the initial GCP infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up GCP infrastructure for News Teller App${NC}"

# Check if required environment variables are set
if [ -z "$GCP_PROJECT_ID" ]; then
    echo -e "${RED}Error: GCP_PROJECT_ID environment variable is not set${NC}"
    echo "Please set it with: export GCP_PROJECT_ID=your-project-id"
    exit 1
fi

if [ -z "$GCP_REGION" ]; then
    echo -e "${YELLOW}GCP_REGION not set, using default: us-central1${NC}"
    export GCP_REGION="us-central1"
fi

# Prefer a single-zone cluster to minimize regional SSD quota usage
if [ -z "$GCP_ZONE" ]; then
    echo -e "${YELLOW}GCP_ZONE not set, using default: ${GCP_REGION}-a${NC}"
    export GCP_ZONE="${GCP_REGION}-a"
fi

echo -e "${GREEN}Using Project ID: $GCP_PROJECT_ID${NC}"
echo -e "${GREEN}Using Region: $GCP_REGION${NC}"

# Set the project
echo -e "${YELLOW}Setting GCP project...${NC}"
gcloud config set project $GCP_PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}Enabling required APIs...${NC}"
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable texttospeech.googleapis.com

# Create GKE cluster with autoscaling (zonal + standard disks to avoid SSD quota)
echo -e "${YELLOW}Creating GKE cluster (zonal, pd-standard disks)...${NC}"
gcloud container clusters create news-teller-cluster \
  --zone "$GCP_ZONE" \
  --num-nodes 1 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 3 \
  --machine-type e2-medium \
  --disk-type pd-standard \
  --disk-size 30 \
  --enable-autorepair \
  --enable-autoupgrade

# Get cluster credentials
echo -e "${YELLOW}Getting cluster credentials...${NC}"
gcloud container clusters get-credentials news-teller-cluster --zone "$GCP_ZONE"

# Configure Docker for GCR
echo -e "${YELLOW}Configuring Docker for Google Container Registry...${NC}"
gcloud auth configure-docker

echo -e "${GREEN}GCP setup completed successfully!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Run ./create-secrets.sh to create Kubernetes secrets"
echo "2. Run ./deploy.sh to build and deploy your application"
