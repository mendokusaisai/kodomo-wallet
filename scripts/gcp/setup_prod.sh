#!/usr/bin/env bash
set -euo pipefail

# Phase 2: GCP base setup for prod.
# Required env vars:
#   PROJECT_ID, REGION
# Optional env vars:
#   AR_REPO (default: kodomo-wallet)

PROJECT_ID="${PROJECT_ID:-kodomo-wallet}"
REGION="${REGION:?REGION is required}"
AR_REPO="${AR_REPO:-kodomo-wallet}"

DEPLOY_SA="deployer@${PROJECT_ID}.iam.gserviceaccount.com"
RUNTIME_SA="cloud-run-runtime@${PROJECT_ID}.iam.gserviceaccount.com"

echo "[1/6] Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com \
  --project "${PROJECT_ID}"

echo "[2/6] Ensuring Artifact Registry exists..."
if ! gcloud artifacts repositories describe "${AR_REPO}" --location="${REGION}" --project "${PROJECT_ID}" >/dev/null 2>&1; then
  gcloud artifacts repositories create "${AR_REPO}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="kodomo-wallet containers" \
    --project "${PROJECT_ID}"
else
  echo "Artifact Registry ${AR_REPO} already exists."
fi

echo "[3/6] Ensuring service accounts exist..."
if ! gcloud iam service-accounts describe "${DEPLOY_SA}" --project "${PROJECT_ID}" >/dev/null 2>&1; then
  gcloud iam service-accounts create deployer \
    --display-name="kodomo-wallet deployer" \
    --project "${PROJECT_ID}"
fi

if ! gcloud iam service-accounts describe "${RUNTIME_SA}" --project "${PROJECT_ID}" >/dev/null 2>&1; then
  gcloud iam service-accounts create cloud-run-runtime \
    --display-name="kodomo-wallet cloud run runtime" \
    --project "${PROJECT_ID}"
fi

echo "[4/6] Applying IAM roles to deployer..."
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${DEPLOY_SA}" \
  --role="roles/run.admin" >/dev/null

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${DEPLOY_SA}" \
  --role="roles/artifactregistry.writer" >/dev/null

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${DEPLOY_SA}" \
  --role="roles/cloudbuild.builds.editor" >/dev/null

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${DEPLOY_SA}" \
  --role="roles/secretmanager.secretAccessor" >/dev/null

echo "[5/6] Allowing deployer to use runtime service account..."
gcloud iam service-accounts add-iam-policy-binding "${RUNTIME_SA}" \
  --member="serviceAccount:${DEPLOY_SA}" \
  --role="roles/iam.serviceAccountUser" \
  --project "${PROJECT_ID}" >/dev/null

echo "[6/6] Applying runtime role..."
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${RUNTIME_SA}" \
  --role="roles/secretmanager.secretAccessor" >/dev/null

echo "Done. Next: register secrets in Secret Manager."
