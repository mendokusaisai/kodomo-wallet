#!/usr/bin/env bash
set -euo pipefail

# Setup Workload Identity Federation for GitHub Actions.
# Required env vars:
#   GITHUB_REPO  (e.g. "your-org/kodomo-wallet")
# Optional env vars:
#   PROJECT_ID   (default: kodomo-wallet)
#   REGION       (default: asia-northeast1)

PROJECT_ID="${PROJECT_ID:-kodomo-wallet}"
GITHUB_REPO="${GITHUB_REPO:?GITHUB_REPO is required (e.g. owner/kodomo-wallet)}"

POOL_ID="github-actions"
PROVIDER_ID="github"
DEPLOY_SA="deployer@${PROJECT_ID}.iam.gserviceaccount.com"

echo "[1/4] Creating Workload Identity Pool..."
if ! gcloud iam workload-identity-pools describe "${POOL_ID}" \
    --location="global" --project "${PROJECT_ID}" >/dev/null 2>&1; then
  gcloud iam workload-identity-pools create "${POOL_ID}" \
    --location="global" \
    --display-name="GitHub Actions" \
    --project "${PROJECT_ID}"
else
  echo "Pool ${POOL_ID} already exists."
fi

echo "[2/4] Creating OIDC provider..."
if ! gcloud iam workload-identity-pools providers describe "${PROVIDER_ID}" \
    --location="global" \
    --workload-identity-pool="${POOL_ID}" \
    --project "${PROJECT_ID}" >/dev/null 2>&1; then
  gcloud iam workload-identity-pools providers create-oidc "${PROVIDER_ID}" \
    --location="global" \
    --workload-identity-pool="${POOL_ID}" \
    --display-name="GitHub" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
    --attribute-condition="attribute.repository=='${GITHUB_REPO}'" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --project "${PROJECT_ID}"
else
  echo "Provider ${PROVIDER_ID} already exists."
fi

echo "[3/4] Getting project number..."
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")

echo "[4/4] Binding deployer SA to WIF pool (repo: ${GITHUB_REPO})..."
gcloud iam service-accounts add-iam-policy-binding "${DEPLOY_SA}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository/${GITHUB_REPO}" \
  --project "${PROJECT_ID}"

echo ""
echo "=== GitHub Actions に登録する値 ==="
echo "WIF_PROVIDER: projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}"
echo "WIF_SERVICE_ACCOUNT: ${DEPLOY_SA}"
