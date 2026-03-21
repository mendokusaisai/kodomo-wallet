#!/usr/bin/env bash
set -euo pipefail

# Initial GCP setup for stg environment.
# Creates service accounts, IAM bindings, and grants access to prod Artifact Registry.
#
# Prerequisites:
#   - gcloud CLI authenticated with an account that has Owner/Editor on STG_PROJECT_ID
#   - prod Artifact Registry already exists in PROD_PROJECT_ID
#
# Required env vars: (none — defaults are pre-configured for kodomo-wallet-stg)
# Optional env vars: STG_PROJECT_ID, PROD_PROJECT_ID, REGION, AR_REPO

STG_PROJECT_ID="${STG_PROJECT_ID:-kodomo-wallet-stg}"
PROD_PROJECT_ID="${PROD_PROJECT_ID:-kodomo-wallet}"
REGION="${REGION:-asia-northeast1}"
AR_REPO="${AR_REPO:-kodomo-wallet}"

DEPLOY_SA="deployer@${STG_PROJECT_ID}.iam.gserviceaccount.com"
RUNTIME_SA="cloud-run-runtime@${STG_PROJECT_ID}.iam.gserviceaccount.com"

echo "=== Setting up stg GCP environment ==="
echo "  STG Project : ${STG_PROJECT_ID}"
echo "  Prod Project: ${PROD_PROJECT_ID}"
echo "  Region      : ${REGION}"
echo ""

echo "[1/7] Enabling required APIs in stg project..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com \
  --project "${STG_PROJECT_ID}"

echo "[2/7] Ensuring service accounts exist..."
if ! gcloud iam service-accounts describe "${DEPLOY_SA}" --project "${STG_PROJECT_ID}" >/dev/null 2>&1; then
  gcloud iam service-accounts create deployer \
    --display-name="kodomo-wallet-stg deployer" \
    --project "${STG_PROJECT_ID}"
  echo "  Created ${DEPLOY_SA}"
else
  echo "  ${DEPLOY_SA} already exists."
fi

if ! gcloud iam service-accounts describe "${RUNTIME_SA}" --project "${STG_PROJECT_ID}" >/dev/null 2>&1; then
  gcloud iam service-accounts create cloud-run-runtime \
    --display-name="kodomo-wallet-stg cloud run runtime" \
    --project "${STG_PROJECT_ID}"
  echo "  Created ${RUNTIME_SA}"
else
  echo "  ${RUNTIME_SA} already exists."
fi

echo "[3/7] Applying IAM roles to deployer in stg project..."
for role in roles/run.admin roles/artifactregistry.writer roles/cloudbuild.builds.editor roles/secretmanager.secretAccessor; do
  gcloud projects add-iam-policy-binding "${STG_PROJECT_ID}" \
    --member="serviceAccount:${DEPLOY_SA}" \
    --role="${role}" >/dev/null
done

echo "[4/7] Allowing deployer to use runtime service account..."
gcloud iam service-accounts add-iam-policy-binding "${RUNTIME_SA}" \
  --member="serviceAccount:${DEPLOY_SA}" \
  --role="roles/iam.serviceAccountUser" \
  --project "${STG_PROJECT_ID}" >/dev/null

echo "[5/7] Applying runtime IAM roles in stg project..."
gcloud projects add-iam-policy-binding "${STG_PROJECT_ID}" \
  --member="serviceAccount:${RUNTIME_SA}" \
  --role="roles/secretmanager.secretAccessor" >/dev/null

echo "[6/7] Granting stg SAs access to prod Artifact Registry..."
# stg pulls images from prod's Artifact Registry (shared registry)
# Cloud Run runtime SA needs reader access
gcloud artifacts repositories add-iam-policy-binding "${AR_REPO}" \
  --location="${REGION}" \
  --member="serviceAccount:${RUNTIME_SA}" \
  --role="roles/artifactregistry.reader" \
  --project "${PROD_PROJECT_ID}" >/dev/null

