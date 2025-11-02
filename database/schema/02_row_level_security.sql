-- ========================================
-- Kodomo Wallet Row Level Security (RLS) 設定
-- ========================================
-- 注意: family_relationships テーブルの RLS は 05_family_relationships.sql で設定

-- RLS を有効化
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE withdrawal_requests ENABLE ROW LEVEL SECURITY;

-- ========================================
-- プロフィールテーブルのポリシー
-- ========================================

-- ユーザーは自分のプロフィールを閲覧可能
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = id);

-- ユーザーは自分のプロフィールを更新可能
CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);

-- ユーザーは自分のプロフィールを挿入可能
CREATE POLICY "Users can insert own profile" ON profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

-- 注意: 親が子供のプロフィールを閲覧するポリシーは 05_family_relationships.sql で設定

-- ========================================
-- アカウントテーブルのポリシー
-- ========================================
-- 注意: 親が子供のアカウントを閲覧/操作するポリシーは 05_family_relationships.sql で追加設定

-- ユーザーは自分のアカウントを閲覧可能
CREATE POLICY "Users can view own accounts" ON accounts
  FOR SELECT USING (
    user_id IN (
      SELECT id FROM profiles WHERE id = auth.uid()
    )
  );

-- ユーザーは自分のアカウントを作成可能
CREATE POLICY "Users can insert own accounts" ON accounts
  FOR INSERT WITH CHECK (user_id = auth.uid());

-- ユーザーは自分のアカウントを更新可能
CREATE POLICY "Users can update own accounts" ON accounts
  FOR UPDATE USING (user_id = auth.uid());

-- ========================================
-- トランザクションテーブルのポリシー
-- ========================================
-- 注意: 親が子供のトランザクションを閲覧/作成するポリシーは 05_family_relationships.sql で追加設定

-- ユーザーは自分のトランザクションを閲覧可能
CREATE POLICY "Users can view own transactions" ON transactions
  FOR SELECT USING (
    account_id IN (
      SELECT id FROM accounts WHERE user_id = auth.uid()
    )
  );

-- ユーザーは自分のトランザクションを作成可能
CREATE POLICY "Users can insert own transactions" ON transactions
  FOR INSERT WITH CHECK (
    account_id IN (
      SELECT id FROM accounts WHERE user_id = auth.uid()
    )
  );

-- ========================================
-- 出金リクエストテーブルのポリシー
-- ========================================
-- 注意: 親が子供の出金リクエストを閲覧/承認するポリシーは 05_family_relationships.sql で追加設定

-- ユーザーは自分の出金リクエストを閲覧可能
CREATE POLICY "Users can view own withdrawal requests" ON withdrawal_requests
  FOR SELECT USING (
    account_id IN (
      SELECT id FROM accounts WHERE user_id = auth.uid()
    )
  );

-- 子供は自分のアカウントで出金リクエストを作成可能
CREATE POLICY "Children can insert own withdrawal requests" ON withdrawal_requests
  FOR INSERT WITH CHECK (
    account_id IN (
      SELECT id FROM accounts WHERE user_id = auth.uid()
    )
  );
