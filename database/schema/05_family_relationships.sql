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
