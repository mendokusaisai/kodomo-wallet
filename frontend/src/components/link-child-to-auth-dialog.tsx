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
import { INVITE_CHILD_TO_AUTH } from "@/lib/graphql/queries";

const linkAuthSchema = z.object({
	email: z.string().email("有効なメールアドレスを入力してください"),
});

type LinkAuthFormData = z.infer<typeof linkAuthSchema>;

interface LinkChildToAuthDialogProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
	childId: string;
	childName: string;
}

export function LinkChildToAuthDialog({
	open,
	onOpenChange,
	childId,
	childName,
}: LinkChildToAuthDialogProps) {
	const {
		register,
		handleSubmit,
		formState: { errors },
		reset,
	} = useForm<LinkAuthFormData>({
		resolver: zodResolver(linkAuthSchema),
		defaultValues: {
			email: "",
		},
	});

	const emailId = useId();

	const [inviteChild, { loading }] = useMutation(INVITE_CHILD_TO_AUTH, {
		refetchQueries: ["GetAccounts"],
		awaitRefetchQueries: true,
	});

	const onSubmit = async (data: LinkAuthFormData) => {
		try {
			await inviteChild({
				variables: {
					childId,
					email: data.email,
				},
			});

			toast.success("招待メールを送信しました", {
				description: `${data.email} に招待メールを送信しました。メールのリンクからパスワードを設定してください。`,
			});

			reset();
			onOpenChange(false);
		} catch (error) {
			console.error("招待メール送信エラー:", error);
			toast.error("招待メールの送信に失敗しました", {
				description: "メールアドレスが正しいか確認してください",
			});
		}
	};

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="sm:max-w-md">
				<DialogHeader>
					<DialogTitle>招待メールを送信</DialogTitle>
					<DialogDescription>
						{childName}
						さんのメールアドレスを入力してください。
						<br />
						招待メールが送信され、メール内のリンクからパスワードを設定できます。
					</DialogDescription>
				</DialogHeader>

				<form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
					{/* メールアドレス */}
					<div className="space-y-2">
						<Label htmlFor={emailId}>メールアドレス</Label>
						<Input
							id={emailId}
							type="email"
							{...register("email")}
							placeholder="例: taro@example.com"
							disabled={loading}
						/>
						{errors.email && (
							<p className="text-sm text-red-600">{errors.email.message}</p>
						)}
						<p className="text-xs text-gray-500">
							※
							招待メールのリンクからパスワードを設定すると、自動的にアカウントが紐付けられます
						</p>
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
							{loading ? "送信中..." : "招待メールを送信"}
						</Button>
					</div>
				</form>
			</DialogContent>
		</Dialog>
	);
}
