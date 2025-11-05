-- ========================================
-- 仮アカウントの auth_user_id を NULL に修正
-- ========================================

-- 仮アカウント（@temp.kodomo-wallet.local）の auth_user_id を NULL に設定
UPDATE profiles
SET auth_user_id = NULL
WHERE id IN (
  SELECT id FROM auth.users
  WHERE email LIKE '%@temp.kodomo-wallet.local'
);

-- 確認用ログ出力
DO $$
DECLARE
  fixed_count INTEGER;
  auth_profiles INTEGER;
  unauth_profiles INTEGER;
BEGIN
  SELECT COUNT(*) INTO fixed_count
  FROM profiles p
  JOIN auth.users u ON p.id = u.id
  WHERE u.email LIKE '%@temp.kodomo-wallet.local' AND p.auth_user_id IS NULL;

  SELECT COUNT(*) INTO auth_profiles FROM profiles WHERE auth_user_id IS NOT NULL;
  SELECT COUNT(*) INTO unauth_profiles FROM profiles WHERE auth_user_id IS NULL;

  RAISE NOTICE '修正された仮アカウント数: %', fixed_count;
  RAISE NOTICE '認証済みプロフィール数: %', auth_profiles;
  RAISE NOTICE '未認証プロフィール数（仮アカウント含む）: %', unauth_profiles;
END $$;
