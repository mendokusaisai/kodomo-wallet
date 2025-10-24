# Kodomo Wallet - Backend API

FastAPI + GraphQL (Strawberry) + SQLAlchemy によるバックエンドAPI

## 🚀 起動方法

### 前提条件

- Python 3.14
- uv (Python パッケージマネージャー)
- Supabase プロジェクト（PostgreSQL）

### 環境変数の設定

`.env` ファイルを作成して以下の環境変数を設定：

```env
# Supabase Database (Transaction Pooler)
DATABASE_URL=postgresql://postgres.xxx:[YOUR-PASSWORD]@xxx.pooler.supabase.com:6543/postgres

# Supabase Configuration
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# CORS Settings
FRONTEND_URL=http://localhost:3000
```

### 依存関係のインストール

```bash
# uvでプロジェクトの依存関係をインストール
uv sync
```

### サーバー起動

```bash
# 開発サーバーを起動（ホットリロード有効）
uv run uvicorn app.main:app --reload
```

サーバーが起動すると、以下のURLでアクセスできます：

- **API**: http://127.0.0.1:8000
- **GraphQL Playground**: http://127.0.0.1:8000/graphql
- **API Docs**: http://127.0.0.1:8000/docs

## 📋 GraphQL API

### クエリ例

```graphql
# ユーザープロフィール取得
query {
  me(userId: "user-uuid-here") {
    id
    name
    role
  }
}

# 子ども一覧取得（親のみ）
query {
  children(parentId: "parent-uuid-here") {
    id
    name
    email
    account {
      balance
      goalName
      goalAmount
    }
  }
}

# アカウント情報取得
query {
  accounts(userId: "user-uuid-here") {
    id
    balance
    currency
    goalName
    goalAmount
  }
}
```

### ミューテーション例

```graphql
# 入金
mutation {
  deposit(
    accountId: "account-uuid-here"
    amount: 1000
    description: "お小遣い"
  ) {
    id
    balance
  }
}

# 認証なし子ども作成
mutation {
  createChild(
    parentId: "parent-uuid-here"
    childName: "田中太郎"
    initialBalance: 1000
  ) {
    id
    name
    role
  }
}

# 招待メール送信
mutation {
  inviteChildToAuth(
    childId: "child-uuid-here"
    email: "child@example.com"
  ) {
    id
    name
    email
  }
}
```

## 🏗️ アーキテクチャ

```
backend/
├── app/
│   ├── main.py                 # FastAPI エントリーポイント
│   ├── api/
│   │   └── graphql/
│   │       ├── schema.py       # GraphQL スキーマ
│   │       ├── types.py        # GraphQL 型定義
│   │       └── resolvers.py    # リゾルバ関数
│   ├── core/
│   │   ├── config.py           # 設定
│   │   ├── database.py         # DB接続
│   │   ├── container.py        # DI コンテナ
│   │   └── context.py          # GraphQL コンテキスト
│   ├── models/
│   │   └── models.py           # SQLAlchemy モデル
│   ├── repositories/
│   │   ├── interfaces.py       # Repository インターフェース
│   │   └── sqlalchemy_repositories.py  # Repository 実装
│   └── services/
│       └── business_services.py  # ビジネスロジック
├── pyproject.toml              # プロジェクト設定
└── README.md                   # このファイル
```

## 🛠️ 技術スタック

- **FastAPI**: 0.1.0
- **Strawberry GraphQL**: 最新版
- **SQLAlchemy**: 2.x
- **PostgreSQL**: Supabase
- **dependency-injector**: DI コンテナ
- **httpx**: HTTP クライアント（Supabase Admin API用）
- **uvicorn**: ASGI サーバー

## 📝 開発メモ

### データベース接続

- Supabase Transaction Pooler を使用（`pooler.supabase.com:6543`）
- IPアドレス直接指定も可能（DNS問題がある場合）

### 注意事項

- Python 3.14 + Pydantic V1 の互換性警告が出ますが、動作に問題ありません
- `SUPABASE_SERVICE_ROLE_KEY` は管理者権限を持つため、安全に管理してください

### トラブルシューティング

**起動時のエラー: "ModuleNotFoundError"**
```bash
# 依存関係を再インストール
uv sync --reinstall
```

**データベース接続エラー**
```bash
# .env ファイルのDATABASE_URLを確認
# Transaction Pooler (port 6543) を使用しているか確認
```

## 📚 関連ドキュメント

- [GraphQL Playground](http://127.0.0.1:8000/graphql) - APIテスト用
- [FastAPI Docs](http://127.0.0.1:8000/docs) - 自動生成されたAPI仕様
- [進捗ログ](../documents/progress-log.md) - 開発進捗
