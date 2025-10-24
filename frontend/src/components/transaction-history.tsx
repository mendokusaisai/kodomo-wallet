"use client";

import { useQuery } from "@apollo/client/react";
import { format } from "date-fns";
import { ja } from "date-fns/locale";
import { ArrowDownIcon, ArrowUpIcon, GiftIcon } from "lucide-react";
import { GET_TRANSACTIONS } from "@/lib/graphql/queries";
import type { GetTransactionsResponse } from "@/lib/graphql/types";

interface TransactionHistoryProps {
	accountId: string;
}

export function TransactionHistory({ accountId }: TransactionHistoryProps) {
	const { data, loading, error } = useQuery<GetTransactionsResponse>(
		GET_TRANSACTIONS,
		{
			variables: { accountId },
			skip: !accountId,
		},
	);

	if (loading) {
		return (
			<div className="mt-4 p-4 bg-gray-50 rounded-lg">
				<p className="text-sm text-gray-500 text-center">
					取引履歴を読み込み中...
				</p>
			</div>
		);
	}

	if (error) {
		return (
			<div className="mt-4 p-4 bg-red-50 rounded-lg">
				<p className="text-sm text-red-600 text-center">
					取引履歴の読み込みに失敗しました
				</p>
			</div>
		);
	}

	if (!data?.transactions || data.transactions.length === 0) {
		return (
			<div className="mt-4 p-4 bg-gray-50 rounded-lg">
				<p className="text-sm text-gray-500 text-center">
					まだ取引履歴がありません
				</p>
			</div>
		);
	}

	// 取引タイプごとのスタイル設定
	const getTransactionStyle = (type: string) => {
		switch (type) {
			case "deposit":
				return {
					icon: <ArrowDownIcon className="w-4 h-4" />,
					bgColor: "bg-green-100",
					textColor: "text-green-700",
					iconColor: "text-green-600",
					label: "入金",
				};
			case "withdraw":
				return {
					icon: <ArrowUpIcon className="w-4 h-4" />,
					bgColor: "bg-red-100",
					textColor: "text-red-700",
					iconColor: "text-red-600",
					label: "出金",
				};
			case "reward":
				return {
					icon: <GiftIcon className="w-4 h-4" />,
					bgColor: "bg-yellow-100",
					textColor: "text-yellow-700",
					iconColor: "text-yellow-600",
					label: "報酬",
				};
			default:
				return {
					icon: <ArrowDownIcon className="w-4 h-4" />,
					bgColor: "bg-gray-100",
					textColor: "text-gray-700",
					iconColor: "text-gray-600",
					label: "その他",
				};
		}
	};

	return (
		<div className="mt-6">
			<h3 className="text-sm font-semibold text-gray-700 mb-3">取引履歴</h3>
			<div className="space-y-2 max-h-64 overflow-y-auto">
				{data.transactions.map((transaction) => {
					const style = getTransactionStyle(transaction.type);
					const date = new Date(transaction.createdAt);
					const formattedDate = format(date, "M月d日 HH:mm", { locale: ja });

					return (
						<div
							key={transaction.id}
							className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:shadow-sm transition-shadow"
						>
							{/* 左側: アイコンと情報 */}
							<div className="flex items-center gap-3">
								<div className={`p-2 rounded-full ${style.bgColor}`}>
									<div className={style.iconColor}>{style.icon}</div>
								</div>
								<div>
									<p className="text-sm font-medium text-gray-900">
										{transaction.description || style.label}
									</p>
									<p className="text-xs text-gray-500">{formattedDate}</p>
								</div>
							</div>

							{/* 右側: 金額 */}
							<div className={`text-right ${style.textColor}`}>
								<p className="text-lg font-bold">
									{transaction.type === "withdraw" ? "-" : "+"}¥
									{transaction.amount.toLocaleString()}
								</p>
							</div>
						</div>
					);
				})}
			</div>
		</div>
	);
}
