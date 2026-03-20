"use client";

import { useMutation, useQuery } from "@apollo/client/react";
import { ArrowLeft } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { useId, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
	FAMILY_ACCOUNTS,
	MY_FAMILY,
	UPDATE_GOAL,
} from "@/lib/graphql/queries";
import type {
	FamilyAccountsResponse,
	MyFamilyResponse,
	UpdateGoalResponse,
} from "@/lib/graphql/types";

export default function AccountSettingsPage() {
	const params = useParams();
	const accountId = params.userId as string;
	const router = useRouter();

	const [goalName, setGoalName] = useState("");
	const [goalAmount, setGoalAmount] = useState("");
	const goalNameId = useId();
	const goalAmountId = useId();

	const { data: familyData, loading: familyLoading } =
		useQuery<MyFamilyResponse>(MY_FAMILY);
	const familyId = familyData?.myFamily?.id;

	const { data: accountsData, loading: accountsLoading } =
		useQuery<FamilyAccountsResponse>(FAMILY_ACCOUNTS, {
			variables: { familyId },
			skip: !familyId,
		});

	const account = accountsData?.familyAccounts?.find((a) => a.id === accountId);

	const [updateGoal, { loading: updating }] = useMutation<UpdateGoalResponse>(
		UPDATE_GOAL,
		{
			refetchQueries: [{ query: FAMILY_ACCOUNTS, variables: { familyId } }],
		},
	);

	const handleUpdateGoal = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!familyId || !accountId) return;
		try {
			await updateGoal({
				variables: {
					familyId,
					accountId,
					goalName: goalName || undefined,
					goalAmount: goalAmount ? Number(goalAmount) : undefined,
				},
			});
			alert("目標を更新しました");
		} catch (error) {
			console.error("目標更新エラー:", error);
			alert("更新に失敗しました");
		}
	};

	const loading = familyLoading || accountsLoading;

	if (loading) {
		return (
			<div className="min-h-screen bg-gray-50 dark:bg-gray-950 p-4 md:p-6 lg:p-8">
				<div className="max-w-xl mx-auto space-y-6">
					<Skeleton className="h-10 w-32" />
					<Skeleton className="h-48 w-full rounded-lg" />
				</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen bg-gray-50 dark:bg-gray-950 p-4 md:p-6 lg:p-8">
			<div className="max-w-xl mx-auto">
				<div className="mb-6 flex items-center gap-4">
					<Button
						variant="outline"
						size="sm"
						onClick={() => router.push("/dashboard")}
					>
						<ArrowLeft className="w-4 h-4 mr-2" />
						戻る
					</Button>
					<h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
						口座設定
					</h1>
				</div>

				{account && (
					<div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-4 md:p-6 mb-6">
						<h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-3">
							{account.name}
						</h2>
						<div className="text-2xl font-bold text-green-600 dark:text-green-400">
							{account.balance.toLocaleString()}円
						</div>
						{account.goalName && (
							<div className="mt-3 text-sm text-gray-600 dark:text-gray-400">
								<span className="font-medium">現在の目標: </span>
								{account.goalName}
								{account.goalAmount != null && (
									<span> (目標金額: {account.goalAmount.toLocaleString()}円)</span>
								)}
							</div>
						)}
					</div>
				)}

				{!account && !loading && (
					<div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-6 mb-6 text-center text-gray-500">
						口座が見つかりませんでした
					</div>
				)}

				{account && (
					<div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-4 md:p-6">
						<h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
							🎯 目標の設定
						</h2>
						<form onSubmit={handleUpdateGoal} className="space-y-4">
							<div>
								<Label htmlFor={goalNameId}>目標名</Label>
								<Input
									id={goalNameId}
									value={goalName}
									onChange={(e) => setGoalName(e.target.value)}
									placeholder={account.goalName ?? "例: ゲームを買う"}
									className="mt-1"
								/>
							</div>
							<div>
								<Label htmlFor={goalAmountId}>目標金額 (円)</Label>
								<Input
									id={goalAmountId}
									type="number"
									value={goalAmount}
									onChange={(e) => setGoalAmount(e.target.value)}
									placeholder={account.goalAmount != null ? String(account.goalAmount) : "3000"}
									min="0"
									className="mt-1"
								/>
							</div>
							<Button
								type="submit"
								disabled={updating}
								className="w-full"
							>
								{updating ? "更新中..." : "目標を保存"}
							</Button>
						</form>
					</div>
				)}
			</div>
		</div>
	);
}
