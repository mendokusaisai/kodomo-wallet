# Firestore スキーマ定義

## 概要

kodomo-wallet は Firestore をデータストアとして使用します。  
データモデルは **家族（Family）中心** で設計されており、口座は特定の子供アカウントに紐づかず、家族全体のリソースとして管理されます。

---

## コレクション構造

```
/families/{familyId}
  /members/{authUid}
  /accounts/{accountId}
    /transactions/{transactionId}

/recurringDeposits/{recurringDepositId}

/parentInvites/{token}

/childInvites/{token}
```

---

## ドキュメント定義

### `/families/{familyId}`

家族グループのルートドキュメント。

| フィールド   | 型         | 説明           |
|------------|-----------|----------------|
| `id`       | `string`  | 家族ID（自動生成） |
| `name`     | `string`  | 家族の名前（任意） |
| `createdAt`| `timestamp` | 作成日時       |

---

### `/families/{familyId}/members/{authUid}`

家族メンバー。`authUid` は Firebase Auth の UID と一致。

| フィールド     | 型         | 説明                     |
|--------------|-----------|--------------------------|
| `uid`        | `string`  | Firebase Auth UID        |
| `familyId`   | `string`  | 所属家族ID               |
| `name`       | `string`  | 表示名                   |
| `role`       | `string`  | `"parent"` or `"child"`  |
| `email`      | `string`  | メールアドレス（親のみ）    |
| `createdAt`  | `timestamp` | 作成日時               |
| `updatedAt`  | `timestamp` | 更新日時               |

**アクセス制御（Security Rules）:**
- `parent`: 読み書き可
- `child`: 読み取りのみ

---

### `/families/{familyId}/accounts/{accountId}`

家族が管理する口座。特定の子供に紐づかない。

| フィールド      | 型          | 説明                                    |
|---------------|------------|----------------------------------------|
| `id`          | `string`   | 口座ID（自動生成）                      |
| `familyId`    | `string`   | 所属家族ID                             |
| `name`        | `string`   | 口座名（例: "太郎の貯金箱"）            |
| `balance`     | `number`   | 残高（円）                              |
| `createdAt`   | `timestamp`| 作成日時                               |
| `updatedAt`   | `timestamp`| 更新日時                               |

**アクセス制御（Security Rules）:**
- `parent`: 読み書き可
- `child`: 読み取りのみ

---

### `/families/{familyId}/accounts/{accountId}/transactions/{transactionId}`

口座のトランザクション（入出金履歴）。

| フィールド       | 型           | 説明                                       |
|----------------|-------------|-------------------------------------------|
| `id`           | `string`    | トランザクションID（自動生成）              |
| `accountId`    | `string`    | 口座ID                                    |
| `familyId`     | `string`    | 家族ID（クエリ最適化用）                   |
| `amount`       | `number`    | 金額（正=入金、負=出金）                   |
| `type`         | `string`    | `"deposit"` / `"withdrawal"`              |
| `note`         | `string`    | 取引メモ（任意）                           |
| `createdAt`    | `timestamp` | 作成日時                                  |
| `createdByUid` | `string`    | 作成者の Firebase Auth UID                |

**アクセス制御（Security Rules）:**
- `parent`: 作成・読み取り可（更新・削除不可）
- `child`: 読み取りのみ

---

### `/recurringDeposits/{recurringDepositId}`

定期入金設定。

| フィールド         | 型           | 説明                                              |
|-----------------|-------------|--------------------------------------------------|
| `id`            | `string`    | 定期入金ID（自動生成）                            |
| `familyId`      | `string`    | 所属家族ID                                       |
| `accountId`     | `string`    | 対象口座ID                                       |
| `amount`        | `number`    | 定期入金額（円）                                 |
| `intervalDays`  | `number`    | 入金間隔（日）                                   |
| `nextExecuteAt` | `timestamp` | 次回実行予定日時                                 |
| `isActive`      | `boolean`   | 有効/無効フラグ                                  |
| `createdAt`     | `timestamp` | 作成日時                                         |
| `createdByUid`  | `string`    | 作成者の Firebase Auth UID                       |

**アクセス制御（Security Rules）:**
- 家族の `parent` のみ読み書き可

---

### `/parentInvites/{token}`

子供から親を招待するためのトークン。

| フィールド      | 型           | 説明                              |
|--------------|-------------|----------------------------------|
| `token`      | `string`    | 招待トークン（ドキュメントID兼用）  |
| `familyId`   | `string`    | 招待先家族ID                      |
| `inviterUid` | `string`    | 招待者（子供）の UID              |
| `email`      | `string`    | 招待先メールアドレス              |
| `expiresAt`  | `timestamp` | 有効期限                          |
| `acceptedAt` | `timestamp` | 承認日時（null = 未承認）         |
| `createdAt`  | `timestamp` | 作成日時                          |

---

### `/childInvites/{token}`

親から子供を招待するためのトークン。

| フィールド      | 型           | 説明                              |
|--------------|-------------|----------------------------------|
| `token`      | `string`    | 招待トークン（ドキュメントID兼用）  |
| `familyId`   | `string`    | 招待先家族ID                      |
| `inviterUid` | `string`    | 招待者（親）の UID                |
| `expiresAt`  | `timestamp` | 有効期限                          |
| `acceptedAt` | `timestamp` | 承認日時（null = 未承認）         |
| `createdByChildName` | `string` | 子供の名前（招待作成時に設定）   |
| `createdAt`  | `timestamp` | 作成日時                          |

---

## インデックス設計

Firestore の複合インデックスが必要なクエリ:

| コレクション                       | クエリ条件                                          | 目的                 |
|----------------------------------|----------------------------------------------------|--------------------|
| `families/{id}/accounts`         | `familyId` ==, `createdAt` desc                    | 家族の口座一覧       |
| `families/{id}/accounts/{id}/transactions` | `accountId` ==, `createdAt` desc        | 口座の取引履歴       |
| `recurringDeposits`              | `familyId` ==, `isActive` == true, `nextExecuteAt` <= now | 定期入金バッチ |
| `parentInvites`                  | `token` == （ドキュメントID のため不要）             | 招待承認             |
| `childInvites`                   | `token` == （ドキュメントID のため不要）             | 招待承認             |

---

## 旧 Supabase PostgreSQL との対応

| Supabase テーブル         | Firestore コレクション                          |
|--------------------------|------------------------------------------------|
| `profiles`               | `/families/{id}/members/{authUid}`             |
| `accounts`               | `/families/{id}/accounts/{id}`                 |
| `transactions`           | `/families/{id}/accounts/{id}/transactions/{id}` |
| `family_relationships`   | → `members` の `role` フィールドで代替          |
| `recurring_deposits`     | `/recurringDeposits/{id}`                      |
| `parent_invites`         | `/parentInvites/{token}`                       |
| `child_invites`          | `/childInvites/{token}`                        |
