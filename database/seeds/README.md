# 🧪 テストデータのセットアップ

⚠️ **開発環境専用です。本番環境では実行しないでください。**

## � 手順

Supabase SQL Editor で以下のスクリプトを**順番に**実行してください：

### 1. 認証ユーザーを作成

```bash
01_create_test_users.sql
```

これにより以下の認証ユーザーが作成されます：

- 親: `parent@test.com` / `password123`
- 子供 1: `child1@test.com` / `password123`
- 子供 2: `child2@test.com` / `password123`

### 2. テストデータを挿入

```bash
02_insert_test_data.sql
```

これにより以下が作成されます：

- プロフィール（親 1 人、子供 2 人）
- アカウント（3 つ）
- トランザクション履歴（8 件）
- 出金リクエスト（2 件）

## ✅ 確認

実行後、NOTICE メッセージに各データの ID が表示されます。

## 🧪 GraphQL API テスト

http://localhost:8000/graphql でテストできます。

**クエリ例：**

```graphql
query {
  me(userId: "生成されたユーザーID") {
    id
    name
    role
  }
}
```

## 🔄 リセット

データを削除してやり直す場合：

```sql
DELETE FROM withdrawal_requests;
DELETE FROM transactions;
DELETE FROM accounts;
DELETE FROM profiles;
DELETE FROM auth.users WHERE email LIKE '%@test.com';
```
