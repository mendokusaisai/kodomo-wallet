#!/usr/bin/env bash
set -euo pipefail

# Delete stg Cloud Run services and Secret Manager secrets.
# The GCP project itself is NOT deleted — run this to clean up resources between test cycles.
#
# Usage:
#   ./scripts/gcp/teardown_stg.sh
#
# Optional env vars: STG_PROJECT_ID, REGION

STG_PROJECT_ID="${STG_PROJECT_ID:-kodomo-wallet-stg}"
REGION="${REGION:-asia-northeast1}"

echo "=== Tearing down stg environment ==="
echo "  Project : ${STG_PROJECT_ID}"
echo "  Region  : ${REGION}"
echo ""
read -r -p "Are you sure? This will delete Cloud Run services and all secrets. [y/N] " confirm
if [[ "${confirm,,}" != "y" ]]; then
  echo "Aborted."
  exit 0
fi

# ---- Cloud Run services ----
echo ""
echo "[1/2] Deleting Cloud Run services..."
for svc in kodomo-wallet-backend kodomo-wallet-frontend; do
  if gcloud run services describe "$svc" --region "$REGION" --project "$STG_PROJECT_ID" >/dev/null 2>&1; then
    gcloud run services delete "$svc" \
      --region "$REGION" \
      --project "$STG_PROJECT_ID" \
      --quiet
    echo "  Deleted Cloud Run service: $svc"
  else
    echo "  Cloud Run service not found (skip): $svc"
  fi
done

# ---- Secret Manager secrets ----
echo ""
echo "[2/2] Deleting Secret Manager secrets..."
SECRETS=(
  FIREBASE_SERVICE_ACCOUNT
  SECRET_KEY
  FRONTEND_ORIGIN
  NEXT_PUBLIC_FIREBASE_API_KEY
  NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
  NEXT_PUBLIC_FIREBASE_PROJECT_ID
  NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
  NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
  NEXT_PUBLIC_FIREBASE_APP_ID
)

for secret in "${SECRETS[@]}"; do
  if gcloud secrets describe "$secret" --project "$STG_PROJECT_ID" >/dev/null 2>&1; then
    gcloud secrets delete "$secret" \
      --project "$STG_PROJECT_ID" \
      --quiet
    echo "  Deleted secret: $secret"
  else
    echo "  Secret not found (skip): $secret"
  fi
done

echo ""
echo "=== Teardown complete! ==="
echo "GCP project ${STG_PROJECT_ID} still exists."
echo "To re-deploy stg: run setup_stg.sh to re-create secrets, then deploy_stg.sh."
