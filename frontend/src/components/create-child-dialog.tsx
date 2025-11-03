"use client";

import { useMutation } from "@apollo/client/react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useId } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CREATE_CHILD } from "@/lib/graphql/queries";

const createChildSchema = z.object({
	childName: z.string().min(1, "名前を入力してください"),
	initialBalance: z
		.number()
		.int("整数を入力してください")
		.nonnegative("0以上の値を入力してください")
		.optional(),
});

type CreateChildFormData = z.infer<typeof createChildSchema>;

interface CreateChildDialogProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
	parentId: string;
}

export function CreateChildDialog({
	open,
	onOpenChange,
	parentId,
}: CreateChildDialogProps) {
	const {
		register,
		handleSubmit,
		formState: { errors },
		reset,
	} = useForm<CreateChildFormData>({
		resolver: zodResolver(createChildSchema),
		defaultValues: {
			childName: "",
			initialBalance: 0,
		},
	});

	const nameId = useId();
	const balanceId = useId();

	const [createChild, { loading }] = useMutation(CREATE_CHILD, {
		refetchQueries: ["GetAccounts"],
		awaitRefetchQueries: true,
	});

	const onSubmit = async (data: CreateChildFormData) => {
		try {
			await createChild({
				variables: {
					parentId,
					childName: data.childName,
					initialBalance: data.initialBalance || 0,
				},
			});

			toast.success("子どもアカウントを作成しました", {
				description: `${data.childName}さんのアカウントが作成されました`,
			});

			reset();
			onOpenChange(false);
		} catch (error) {
			console.error("子どもアカウント作成エラー:", error);
			const errorMessage =
				error instanceof Error ? error.message : "不明なエラーが発生しました";
			toast.error("子どもアカウントの作成に失敗しました", {
				description: errorMessage,
			});
		}
	};

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="sm:max-w-md">
				<DialogHeader>
					<DialogTitle>子どもアカウント追加</DialogTitle>
					<DialogDescription>
						お子さんの名前と初期残高を入力してください。
						<br />
						後でお子さん自身が認証アカウントを作成できます。
					</DialogDescription>
				</DialogHeader>

				<form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
					{/* 子どもの名前 */}
					<div className="space-y-2">
						<Label htmlFor={nameId}>子どもの名前</Label>
						<Input
							id={nameId}
							{...register("childName")}
							placeholder="例: 太郎"
							disabled={loading}
						/>
						{errors.childName && (
							<p className="text-sm text-red-600">{errors.childName.message}</p>
						)}
					</div>

					{/* 初期残高 */}
					<div className="space-y-2">
						<Label htmlFor={balanceId}>初期残高（円）</Label>
						<Input
							id={balanceId}
							type="number"
							{...register("initialBalance", { valueAsNumber: true })}
							placeholder="0"
							disabled={loading}
						/>
						{errors.initialBalance && (
							<p className="text-sm text-red-600">
								{errors.initialBalance.message}
							</p>
						)}
					</div>

					{/* ボタン */}
					<div className="flex justify-end gap-3">
						<Button
							type="button"
							variant="outline"
							onClick={() => {
								reset();
								onOpenChange(false);
							}}
							disabled={loading}
						>
							キャンセル
						</Button>
						<Button type="submit" disabled={loading}>
							{loading ? "作成中..." : "作成"}
						</Button>
					</div>
				</form>
			</DialogContent>
		</Dialog>
	);
}
