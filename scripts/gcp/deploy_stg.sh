#!/usr/bin/env bash
set -euo pipefail

# Deploy backend + frontend to stg Cloud Run.
# Images are pulled from prod Artifact Registry.
#
# Usage:
#   IMAGE_TAG=<git-sha> ./scripts/gcp/deploy_stg.sh
#
# Required env vars:
#   IMAGE_TAG — docker image tag to deploy (e.g. git SHA or "latest")
#
# Required secrets in stg Secret Manager (${STG_PROJECT_ID}):
#   FIREBASE_SERVICE_ACCOUNT, SECRET_KEY, FRONTEND_ORIGIN
#   NEXT_PUBLIC_FIREBASE_API_KEY, NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
#   NEXT_PUBLIC_FIREBASE_PROJECT_ID, NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
#   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID, NEXT_PUBLIC_FIREBASE_APP_ID
#
# Optional env vars: STG_PROJECT_ID, PROD_PROJECT_ID, REGION

STG_PROJECT_ID="${STG_PROJECT_ID:-kodomo-wallet-stg}"
PROD_PROJECT_ID="${PROD_PROJECT_ID:-kodomo-wallet}"
REGION="${REGION:-asia-northeast1}"
IMAGE_TAG="${IMAGE_TAG:?IMAGE_TAG is required (e.g. git SHA or 'latest')}"

BACKEND_SERVICE="kodomo-wallet-backend"
FRONTEND_SERVICE="kodomo-wallet-frontend"
AR_BASE="$REGION-docker.pkg.dev/$PROD_PROJECT_ID/kodomo-wallet"
BACKEND_IMAGE="$AR_BASE/backend:$IMAGE_TAG"
FRONTEND_IMAGE="$AR_BASE/frontend:$IMAGE_TAG"
RUNTIME_SA="cloud-run-runtime@${STG_PROJECT_ID}.iam.gserviceaccount.com"

echo "=== Deploying stg environment ==="
echo "  STG Project : ${STG_PROJECT_ID}"
echo "  IMAGE_TAG   : ${IMAGE_TAG}"
echo "  Backend     : ${BACKEND_IMAGE}"
echo "  Frontend    : ${FRONTEND_IMAGE}"
echo ""

# ---- 1. Deploy backend ----
echo "[1/4] Deploying backend..."
gcloud run deploy "$BACKEND_SERVICE" \
  --image "$BACKEND_IMAGE" \
  --region "$REGION" \
  --platform managed \
  --service-account "$RUNTIME_SA" \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 2 \
  --concurrency 80 \
  --timeout 300s \
  --port 8080 \
  --set-env-vars "ENVIRONMENT=staging" \
  --set-secrets "FIREBASE_SERVICE_ACCOUNT=FIREBASE_SERVICE_ACCOUNT:latest,SECRET_KEY=SECRET_KEY:latest,FRONTEND_ORIGIN=FRONTEND_ORIGIN:latest" \
  --project "$STG_PROJECT_ID"

BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE" \
  --region "$REGION" \
  --project "$STG_PROJECT_ID" \
  --format "value(status.url)")

echo "  Backend URL: ${BACKEND_URL}"
GRAPHQL_ENDPOINT="${BACKEND_URL}/graphql"

# ---- 2. Read Firebase public config from stg Secret Manager ----
echo "[2/4] Reading Firebase public config from stg Secret Manager..."
get_secret() {
  gcloud secrets versions access latest --secret="$1" --project="$STG_PROJECT_ID"
}

NEXT_PUBLIC_FIREBASE_API_KEY=$(get_secret "NEXT_PUBLIC_FIREBASE_API_KEY")
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=$(get_secret "NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN")
NEXT_PUBLIC_FIREBASE_PROJECT_ID=$(get_secret "NEXT_PUBLIC_FIREBASE_PROJECT_ID")
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=$(get_secret "NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET")
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=$(get_secret "NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID")
NEXT_PUBLIC_FIREBASE_APP_ID=$(get_secret "NEXT_PUBLIC_FIREBASE_APP_ID")

# ---- 3. Build and push frontend image ----
echo "[3/4] Building and pushing frontend image..."
docker build --platform linux/amd64 \
  --build-arg NEXT_PUBLIC_FIREBASE_API_KEY="$NEXT_PUBLIC_FIREBASE_API_KEY" \
  --build-arg NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN="$NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN" \
  --build-arg NEXT_PUBLIC_FIREBASE_PROJECT_ID="$NEXT_PUBLIC_FIREBASE_PROJECT_ID" \
  --build-arg NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET="$NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET" \
  --build-arg NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID="$NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID" \
  --build-arg NEXT_PUBLIC_FIREBASE_APP_ID="$NEXT_PUBLIC_FIREBASE_APP_ID" \
  --build-arg NEXT_PUBLIC_GRAPHQL_ENDPOINT="$GRAPHQL_ENDPOINT" \
  -t "$FRONTEND_IMAGE" \
  ./frontend

docker push "$FRONTEND_IMAGE"

# ---- 4. Deploy frontend ----
echo "[4/4] Deploying frontend..."
gcloud run deploy "$FRONTEND_SERVICE" \
  --image "$FRONTEND_IMAGE" \
  --region "$REGION" \
  --platform managed \
  --service-account "$RUNTIME_SA" \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 2 \
  --concurrency 80 \
  --timeout 60s \
  --port 8080 \
  --project "$STG_PROJECT_ID"

FRONTEND_URL=$(gcloud run services describe "$FRONTEND_SERVICE" \
  --region "$REGION" \
  --project "$STG_PROJECT_ID" \
  --format "value(status.url)")

# ---- Update FRONTEND_ORIGIN secret ----
echo ""
echo "Updating FRONTEND_ORIGIN secret to ${FRONTEND_URL} ..."
echo -n "$FRONTEND_URL" | gcloud secrets versions add FRONTEND_ORIGIN \
  --data-file=- \
  --project="$STG_PROJECT_ID"

echo ""
echo "=== stg Deploy Complete! ==="
echo "  Backend  : ${BACKEND_URL}"
echo "  Frontend : ${FRONTEND_URL}"
echo "  GraphQL  : ${GRAPHQL_ENDPOINT}"
echo ""
echo "NOTE: Backend FRONTEND_ORIGIN has been updated to ${FRONTEND_URL}."
echo "      Re-deploy backend if CORS errors occur (new secret version takes effect on next revision):"
echo "  IMAGE_TAG=${IMAGE_TAG} ./scripts/gcp/deploy_stg.sh"
