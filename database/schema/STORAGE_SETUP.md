# Supabase Storage セットアップ

アバター画像のアップロード機能を使用するには、Supabaseでストレージバケットを作成する必要があります。

## セットアップ手順

### 方法1: SQLを実行する（推奨）

1. Supabaseダッシュボードにログイン
2. プロジェクトを選択
3. 左メニューから「SQL Editor」を選択
4. `database/schema/03_storage_setup.sql` の内容をコピー＆ペースト
5. 「Run」ボタンをクリックして実行

### 方法2: UIから手動作成

1. Supabaseダッシュボードにログイン
2. プロジェクトを選択
3. 左メニューから「Storage」を選択
4. 「New bucket」ボタンをクリック
5. 以下の設定でバケットを作成：
   - **Name**: `avatars`
   - **Public bucket**: チェックを入れる ✓
6. 作成したバケットを選択
7. 「Policies」タブを開く
8. 以下のポリシーを追加：

#### アップロードポリシー
- **Policy name**: Users can upload their own avatars
- **Allowed operation**: INSERT
- **Target roles**: authenticated
- **WITH CHECK expression**:
  ```sql
  bucket_id = 'avatars' AND (storage.foldername(name))[1] = auth.uid()::text
  ```

#### 閲覧ポリシー
- **Policy name**: Anyone can view avatars
- **Allowed operation**: SELECT
- **Target roles**: public
- **USING expression**:
  ```sql
  bucket_id = 'avatars'
  ```

#### 更新ポリシー
- **Policy name**: Users can update their own avatars
- **Allowed operation**: UPDATE
- **Target roles**: authenticated
- **USING expression**:
  ```sql
  bucket_id = 'avatars' AND (storage.foldername(name))[1] = auth.uid()::text
  ```
- **WITH CHECK expression**:
  ```sql
  bucket_id = 'avatars' AND (storage.foldername(name))[1] = auth.uid()::text
  ```

#### 削除ポリシー
- **Policy name**: Users can delete their own avatars
- **Allowed operation**: DELETE
- **Target roles**: authenticated
- **USING expression**:
  ```sql
  bucket_id = 'avatars' AND (storage.foldername(name))[1] = auth.uid()::text
  ```

## 動作確認

1. フロントエンドアプリケーションを起動
2. 設定ページにアクセス
3. アバター画像をアップロード
4. Supabaseダッシュボードの「Storage」で画像が保存されていることを確認

## セキュリティポリシー

- ユーザーは自分のユーザーIDフォルダ内にのみアップロード可能
- すべてのユーザーがアバター画像を閲覧可能（公開バケット）
- ユーザーは自分がアップロードした画像のみ更新・削除可能
- 最大ファイルサイズ: 5MB（フロントエンドで制限）
- 許可されるファイル形式: 画像ファイル（image/*）
