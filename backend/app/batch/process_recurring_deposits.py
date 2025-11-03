"""
定期入金バッチ処理スクリプト

このスクリプトは毎日実行され、以下の処理を行います:
1. 今日が実行日の定期入金設定を取得
2. 今月まだ実行されていない設定に対してトランザクションを作成
3. 実行履歴を記録（成功/失敗）

使用方法:
    python -m app.batch.process_recurring_deposits
"""

import sys
from datetime import UTC, datetime
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.container import create_injector
from app.core.database import get_db
from app.repositories.interfaces import (
    AccountRepository,
    RecurringDepositExecutionRepository,
    RecurringDepositRepository,
)
from app.services import TransactionService


def process_recurring_deposits():
    """定期入金を処理するメイン関数"""
    print("=" * 60)
    print("定期入金バッチ処理開始")
    print("=" * 60)

    # 今日の日付を取得
    now = datetime.now(UTC)
    today = now.day
    year = now.year
    month = now.month

    print(f"実行日時: {now.isoformat()}")
    print(f"処理対象日: {today}日")
    print("-" * 60)

    # データベースセッションを取得
    db = next(get_db())

    try:
        # DIコンテナを作成
        injector = create_injector(db)

        # 必要なサービスとリポジトリを取得
        recurring_deposit_repo = injector.get(RecurringDepositRepository)
        execution_repo = injector.get(RecurringDepositExecutionRepository)
        transaction_service = injector.get(TransactionService)
        account_repo = injector.get(AccountRepository)

        # 今日が実行日で有効な定期入金設定を取得
        recurring_deposits = recurring_deposit_repo.get_active_by_day_of_month(today)

        print(f"📋 対象の定期入金設定: {len(recurring_deposits)}件")

        if not recurring_deposits:
            print("✅ 処理対象なし")
            return

        # 統計情報
        stats = {"success": 0, "skipped": 0, "failed": 0}

        # 各定期入金設定を処理
        for rd in recurring_deposits:
            print(f"\n処理中: 定期入金ID={rd.id}, 金額={rd.amount}円")

            # 今月既に実行済みかチェック
            if execution_repo.has_execution_this_month(rd.id, year, month):
                print("⏭️  スキップ: 今月既に実行済み")
                stats["skipped"] += 1

                # スキップ履歴を記録
                execution_repo.create(
                    recurring_deposit_id=rd.id,
                    transaction_id=None,
                    status="skipped",
                    amount=rd.amount,
                    day_of_month=rd.day_of_month,
                    error_message="Already executed this month",
                    executed_at=now,
                    created_at=now,
                )
                continue

            try:
                # アカウントを取得
                account = account_repo.get_by_id(rd.account_id)
                if not account:
                    raise ValueError(f"Account {rd.account_id} not found")

                # トランザクションを作成
                transaction = transaction_service.create_deposit(
                    account_id=rd.account_id,
                    amount=rd.amount,
                    description="定期お小遣い",
                )

                print(f"✅ 成功: トランザクションID={transaction.id}")
                stats["success"] += 1

                # 成功履歴を記録
                execution_repo.create(
                    recurring_deposit_id=rd.id,
                    transaction_id=transaction.id,
                    status="success",
                    amount=rd.amount,
                    day_of_month=rd.day_of_month,
                    error_message=None,
                    executed_at=now,
                    created_at=now,
                )

            except Exception as e:
                error_message = str(e)
                print(f"❌ 失敗: {error_message}")
                stats["failed"] += 1

                # 失敗履歴を記録
                execution_repo.create(
                    recurring_deposit_id=rd.id,
                    transaction_id=None,
                    status="failed",
                    amount=rd.amount,
                    day_of_month=rd.day_of_month,
                    error_message=error_message,
                    executed_at=now,
                    created_at=now,
                )

        # 統計情報を表示
        print("\n" + "=" * 60)
        print("処理結果")
        print("=" * 60)
        print(f"✅ 成功: {stats['success']}件")
        print(f"⏭️  スキップ: {stats['skipped']}件")
        print(f"❌ 失敗: {stats['failed']}件")
        print(f"📊 合計: {sum(stats.values())}件")
        print("=" * 60)

        # データベースにコミット
        db.commit()
        print("✅ データベースコミット完了")

    except Exception as e:
        print(f"\n❌ バッチ処理エラー: {e}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    try:
        process_recurring_deposits()
        print("\n✅ バッチ処理が正常に完了しました")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ バッチ処理が失敗しました: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
