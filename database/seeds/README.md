# 🧪 テストデータのセットアップ# 🧪 テストデータのセットアップ



⚠️ **開発環境専用です。本番環境では実行しないでください。**⚠️ **開発環境専用です。本番環境では実行しないでください。**



## 📋 前提条件## � 手順



1. スキーマが作成済み（`database/schema/` の SQL を実行済み）Supabase SQL Editor で以下のスクリプトを**順番に**実行してください：

2. トリガーが設定済み（`04_update_handle_new_user_trigger.sql` 実行済み）

3. 親アカウントを作成済み（`/signup` から登録）### 1. 認証ユーザーを作成



## 🚀 手順```bash

01_create_test_users.sql

### 1. 親アカウントを作成```



フロントエンドの `/signup` ページから親アカウントを作成してください。これにより以下の認証ユーザーが作成されます：



- 例: `parent@example.com` / `password123`- 親: `parent@test.com` / `password123`

- 子供 1: `child1@test.com` / `password123`

トリガーにより自動的に `role = 'parent'` のプロフィールが作成されます。- 子供 2: `child2@test.com` / `password123`



### 2. テストデータを挿入### 2. テストデータを挿入



Supabase SQL Editor で以下のスクリプトを実行：```bash

02_insert_test_data.sql

```sql```

-- 01_test_data.sql を実行

```これにより以下が作成されます：



これにより以下が作成されます：- プロフィール（親 1 人、子供 2 人）

- アカウント（3 つ）

- **認証なし子どもプロフィール**（2人）- トランザクション履歴（8 件）

  - 田中太郎 (`test-taro@example.com`)- 出金リクエスト（2 件）

  - 田中花子 (`test-hanako@example.com`)

- **子どものアカウント**（2つ、貯金目標付き）## ✅ 確認

- **トランザクション履歴**（お小遣い、お手伝い報酬など）

実行後、NOTICE メッセージに各データの ID が表示されます。

## ✅ 確認

## 🧪 GraphQL API テスト

実行後、以下のクエリで確認できます：

http://localhost:8000/graphql でテストできます。

```sql

-- プロフィール確認**クエリ例：**

SELECT id, name, role, email,

  CASE WHEN auth_user_id IS NULL THEN '認証なし' ELSE '認証あり' END as status```graphql

FROM profilesquery {

ORDER BY role DESC, created_at;  me(userId: "生成されたユーザーID") {

    id

-- アカウント確認    name

SELECT p.name, a.balance, a.goal_name, a.goal_amount    role

FROM accounts a  }

JOIN profiles p ON a.user_id = p.id;}

``````



## 🔐 子どもの招待フロー（オプション）## 🔄 リセット



認証なし子どもを認証アカウントに移行する場合：データを削除してやり直す場合：



1. フロントエンドで親としてログイン```sql

2. ダッシュボードで「📧 招待メールを送信」をクリックDELETE FROM withdrawal_requests;

3. 子どものメールアドレスを入力して送信DELETE FROM transactions;

4. 子どもが招待メールからパスワード設定DELETE FROM accounts;

5. トリガーが自動的に既存プロフィールと紐付けDELETE FROM profiles;

DELETE FROM auth.users WHERE email LIKE '%@test.com';

## 🧪 GraphQL API テスト```


親アカウントでログイン後、http://localhost:8000/graphql でテストできます。

**クエリ例：**

```graphql
query {
  me {
    id
    name
    role
  }
  children {
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

## 🔄 リセット

データを削除してやり直す場合：

```sql
-- トランザクションとアカウントを削除
DELETE FROM transactions;
DELETE FROM accounts;

-- 認証なし子どもプロフィールを削除
DELETE FROM profiles WHERE auth_user_id IS NULL;

-- 親プロフィールは手動で削除（認証ユーザーも削除される）
-- DELETE FROM auth.users WHERE email = 'parent@example.com';
```

## 📁 ファイル構成

```
database/
├── schema/           # データベーススキーマ
│   ├── 01_create_tables.sql              # テーブル定義
│   ├── 02_row_level_security.sql         # RLSポリシー
│   └── 04_update_handle_new_user_trigger.sql  # トリガー（親/子ロール自動設定）
└── seeds/            # テストデータ
    ├── 01_test_data.sql   # テストデータ（認証なし子ども2人）
    └── README.md          # このファイル
```
