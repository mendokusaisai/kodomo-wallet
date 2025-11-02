-- ========================================
-- parent_invites テーブル作成
-- 親招待（メール/リンク）機能用のテーブル
-- ========================================

-- 依存: gen_random_uuid()
-- 拡張機能が未有効の場合: CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS parent_invites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  token UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  child_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  inviter_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','accepted','expired','cancelled')),
  expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '7 days'),
  created_at TIMESTAMPTZ NOT NULL DEFAULT TIMEZONE('utc'::text, NOW())
);

CREATE INDEX IF NOT EXISTS idx_parent_invites_token ON parent_invites(token);
CREATE INDEX IF NOT EXISTS idx_parent_invites_child ON parent_invites(child_id);
CREATE INDEX IF NOT EXISTS idx_parent_invites_inviter ON parent_invites(inviter_id);
CREATE INDEX IF NOT EXISTS idx_parent_invites_email ON parent_invites(email);

-- 既存データ移行は不要（新規発行のみ）
