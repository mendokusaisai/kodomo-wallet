"use client";

import { useMutation } from "@apollo/client/react";
import { Target } from "lucide-react";
import { useState } from "react";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { UPDATE_GOAL } from "@/lib/graphql/queries";
import { showError, showSuccess } from "@/lib/toast";

interface GoalDialogProps {
	accountId: string;
	currentGoalName?: string | null;
	currentGoalAmount?: number | null;
}

export default function GoalDialog({
	accountId,
	currentGoalName,
	currentGoalAmount,
}: GoalDialogProps) {
	const [open, setOpen] = useState(false);
	const [goalName, setGoalName] = useState(currentGoalName || "");
	const [goalAmount, setGoalAmount] = useState(
		currentGoalAmount ? currentGoalAmount.toString() : "",
	);

	const [updateGoal, { loading }] = useMutation(UPDATE_GOAL, {
		refetchQueries: ["GetAccounts"],
		onCompleted: () => {
			showSuccess("目標を設定しました");
			setOpen(false);
		},
		onError: (error: { message: string }) => {
			showError("目標設定に失敗しました", error.message);
		},
	});

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();

		const amountNum = goalAmount ? Number.parseInt(goalAmount) : null;
		if (amountNum !== null && (Number.isNaN(amountNum) || amountNum < 0)) {
			showError("有効な金額を入力してください");
			return;
		}

		await updateGoal({
			variables: {
				accountId,
				goalName: goalName || null,
				goalAmount: amountNum,
			},
		});
	};

	const handleClearGoal = async () => {
		await updateGoal({
			variables: {
				accountId,
				goalName: null,
				goalAmount: null,
			},
		});
		setGoalName("");
		setGoalAmount("");
		showSuccess("目標をクリアしました");
	};

	return (
		<Dialog open={open} onOpenChange={setOpen}>
			<DialogTrigger asChild>
				<Button
					variant="outline"
					size="sm"
					className="w-full border-purple-600 text-purple-600 hover:bg-purple-50"
				>
					<Target className="w-4 h-4 mr-2" />
					{currentGoalName ? "目標を編集" : "目標を設定"}
				</Button>
			</DialogTrigger>
			<DialogContent>
				<DialogHeader>
					<DialogTitle>貯金目標の設定</DialogTitle>
				</DialogHeader>
				<form onSubmit={handleSubmit} className="space-y-4">
					<div>
						<Label htmlFor="goal-name">目標名</Label>
						<Input
							id="goal-name"
							type="text"
							placeholder="例: 新しいゲーム機"
							value={goalName}
							onChange={(e) => setGoalName(e.target.value)}
						/>
					</div>
					<div>
						<Label htmlFor="goal-amount">目標金額 (円)</Label>
						<Input
							id="goal-amount"
							type="number"
							placeholder="10000"
							value={goalAmount}
							onChange={(e) => setGoalAmount(e.target.value)}
							min="0"
						/>
					</div>
					<div className="flex gap-2">
						<Button
							type="submit"
							className="flex-1 bg-purple-600 hover:bg-purple-700 dark:bg-purple-700 dark:hover:bg-purple-600"
							disabled={loading}
						>
							{loading ? "保存中..." : "保存"}
						</Button>
						{(currentGoalName || currentGoalAmount) && (
							<ConfirmDialog
								title="目標をクリア"
								description="目標をクリアしますか？この操作は取り消せません。"
								confirmLabel="クリア"
								onConfirm={handleClearGoal}
								variant="outline"
								disabled={loading}
							>
								クリア
							</ConfirmDialog>
						)}
					</div>
				</form>
			</DialogContent>
		</Dialog>
	);
}
