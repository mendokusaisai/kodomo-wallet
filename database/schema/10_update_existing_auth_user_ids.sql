-- ========================================
-- 既存の認証済みプロフィールに auth_user_id を設定
-- ========================================

-- 認証済みプロフィール（profiles.id が auth.users.id と一致）の auth_user_id を設定
-- 重要: 仮アカウント（@temp.kodomo-wallet.local）は除外
UPDATE profiles
SET auth_user_id = id
WHERE id IN (
  SELECT id FROM auth.users
  WHERE email NOT LIKE '%@temp.kodomo-wallet.local'
);

-- 確認用ログ出力
DO $$
DECLARE
  total_profiles INTEGER;
  auth_profiles INTEGER;
  temp_profiles INTEGER;
BEGIN
  SELECT COUNT(*) INTO total_profiles FROM profiles;
  SELECT COUNT(*) INTO auth_profiles FROM profiles WHERE auth_user_id IS NOT NULL;
  SELECT COUNT(*) INTO temp_profiles FROM auth.users WHERE email LIKE '%@temp.kodomo-wallet.local';
  RAISE NOTICE '全プロフィール数: %', total_profiles;
  RAISE NOTICE '認証済みプロフィール数: %', auth_profiles;
  RAISE NOTICE '仮アカウント数: %', temp_profiles;
  RAISE NOTICE '未認証プロフィール数: %', (total_profiles - auth_profiles);
END $$;
