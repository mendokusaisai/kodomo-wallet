-- ========================================
-- handle_new_user トリガーの作成
-- ========================================
-- 変更内容:
-- auth.users に新規ユーザーが作成されたら、
-- 対応する profiles レコードを自動作成
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
BEGIN
  -- 新規プロフィール作成（通常のサインアップは必ず親）
  INSERT INTO public.profiles (id, name, role, created_at, updated_at)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'name', 'ユーザー'),
    COALESCE(NEW.raw_user_meta_data->>'role', 'parent'),
    NOW(),
    NOW()
  );

  RAISE NOTICE '新規プロフィールを作成しました（id: %）', NEW.id;

  RETURN NEW;
END;
$$;

-- トリガーを再作成
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();
