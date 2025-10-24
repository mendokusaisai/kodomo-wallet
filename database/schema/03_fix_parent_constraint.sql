-- ========================================
-- 親アカウント削除制約の修正
-- ========================================
-- 既存のデータベースに適用するマイグレーションスクリプト
-- 子どもがいる親は削除できないように ON DELETE RESTRICT を設定

-- 既存の外部キー制約を削除
ALTER TABLE profiles
DROP CONSTRAINT IF EXISTS profiles_parent_id_fkey;

-- ON DELETE RESTRICT を指定した外部キー制約を再作成
ALTER TABLE profiles
ADD CONSTRAINT profiles_parent_id_fkey
  FOREIGN KEY (parent_id)
  REFERENCES profiles(id)
  ON DELETE RESTRICT;

-- ========================================
-- 説明
-- ========================================
-- ON DELETE RESTRICT:
--   親プロフィールを削除しようとした際、
--   その親に紐づく子どもプロフィールが存在する場合、
--   削除操作がブロックされエラーが返されます。
--
-- これにより、親を削除する前に
-- すべての子どもアカウントを先に削除する必要があります。
