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

## Phase4: frontend Cloud Run デプロイ

### 1. NEXT_PUBLIC_GRAPHQL_ENDPOINT が登録済みか確認

Phase3 の疎通確認後に登録しているはず。未登録の場合は先に登録する（Phase3 手順 6 参照）。

### 2. 初回デプロイ（手動）

Secret Manager から値を取得してデプロイ：

```bash
export NEXT_PUBLIC_SUPABASE_URL=$(gcloud secrets versions access latest --secret=NEXT_PUBLIC_SUPABASE_URL --project=kodomo-wallet)
export NEXT_PUBLIC_SUPABASE_ANON_KEY=$(gcloud secrets versions access latest --secret=NEXT_PUBLIC_SUPABASE_ANON_KEY --project=kodomo-wallet)
export NEXT_PUBLIC_GRAPHQL_ENDPOINT=$(gcloud secrets versions access latest --secret=NEXT_PUBLIC_GRAPHQL_ENDPOINT --project=kodomo-wallet)
export IMAGE_TAG=latest

./scripts/gcp/deploy_frontend.sh
```

### 3. 以降のデプロイ

`main` ブランチへの push で GitHub Actions (`deploy-frontend.yml`) が自動実行。

### 4. Supabase OAuth リダイレクト URL に追加

Supabase ダッシュボード → Authentication → URL Configuration → Redirect URLs に追加：

```
https://kodomo-wallet-frontend-<hash>-an.a.run.app/**
```

### 5. FRONTEND_ORIGIN を正式な URL に更新

```bash
FRONTEND_URL=$(gcloud run services describe kodomo-wallet-frontend \
  --region asia-northeast1 --project kodomo-wallet --format "value(status.url)")

printf '%s' "$FRONTEND_URL" | gcloud secrets versions add FRONTEND_ORIGIN \
  --data-file=- --project kodomo-wallet
```

その後、backend を再デプロイして CORS 設定を反映：

```bash
export IMAGE_TAG=latest
./scripts/gcp/deploy_backend.sh
```

### 6. 疎通確認

```bash
FRONTEND_URL=$(gcloud run services describe kodomo-wallet-frontend \
  --region asia-northeast1 --project kodomo-wallet --format "value(status.url)")

# トップページ
curl -o /dev/null -s -w "%{http_code}" "$FRONTEND_URL"
# → 200

# ログインページ
curl -o /dev/null -s -w "%{http_code}" "$FRONTEND_URL/login"
# → 200
```

## Phase5: バッチ/定期実行

GitHub Actions で継続運用。設定済みのワークフロー：

| ワークフロー | スケジュール | 用途 |
|---|---|---|
| `recurring-deposits.yml` | 毎日 UTC 15:00 (JST 0:00) | 定期入金バッチ |
| `keepalive.yml` | 毎日 UTC 00:00 (JST 9:00) | Supabase / Cloud Run ping |

### keepalive に必要な GitHub Secret の追加

`CLOUD_RUN_BACKEND_URL` が未設定の場合は追加する（`FRONTEND_ORIGIN` は Phase4 で登録済み）：

```bash
BACKEND_URL=$(gcloud run services describe kodomo-wallet-backend \
  --region asia-northeast1 --project kodomo-wallet --format "value(status.url)")
echo "Add to GitHub Secrets → CLOUD_RUN_BACKEND_URL = $BACKEND_URL"
```

GitHub → Settings → Secrets and variables → Actions → New repository secret

## Phase6: 切替・検証・ロールバック

### 1. 切替前チェックリスト

#### Cloud Run サービス確認

```bash
export PROJECT_ID=kodomo-wallet
export REGION=asia-northeast1

# 両サービスが READY か確認
gcloud run services list --region "$REGION" --project "$PROJECT_ID"

BACKEND_URL=$(gcloud run services describe kodomo-wallet-backend \
  --region "$REGION" --project "$PROJECT_ID" --format "value(status.url)")
FRONTEND_URL=$(gcloud run services describe kodomo-wallet-frontend \
  --region "$REGION" --project "$PROJECT_ID" --format "value(status.url)")

echo "BACKEND:  $BACKEND_URL"
echo "FRONTEND: $FRONTEND_URL"
```

#### backend ヘルスチェック

```bash
# /health レスポンス確認
curl "$BACKEND_URL/health"
# → {"status":"healthy"}

# GraphQL 疎通確認
curl -X POST "$BACKEND_URL/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __typename }"}'
# → {"data":{"__typename":"Query"}}
```

#### frontend 疎通確認

