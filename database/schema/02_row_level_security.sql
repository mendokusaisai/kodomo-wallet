-- ========================================
-- Kodomo Wallet Row Level Security (RLS) 設定
-- ========================================

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

-- 親は子供のプロフィールを閲覧可能
CREATE POLICY "Parents can view children profiles" ON profiles
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE id = auth.uid() AND role = 'parent'
    ) AND parent_id = auth.uid()
  );

-- ユーザーは自分のプロフィールを更新可能
CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);

-- ユーザーは自分のプロフィールを挿入可能
CREATE POLICY "Users can insert own profile" ON profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

-- 親は子供のプロフィールを作成可能
CREATE POLICY "Parents can insert children profiles" ON profiles
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE id = auth.uid() AND role = 'parent'
    ) AND parent_id = auth.uid()
  );

-- ========================================
-- アカウントテーブルのポリシー
-- ========================================

-- ユーザーは自分のアカウントを閲覧可能
CREATE POLICY "Users can view own accounts" ON accounts
  FOR SELECT USING (
    user_id IN (
      SELECT id FROM profiles WHERE id = auth.uid()
    )
  );

-- 親は子供のアカウントを閲覧可能
CREATE POLICY "Parents can view children accounts" ON accounts
  FOR SELECT USING (
    user_id IN (
      SELECT id FROM profiles
      WHERE parent_id = auth.uid()
    )
  );

-- ユーザーは自分のアカウントを作成可能
CREATE POLICY "Users can insert own accounts" ON accounts
  FOR INSERT WITH CHECK (user_id = auth.uid());

-- 親は子供のアカウントを作成可能
CREATE POLICY "Parents can insert children accounts" ON accounts
  FOR INSERT WITH CHECK (
    user_id IN (
      SELECT id FROM profiles
      WHERE parent_id = auth.uid()
    )
  );

-- ユーザーは自分のアカウントを更新可能
CREATE POLICY "Users can update own accounts" ON accounts
  FOR UPDATE USING (user_id = auth.uid());

-- 親は子供のアカウントを更新可能
CREATE POLICY "Parents can update children accounts" ON accounts
  FOR UPDATE USING (
    user_id IN (
      SELECT id FROM profiles
      WHERE parent_id = auth.uid()
    )
  );

-- ========================================
-- トランザクションテーブルのポリシー
-- ========================================

-- ユーザーは自分のトランザクションを閲覧可能
CREATE POLICY "Users can view own transactions" ON transactions
  FOR SELECT USING (
    account_id IN (
      SELECT id FROM accounts WHERE user_id = auth.uid()
    )
  );

-- 親は子供のトランザクションを閲覧可能
CREATE POLICY "Parents can view children transactions" ON transactions
  FOR SELECT USING (
    account_id IN (
      SELECT a.id FROM accounts a
      JOIN profiles p ON a.user_id = p.id
      WHERE p.parent_id = auth.uid()
    )
  );

-- 親のみトランザクションを作成可能（入金・出金）
CREATE POLICY "Parents can insert transactions" ON transactions
  FOR INSERT WITH CHECK (
    account_id IN (
      SELECT a.id FROM accounts a
      JOIN profiles p ON a.user_id = p.id
      WHERE p.parent_id = auth.uid() OR a.user_id = auth.uid()
    )
  );

-- ========================================
-- 出金リクエストテーブルのポリシー
-- ========================================

-- ユーザーは自分の出金リクエストを閲覧可能
CREATE POLICY "Users can view own withdrawal requests" ON withdrawal_requests
  FOR SELECT USING (
    account_id IN (
      SELECT id FROM accounts WHERE user_id = auth.uid()
    )
  );

-- 親は子供の出金リクエストを閲覧可能
CREATE POLICY "Parents can view children withdrawal requests" ON withdrawal_requests
  FOR SELECT USING (
    account_id IN (
      SELECT a.id FROM accounts a
      JOIN profiles p ON a.user_id = p.id
      WHERE p.parent_id = auth.uid()
    )
  );

-- 子供は自分のアカウントで出金リクエストを作成可能
CREATE POLICY "Children can insert own withdrawal requests" ON withdrawal_requests
  FOR INSERT WITH CHECK (
    account_id IN (
      SELECT id FROM accounts WHERE user_id = auth.uid()
    )
  );

-- 親のみ出金リクエストを更新可能（承認・拒否）
CREATE POLICY "Parents can update children withdrawal requests" ON withdrawal_requests
  FOR UPDATE USING (
    account_id IN (
      SELECT a.id FROM accounts a
      JOIN profiles p ON a.user_id = p.id
      WHERE p.parent_id = auth.uid()
    )
  );
