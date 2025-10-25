"use client";

import { useQuery } from "@apollo/client/react";
import { format } from "date-fns";
import { ja } from "date-fns/locale";
import { ArrowDownIcon, ArrowUpIcon, GiftIcon } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
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
			<div className="mt-4 md:mt-6">
				<Skeleton className="h-5 w-24 mb-3" />
				<div className="space-y-2">
					{[1, 2, 3].map((i) => (
						<Skeleton key={i} className="h-16 w-full" />
					))}
				</div>
			</div>
		);
	}

	if (error) {
		return (
			<div className="mt-4 p-4 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-900 rounded-lg">
				<p className="text-sm text-red-600 dark:text-red-400 text-center">
					取引履歴の読み込みに失敗しました
				</p>
			</div>
		);
	}

	if (!data?.transactions || data.transactions.length === 0) {
		return (
			<div className="mt-4 p-4 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg">
				<p className="text-sm text-gray-500 dark:text-gray-400 text-center">
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
					bgColor: "bg-green-100 dark:bg-green-950",
					textColor: "text-green-700 dark:text-green-400",
					iconColor: "text-green-600 dark:text-green-500",
					label: "入金",
				};
			case "withdraw":
				return {
					icon: <ArrowUpIcon className="w-4 h-4" />,
					bgColor: "bg-red-100 dark:bg-red-950",
					textColor: "text-red-700 dark:text-red-400",
					iconColor: "text-red-600 dark:text-red-500",
					label: "出金",
				};
			case "reward":
				return {
					icon: <GiftIcon className="w-4 h-4" />,
					bgColor: "bg-yellow-100 dark:bg-yellow-950",
					textColor: "text-yellow-700 dark:text-yellow-400",
					iconColor: "text-yellow-600 dark:text-yellow-500",
					label: "報酬",
				};
			default:
				return {
					icon: <ArrowDownIcon className="w-4 h-4" />,
					bgColor: "bg-gray-100 dark:bg-gray-800",
					textColor: "text-gray-700 dark:text-gray-400",
					iconColor: "text-gray-600 dark:text-gray-500",
					label: "その他",
				};
		}
	};

	return (
		<div className="mt-4 md:mt-6">
			<h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
				取引履歴
			</h3>
			<div className="space-y-2 max-h-64 md:max-h-80 overflow-y-auto">
				{data.transactions.map((transaction) => {
					const style = getTransactionStyle(transaction.type);
					const date = new Date(transaction.createdAt);
					const formattedDate = format(date, "M月d日 HH:mm", { locale: ja });

					return (
						<div
							key={transaction.id}
							className="flex items-center justify-between p-3 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-sm transition-shadow"
						>
							{/* 左側: アイコンと情報 */}
							<div className="flex items-center gap-2 md:gap-3 flex-1 min-w-0">
								<div
									className={`p-2 rounded-full ${style.bgColor} flex-shrink-0`}
								>
									<div className={style.iconColor}>{style.icon}</div>
								</div>
								<div className="min-w-0 flex-1">
									<p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
										{transaction.description || style.label}
									</p>
									<p className="text-xs text-gray-500 dark:text-gray-400">
										{formattedDate}
									</p>
								</div>
							</div>

							{/* 右側: 金額 */}
							<div
								className={`text-right ${style.textColor} flex-shrink-0 ml-2`}
							>
								<p className="text-base md:text-lg font-bold whitespace-nowrap">
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
