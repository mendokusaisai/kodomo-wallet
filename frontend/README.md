# こどもウォレット - フロントエンド 💰

親子でお小遣いを管理できるWebアプリケーションのフロントエンド。

## 技術スタック 🛠️

- **Next.js 15** (App Router)
- **TypeScript**
- **Apollo Client** (GraphQL)
- **Tailwind CSS**
- **Firebase Auth** (Google OAuth)

## 開発環境セットアップ 🚀

### 1. 依存関係のインストール

```bash
npm install
```

### 2. 環境変数の設定

`.env.local` ファイルを作成:

```env
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
NEXT_PUBLIC_GRAPHQL_ENDPOINT=http://localhost:8000/graphql
```

### 3. 開発サーバー起動

```bash
npm run dev
```

http://localhost:3000 でアクセス可能

## 主な機能 ✨

- 👨‍👩‍👧‍👦 親子アカウント管理
- 💸 お小遣いの入金・出金
- 🎯 貯金目標の設定
- 📊 トランザクション履歴
- 🔗 Google認証による子どもアカウント招待

## ディレクトリ構成 📁

```
src/
├── app/              # Next.js App Router
├── components/       # Reactコンポーネント
└── lib/
    ├── graphql/      # GraphQLクエリ・型定義
    └── firebase/     # Firebase認証
```

## デプロイ 🌐

Google Cloud Run にデプロイ。詳細は [docs/gcp-runbook.md](../docs/gcp-runbook.md) を参照。
