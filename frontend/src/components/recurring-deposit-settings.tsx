"use client";

import { useMutation, useQuery } from "@apollo/client/react";
import { Calendar, DollarSign, Save, Trash2 } from "lucide-react";
import { useEffect, useId, useState } from "react";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
	CREATE_OR_UPDATE_RECURRING_DEPOSIT,
	DELETE_RECURRING_DEPOSIT,
	GET_ACCOUNTS,
	GET_RECURRING_DEPOSIT,
} from "@/lib/graphql/queries";
import type {
	CreateOrUpdateRecurringDepositResponse,
	DeleteRecurringDepositResponse,
	GetAccountsResponse,
	GetRecurringDepositResponse,
} from "@/lib/graphql/types";
import { showError, showSuccess } from "@/lib/toast";

interface RecurringDepositSettingsProps {
	childUserId: string;
	currentUserId: string;
	childName: string;
}

export default function RecurringDepositSettings({
	childUserId,
	currentUserId,
	childName,
}: RecurringDepositSettingsProps) {
	const [amount, setAmount] = useState<number>(0);
	const [dayOfMonth, setDayOfMonth] = useState<number>(1);
	const [isActive, setIsActive] = useState(true);
	const [accountId, setAccountId] = useState<string | null>(null);

	const amountInputId = useId();
	const dayInputId = useId();
	const activeInputId = useId();

	// アカウント情報を取得
	const { data: accountsData } = useQuery<GetAccountsResponse>(GET_ACCOUNTS, {
		variables: { userId: childUserId },
	});

	// アカウントIDを設定
	useEffect(() => {
		if (accountsData?.accounts && accountsData.accounts.length > 0) {
			setAccountId(accountsData.accounts[0].id);
		}
	}, [accountsData]);

	// 定期入金設定を取得
	const {
		data: recurringDepositData,
		loading: loadingRecurringDeposit,
		refetch,
	} = useQuery<GetRecurringDepositResponse>(GET_RECURRING_DEPOSIT, {
		variables: { accountId: accountId || "", currentUserId },
		skip: !accountId,
	});

	// 定期入金データの初期化
	useEffect(() => {
		if (recurringDepositData?.recurringDeposit) {
			setAmount(recurringDepositData.recurringDeposit.amount);
			setDayOfMonth(recurringDepositData.recurringDeposit.dayOfMonth);
			setIsActive(recurringDepositData.recurringDeposit.isActive);
		}
	}, [recurringDepositData]);

	// 作成・更新用mutation
	const [createOrUpdate, { loading: updating }] =
		useMutation<CreateOrUpdateRecurringDepositResponse>(
			CREATE_OR_UPDATE_RECURRING_DEPOSIT,
			{
				onCompleted: () => {
					showSuccess("定期お小遣い設定を保存しました");
					refetch();
				},
				onError: (error: { message: string }) => {
					showError("保存に失敗しました", error.message);
				},
			},
		);

	// 削除用mutation
	const [deleteRecurringDeposit, { loading: deleting }] =
		useMutation<DeleteRecurringDepositResponse>(DELETE_RECURRING_DEPOSIT, {
			onCompleted: () => {
				showSuccess("定期お小遣い設定を削除しました");
				setAmount(0);
				setDayOfMonth(1);
				setIsActive(true);
				refetch();
			},
			onError: (error: { message: string }) => {
				showError("削除に失敗しました", error.message);
			},
		});

	const handleSave = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!accountId) {
			showError("アカウントが見つかりません");
			return;
		}

		if (amount <= 0) {
			showError("金額は1円以上を指定してください");
			return;
		}

		if (dayOfMonth < 1 || dayOfMonth > 31) {
			showError("日付は1〜31の範囲で指定してください");
			return;
		}

		await createOrUpdate({
			variables: {
				accountId,
				currentUserId,
				amount,
				dayOfMonth,
				isActive,
			},
		});
	};

	const handleDelete = async () => {
		if (!accountId) return;
		await deleteRecurringDeposit({
			variables: {
				accountId,
				currentUserId,
			},
		});
	};

	if (loadingRecurringDeposit) {
		return (
			<div className="bg-white rounded-lg shadow-md p-6">
				<div className="text-gray-600">定期お小遣い設定を読み込み中...</div>
			</div>
		);
	}

	const hasExistingSettings = !!recurringDepositData?.recurringDeposit;

	return (
		<div className="bg-white rounded-lg shadow-md p-6">
			<div className="flex items-center gap-3 mb-6">
				<DollarSign className="w-6 h-6 text-green-600" />
				<h2 className="text-xl font-bold text-gray-900">
					定期お小遣い設定（親のみ）
				</h2>
			</div>

			<p className="text-sm text-gray-600 mb-4">
				毎月指定した日にちに自動でお小遣いを入金できます。
			</p>

			<form onSubmit={handleSave} className="space-y-4">
				<div>
					<Label htmlFor={amountInputId}>月額（円）</Label>
					<Input
						id={amountInputId}
						type="number"
						min="1"
						value={amount}
						onChange={(e) => setAmount(Number.parseInt(e.target.value, 10))}
						placeholder="1000"
						required
					/>
				</div>

				<div>
					<Label htmlFor={dayInputId} className="flex items-center gap-2">
						<Calendar className="w-4 h-4" />
						入金日（毎月）
					</Label>
					<Input
						id={dayInputId}
						type="number"
						min="1"
						max="31"
						value={dayOfMonth}
						onChange={(e) => setDayOfMonth(Number.parseInt(e.target.value, 10))}
						placeholder="1"
						required
					/>
					<p className="text-xs text-gray-500 mt-1">
						1〜31の範囲で指定してください（例：毎月25日 → 25）
					</p>
				</div>

				<div className="flex items-center gap-2">
					<input
						type="checkbox"
						id={activeInputId}
						checked={isActive}
						onChange={(e) => setIsActive(e.target.checked)}
						className="w-4 h-4 text-blue-600 rounded"
					/>
					<Label htmlFor={activeInputId} className="cursor-pointer">
						有効にする
					</Label>
				</div>

				<div className="flex gap-3">
					<Button
						type="submit"
						className="flex-1 bg-green-600 hover:bg-green-700"
						disabled={updating}
					>
						<Save className="w-4 h-4 mr-2" />
						{updating ? "保存中..." : "保存"}
					</Button>

					{hasExistingSettings && (
						<ConfirmDialog
							title="設定を削除"
							description={`${childName}の定期お小遣い設定を削除しますか？この操作は取り消せません。`}
							confirmLabel="削除"
							onConfirm={handleDelete}
							variant="destructive"
							disabled={deleting}
						>
							<Trash2 className="w-4 h-4 mr-2" />
							{deleting ? "削除中..." : "削除"}
						</ConfirmDialog>
					)}
				</div>
			</form>

			{hasExistingSettings && (
				<div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
					<p className="text-sm text-green-800">
						<strong>現在の設定：</strong>
						毎月{recurringDepositData?.recurringDeposit?.dayOfMonth}日に
						{recurringDepositData?.recurringDeposit?.amount.toLocaleString()}
						円を自動入金
						{recurringDepositData?.recurringDeposit?.isActive
							? "（有効）"
							: "（無効）"}
					</p>
				</div>
			)}
		</div>
	);
}
