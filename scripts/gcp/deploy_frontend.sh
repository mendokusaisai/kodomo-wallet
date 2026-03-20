#!/usr/bin/env bash
set -euo pipefail

# Manual / initial deploy of frontend to Cloud Run.
# Required env vars: IMAGE_TAG, NEXT_PUBLIC_FIREBASE_API_KEY, NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
#   NEXT_PUBLIC_FIREBASE_PROJECT_ID, NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
#   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID, NEXT_PUBLIC_FIREBASE_APP_ID,
#   NEXT_PUBLIC_GRAPHQL_ENDPOINT
# Optional env vars: PROJECT_ID, REGION

PROJECT_ID="${PROJECT_ID:-kodomo-wallet}"
REGION="${REGION:-asia-northeast1}"
SERVICE="kodomo-wallet-frontend"
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/kodomo-wallet/frontend"
IMAGE_TAG="${IMAGE_TAG:-latest}"

: "${NEXT_PUBLIC_FIREBASE_API_KEY:?NEXT_PUBLIC_FIREBASE_API_KEY is required}"
: "${NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN:?NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN is required}"
: "${NEXT_PUBLIC_FIREBASE_PROJECT_ID:?NEXT_PUBLIC_FIREBASE_PROJECT_ID is required}"
: "${NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET:?NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET is required}"
: "${NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID:?NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID is required}"
: "${NEXT_PUBLIC_FIREBASE_APP_ID:?NEXT_PUBLIC_FIREBASE_APP_ID is required}"
: "${NEXT_PUBLIC_GRAPHQL_ENDPOINT:?NEXT_PUBLIC_GRAPHQL_ENDPOINT is required}"

echo "Building $SERVICE image..."
docker build --platform linux/amd64 \
  --build-arg NEXT_PUBLIC_FIREBASE_API_KEY="$NEXT_PUBLIC_FIREBASE_API_KEY" \
  --build-arg NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN="$NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN" \
  --build-arg NEXT_PUBLIC_FIREBASE_PROJECT_ID="$NEXT_PUBLIC_FIREBASE_PROJECT_ID" \
  --build-arg NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET="$NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET" \
  --build-arg NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID="$NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID" \
  --build-arg NEXT_PUBLIC_FIREBASE_APP_ID="$NEXT_PUBLIC_FIREBASE_APP_ID" \
  --build-arg NEXT_PUBLIC_GRAPHQL_ENDPOINT="$NEXT_PUBLIC_GRAPHQL_ENDPOINT" \
  -t "$IMAGE:$IMAGE_TAG" \
  ./frontend

docker push "$IMAGE:$IMAGE_TAG"

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
  --timeout 60s \
  --port 8080 \
  --project "$PROJECT_ID"

echo ""
echo "=== Service URL ==="
gcloud run services describe "$SERVICE" \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --format "value(status.url)"
