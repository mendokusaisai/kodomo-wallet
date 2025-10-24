-- ========================================
-- 親アカウントの不要なアカウントを削除
-- ========================================
-- 親アカウント（role='parent'）は自分のアカウントを持たず、
-- 子どものアカウント管理のみを行う
-- ========================================

DO $$
DECLARE
  parent_user_id UUID;
BEGIN
  -- kodomo-test@outlook.com の親アカウントIDを取得
  SELECT id INTO parent_user_id
  FROM auth.users
  WHERE email = 'kodomo-test@outlook.com';

  IF parent_user_id IS NOT NULL THEN
    -- 親アカウントに紐づくアカウント（存在する場合）を削除
    DELETE FROM accounts
    WHERE user_id = parent_user_id;

    RAISE NOTICE '親アカウント（kodomo-test@outlook.com）のアカウントを削除しました';
  ELSE
    RAISE NOTICE '親アカウント（kodomo-test@outlook.com）が見つかりません';
  END IF;

  -- parent@test.com の親アカウントも同様に処理
  SELECT id INTO parent_user_id
  FROM auth.users
  WHERE email = 'parent@test.com';

  IF parent_user_id IS NOT NULL THEN
    DELETE FROM accounts
    WHERE user_id = parent_user_id;

    RAISE NOTICE '親アカウント（parent@test.com）のアカウントを削除しました';
  END IF;

END $$;

-- 確認: 親アカウントのアカウント数（0であるべき）
SELECT
  u.email,
  p.name,
  p.role,
  COUNT(a.id) as account_count
FROM auth.users u
JOIN profiles p ON u.id = p.id
LEFT JOIN accounts a ON p.id = a.user_id
WHERE p.role = 'parent'
GROUP BY u.email, p.name, p.role;

-- 確認: 子どもアカウントの一覧
SELECT
  u.email,
  p.name,
  p.role,
  a.balance,
  a.goal_name,
  a.goal_amount
FROM auth.users u
JOIN profiles p ON u.id = p.id
LEFT JOIN accounts a ON p.id = a.user_id
WHERE p.role = 'child'
ORDER BY u.email;
