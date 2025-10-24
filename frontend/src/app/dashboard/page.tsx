"use client";

import { useQuery } from "@apollo/client/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { CreateChildDialog } from "@/components/create-child-dialog";
import { DepositDialog } from "@/components/deposit-dialog";
import { LinkChildToAuthDialog } from "@/components/link-child-to-auth-dialog";
import { LogoutButton } from "@/components/logout-button";
import { TransactionHistory } from "@/components/transaction-history";
import { Button } from "@/components/ui/button";
import { WithdrawDialog } from "@/components/withdraw-dialog";
import { GET_ACCOUNTS, GET_ME } from "@/lib/graphql/queries";
import type {
	Account,
	GetAccountsResponse,
	GetMeResponse,
} from "@/lib/graphql/types";
import { getUser } from "@/lib/supabase/auth";

export default function DashboardPage() {
	const router = useRouter();
	const [userId, setUserId] = useState<string | null>(null);
	const [depositDialogOpen, setDepositDialogOpen] = useState(false);
	const [withdrawDialogOpen, setWithdrawDialogOpen] = useState(false);
	const [createChildDialogOpen, setCreateChildDialogOpen] = useState(false);
	const [linkAuthDialogOpen, setLinkAuthDialogOpen] = useState(false);
	const [selectedAccount, setSelectedAccount] = useState<{
		id: string;
		name: string;
		balance: number;
	} | null>(null);
	const [selectedChild, setSelectedChild] = useState<{
		id: string;
		name: string;
	} | null>(null);

	// Supabaseからユーザー情報を取得
	useEffect(() => {
		const fetchUser = async () => {
			try {
				const user = await getUser();
				if (!user) {
					router.push("/login");
					return;
				}
				setUserId(user.id);
			} catch (error) {
				console.error("ユーザー取得エラー:", error);
				router.push("/login");
			}
		};
		fetchUser();
	}, [router]);

	const {
		data: meData,
		loading: meLoading,
		error: meError,
	} = useQuery<GetMeResponse>(GET_ME, {
		variables: { userId },
		skip: !userId,
	});
	const {
		data: accountsData,
		loading: accountsLoading,
		error: accountsError,
	} = useQuery<GetAccountsResponse>(GET_ACCOUNTS, {
		variables: { userId },
		skip: !userId,
	});

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
				<div className="mb-8 flex justify-between items-start">
					<div>
						<h1 className="text-3xl font-bold text-gray-900">
							こんにちは、{meData?.me?.name}さん
						</h1>
						<p className="text-gray-600 mt-2">
							ロール: {meData?.me?.role === "parent" ? "親" : "子供"}
						</p>
					</div>
					<div className="flex gap-3">
						{/* 親の場合は子ども追加ボタンを表示 */}
						{meData?.me?.role === "parent" && (
							<Button
								onClick={() => setCreateChildDialogOpen(true)}
								variant="outline"
								className="border-green-500 text-green-600 hover:bg-green-50"
							>
								+ 子どもを追加
							</Button>
						)}
						<LogoutButton />
					</div>
				</div>{" "}
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
								{/* アカウント所有者名 */}
								{account.user && (
									<div className="mb-3 pb-3 border-b border-gray-200">
										<p className="text-sm text-gray-500">アカウント所有者</p>
										<p className="text-lg font-semibold text-gray-900">
											{account.user.name}
										</p>
									</div>
								)}
								{/* 残高 */}
								<div className="mb-4">
									<p className="text-sm text-gray-600 mb-1">残高</p>
									<p className="text-3xl font-bold text-gray-900">
										¥{account.balance.toLocaleString()}
									</p>
								</div>

								{/* 入金ボタン（親のみ表示） */}
								{meData?.me?.role === "parent" && (
									<div className="mb-2">
										<Button
											onClick={() => {
												setSelectedAccount({
													id: account.id,
													name: `口座 (残高: ¥${account.balance.toLocaleString()})`,
													balance: account.balance,
												});
												setDepositDialogOpen(true);
											}}
											className="w-full"
										>
											入金する
										</Button>
									</div>
								)}

								{/* 出金ボタン（親のみ表示） */}
								{meData?.me?.role === "parent" && (
									<div className="mb-4">
										<Button
											onClick={() => {
												setSelectedAccount({
													id: account.id,
													name: `口座 (残高: ¥${account.balance.toLocaleString()})`,
													balance: account.balance,
												});
												setWithdrawDialogOpen(true);
											}}
											className="w-full bg-red-600 hover:bg-red-700"
											variant="destructive"
										>
											出金する
										</Button>
									</div>
								)}

								{/* 認証アカウント移行ボタン（認証なし子どものみ表示） */}
								{meData?.me?.role === "parent" &&
									account.user &&
									!account.user.authUserId && (
										<div className="mb-4">
											<Button
												onClick={() => {
													if (account.user) {
														setSelectedChild({
															id: account.user.id,
															name: account.user.name,
														});
														setLinkAuthDialogOpen(true);
													}
												}}
												variant="outline"
												className="w-full border-purple-500 text-purple-600 hover:bg-purple-50"
											>
												📧 招待メールを送信
											</Button>
										</div>
									)}
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
											/>
										</div>
										<p className="text-xs text-gray-500 mt-1">
											目標金額: ¥{account.goalAmount.toLocaleString()}
										</p>
									</div>
								)}

								{/* トランザクション履歴 */}
								<TransactionHistory accountId={account.id} />

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
				{/* 入金ダイアログ */}
				{selectedAccount && (
					<DepositDialog
						open={depositDialogOpen}
						onOpenChange={setDepositDialogOpen}
						accountId={selectedAccount.id}
						accountName={selectedAccount.name}
					/>
				)}
				{/* 出金ダイアログ */}
				{selectedAccount && (
					<WithdrawDialog
						open={withdrawDialogOpen}
						onOpenChange={setWithdrawDialogOpen}
						accountId={selectedAccount.id}
						accountName={selectedAccount.name}
						currentBalance={selectedAccount.balance}
					/>
				)}
				{/* 子ども追加ダイアログ */}
				{userId && (
					<CreateChildDialog
						open={createChildDialogOpen}
						onOpenChange={setCreateChildDialogOpen}
						parentId={userId}
					/>
				)}
				{/* 認証アカウント移行ダイアログ */}
				{selectedChild && (
					<LinkChildToAuthDialog
						open={linkAuthDialogOpen}
						onOpenChange={setLinkAuthDialogOpen}
						childId={selectedChild.id}
						childName={selectedChild.name}
					/>
				)}
			</div>
		</div>
	);
}
