-- ========================================
-- テストデータ挿入スクリプト (完全版)
-- ========================================
-- 前提: 01_create_test_users.sql を先に実行済み
-- ========================================

DO $$
DECLARE
  parent_user_id UUID;
  child1_id UUID;
  child2_id UUID;
  parent_account_id UUID;
  child1_account_id UUID;
  child2_account_id UUID;
BEGIN
  -- auth.users から作成済みユーザーのIDを取得
  SELECT id INTO parent_user_id FROM auth.users WHERE email = 'parent@test.com';
  SELECT id INTO child1_id FROM auth.users WHERE email = 'child1@test.com';
  SELECT id INTO child2_id FROM auth.users WHERE email = 'child2@test.com';

  -- ユーザーが見つからない場合はエラー
  IF parent_user_id IS NULL THEN
    RAISE EXCEPTION '親ユーザーが見つかりません。先に 01_create_test_users.sql を実行してください。';
  END IF;

  -- ========================================
  -- 1. プロフィールを作成
  -- ========================================

  -- 親ユーザーのプロフィール
  INSERT INTO profiles (id, name, role, avatar_url, created_at, updated_at)
  VALUES (parent_user_id, '田中太郎（親）', 'parent', NULL, NOW(), NOW())
  ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

  -- 子供1のプロフィール
  INSERT INTO profiles (id, name, role, parent_id, avatar_url, created_at, updated_at)
  VALUES (child1_id, '田中花子', 'child', parent_user_id, NULL, NOW(), NOW())
  ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

  -- 子供2のプロフィール
  INSERT INTO profiles (id, name, role, parent_id, avatar_url, created_at, updated_at)
  VALUES (child2_id, '田中次郎', 'child', parent_user_id, NULL, NOW(), NOW())
  ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

  -- ========================================
  -- 2. アカウントを作成
  -- ========================================

  -- 親のアカウント
  INSERT INTO accounts (id, user_id, balance, currency, goal_name, goal_amount, created_at, updated_at)
  VALUES (gen_random_uuid(), parent_user_id, 50000, 'JPY', NULL, NULL, NOW(), NOW())
  ON CONFLICT DO NOTHING
  RETURNING id INTO parent_account_id;

  -- 子供1のアカウント（貯金目標あり）
  INSERT INTO accounts (id, user_id, balance, currency, goal_name, goal_amount, created_at, updated_at)
  VALUES (gen_random_uuid(), child1_id, 3500, 'JPY', 'ゲーム機を買う', 30000, NOW(), NOW())
  ON CONFLICT DO NOTHING
  RETURNING id INTO child1_account_id;

  -- 子供2のアカウント
  INSERT INTO accounts (id, user_id, balance, currency, goal_name, goal_amount, created_at, updated_at)
  VALUES (gen_random_uuid(), child2_id, 1200, 'JPY', '自転車', 25000, NOW(), NOW())
  ON CONFLICT DO NOTHING
  RETURNING id INTO child2_account_id;

  -- アカウントIDが取得できなかった場合（既存データ）、既存のIDを取得
  IF parent_account_id IS NULL THEN
    SELECT id INTO parent_account_id FROM accounts WHERE user_id = parent_user_id LIMIT 1;
  END IF;
  IF child1_account_id IS NULL THEN
    SELECT id INTO child1_account_id FROM accounts WHERE user_id = child1_id LIMIT 1;
  END IF;
  IF child2_account_id IS NULL THEN
    SELECT id INTO child2_account_id FROM accounts WHERE user_id = child2_id LIMIT 1;
  END IF;

  -- ========================================
  -- 3. トランザクション履歴を作成
  -- ========================================

  -- 既存のトランザクションを削除（重複を避けるため）
  DELETE FROM transactions WHERE account_id IN (child1_account_id, child2_account_id);

  -- 子供1のトランザクション
  INSERT INTO transactions (id, account_id, type, amount, description, created_at)
  VALUES
    (gen_random_uuid(), child1_account_id, 'deposit', 1000, 'お年玉', NOW() - INTERVAL '10 days'),
    (gen_random_uuid(), child1_account_id, 'deposit', 500, 'お手伝い', NOW() - INTERVAL '7 days'),
    (gen_random_uuid(), child1_account_id, 'deposit', 1000, '月のお小遣い', NOW() - INTERVAL '5 days'),
    (gen_random_uuid(), child1_account_id, 'reward', 500, 'テスト100点のご褒美', NOW() - INTERVAL '3 days'),
    (gen_random_uuid(), child1_account_id, 'deposit', 500, 'お手伝い', NOW() - INTERVAL '1 day');

  -- 子供2のトランザクション
  INSERT INTO transactions (id, account_id, type, amount, description, created_at)
  VALUES
    (gen_random_uuid(), child2_account_id, 'deposit', 500, '月のお小遣い', NOW() - INTERVAL '8 days'),
    (gen_random_uuid(), child2_account_id, 'deposit', 200, 'お手伝い', NOW() - INTERVAL '5 days'),
    (gen_random_uuid(), child2_account_id, 'deposit', 500, 'お手伝い', NOW() - INTERVAL '2 days');

  -- ========================================
  -- 4. 出金リクエストを作成
  -- ========================================

  -- 既存の出金リクエストを削除
  DELETE FROM withdrawal_requests WHERE account_id IN (child1_account_id, child2_account_id);

  -- 子供1からの出金リクエスト（保留中）
  INSERT INTO withdrawal_requests (id, account_id, amount, description, status, created_at, updated_at)
  VALUES
    (gen_random_uuid(), child1_account_id, 500, 'お菓子を買いたい', 'pending', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days');

  -- 子供2からの出金リクエスト（承認済み）
  INSERT INTO withdrawal_requests (id, account_id, amount, description, status, created_at, updated_at)
  VALUES
    (gen_random_uuid(), child2_account_id, 300, '文房具', 'approved', NOW() - INTERVAL '5 days', NOW() - INTERVAL '4 days');

  -- 作成したデータのIDを表示
  RAISE NOTICE '==========================================';
  RAISE NOTICE 'テストデータ作成完了！';
  RAISE NOTICE '==========================================';
  RAISE NOTICE '親ユーザーID: %', parent_user_id;
  RAISE NOTICE '子供1 ID: %', child1_id;
  RAISE NOTICE '子供2 ID: %', child2_id;
  RAISE NOTICE '親アカウントID: %', parent_account_id;
  RAISE NOTICE '子供1アカウントID: %', child1_account_id;
  RAISE NOTICE '子供2アカウントID: %', child2_account_id;
  RAISE NOTICE '==========================================';
  RAISE NOTICE 'ログイン情報:';
  RAISE NOTICE '親: parent@test.com / password123';
  RAISE NOTICE '子供1: child1@test.com / password123';
  RAISE NOTICE '子供2: child2@test.com / password123';
  RAISE NOTICE '==========================================';
END $$;