# Cloud Run Service Agent also needs reader access to pull images across projects
# The project number is needed: retrieve it dynamically
STG_PROJECT_NUMBER=$(gcloud projects describe "${STG_PROJECT_ID}" --format="value(projectNumber)")
CR_SERVICE_AGENT="service-${STG_PROJECT_NUMBER}@serverless-robot-prod.iam.gserviceaccount.com"
gcloud artifacts repositories add-iam-policy-binding "${AR_REPO}" \
  --location="${REGION}" \
  --member="serviceAccount:${CR_SERVICE_AGENT}" \
  --role="roles/artifactregistry.reader" \
  --project "${PROD_PROJECT_ID}" >/dev/null

# deployer SA needs writer access to push stg-tagged images
gcloud artifacts repositories add-iam-policy-binding "${AR_REPO}" \
  --location="${REGION}" \
  --member="serviceAccount:${DEPLOY_SA}" \
  --role="roles/artifactregistry.writer" \
  --project "${PROD_PROJECT_ID}" >/dev/null

echo "[7/7] Creating Firestore (default) database and indexes..."
# Create (default) database if it doesn't exist
if ! gcloud firestore databases describe --database="(default)" --project "${STG_PROJECT_ID}" >/dev/null 2>&1; then
  gcloud firestore databases create \
    --database="(default)" \
    --location="${REGION}" \
    --project "${STG_PROJECT_ID}"
  echo "  Firestore (default) database created."
else
  echo "  Firestore (default) database already exists."
fi

# Collection group index for members.uid (required for MY_FAMILY query)
if ! gcloud firestore indexes fields list \
    --collection-group=members \
    --project "${STG_PROJECT_ID}" 2>/dev/null | grep -q "uid"; then
  gcloud firestore indexes fields update uid \
    --collection-group=members \
    --index=order=ASCENDING \
    --project "${STG_PROJECT_ID}" --async
  echo "  Firestore index for members.uid created (building in background)."
else
  echo "  Firestore index for members.uid already exists."
fi

echo "[Done]"
echo ""
echo "=== Next Steps ==="
echo "1. Create a Firebase project for stg: https://console.firebase.google.com"
echo "   - Enable Authentication (Email/Password)"
echo "   - Create a service account key (JSON)"
echo ""
echo "2. Register the following secrets in stg Secret Manager (${STG_PROJECT_ID}):"
echo "   $ gcloud secrets create FIREBASE_SERVICE_ACCOUNT --project ${STG_PROJECT_ID}"
echo "   $ gcloud secrets versions add FIREBASE_SERVICE_ACCOUNT --data-file=stg-firebase-sa.json --project ${STG_PROJECT_ID}"
echo ""
echo "   $ echo -n 'your-random-secret-key' | gcloud secrets create SECRET_KEY --data-file=- --project ${STG_PROJECT_ID}"
echo "   $ echo -n 'https://placeholder.run.app' | gcloud secrets create FRONTEND_ORIGIN --data-file=- --project ${STG_PROJECT_ID}"
echo ""
echo "   # Firebase public config (6 vars):"
echo "   $ echo -n 'your-api-key'    | gcloud secrets create NEXT_PUBLIC_FIREBASE_API_KEY --data-file=- --project ${STG_PROJECT_ID}"
echo "   $ echo -n 'xxx.firebaseapp.com' | gcloud secrets create NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN --data-file=- --project ${STG_PROJECT_ID}"
echo "   $ echo -n 'kodomo-wallet-stg' | gcloud secrets create NEXT_PUBLIC_FIREBASE_PROJECT_ID --data-file=- --project ${STG_PROJECT_ID}"
echo "   $ echo -n 'xxx.appspot.com' | gcloud secrets create NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET --data-file=- --project ${STG_PROJECT_ID}"
echo "   $ echo -n '123456789'       | gcloud secrets create NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID --data-file=- --project ${STG_PROJECT_ID}"
echo "   $ echo -n '1:xxx:web:yyy'   | gcloud secrets create NEXT_PUBLIC_FIREBASE_APP_ID --data-file=- --project ${STG_PROJECT_ID}"
echo ""
echo "3. Run deploy_stg.sh to deploy backend + frontend."
