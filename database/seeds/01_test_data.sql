-- ========================================
-- Kodomo Wallet テストデータ
-- ========================================
-- 前提: handle_new_user トリガーが設定済み
-- 実行方法: Supabase SQL Editor で実行
-- ========================================

DO $$
DECLARE
  parent_profile_id UUID;
  child1_profile_id UUID;
  child2_profile_id UUID;
  child1_account_id UUID;
  child2_account_id UUID;
BEGIN
  -- ========================================
  -- 1. 親プロフィールを取得（認証アカウント経由で作成済みと想定）
  -- ========================================
  -- 実際の運用では、親は /signup から登録し、トリガーで自動作成される
  -- テスト用に、既存の親アカウントを検索（なければスキップ）

  SELECT p.id INTO parent_profile_id
  FROM profiles p
  WHERE p.role = 'parent'
  LIMIT 1;

  IF parent_profile_id IS NULL THEN
    RAISE NOTICE '親プロフィールが見つかりません。先に親アカウントを作成してください（/signup から登録）';
    RETURN;
  END IF;

  RAISE NOTICE '親プロフィール ID: %', parent_profile_id;

  -- ========================================
  -- 2. 認証なし子どもプロフィールを作成
  -- ========================================

  -- 子ども1: 田中太郎
  INSERT INTO profiles (id, auth_user_id, email, name, role, parent_id, created_at, updated_at)
  VALUES (
    gen_random_uuid(),
    NULL,  -- 認証なし
    'test-taro@example.com',  -- 将来の招待用メールアドレス
    '田中太郎',
    'child',
    parent_profile_id,
    NOW(),
    NOW()
  )
  ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
  RETURNING id INTO child1_profile_id;

  -- 子ども2: 田中花子
  INSERT INTO profiles (id, auth_user_id, email, name, role, parent_id, created_at, updated_at)
  VALUES (
    gen_random_uuid(),
    NULL,  -- 認証なし
    'test-hanako@example.com',  -- 将来の招待用メールアドレス
    '田中花子',
    'child',
    parent_profile_id,
    NOW(),
    NOW()
  )
  ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
  RETURNING id INTO child2_profile_id;

  RAISE NOTICE '子ども1 プロフィール ID: %', child1_profile_id;
  RAISE NOTICE '子ども2 プロフィール ID: %', child2_profile_id;

  -- ========================================
  -- 3. 子どものアカウントを作成
  -- ========================================

  -- 子ども1のアカウント（貯金目標あり）
  INSERT INTO accounts (id, user_id, balance, currency, goal_name, goal_amount, created_at, updated_at)
  VALUES (
    gen_random_uuid(),
    child1_profile_id,
    3500,
    'JPY',
    'ゲーム機を買う',
    30000,
    NOW(),
    NOW()
  )
  ON CONFLICT DO NOTHING
  RETURNING id INTO child1_account_id;

  -- 子ども2のアカウント
  INSERT INTO accounts (id, user_id, balance, currency, goal_name, goal_amount, created_at, updated_at)
  VALUES (
    gen_random_uuid(),
    child2_profile_id,
    1200,
    'JPY',
    '自転車',
    25000,
    NOW(),
    NOW()
  )
  ON CONFLICT DO NOTHING
  RETURNING id INTO child2_account_id;

  -- 既存アカウントがある場合は取得
  IF child1_account_id IS NULL THEN
    SELECT id INTO child1_account_id FROM accounts WHERE user_id = child1_profile_id LIMIT 1;
  END IF;
  IF child2_account_id IS NULL THEN
    SELECT id INTO child2_account_id FROM accounts WHERE user_id = child2_profile_id LIMIT 1;
  END IF;

  RAISE NOTICE '子ども1 アカウント ID: %', child1_account_id;
  RAISE NOTICE '子ども2 アカウント ID: %', child2_account_id;

  -- ========================================
  -- 4. トランザクション履歴を作成
  -- ========================================

  -- 既存のトランザクションを削除（重複を避けるため）
  DELETE FROM transactions WHERE account_id IN (child1_account_id, child2_account_id);

  -- 子ども1のトランザクション
  INSERT INTO transactions (id, account_id, type, amount, description, created_at)
  VALUES
    (gen_random_uuid(), child1_account_id, 'deposit', 1000, 'お年玉', NOW() - INTERVAL '10 days'),
    (gen_random_uuid(), child1_account_id, 'deposit', 500, 'お手伝い', NOW() - INTERVAL '7 days'),
    (gen_random_uuid(), child1_account_id, 'deposit', 1000, '月のお小遣い', NOW() - INTERVAL '5 days'),
    (gen_random_uuid(), child1_account_id, 'reward', 500, 'テスト100点のご褒美', NOW() - INTERVAL '3 days'),
    (gen_random_uuid(), child1_account_id, 'deposit', 500, 'お手伝い', NOW() - INTERVAL '1 day');

  -- 子ども2のトランザクション
  INSERT INTO transactions (id, account_id, type, amount, description, created_at)
  VALUES
    (gen_random_uuid(), child2_account_id, 'deposit', 500, '月のお小遣い', NOW() - INTERVAL '8 days'),
    (gen_random_uuid(), child2_account_id, 'deposit', 200, 'お手伝い', NOW() - INTERVAL '5 days'),
    (gen_random_uuid(), child2_account_id, 'deposit', 500, 'お手伝い', NOW() - INTERVAL '2 days');

  RAISE NOTICE 'トランザクション作成完了';

END $$;

-- ========================================
-- 確認クエリ
-- ========================================

-- プロフィール確認
SELECT
  p.id,
  p.auth_user_id,
  p.email,
  p.name,
  p.role,
  CASE
    WHEN p.auth_user_id IS NULL THEN '認証なし'
    ELSE '認証あり'
  END as auth_status,
  pp.name as parent_name
FROM profiles p
LEFT JOIN profiles pp ON p.parent_id = pp.id
ORDER BY p.role DESC, p.created_at;

-- アカウント確認
SELECT
  a.id,
  p.name as user_name,
  p.role,
  a.balance,
  a.currency,
  a.goal_name,
  a.goal_amount
FROM accounts a
JOIN profiles p ON a.user_id = p.id
ORDER BY p.role DESC, p.created_at;

-- トランザクション確認
SELECT
  t.created_at,
  p.name as user_name,
  t.type,
  t.amount,
  t.description
FROM transactions t
JOIN accounts a ON t.account_id = a.id
JOIN profiles p ON a.user_id = p.id
ORDER BY t.created_at DESC;