```bash
# トップ / ログインページが 200 を返すか
curl -o /dev/null -s -w "%{http_code}\n" "$FRONTEND_URL"
curl -o /dev/null -s -w "%{http_code}\n" "$FRONTEND_URL/login"
# → 200
```

#### Supabase OAuth リダイレクト URL 確認

Supabase ダッシュボード → Authentication → URL Configuration で以下が登録済みか確認：

```
https://kodomo-wallet-frontend-<hash>-an.a.run.app/**
```

未登録の場合は追加してから続行する。

#### Secret Manager 登録値の確認

```bash
for SECRET in DATABASE_URL SUPABASE_URL SUPABASE_KEY SECRET_KEY FRONTEND_ORIGIN \
              NEXT_PUBLIC_SUPABASE_URL NEXT_PUBLIC_SUPABASE_ANON_KEY \
              NEXT_PUBLIC_GRAPHQL_ENDPOINT; do
  echo -n "$SECRET: "
  gcloud secrets versions access latest --secret="$SECRET" --project="$PROJECT_ID" \
    | cut -c1-40
done
```

### 2. 機能確認（ブラウザ手動）

以下の導線をブラウザで動作確認する：

| 確認項目 | 手順 |
|---|---|
| ログイン | `$FRONTEND_URL/login` → Supabase 認証 → ダッシュボードへリダイレクト |
| 入金 | ダッシュボード → 入金操作 → 残高反映 |
| 出金申請 | 出金申請 → 承認フロー確認 |
| 定期入金確認 | Supabase DB で recurring_deposits テーブルの内容確認 |
| 画像アップロード | プロフィール画像など Supabase Storage 連携確認 |
| 親招待 | 招待メール送信 → 受諾フロー |

### 3. 旧サービス停止（Vercel / Render）

機能確認がすべて Pass したら旧サービスを停止する。

#### Vercel 停止手順

1. Vercel ダッシュボード → プロジェクト → Settings → General → "Delete Project"
   （または一時的に無効化する場合は Environment Variables を削除して再デプロイ）

#### Render 停止手順

1. Render ダッシュボード → サービス → "Suspend" または "Delete"
2. `render.yaml` はリファレンスとして残しておくか、不要なら削除する

### 4. 切替後の監視（24〜48 時間）

#### Cloud Run ログ確認

```bash
# backend エラーログ
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="kodomo-wallet-backend" AND severity>=ERROR' \
  --limit 50 --project "$PROJECT_ID" --format "table(timestamp,jsonPayload.message)"

# frontend エラーログ
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="kodomo-wallet-frontend" AND severity>=ERROR' \
  --limit 50 --project "$PROJECT_ID" --format "table(timestamp,jsonPayload.message)"
```

#### Cloud Run メトリクス確認

```bash
# リクエスト数・エラー率・レイテンシを確認
open "https://console.cloud.google.com/run/detail/asia-northeast1/kodomo-wallet-backend/metrics?project=$PROJECT_ID"
open "https://console.cloud.google.com/run/detail/asia-northeast1/kodomo-wallet-frontend/metrics?project=$PROJECT_ID"
```

#### keepalive の動作確認

GitHub Actions → `keepalive.yml` の直近実行が成功しているか確認する。

### 5. ロールバック手順

Cloud Run での問題が解決できない場合、旧サービスに戻す手順：

#### frontend ロールバック

1. Vercel プロジェクトを再有効化（または再デプロイ）
2. Vercel の `NEXT_PUBLIC_GRAPHQL_ENDPOINT` を旧 Render の backend URL に戻す
3. Supabase OAuth リダイレクト URL を旧 Vercel URL に変更

#### backend ロールバック

1. Render サービスを Resume（または再デプロイ）
2. Vercel 側の `NEXT_PUBLIC_GRAPHQL_ENDPOINT` を Render の URL に戻す

#### Cloud Run の前バージョンへのロールバック

旧 Render/Vercel に戻さず Cloud Run の前リビジョンに戻す場合：

```bash
# 直前のリビジョン一覧
gcloud run revisions list --service kodomo-wallet-backend \
  --region "$REGION" --project "$PROJECT_ID" --limit 5

# 特定リビジョンにトラフィックを全量戻す
gcloud run services update-traffic kodomo-wallet-backend \
  --to-revisions [REVISION_NAME]=100 \
  --region "$REGION" --project "$PROJECT_ID"
```

### 6. 完了条件

- [ ] `$BACKEND_URL/health` が `{"status":"healthy"}` を返す
- [ ] `$FRONTEND_URL` がブラウザで正常表示される
- [ ] Supabase 認証（ログイン）が動作する
- [ ] keepalive workflow が正常実行される
- [ ] 旧 Vercel / Render サービスが停止済み（または停止計画が確定済み）
