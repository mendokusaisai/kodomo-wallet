# こどもウォレット - フロントエンド 💰

親子でお小遣いを管理できるWebアプリケーションのフロントエンド。

## 技術スタック 🛠️

- **Next.js 14+** (App Router)
- **TypeScript**
- **Apollo Client** (GraphQL)
- **Tailwind CSS**
- **Supabase Auth** (Google OAuth)

## 開発環境セットアップ 🚀

### 1. 依存関係のインストール

```bash
npm install
```

### 2. 環境変数の設定

`.env.local` ファイルを作成:

```env
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
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
- 🔄 定期お小遣い設定
- 🔗 Google認証による子どもアカウント招待

## ディレクトリ構成 📁

```
src/
├── app/              # Next.js App Router
├── components/       # Reactコンポーネント
└── lib/
    ├── graphql/      # GraphQLクエリ・型定義
    └── supabase/     # Supabase認証・ストレージ
```

## デプロイ 🌐

Vercelにデプロイ可能。環境変数を設定してください。
