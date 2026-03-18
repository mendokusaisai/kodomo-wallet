# GCP Runbook (prod)

## 基盤セットアップ

API有効化・Artifact Registry・サービスアカウント・IAM付与は以下のスクリプトで自動化済み：

```bash
export REGION="asia-northeast1"
./scripts/gcp/setup_phase2_prod.sh
```

## Secret Manager 登録

本番で使用する最小シークレット:
- DATABASE_URL
- SUPABASE_URL
- SUPABASE_KEY
- SECRET_KEY
- FRONTEND_ORIGIN
- NEXT_PUBLIC_SUPABASE_URL
- NEXT_PUBLIC_SUPABASE_ANON_KEY
- NEXT_PUBLIC_GRAPHQL_ENDPOINT

作成（初回）:

```bash
printf '%s' "$DATABASE_URL" | gcloud secrets create DATABASE_URL \
  --replication-policy="automatic" \
  --data-file=- \
  --project "$PROJECT_ID"
```

更新（2回目以降）:

```bash
printf '%s' "$DATABASE_URL" | gcloud secrets versions add DATABASE_URL \
  --data-file=- \
  --project "$PROJECT_ID"
```

## 検証コマンド

```bash
gcloud services list --enabled --project "$PROJECT_ID" | grep -E 'run|cloudbuild|artifactregistry|secretmanager'

gcloud iam service-accounts list --project "$PROJECT_ID" | grep -E 'deployer|cloud-run-runtime'

gcloud artifacts repositories list --location="$REGION" --project "$PROJECT_ID"

gcloud secrets list --project "$PROJECT_ID"
```

## Phase3: backend Cloud Run デプロイ

### 1. WIF セットアップ（初回のみ）

```bash
export GITHUB_REPO="your-org/kodomo-wallet"
./scripts/gcp/setup_wif.sh
```

出力された `WIF_PROVIDER` と `WIF_SERVICE_ACCOUNT` を GitHub リポジトリの Secrets に登録：
- Settings → Secrets and variables → Actions → New repository secret

### 2. FRONTEND_ORIGIN を Secret Manager に登録（placeholder でよい）

Phase4 で URL が確定するまで仮値を入れておく：

```bash
printf '%s' "https://placeholder.run.app" \
  | gcloud secrets create FRONTEND_ORIGIN \
  --replication-policy="automatic" --data-file=- --project kodomo-wallet
```

### 3. 初回デプロイ（手動）

```bash
# Artifact Registry に Docker 認証
gcloud auth configure-docker asia-northeast1-docker.pkg.dev

# イメージをビルド＆プッシュ（amd64 を明示：Apple Silicon Mac でも Cloud Run で動く）
docker build --platform linux/amd64 \
  -t asia-northeast1-docker.pkg.dev/kodomo-wallet/kodomo-wallet/backend:latest \
  ./backend
docker push asia-northeast1-docker.pkg.dev/kodomo-wallet/kodomo-wallet/backend:latest

# Cloud Run へデプロイ
export IMAGE_TAG=latest
./scripts/gcp/deploy_backend.sh
```

### 4. 以降のデプロイ

`main` ブランチへの push で GitHub Actions (`deploy-backend.yml`) が自動実行。

### 5. 疎通確認

```bash
SERVICE_URL=$(gcloud run services describe kodomo-wallet-backend \
  --region asia-northeast1 --project kodomo-wallet --format "value(status.url)")

curl "$SERVICE_URL/health"
# → {"status":"healthy"}

curl -X POST "$SERVICE_URL/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __typename }"}'
```

### 6. NEXT_PUBLIC_GRAPHQL_ENDPOINT を Secret Manager に登録

疎通確認後、確定した URL で更新：

```bash
printf '%s' "$SERVICE_URL/graphql" \
  | gcloud secrets create NEXT_PUBLIC_GRAPHQL_ENDPOINT \
  --replication-policy="automatic" --data-file=- --project kodomo-wallet
```

## 補足
- `FRONTEND_ORIGIN` は Phase4 の frontend デプロイ後に正式な URL に更新する。
- stg は必要になった時点でスクリプトを複製して対応する。
