# News Teller App - GCP Deployment Guide

This guide will help you deploy your Flask News Teller application to Google Cloud Platform using Docker and Kubernetes.

## Prerequisites

1. **Google Cloud CLI**: Install from [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)
2. **Docker**: Install from [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
3. **kubectl**: Usually comes with gcloud CLI
4. **GCP Project**: Active Google Cloud project with billing enabled
5. **Service Account**: JSON key file for a service account with required permissions

## Required GCP APIs

The setup script will automatically enable these APIs:
- Container Registry API
- Kubernetes Engine API
- Text-to-Speech API

## Environment Setup

1. **Copy and update environment variables**:
   ```bash
   cp production.env .env
   # Edit .env with your actual values
   ```

2. **Set required environment variables**:
   ```bash
   export GCP_PROJECT_ID="your-project-id"
   export GCP_REGION="us-central1"  # Optional, defaults to us-central1
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account.json"
   export GOOGLE_API_KEY="your-google-api-key"
   export GOOGLE_CSE_ID="your-cse-id"
   ```

## Deployment Steps

### Step 1: Initial GCP Setup
```bash
./setup-gcp.sh
```
This script will:
- Set your GCP project
- Enable required APIs
- Create a GKE cluster with autoscaling (e2-medium instances)
- Configure Docker for GCR

### Step 2: Create Kubernetes Secrets
```bash
./create-secrets.sh
```
This script will:
- Create application secrets for API keys
- Create Google Cloud service account secret

### Step 3: Build and Deploy
```bash
./deploy.sh
```
This script will:
- Build your Docker image
- Push to Google Container Registry
- Deploy to Kubernetes
- Set up load balancer and autoscaling

## Architecture Overview

### Infrastructure
- **GKE Cluster**: Regional cluster with 1-5 nodes (e2-medium)
- **Load Balancer**: External load balancer for public access
- **Autoscaling**: HPA based on CPU (70%) and memory (80%) utilization
- **Pod Resources**: 512Mi-1Gi memory, 250m-500m CPU per pod

### Scaling Configuration
- **Min Replicas**: 2
- **Max Replicas**: 10
- **Node Autoscaling**: 1-5 nodes based on demand

## Monitoring and Management

### Check Deployment Status
```bash
kubectl get deployments
kubectl get pods -l app=news-teller
kubectl get services
```

### View Logs
```bash
kubectl logs -l app=news-teller --tail=100 -f
```

### Scale Manually
```bash
kubectl scale deployment news-teller-app --replicas=3
```

### Update Application
```bash
# Make your code changes, then:
./deploy.sh
```

## Cost Optimization

This setup is designed for medium cost with good performance:

- **e2-medium instances**: Balance of cost and performance
- **Autoscaling**: Only pay for resources you use
- **Regional deployment**: Better availability than single-zone
- **Efficient resource limits**: Prevents over-provisioning

### Estimated Monthly Costs (us-central1)
- **2 e2-medium nodes**: ~$50-70/month
- **Load Balancer**: ~$18/month
- **Additional nodes**: Scale based on usage

## Security Features

- **Secrets Management**: API keys stored as Kubernetes secrets
- **Service Account**: Dedicated service account with minimal permissions
- **Container Security**: Minimal base image with security updates
- **Network Policies**: Can be added for additional network security

## Troubleshooting

### Common Issues

1. **Permission Denied**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Service Account Issues**:
   - Ensure the service account has the following roles:
     - Text-to-Speech API Service Agent
     - Storage Object Admin (for Container Registry)
     - Kubernetes Engine Developer

3. **Image Pull Errors**:
   ```bash
   gcloud auth configure-docker
   docker push gcr.io/YOUR_PROJECT_ID/news-teller:latest
   ```

4. **Pod Startup Issues**:
   ```bash
   kubectl describe pod POD_NAME
   kubectl logs POD_NAME
   ```

### Useful Commands

```bash
# Get external IP
kubectl get services news-teller-service

# Check autoscaler status
kubectl get hpa

# Check node status
kubectl get nodes

# Port forward for local testing
kubectl port-forward service/news-teller-service 8080:80
```

## Cleanup

To delete all resources:
```bash
kubectl delete -f hpa.yaml
kubectl delete -f service.yaml
kubectl delete -f deployment.yaml
gcloud container clusters delete news-teller-cluster --region $GCP_REGION
```

## Support

For issues with deployment, check:
1. GCP quotas and limits
2. Service account permissions
3. Network connectivity
4. Application logs via kubectl

