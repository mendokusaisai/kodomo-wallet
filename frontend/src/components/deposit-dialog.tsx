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
import { DEPOSIT } from "@/lib/graphql/queries";

const depositSchema = z.object({
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

type DepositFormValues = z.infer<typeof depositSchema>;

interface DepositDialogProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
	accountId: string;
	accountName: string;
}

export function DepositDialog({
	open,
	onOpenChange,
	accountId,
	accountName,
}: DepositDialogProps) {
	const [isSubmitting, setIsSubmitting] = useState(false);
	const amountId = useId();
	const descriptionId = useId();

	const {
		register,
		handleSubmit,
		formState: { errors },
		reset,
	} = useForm<DepositFormValues>({
		resolver: zodResolver(depositSchema),
	});

	const [depositMutation] = useMutation(DEPOSIT, {
		refetchQueries: ["GetAccounts", "GetTransactions"],
		awaitRefetchQueries: true,
	});

	const onSubmit = async (data: DepositFormValues) => {
		setIsSubmitting(true);
		try {
			await depositMutation({
				variables: {
					accountId,
					amount: Number.parseInt(data.amount, 10),
					description: data.description,
				},
			});

			toast.success("入金が完了しました", {
				description: `${data.amount}円を${accountName}に入金しました`,
			});

			reset();
			onOpenChange(false);
		} catch (error) {
			console.error("入金エラー:", error);
			toast.error("入金に失敗しました", {
				description: "もう一度お試しください",
			});
		} finally {
			setIsSubmitting(false);
		}
	};

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="sm:max-w-[425px]">
				<DialogHeader>
					<DialogTitle>入金</DialogTitle>
					<DialogDescription>
						{accountName}に入金する金額と説明を入力してください
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
								placeholder="お小遣い"
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
						<Button type="submit" disabled={isSubmitting}>
							{isSubmitting ? "処理中..." : "入金する"}
						</Button>
					</DialogFooter>
				</form>
			</DialogContent>
		</Dialog>
	);
}
