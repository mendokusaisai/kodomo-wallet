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

## 補足
- `FRONTEND_ORIGIN` / `NEXT_PUBLIC_GRAPHQL_ENDPOINT` は Phase3/4 の Cloud Run デプロイ後に URL が確定してから登録する。
- stg は必要になった時点でスクリプトを複製して対応する。
