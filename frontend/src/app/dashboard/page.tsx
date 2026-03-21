"use client";

import { useMutation, useQuery } from "@apollo/client/react";
import { Settings } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { DashboardSkeleton } from "@/components/dashboard-skeleton";
import { DepositDialog } from "@/components/deposit-dialog";
import { LogoutButton } from "@/components/logout-button";
import { ThemeToggle } from "@/components/theme-toggle";
import { TransactionHistory } from "@/components/transaction-history";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { WithdrawDialog } from "@/components/withdraw-dialog";
import { auth } from "@/lib/firebase/client";
import {
	CREATE_FAMILY,
	FAMILY_ACCOUNTS,
	MY_FAMILY,
} from "@/lib/graphql/queries";
import type {
	Account,
	CreateFamilyResponse,
	FamilyAccountsResponse,
	MyFamilyResponse,
} from "@/lib/graphql/types";

export default function DashboardPage() {
	const router = useRouter();
	const [depositDialogOpen, setDepositDialogOpen] = useState(false);
	const [withdrawDialogOpen, setWithdrawDialogOpen] = useState(false);
	const [selectedAccount, setSelectedAccount] = useState<{
		id: string;
		name: string;
		balance: number;
	} | null>(null);

	// 家族作成フォーム
	const [myName, setMyName] = useState("");
	const [familyName, setFamilyName] = useState("");
	const [isCreating, setIsCreating] = useState(false);

	const currentUid = auth.currentUser?.uid;

	const {
		data: familyData,
		loading: familyLoading,
		error: familyError,
	} = useQuery<MyFamilyResponse>(MY_FAMILY);

	const familyId = familyData?.myFamily?.id;
	const currentMember = familyData?.myFamily?.members.find(
		(m) => m.uid === currentUid,
	);
	const isParent = currentMember?.role === "parent";

	const {
		data: accountsData,
		loading: accountsLoading,
		error: accountsError,
		refetch: refetchAccounts,
	} = useQuery<FamilyAccountsResponse>(FAMILY_ACCOUNTS, {
		variables: { familyId },
		skip: !familyId,
	});

	const [createFamily] = useMutation<CreateFamilyResponse>(CREATE_FAMILY, {
		refetchQueries: [{ query: MY_FAMILY }],
	});

	const handleCreateFamily = async (e: React.FormEvent) => {
		e.preventDefault();
		const email = auth.currentUser?.email || "";
		if (!myName.trim() || !email) return;

		setIsCreating(true);
		try {
			await createFamily({
				variables: { myName: myName.trim(), email, familyName: familyName.trim() || null },
			});
			toast.success("家族を作成しました！");
		} catch (error) {
			console.error("家族作成エラー:", error);
			toast.error("家族の作成に失敗しました", {
				description: error instanceof Error ? error.message : "もう一度お試しください",
			});
		} finally {
			setIsCreating(false);
		}
	};

	if (familyLoading || accountsLoading) {
		return <DashboardSkeleton />;
	}

	if (familyError || accountsError) {
		const errorMessage = familyError?.message || accountsError?.message || "";
		const is503Error =
			errorMessage.includes("503") ||
			errorMessage.includes("Service Unavailable");

		return (
			<div className="min-h-screen flex items-center justify-center p-4">
				<div className="text-center max-w-md">
					{is503Error ? (
						<>
							<div className="mb-4">
								<div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto" />
							</div>
							<h2 className="text-xl font-bold mb-2 text-gray-900 dark:text-gray-100">
								サーバーを起動しています...
							</h2>
							<p className="text-gray-600 dark:text-gray-400 text-sm">
								起動に30秒〜1分程度かかる場合があります。
								<br />
								自動的に再試行しています。
							</p>
						</>
					) : (
						<>
							<h2 className="text-xl font-bold mb-2 text-red-600">
								エラーが発生しました
							</h2>
							<p className="text-gray-600 dark:text-gray-400">{errorMessage}</p>
							<Button onClick={() => window.location.reload()} className="mt-4">
								再読み込み
							</Button>
						</>
					)}
				</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen bg-gray-50 dark:bg-gray-950 p-4 md:p-6 lg:p-8">
			<div className="max-w-7xl mx-auto">
				{/* ヘッダー */}
				<div className="mb-6 md:mb-8 flex flex-col sm:flex-row justify-between items-start gap-4">
					<div className="flex items-center gap-3">
						<div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl p-2 shadow-lg">
							<svg
								className="w-6 h-6 md:w-8 md:h-8 text-white"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									strokeLinecap="round"
									strokeLinejoin="round"
									strokeWidth={2}
									d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
								/>
							</svg>
						</div>
						<div>
							<h1 className="text-xl md:text-2xl lg:text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
								Kodomo Wallet
							</h1>
							{familyData?.myFamily?.name && (
								<p className="text-xs md:text-sm text-gray-600 dark:text-gray-400">
									{familyData.myFamily.name}家
								</p>
							)}
						</div>
					</div>
					<div className="flex gap-2 md:gap-3 w-full sm:w-auto">
						<Button
							onClick={() => router.push("/settings")}
							variant="outline"
							className="flex-1 sm:flex-none text-sm md:text-base"
						>
							設定
						</Button>
						<ThemeToggle />
						<LogoutButton />
					</div>
				</div>

				{/* 家族が未作成の場合 */}
				{!familyData?.myFamily && (
					<div className="bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-6 md:p-8 max-w-md mx-auto">
						<h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
							🏠 家族を作成しましょう
						</h2>
						<p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
							まず家族を作成して、お子さまの口座を管理できるようにしましょう。
						</p>
						<form onSubmit={handleCreateFamily} className="space-y-4">
							<div>
								<Label htmlFor="myName">あなたのお名前</Label>
								<Input
									id="myName"
									value={myName}
									onChange={(e) => setMyName(e.target.value)}
									placeholder="山田太郎"
									required
									className="mt-1"
								/>
							</div>
							<div>
								<Label htmlFor="familyName">家族名（任意）</Label>
								<Input
									id="familyName"
									value={familyName}
									onChange={(e) => setFamilyName(e.target.value)}
									placeholder="山田"
									className="mt-1"
								/>
							</div>
							<Button type="submit" disabled={isCreating} className="w-full">
								{isCreating ? "作成中..." : "家族を作成する"}
							</Button>
						</form>
					</div>
				)}

				{/* アカウント一覧 */}
				{familyId && (
					<>
						<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
							{accountsData?.familyAccounts.map((account: Account) => {
								const goalProgress = account.goalAmount
									? Math.round((account.balance / account.goalAmount) * 100)
									: 0;

								return (
									<div
										key={account.id}
										className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-4 md:p-6 hover:shadow-lg transition-shadow"
									>
										{/* アカウント名 */}
										<div className="mb-3 pb-3 border-b border-gray-200 dark:border-gray-700">
											<div className="flex items-center justify-between gap-2">
												<p className="text-base md:text-lg font-semibold text-gray-900 dark:text-gray-100 truncate">
													{account.name}
												</p>
												{isParent && (
													<Button
														onClick={() => router.push(`/settings/${account.id}`)}
														variant="ghost"
														size="icon"
														className="flex-shrink-0 w-10 h-10"
													>
														<Settings className="!w-6 !h-6 text-gray-600 dark:text-gray-400" />
													</Button>
												)}
											</div>
										</div>

										{/* 残高 */}
										<div className="mb-4">
											<p className="text-xs md:text-sm text-gray-600 dark:text-gray-400 mb-1">
												残高
											</p>
											<p className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-gray-100">
												¥{account.balance.toLocaleString()}
											</p>
										</div>

										{/* 入金ボタン（親のみ） */}
										{isParent && (
											<div className="mb-2">
												<Button
													onClick={() => {
														setSelectedAccount({
															id: account.id,
															name: account.name,
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

										{/* 出金ボタン（親のみ） */}
										{isParent && (
											<div className="mb-4">
												<Button
													onClick={() => {
														setSelectedAccount({
															id: account.id,
															name: account.name,
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

										{/* 貯金目標 */}
										<div className="mt-4">
											{account.goalName && account.goalAmount ? (
												<>
													<div className="flex justify-between items-center mb-2">
														<p className="text-sm font-medium text-gray-700 dark:text-gray-300">
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
												</>
											) : null}
										</div>

										<TransactionHistory
											accountId={account.id}
											familyId={familyId}
										/>
									</div>
								);
							})}
						</div>

						{/* アカウントが無い場合 */}
						{accountsData?.familyAccounts.length === 0 && (
							<div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-8 text-center">
								<p className="text-gray-600 dark:text-gray-400">
									口座がありません。設定ページから口座を作成できます。
								</p>
								<Button
									onClick={() => router.push("/settings")}
									className="mt-4"
								>
									設定ページへ
								</Button>
							</div>
						)}

						{/* 入金ダイアログ */}
						{selectedAccount && (
							<DepositDialog
								open={depositDialogOpen}
								onOpenChange={setDepositDialogOpen}
								accountId={selectedAccount.id}
								accountName={selectedAccount.name}
								familyId={familyId}
								onSuccess={() => refetchAccounts()}
							/>
						)}

						{/* 出金ダイアログ */}
						{selectedAccount && (
							<WithdrawDialog
								open={withdrawDialogOpen}
								onOpenChange={setWithdrawDialogOpen}
								accountId={selectedAccount.id}
								accountName={selectedAccount.name}
								familyId={familyId}
								currentBalance={selectedAccount.balance}
								onSuccess={() => refetchAccounts()}
							/>
						)}
					</>
				)}
			</div>
		</div>
	);
}
