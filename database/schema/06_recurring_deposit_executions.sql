-- 定期入金実行履歴テーブル

-- recurring_deposit_executionsテーブル作成
CREATE TABLE IF NOT EXISTS recurring_deposit_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recurring_deposit_id UUID NOT NULL REFERENCES recurring_deposits(id) ON DELETE CASCADE,
    transaction_id UUID REFERENCES transactions(id) ON DELETE SET NULL,
    executed_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT NOT NULL CHECK (status IN ('success', 'failed', 'skipped')),
    error_message TEXT,
    amount INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL CHECK (day_of_month >= 1 AND day_of_month <= 31),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX idx_recurring_deposit_executions_recurring_deposit_id
    ON recurring_deposit_executions(recurring_deposit_id);
CREATE INDEX idx_recurring_deposit_executions_executed_at
    ON recurring_deposit_executions(executed_at);
CREATE INDEX idx_recurring_deposit_executions_status
    ON recurring_deposit_executions(status);

-- コメント追加
COMMENT ON TABLE recurring_deposit_executions IS '定期入金実行履歴（重複実行防止とエラーログ）';
COMMENT ON COLUMN recurring_deposit_executions.id IS '実行履歴ID';
COMMENT ON COLUMN recurring_deposit_executions.recurring_deposit_id IS '定期入金設定ID';
COMMENT ON COLUMN recurring_deposit_executions.transaction_id IS '作成されたトランザクションID（失敗時はNULL）';
COMMENT ON COLUMN recurring_deposit_executions.executed_at IS '実行日時';
COMMENT ON COLUMN recurring_deposit_executions.status IS '実行ステータス (success/failed/skipped)';
COMMENT ON COLUMN recurring_deposit_executions.error_message IS 'エラーメッセージ（失敗時のみ）';
COMMENT ON COLUMN recurring_deposit_executions.amount IS '実行時の金額';
COMMENT ON COLUMN recurring_deposit_executions.day_of_month IS '実行時の実行日設定';
COMMENT ON COLUMN recurring_deposit_executions.created_at IS '作成日時';
