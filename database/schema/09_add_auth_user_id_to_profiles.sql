-- ========================================
-- profiles テーブルに auth_user_id カラムを追加
-- ========================================

-- auth_user_id カラムを追加（認証済みユーザーのID）
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS auth_user_id UUID;

-- インデックスを追加（auth_user_id での検索を高速化）
CREATE INDEX IF NOT EXISTS idx_profiles_auth_user_id ON profiles(auth_user_id);

-- コメント
COMMENT ON COLUMN profiles.auth_user_id IS '認証済みユーザーのID（auth.users.id）。認証なし子どもアカウントの場合はNULL';
