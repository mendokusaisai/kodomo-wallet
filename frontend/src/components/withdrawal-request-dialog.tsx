"use client";

import { useMutation } from "@apollo/client/react";
import { useState } from "react";
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
import { CREATE_WITHDRAWAL_REQUEST } from "@/lib/graphql/queries";
import { showError, showSuccess } from "@/lib/toast";

interface WithdrawalRequestDialogProps {
	accountId: string;
	currentBalance: number;
}

export default function WithdrawalRequestDialog({
	accountId,
	currentBalance,
}: WithdrawalRequestDialogProps) {
	const [open, setOpen] = useState(false);
	const [amount, setAmount] = useState("");
	const [description, setDescription] = useState("");

	const [createWithdrawalRequest, { loading }] = useMutation(
		CREATE_WITHDRAWAL_REQUEST,
		{
			refetchQueries: ["GetWithdrawalRequests"],
			onCompleted: () => {
				showSuccess("出金申請を送信しました", "承認をお待ちください");
				setAmount("");
				setDescription("");
				setOpen(false);
			},
			onError: (error) => {
				showError("出金申請に失敗しました", error.message);
			},
		},
	);

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();

		const amountNum = Number.parseInt(amount);
		if (Number.isNaN(amountNum) || amountNum <= 0) {
			showError("有効な金額を入力してください");
			return;
		}

		if (amountNum > currentBalance) {
			showError("残高不足です", "申請金額が残高を超えています");
			return;
		}

		await createWithdrawalRequest({
			variables: {
				accountId,
				amount: amountNum,
				description: description || "出金申請",
			},
		});
	};

	return (
		<Dialog open={open} onOpenChange={setOpen}>
			<DialogTrigger asChild>
				<Button
					variant="outline"
					className="border-yellow-600 text-yellow-600 hover:bg-yellow-50"
				>
					出金申請
				</Button>
			</DialogTrigger>
			<DialogContent>
				<DialogHeader>
					<DialogTitle>出金申請</DialogTitle>
				</DialogHeader>
				<form onSubmit={handleSubmit} className="space-y-4">
					<div>
						<Label htmlFor="current-balance">現在の残高</Label>
						<div className="text-2xl font-bold text-gray-900">
							¥{currentBalance.toLocaleString()}
						</div>
					</div>
					<div>
						<Label htmlFor="amount">金額 (円)</Label>
						<Input
							id="amount"
							type="number"
							placeholder="1000"
							value={amount}
							onChange={(e) => setAmount(e.target.value)}
							min="1"
							max={currentBalance}
							required
						/>
					</div>
					<div>
						<Label htmlFor="description">メモ（任意）</Label>
						<Input
							id="description"
							type="text"
							placeholder="例: お小遣い"
							value={description}
							onChange={(e) => setDescription(e.target.value)}
						/>
					</div>
					<Button
						type="submit"
						className="w-full bg-yellow-600 hover:bg-yellow-700"
						disabled={loading}
					>
						{loading ? "申請中..." : "申請する"}
					</Button>
				</form>
			</DialogContent>
		</Dialog>
	);
}
