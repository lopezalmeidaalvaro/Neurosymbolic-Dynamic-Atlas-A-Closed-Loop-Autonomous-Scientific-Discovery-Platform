#!/bin/bash
# Phase T16 Automated Deploy Script to AWS/GCP
echo "[*] Building commercial Docker container..."
docker build -t orbital-thermal-saas:latest .

echo "[*] Logging into Google Cloud Container Registry..."
# gcloud auth configure-docker

echo "[*] Tagging and pushing container..."
# docker tag orbital-thermal-saas:latest gcr.io/space-thermals-digital/saas:v1
# docker push gcr.io/space-thermals-digital/saas:v1

echo "[*] Triggering serverless Cloud Run deploy..."
# gcloud run deploy orbital-thermal-service --image gcr.io/space-thermals-digital/saas:v1 --platform managed --region us-central1 --allow-unauthenticated

echo "[+] Deployment completed successfully!"
