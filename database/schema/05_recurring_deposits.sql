-- 定期お小遣い自動入金設定テーブル

-- recurring_depositsテーブル作成
CREATE TABLE IF NOT EXISTS recurring_deposits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL CHECK (amount > 0),
    day_of_month INTEGER NOT NULL CHECK (day_of_month >= 1 AND day_of_month <= 31),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX idx_recurring_deposits_account_id ON recurring_deposits(account_id);
CREATE INDEX idx_recurring_deposits_is_active ON recurring_deposits(is_active);

-- コメント追加
COMMENT ON TABLE recurring_deposits IS '定期お小遣い自動入金設定';
COMMENT ON COLUMN recurring_deposits.id IS '設定ID';
COMMENT ON COLUMN recurring_deposits.account_id IS 'アカウントID';
COMMENT ON COLUMN recurring_deposits.amount IS '入金額（円）';
COMMENT ON COLUMN recurring_deposits.day_of_month IS '毎月の入金日（1-31）';
COMMENT ON COLUMN recurring_deposits.is_active IS '有効/無効フラグ';
COMMENT ON COLUMN recurring_deposits.created_at IS '作成日時';
COMMENT ON COLUMN recurring_deposits.updated_at IS '更新日時';

-- 更新日時の自動更新トリガー
CREATE OR REPLACE FUNCTION update_recurring_deposits_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_recurring_deposits_updated_at
    BEFORE UPDATE ON recurring_deposits
    FOR EACH ROW
    EXECUTE FUNCTION update_recurring_deposits_updated_at();
