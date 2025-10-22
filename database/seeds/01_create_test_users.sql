-- ========================================
-- テストユーザー作成スクリプト
-- ========================================
-- Supabase Dashboard で認証ユーザーを作成する代わりに、
-- SQLで直接 auth.users にテストユーザーを作成します
-- ========================================

DO $$
DECLARE
  parent_id UUID;
  child1_id UUID;
  child2_id UUID;
BEGIN
  -- 既存ユーザーをチェックして、なければ作成

  -- 親ユーザー
  SELECT id INTO parent_id FROM auth.users WHERE email = 'parent@test.com';

  IF parent_id IS NULL THEN
    INSERT INTO auth.users (
      id,
      instance_id,
      email,
      encrypted_password,
      email_confirmed_at,
      raw_app_meta_data,
      raw_user_meta_data,
      aud,
      role,
      created_at,
      updated_at,
      confirmation_token,
      email_change,
      email_change_token_new,
      recovery_token
    ) VALUES (
      gen_random_uuid(),
      '00000000-0000-0000-0000-000000000000',
      'parent@test.com',
      crypt('password123', gen_salt('bf')),
      NOW(),
      '{"provider":"email","providers":["email"]}',
      '{}',
      'authenticated',
      'authenticated',
      NOW(),
      NOW(),
      '',
      '',
      '',
      ''
    )
    RETURNING id INTO parent_id;
    RAISE NOTICE '親ユーザー作成: %', parent_id;
  ELSE
    RAISE NOTICE '親ユーザー既存: %', parent_id;
  END IF;

  -- 子供1
  SELECT id INTO child1_id FROM auth.users WHERE email = 'child1@test.com';

  IF child1_id IS NULL THEN
    INSERT INTO auth.users (
      id,
      instance_id,
      email,
      encrypted_password,
      email_confirmed_at,
      raw_app_meta_data,
      raw_user_meta_data,
      aud,
      role,
      created_at,
      updated_at,
      confirmation_token,
      email_change,
      email_change_token_new,
      recovery_token
    ) VALUES (
      gen_random_uuid(),
      '00000000-0000-0000-0000-000000000000',
      'child1@test.com',
      crypt('password123', gen_salt('bf')),
      NOW(),
      '{"provider":"email","providers":["email"]}',
      '{}',
      'authenticated',
      'authenticated',
      NOW(),
      NOW(),
      '',
      '',
      '',
      ''
    )
    RETURNING id INTO child1_id;
    RAISE NOTICE '子供1作成: %', child1_id;
  ELSE
    RAISE NOTICE '子供1既存: %', child1_id;
  END IF;

  -- 子供2
  SELECT id INTO child2_id FROM auth.users WHERE email = 'child2@test.com';

  IF child2_id IS NULL THEN
    INSERT INTO auth.users (
      id,
      instance_id,
      email,
      encrypted_password,
      email_confirmed_at,
      raw_app_meta_data,
      raw_user_meta_data,
      aud,
      role,
      created_at,
      updated_at,
      confirmation_token,
      email_change,
      email_change_token_new,
      recovery_token
    ) VALUES (
      gen_random_uuid(),
      '00000000-0000-0000-0000-000000000000',
      'child2@test.com',
      crypt('password123', gen_salt('bf')),
      NOW(),
      '{"provider":"email","providers":["email"]}',
      '{}',
      'authenticated',
      'authenticated',
      NOW(),
      NOW(),
      '',
      '',
      '',
      ''
    )
    RETURNING id INTO child2_id;
    RAISE NOTICE '子供2作成: %', child2_id;
  ELSE
    RAISE NOTICE '子供2既存: %', child2_id;
  END IF;

  RAISE NOTICE '==========================================';
  RAISE NOTICE 'テストユーザー作成完了！';
  RAISE NOTICE '==========================================';
END $$;

-- 作成したユーザーを確認
SELECT id, email, created_at
FROM auth.users
WHERE email LIKE '%@test.com'
ORDER BY created_at DESC;
