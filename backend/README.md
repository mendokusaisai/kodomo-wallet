# こどもウォレット - バックエンド API 🚀

FastAPI + GraphQL (Strawberry) によるバックエンドAPI。

## 技術スタック 🛠️

- **Python 3.14**
- **FastAPI**
- **Strawberry GraphQL**
- **Firestore** (NoSQL データベース)
- **Firebase Auth** (認証)
- **uv** (パッケージマネージャー)

## 開発環境セットアップ 🚀

### 1. 依存関係のインストール

```bash
uv sync
```

### 2. 環境変数の設定

`.env` ファイルを作成:

```env
# Firebase サービスアカウント (JSONファイルのパスまたはJSON文字列)
FIREBASE_SERVICE_ACCOUNT=path/to/service-account.json

# フロントエンド Origin (CORS)
FRONTEND_ORIGIN=http://localhost:3000

# アプリセキュリティ
SECRET_KEY=your-secret-key
```

### 3. サーバー起動

```bash
uv run uvicorn app.main:app --reload
```

**アクセス先:**
- GraphQL Playground: http://localhost:8000/graphql
- API Docs: http://localhost:8000/docs

## 主な機能 ✨

- 👨‍👩‍👧‍👦 プロフィール・親子関係管理
- 💰 アカウント・残高管理
- 📊 トランザクション (入金・出金・承認)
- ✉️ 親子招待システム
- 🔐 Firebase Auth 統合

## ディレクトリ構成 📁

```
app/
├── api/
│   └── graphql/        # GraphQLスキーマ・リゾルバー
├── core/               # 設定・DI・データベース
├── domain/             # エンティティ
├── repositories/       # データアクセス層
└── services/           # ビジネスロジック
```

## テスト 🧪

```bash
uv run pytest
```

## デプロイ 🌐

Google Cloud Run にデプロイ。Secret Manager で環境変数を管理。

詳細は [docs/gcp-runbook.md](../docs/gcp-runbook.md) を参照。

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
│   │   ├── database.py         # Firestore 接続
│   │   ├── container.py        # DI コンテナ
│   │   └── context.py          # GraphQL コンテキスト
│   ├── domain/
│   │   └── entities.py         # ドメインエンティティ
│   ├── repositories/
│   │   └── interfaces.py       # Repository インターフェース
│   └── services/               # ビジネスロジック
├── pyproject.toml              # プロジェクト設定
└── README.md                   # このファイル
```

### トラブルシューティング

**起動時のエラー: "ModuleNotFoundError"**
```bash
# 依存関係を再インストール
uv sync --reinstall
```

## 📚 関連ドキュメント

- [GraphQL Playground](http://127.0.0.1:8000/graphql) - APIテスト用
- [FastAPI Docs](http://127.0.0.1:8000/docs) - 自動生成されたAPI仕様
- [GCP Runbook](../docs/gcp-runbook.md) - デプロイ・運用手順
