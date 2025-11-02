-- ========================================
-- family_relationships テーブル作成と移行
-- ========================================

-- 新規テーブル作成
CREATE TABLE IF NOT EXISTS family_relationships (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  parent_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
  child_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
  relationship_type TEXT DEFAULT 'parent' CHECK (relationship_type IN ('parent', 'guardian')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  UNIQUE(parent_id, child_id)
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_family_relationships_parent_id ON family_relationships(parent_id);
CREATE INDEX IF NOT EXISTS idx_family_relationships_child_id ON family_relationships(child_id);

-- 既存データ移行（profiles.parent_id → family_relationships）
INSERT INTO family_relationships (parent_id, child_id, relationship_type, created_at)
SELECT parent_id, id, 'parent', created_at
FROM profiles
WHERE parent_id IS NOT NULL
ON CONFLICT (parent_id, child_id) DO NOTHING;

-- スキーマ変更: profiles.parent_id を削除
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'profiles' AND column_name = 'parent_id'
  ) THEN
    ALTER TABLE profiles DROP COLUMN parent_id;
  END IF;
END $$;

-- ========================================
-- family_relationships テーブルの RLS 設定
-- ========================================

-- RLS を有効化
ALTER TABLE family_relationships ENABLE ROW LEVEL SECURITY;

-- ユーザーは自分の家族関係を閲覧可能
CREATE POLICY "Users can view own family relationships" ON family_relationships
  FOR SELECT USING (parent_id = auth.uid() OR child_id = auth.uid());

-- 親は家族関係を作成可能
CREATE POLICY "Parents can create family relationships" ON family_relationships
  FOR INSERT WITH CHECK (
    parent_id = auth.uid() AND EXISTS (
      SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'parent'
    )
  );

-- 親は家族関係を削除可能
CREATE POLICY "Parents can delete family relationships" ON family_relationships
  FOR DELETE USING (parent_id = auth.uid());

-- ========================================
-- 親子関係に基づく追加ポリシー
-- ========================================

-- 親は子供のプロフィールを閲覧可能
CREATE POLICY "Parents can view children profiles" ON profiles
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM family_relationships fr
      WHERE fr.parent_id = auth.uid() AND fr.child_id = profiles.id
    )
  );

-- 親は子供のアカウントを閲覧可能
CREATE POLICY "Parents can view children accounts" ON accounts
  FOR SELECT USING (
    user_id IN (
      SELECT fr.child_id FROM family_relationships fr WHERE fr.parent_id = auth.uid()
    )
  );

-- 親は子供のアカウントを作成可能
CREATE POLICY "Parents can insert children accounts" ON accounts
  FOR INSERT WITH CHECK (
    user_id IN (
      SELECT fr.child_id FROM family_relationships fr WHERE fr.parent_id = auth.uid()
    )
  );

-- 親は子供のアカウントを更新可能
CREATE POLICY "Parents can update children accounts" ON accounts
  FOR UPDATE USING (
    user_id IN (
      SELECT fr.child_id FROM family_relationships fr WHERE fr.parent_id = auth.uid()
    )
  );

-- 親は子供のトランザクションを閲覧可能
CREATE POLICY "Parents can view children transactions" ON transactions
  FOR SELECT USING (
    account_id IN (
      SELECT a.id FROM accounts a
      JOIN family_relationships fr ON a.user_id = fr.child_id
      WHERE fr.parent_id = auth.uid()
    )
  );

-- 親はトランザクションを作成可能（自分または子供のアカウント）
CREATE POLICY "Parents can insert transactions" ON transactions
  FOR INSERT WITH CHECK (
    account_id IN (
      SELECT a.id FROM accounts a
      LEFT JOIN family_relationships fr ON a.user_id = fr.child_id
      WHERE fr.parent_id = auth.uid() OR a.user_id = auth.uid()
    )
  );

-- 親は子供の出金リクエストを閲覧可能
CREATE POLICY "Parents can view children withdrawal requests" ON withdrawal_requests
  FOR SELECT USING (
    account_id IN (
      SELECT a.id FROM accounts a
      JOIN family_relationships fr ON a.user_id = fr.child_id
      WHERE fr.parent_id = auth.uid()
    )
  );

-- 親のみ出金リクエストを更新可能（承認・拒否）
CREATE POLICY "Parents can update children withdrawal requests" ON withdrawal_requests
  FOR UPDATE USING (
    account_id IN (
      SELECT a.id FROM accounts a
      JOIN family_relationships fr ON a.user_id = fr.child_id
      WHERE fr.parent_id = auth.uid()
    )
  );
