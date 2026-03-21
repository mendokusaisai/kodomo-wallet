# GCP Runbook (prod)

## 基盤セットアップ

API有効化・Artifact Registry・サービスアカウント・IAM付与・Firestore DB・インデックス作成は以下のスクリプトで自動化済み：

```bash
export REGION="asia-northeast1"
./scripts/gcp/setup_prod.sh
```

## Firebase セットアップ（手動）

以下は Firebase Console で手動実施が必要：

### 1. Firebase プロジェクトの有効化

1. [Firebase Console](https://console.firebase.google.com/) を開く
2. `kodomo-wallet` GCP プロジェクトを選択し「Firebase を追加」
3. Authentication → Sign-in method → Google を有効化
4. Authentication → Settings → 承認済みドメイン に prod frontend URL を追加:
   ```
   kodomo-wallet-frontend-ptfunabkpq-an.a.run.app
   ```

### 2. サービスアカウントキーの取得

Firebase Console → プロジェクト設定 → サービスアカウント → 「新しい秘密鍵の生成」で JSON をダウンロード。
このJSONが `FIREBASE_SERVICE_ACCOUNT` シークレットの値になる。

### 3. Web アプリの設定値取得

Firebase Console → プロジェクト設定 → マイアプリ → Web アプリを追加（または既存選択）。

以下の値を控える：
```json
{
  "apiKey": "...",
  "authDomain": "kodomo-wallet.firebaseapp.com",
  "projectId": "kodomo-wallet",
  "storageBucket": "kodomo-wallet.firebasestorage.app",
  "messagingSenderId": "...",
  "appId": "..."
}
```

## Secret Manager 登録

### 必要なシークレット一覧

| シークレット名 | 説明 |
|---|---|
| `FIREBASE_SERVICE_ACCOUNT` | Firebase Admin SDK 用サービスアカウントキー JSON（全体） |
| `SECRET_KEY` | FastAPI セッション用ランダム秘密鍵（既存流用可） |
| `FRONTEND_ORIGIN` | frontend の Cloud Run URL（CORS 許可用） |
| `NEXT_PUBLIC_FIREBASE_API_KEY` | Firebase Web アプリ apiKey |
| `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` | Firebase Web アプリ authDomain |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` | Firebase Web アプリ projectId |
| `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET` | Firebase Web アプリ storageBucket |
| `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` | Firebase Web アプリ messagingSenderId |
| `NEXT_PUBLIC_FIREBASE_APP_ID` | Firebase Web アプリ appId |
| `NEXT_PUBLIC_GRAPHQL_ENDPOINT` | backend の Cloud Run URL + `/graphql` |

### 登録コマンド

初回作成:

```bash
export PROJECT_ID=kodomo-wallet

# Firebase Service Account (JSONファイルから)
gcloud secrets create FIREBASE_SERVICE_ACCOUNT \
  --replication-policy="automatic" \
  --data-file=/path/to/serviceAccountKey.json \
  --project "$PROJECT_ID"

# 文字列をそのまま渡す場合
printf '%s' "$VALUE" | gcloud secrets create SECRET_NAME \
  --replication-policy="automatic" \
  --data-file=- \
  --project "$PROJECT_ID"
```

更新（2回目以降）:

```bash
printf '%s' "$VALUE" | gcloud secrets versions add SECRET_NAME \
  --data-file=- \
  --project "$PROJECT_ID"
```

### 旧 Supabase シークレットの削除（移行完了後）

prod 動作確認が完了したら旧シークレットを削除する:

```bash
export PROJECT_ID=kodomo-wallet

for SECRET in DATABASE_URL SUPABASE_URL SUPABASE_KEY \
              NEXT_PUBLIC_SUPABASE_URL NEXT_PUBLIC_SUPABASE_ANON_KEY; do
  gcloud secrets delete "$SECRET" --project "$PROJECT_ID" --quiet && echo "deleted $SECRET"
done
```

## 検証コマンド

```bash
gcloud services list --enabled --project "$PROJECT_ID" | grep -E 'run|cloudbuild|artifactregistry|secretmanager|firestore'

gcloud iam service-accounts list --project "$PROJECT_ID" | grep -E 'deployer|cloud-run-runtime'

gcloud artifacts repositories list --location="$REGION" --project "$PROJECT_ID"

gcloud secrets list --project "$PROJECT_ID"

# Firestore DB 確認
gcloud firestore databases list --project "$PROJECT_ID"
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
docker buildx build --platform linux/amd64 --provenance=false \
  -t asia-northeast1-docker.pkg.dev/kodomo-wallet/kodomo-wallet/backend:latest \
  --push \
  ./backend

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

### 1. Firebase シークレットが登録済みか確認

```bash
for SECRET in NEXT_PUBLIC_FIREBASE_API_KEY NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN \
              NEXT_PUBLIC_FIREBASE_PROJECT_ID NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET \
              NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID NEXT_PUBLIC_FIREBASE_APP_ID \
              NEXT_PUBLIC_GRAPHQL_ENDPOINT; do
  echo -n "$SECRET: "
  gcloud secrets versions access latest --secret="$SECRET" --project=kodomo-wallet \
    | cut -c1-40
done
```

### 2. 初回デプロイ（手動）

Secret Manager から値を取得してデプロイ：

```bash
export NEXT_PUBLIC_FIREBASE_API_KEY=$(gcloud secrets versions access latest --secret=NEXT_PUBLIC_FIREBASE_API_KEY --project=kodomo-wallet)
export NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=$(gcloud secrets versions access latest --secret=NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN --project=kodomo-wallet)
export NEXT_PUBLIC_FIREBASE_PROJECT_ID=$(gcloud secrets versions access latest --secret=NEXT_PUBLIC_FIREBASE_PROJECT_ID --project=kodomo-wallet)
export NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=$(gcloud secrets versions access latest --secret=NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET --project=kodomo-wallet)
export NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=$(gcloud secrets versions access latest --secret=NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID --project=kodomo-wallet)
export NEXT_PUBLIC_FIREBASE_APP_ID=$(gcloud secrets versions access latest --secret=NEXT_PUBLIC_FIREBASE_APP_ID --project=kodomo-wallet)
export NEXT_PUBLIC_GRAPHQL_ENDPOINT=$(gcloud secrets versions access latest --secret=NEXT_PUBLIC_GRAPHQL_ENDPOINT --project=kodomo-wallet)
export IMAGE_TAG=latest

./scripts/gcp/deploy_frontend.sh
```

### 3. 以降のデプロイ

`main` ブランチへの push で GitHub Actions (`deploy-frontend.yml`) が自動実行。

### 4. Firebase 承認済みドメインに追加

Firebase Console → Authentication → Settings → 承認済みドメイン に追加：

```
kodomo-wallet-frontend-ptfunabkpq-an.a.run.app
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
| `keepalive.yml` | 毎日 UTC 00:00 (JST 9:00) | Cloud Run ping |

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

#### Firebase 設定確認

- [ ] Firebase Console の承認済みドメインに prod frontend URL が追加済み
- [ ] Firebase Authentication で Google ログインが有効化済み
- [ ] Firestore `(default)` DB が作成済み（`setup_prod.sh` で自動作成）

#### Secret Manager 登録値の確認

```bash
export PROJECT_ID=kodomo-wallet

for SECRET in FIREBASE_SERVICE_ACCOUNT SECRET_KEY FRONTEND_ORIGIN \
              NEXT_PUBLIC_FIREBASE_API_KEY NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN \
              NEXT_PUBLIC_FIREBASE_PROJECT_ID NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET \
              NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID NEXT_PUBLIC_FIREBASE_APP_ID \
              NEXT_PUBLIC_GRAPHQL_ENDPOINT; do
  echo -n "$SECRET: "
  gcloud secrets versions access latest --secret="$SECRET" --project="$PROJECT_ID" \
    | cut -c1-40
  echo
done
```

### 2. main ブランチへのマージ・デプロイ

すべての確認が完了したら feature ブランチを main にマージする：

```bash
git checkout main
git merge feature/migrate-supabase-to-firestore
git push origin main
```

`main` へのプッシュで GitHub Actions が自動的に backend・frontend を prod にデプロイする。

### 3. 機能確認（ブラウザ手動）

デプロイ完了後、以下の導線をブラウザで動作確認する：

| 確認項目 | 手順 |
|---|---|
| Google ログイン | `$FRONTEND_URL/login` → Google 認証 → ダッシュボードへリダイレクト |
| 家族作成 | 初回ログイン → 家族作成フォーム → toast 表示 → ダッシュボード表示 |
| 入金 | ダッシュボード → 入金操作 → 残高反映 |
| 出金申請 | 出金申請 → 承認フロー確認 |
| 親招待 | 招待フロー → 受諾 |
| プロフィール | プロフィール画像アップロード |

### 4. 旧サービス停止（確認後）

機能確認がすべて Pass したら旧シークレットを削除する：

```bash
export PROJECT_ID=kodomo-wallet

for SECRET in DATABASE_URL SUPABASE_URL SUPABASE_KEY \
              NEXT_PUBLIC_SUPABASE_URL NEXT_PUBLIC_SUPABASE_ANON_KEY; do
  gcloud secrets delete "$SECRET" --project "$PROJECT_ID" --quiet && echo "deleted $SECRET"
done
```

### 5. 切替後の監視（24〜48 時間）

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

### 6. ロールバック手順

問題が発生した場合、Cloud Run の前リビジョンに戻す：

```bash
export PROJECT_ID=kodomo-wallet
export REGION=asia-northeast1

# 直前のリビジョン一覧
gcloud run revisions list --service kodomo-wallet-backend \
  --region "$REGION" --project "$PROJECT_ID" --limit 5

# 特定リビジョンにトラフィックを全量戻す
gcloud run services update-traffic kodomo-wallet-backend \
  --to-revisions [REVISION_NAME]=100 \
  --region "$REGION" --project "$PROJECT_ID"
```

### 7. 完了条件

- [ ] `$BACKEND_URL/health` が `{"status":"healthy"}` を返す
- [ ] `$FRONTEND_URL` でブラウザから Google ログインできる
- [ ] 家族作成・入金・出金申請が正常動作する
- [ ] keepalive workflow が正常実行される
- [ ] 旧 Supabase シークレットが削除済み（または削除計画が確定済み）
