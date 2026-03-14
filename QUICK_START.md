# 🚀 Quick Start Guide - News Teller GCP Deployment

## Prerequisites Checklist ✅
- [ ] Google Cloud CLI installed and authenticated
- [ ] Docker installed and running
- [ ] Active GCP project with billing enabled
- [ ] Service account JSON key file downloaded

On Windows, run the repo `*.sh` scripts from Git Bash or WSL.

## Environment Variables Setup 🔧

Create a `.env` file or export these variables:

```bash
export GCP_PROJECT_ID="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
export GOOGLE_API_KEY="your-google-api-key"
export GOOGLE_CSE_ID="your-custom-search-engine-id"
export NEWS_API_KEY="your-newsapi-key"
export GCP_REGION="us-central1"  # Optional
```

`NEWS_API_KEY` is required for `/get_daily_news` and can be created at `https://newsapi.org/account`.

## Three-Step Deployment 🎯

### 1. Setup GCP Infrastructure
```bash
./setup-gcp.sh
```
⏱️ *Takes 5-10 minutes*

### 2. Configure Secrets
```bash
./create-secrets.sh
```
⏱️ *Takes 30 seconds*

### 3. Build & Deploy
```bash
./deploy.sh
```
⏱️ *Takes 3-5 minutes*

## Get Your App URL 🌐

```bash
kubectl get services news-teller-service
```

Look for the `EXTERNAL-IP` column. Your app will be available at:
`http://EXTERNAL-IP/`

## Quick Commands 📝

```bash
# Check status
kubectl get pods -l app=news-teller

# View logs
kubectl logs -l app=news-teller --tail=50

# Scale up/down
kubectl scale deployment news-teller-app --replicas=5

# Update app (after code changes)
./deploy.sh
```

## Cost Estimate 💰

**Medium Performance Setup:**
- 2-5 e2-medium nodes: ~$50-120/month
- Load balancer: ~$18/month
- **Total: ~$70-140/month** (scales with usage)

## Architecture Features 🏗️

✅ **Auto-scaling**: 2-10 pods based on CPU/memory  
✅ **Load balancing**: External traffic distribution  
✅ **Health checks**: Automatic pod restart if unhealthy  
✅ **Rolling updates**: Zero-downtime deployments  
✅ **Secrets management**: Secure API key storage  

## Need Help? 🆘

1. Check `DEPLOYMENT.md` for detailed instructions
2. View logs: `kubectl logs -l app=news-teller --tail=100`
3. Describe pods: `kubectl describe pods -l app=news-teller`

---

**Ready to deploy?** Just run the three commands above! 🚀
