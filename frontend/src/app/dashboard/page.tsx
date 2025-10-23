"use client";

import { useQuery } from "@apollo/client/react";
import { GET_ACCOUNTS, GET_ME } from "@/lib/graphql/queries";
import type {
	Account,
	GetAccountsResponse,
	GetMeResponse,
} from "@/lib/graphql/types";

export default function DashboardPage() {
	const {
		data: meData,
		loading: meLoading,
		error: meError,
	} = useQuery<GetMeResponse>(GET_ME);
	const {
		data: accountsData,
		loading: accountsLoading,
		error: accountsError,
	} = useQuery<GetAccountsResponse>(GET_ACCOUNTS);

	if (meLoading || accountsLoading) {
		return (
			<div className="min-h-screen flex items-center justify-center">
				<div className="text-lg">読み込み中...</div>
			</div>
		);
	}

	if (meError || accountsError) {
		return (
			<div className="min-h-screen flex items-center justify-center">
				<div className="text-red-600">
					<h2 className="text-xl font-bold mb-2">エラーが発生しました</h2>
					<p>{meError?.message || accountsError?.message}</p>
				</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen bg-gray-50 p-8">
			<div className="max-w-7xl mx-auto">
				{/* ヘッダー */}
				<div className="mb-8">
					<h1 className="text-3xl font-bold text-gray-900">
						こんにちは、{meData?.me?.name}さん
					</h1>
					<p className="text-gray-600 mt-2">
						ロール: {meData?.me?.role === "parent" ? "親" : "子供"}
					</p>
				</div>

				{/* アカウント一覧 */}
				<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					{accountsData?.accounts.map((account: Account) => {
						const goalProgress = account.goalAmount
							? Math.round((account.balance / account.goalAmount) * 100)
							: 0;

						return (
							<div
								key={account.id}
								className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
							>
								{/* 残高 */}
								<div className="mb-4">
									<p className="text-sm text-gray-600 mb-1">残高</p>
									<p className="text-3xl font-bold text-gray-900">
										¥{account.balance.toLocaleString()}
									</p>
								</div>

								{/* 貯金目標 */}
								{account.goalName && account.goalAmount && (
									<div className="mt-4">
										<div className="flex justify-between items-center mb-2">
											<p className="text-sm font-medium text-gray-700">
												目標: {account.goalName}
											</p>
											<p className="text-sm font-bold text-blue-600">
												{goalProgress}%
											</p>
										</div>
										<div className="w-full bg-gray-200 rounded-full h-2.5">
											<div
												className="bg-blue-600 h-2.5 rounded-full transition-all"
												style={{ width: `${Math.min(goalProgress, 100)}%` }}
											></div>
										</div>
										<p className="text-xs text-gray-500 mt-1">
											目標金額: ¥{account.goalAmount.toLocaleString()}
										</p>
									</div>
								)}

								{/* アカウント情報 */}
								<div className="mt-4 pt-4 border-t border-gray-200">
									<p className="text-xs text-gray-500">
										アカウントID: {account.id.slice(0, 8)}...
									</p>
								</div>
							</div>
						);
					})}
				</div>

				{/* アカウントが無い場合 */}
				{accountsData?.accounts.length === 0 && (
					<div className="bg-white rounded-lg shadow-md p-8 text-center">
						<p className="text-gray-600">アカウントがありません</p>
					</div>
				)}
			</div>
		</div>
	);
}
