-- ========================================
-- 既存の認証済みプロフィールに auth_user_id を設定
-- ========================================

-- 認証済みプロフィール（profiles.id が auth.users.id と一致）の auth_user_id を設定
UPDATE profiles
SET auth_user_id = id
WHERE id IN (SELECT id FROM auth.users);

-- 確認用ログ出力
DO $$
DECLARE
  updated_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO updated_count FROM profiles WHERE auth_user_id IS NOT NULL;
  RAISE NOTICE '認証済みプロフィール数: %', updated_count;
END $$;
