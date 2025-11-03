-- ========================================
-- child_invites テーブル作成
-- 子どもの認証アカウント作成招待機能用のテーブル
-- ========================================

-- 依存: gen_random_uuid()
-- 拡張機能が未有効の場合: CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS child_invites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  token UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  child_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','accepted','expired','cancelled')),
  expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '7 days'),
  created_at TIMESTAMPTZ NOT NULL DEFAULT TIMEZONE('utc'::text, NOW())
);

CREATE INDEX IF NOT EXISTS idx_child_invites_token ON child_invites(token);
CREATE INDEX IF NOT EXISTS idx_child_invites_child ON child_invites(child_id);
CREATE INDEX IF NOT EXISTS idx_child_invites_email ON child_invites(email);

-- 既存データ移行は不要（新規発行のみ）
