"use client";

import { useMutation } from "@apollo/client/react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useId, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { WITHDRAW } from "@/lib/graphql/queries";

const withdrawSchema = z.object({
	amount: z
		.string()
		.min(1, "金額を入力してください")
		.refine(
			(val) => {
				const num = Number.parseInt(val, 10);
				return !Number.isNaN(num) && num > 0;
			},
			{
				message: "正の整数を入力してください",
			},
		),
	description: z.string().min(1, "説明を入力してください"),
});

type WithdrawFormValues = z.infer<typeof withdrawSchema>;

interface WithdrawDialogProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
	accountId: string;
	accountName: string;
	currentBalance: number;
}

export function WithdrawDialog({
	open,
	onOpenChange,
	accountId,
	accountName,
	currentBalance,
}: WithdrawDialogProps) {
	const [isSubmitting, setIsSubmitting] = useState(false);
	const amountId = useId();
	const descriptionId = useId();

	const {
		register,
		handleSubmit,
		formState: { errors },
		reset,
	} = useForm<WithdrawFormValues>({
		resolver: zodResolver(withdrawSchema),
	});

	const [withdrawMutation] = useMutation(WITHDRAW, {
		refetchQueries: ["GetAccounts", "GetTransactions"],
		awaitRefetchQueries: true,
	});

	const onSubmit = async (data: WithdrawFormValues) => {
		const amount = Number.parseInt(data.amount, 10);

		// 残高チェック（フロントエンドでも確認）
		if (amount > currentBalance) {
			toast.error("残高不足です", {
				description: `現在の残高: ¥${currentBalance.toLocaleString()}`,
			});
			return;
		}

		setIsSubmitting(true);
		try {
			await withdrawMutation({
				variables: {
					accountId,
					amount,
					description: data.description,
				},
			});

			toast.success("出金が完了しました", {
				description: `${data.amount}円を${accountName}から出金しました`,
			});

			reset();
			onOpenChange(false);
		} catch (error) {
			console.error("出金エラー:", error);
			const errorMessage =
				error instanceof Error ? error.message : "もう一度お試しください";
			toast.error("出金に失敗しました", {
				description: errorMessage,
			});
		} finally {
			setIsSubmitting(false);
		}
	};

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="sm:max-w-[425px]">
				<DialogHeader>
					<DialogTitle>出金</DialogTitle>
					<DialogDescription>
						{accountName}から出金する金額と説明を入力してください
						<br />
						<span className="text-sm font-semibold text-gray-700">
							現在の残高: ¥{currentBalance.toLocaleString()}
						</span>
					</DialogDescription>
				</DialogHeader>
				<form onSubmit={handleSubmit(onSubmit)}>
					<div className="grid gap-4 py-4">
						<div className="grid gap-2">
							<Label htmlFor={amountId}>金額(円)</Label>
							<Input
								id={amountId}
								type="number"
								placeholder="1000"
								max={currentBalance}
								{...register("amount")}
							/>
							{errors.amount && (
								<p className="text-sm text-red-500">{errors.amount.message}</p>
							)}
						</div>
						<div className="grid gap-2">
							<Label htmlFor={descriptionId}>説明</Label>
							<Input
								id={descriptionId}
								placeholder="おもちゃ購入"
								{...register("description")}
							/>
							{errors.description && (
								<p className="text-sm text-red-500">
									{errors.description.message}
								</p>
							)}
						</div>
					</div>
					<DialogFooter>
						<Button
							type="button"
							variant="outline"
							onClick={() => onOpenChange(false)}
							disabled={isSubmitting}
						>
							キャンセル
						</Button>
						<Button
							type="submit"
							disabled={isSubmitting}
							className="bg-red-600 hover:bg-red-700"
						>
							{isSubmitting ? "処理中..." : "出金する"}
						</Button>
					</DialogFooter>
				</form>
			</DialogContent>
		</Dialog>
	);
}
