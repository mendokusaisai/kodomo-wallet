#!/usr/bin/env bash
set -euo pipefail

# Manual / initial deploy of backend to Cloud Run.
# Run once to create the service, then let GitHub Actions handle subsequent deploys.
# Required env vars: IMAGE_TAG (docker image tag, e.g. git SHA or "latest")
# Optional env vars: PROJECT_ID, REGION
# Secrets required in Secret Manager: FIREBASE_SERVICE_ACCOUNT, SECRET_KEY, FRONTEND_ORIGIN

PROJECT_ID="${PROJECT_ID:-kodomo-wallet}"
REGION="${REGION:-asia-northeast1}"
SERVICE="kodomo-wallet-backend"
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/kodomo-wallet/backend"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "Deploying $SERVICE from $IMAGE:$IMAGE_TAG ..."

gcloud run deploy "$SERVICE" \
  --image "$IMAGE:$IMAGE_TAG" \
  --region "$REGION" \
  --platform managed \
  --service-account "cloud-run-runtime@${PROJECT_ID}.iam.gserviceaccount.com" \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 3 \
  --concurrency 80 \
  --timeout 300s \
  --port 8080 \
  --set-env-vars "ENVIRONMENT=production" \
  --set-secrets "FIREBASE_SERVICE_ACCOUNT=FIREBASE_SERVICE_ACCOUNT:latest,SECRET_KEY=SECRET_KEY:latest,FRONTEND_ORIGIN=FRONTEND_ORIGIN:latest" \
  --project "$PROJECT_ID"

echo ""
echo "=== Service URL ==="
gcloud run services describe "$SERVICE" \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --format "value(status.url)"
