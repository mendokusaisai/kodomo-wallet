"use client";

import { useQuery } from "@apollo/client/react";
import { Settings } from "lucide-react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { CreateChildDialog } from "@/components/create-child-dialog";
import { DashboardSkeleton } from "@/components/dashboard-skeleton";
import { DepositDialog } from "@/components/deposit-dialog";
import GoalDialog from "@/components/goal-dialog";
import { LinkChildToAuthDialog } from "@/components/link-child-to-auth-dialog";
import { LogoutButton } from "@/components/logout-button";
import { ThemeToggle } from "@/components/theme-toggle";
import { TransactionHistory } from "@/components/transaction-history";
import { Button } from "@/components/ui/button";
import { WithdrawDialog } from "@/components/withdraw-dialog";
import WithdrawalRequestDialog from "@/components/withdrawal-request-dialog";
import WithdrawalRequestsList from "@/components/withdrawal-requests-list";
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
		return <DashboardSkeleton />;
	}

	if (meError || accountsError) {
		const errorMessage = meError?.message || accountsError?.message || "";
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
								無料プランのため、起動に30秒〜1分程度かかる場合があります。
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
					<div className="flex items-center gap-3 md:gap-4">
						{/* アバター表示 */}
						{meData?.me?.avatarUrl ? (
							<div className="w-12 h-12 md:w-16 md:h-16 rounded-full overflow-hidden bg-gray-200 flex-shrink-0">
								<Image
									src={meData.me.avatarUrl}
									alt={meData.me.name}
									width={64}
									height={64}
									className="w-full h-full object-cover"
									onError={(e) => {
										e.currentTarget.style.display = "none";
									}}
									unoptimized
								/>
							</div>
						) : (
							<div className="w-12 h-12 md:w-16 md:h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-lg md:text-2xl font-bold flex-shrink-0">
								{meData?.me?.name?.charAt(0) || "?"}
							</div>
						)}
						<div>
							<h1 className="text-xl md:text-2xl lg:text-3xl font-bold text-gray-900 dark:text-gray-100">
								こんにちは、{meData?.me?.name}さん
							</h1>
							<p className="text-sm md:text-base text-gray-600 dark:text-gray-400 mt-1">
								ロール: {meData?.me?.role === "parent" ? "親" : "子供"}
							</p>
						</div>
					</div>
					<div className="flex gap-2 md:gap-3 w-full sm:w-auto">
						{/* 親の場合は子ども追加ボタンを表示 */}
						{meData?.me?.role === "parent" && (
							<Button
								onClick={() => setCreateChildDialogOpen(true)}
								variant="outline"
								className="border-green-500 text-green-600 hover:bg-green-50 dark:hover:bg-green-950 flex-1 sm:flex-none text-sm md:text-base"
							>
								+ 子どもを追加
							</Button>
						)}
						{/* 設定ページへのリンク */}
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
				</div>{" "}
				{/* アカウント一覧 */}
				<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
					{accountsData?.accounts.map((account: Account) => {
						const goalProgress = account.goalAmount
							? Math.round((account.balance / account.goalAmount) * 100)
							: 0;

						return (
							<div
								key={account.id}
								className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-4 md:p-6 hover:shadow-lg transition-shadow"
							>
								{/* アカウント所有者名 */}
								{account.user && (
									<div className="mb-3 pb-3 border-b border-gray-200 dark:border-gray-700">
										<p className="text-xs md:text-sm text-gray-500 dark:text-gray-400 mb-2">
											アカウント所有者
										</p>
										<div className="flex items-center gap-2 md:gap-3">
											{/* アバター表示 */}
											{account.user.avatarUrl ? (
												<div className="w-10 h-10 md:w-12 md:h-12 rounded-full overflow-hidden bg-gray-200 flex-shrink-0">
													<Image
														src={account.user.avatarUrl}
														alt={account.user.name}
														width={48}
														height={48}
														className="w-full h-full object-cover"
														onError={(e) => {
															e.currentTarget.style.display = "none";
														}}
														unoptimized
													/>
												</div>
											) : (
												<div className="w-10 h-10 md:w-12 md:h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-base md:text-lg font-bold flex-shrink-0">
													{account.user.name?.charAt(0) || "?"}
												</div>
											)}
											<p className="text-base md:text-lg font-semibold text-gray-900 dark:text-gray-100 truncate">
												{account.user.name}
											</p>
										</div>
									</div>
								)}
								{/* 残高 */}
								<div className="mb-4">
									<p className="text-xs md:text-sm text-gray-600 dark:text-gray-400 mb-1">
										残高
									</p>
									<p className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-gray-100">
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

								{/* 出金申請ボタン（子どものみ表示） */}
								{meData?.me?.role === "child" && (
									<div className="mb-4">
										<WithdrawalRequestDialog
											accountId={account.id}
											currentBalance={account.balance}
										/>
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

								{/* 子どもアカウント設定ボタン（親のみ表示） */}
								{meData?.me?.role === "parent" && account.user && (
									<div className="mb-4">
										<Button
											onClick={() => {
												if (account.user) {
													router.push(`/settings/${account.user.id}`);
												}
											}}
											variant="outline"
											className="w-full border-gray-300 text-gray-700 hover:bg-gray-50"
										>
											<Settings className="w-4 h-4 mr-2" />
											プロフィール設定
										</Button>
									</div>
								)}

								{/* 貯金目標 */}
								<div className="mt-4">
									{account.goalName && account.goalAmount ? (
										<>
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
										</>
									) : null}

									{/* 目標設定ボタン */}
									<div className="mt-2">
										<GoalDialog
											accountId={account.id}
											currentGoalName={account.goalName}
											currentGoalAmount={account.goalAmount}
										/>
									</div>
								</div>

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
				{/* 親の場合、出金申請リストを表示 */}
				{meData?.me?.role === "parent" && userId && (
					<div className="mt-8">
						<h2 className="text-2xl font-bold text-gray-900 mb-4">
							出金申請リスト
						</h2>
						<WithdrawalRequestsList parentId={userId} />
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
