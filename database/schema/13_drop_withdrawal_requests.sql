-- 出金申請機能の削除マイグレーション
-- withdrawal_requests テーブルおよび関連オブジェクトを削除する

-- RLS ポリシーを削除
DROP POLICY IF EXISTS "Users can view own withdrawal requests" ON withdrawal_requests;
DROP POLICY IF EXISTS "Children can insert own withdrawal requests" ON withdrawal_requests;
DROP POLICY IF EXISTS "Parents can view children withdrawal requests" ON withdrawal_requests;
DROP POLICY IF EXISTS "Parents can update children withdrawal requests" ON withdrawal_requests;

-- トリガーを削除
DROP TRIGGER IF EXISTS update_withdrawal_requests_updated_at ON withdrawal_requests;

-- テーブルを削除（インデックスも自動削除）
DROP TABLE IF EXISTS withdrawal_requests;
