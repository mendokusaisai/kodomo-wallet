-- ========================================
-- handle_new_user トリガーの更新
-- ========================================
-- 変更内容:
-- 既存の認証なしプロフィール（email照合）があれば紐付け、
-- なければ新規作成
-- ========================================

-- 既存のトリガー関数を削除
DROP FUNCTION IF EXISTS public.handle_new_user() CASCADE;

-- 新しいトリガー関数を作成
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  existing_profile_id UUID;
BEGIN
  -- 同じメールアドレスで認証なしプロフィールが存在するか確認
  SELECT id INTO existing_profile_id
  FROM public.profiles
  WHERE email = NEW.email
    AND auth_user_id IS NULL
  LIMIT 1;

  IF existing_profile_id IS NOT NULL THEN
    -- 既存プロフィールに auth_user_id を設定（紐付け）
    UPDATE public.profiles
    SET auth_user_id = NEW.id,
        updated_at = NOW()
    WHERE id = existing_profile_id;

    RAISE NOTICE '既存プロフィール % を認証アカウント % に紐付けました', existing_profile_id, NEW.id;
  ELSE
    -- 新規プロフィール作成（通常のサインアップは必ず親）
    INSERT INTO public.profiles (id, auth_user_id, name, role, created_at, updated_at)
    VALUES (
      gen_random_uuid(),
      NEW.id,
      COALESCE(NEW.raw_user_meta_data->>'name', 'ユーザー'),
      COALESCE(NEW.raw_user_meta_data->>'role', 'parent'),
      NOW(),
      NOW()
    );

    RAISE NOTICE '新規プロフィールを作成しました（auth_user_id: %）', NEW.id;
  END IF;

  RETURN NEW;
END;
$$;

-- トリガーを再作成
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- 確認クエリ
SELECT
  p.id,
  p.auth_user_id,
  p.email,
  p.name,
  p.role,
  CASE
    WHEN p.auth_user_id IS NULL THEN '認証なし'
    ELSE '認証あり'
  END as status
FROM profiles p
ORDER BY p.created_at DESC;
