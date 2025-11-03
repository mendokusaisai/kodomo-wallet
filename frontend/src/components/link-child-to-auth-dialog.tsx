"use client";

import { useMutation } from "@apollo/client/react";
import { zodResolver } from "@hookform/resolvers/zod";
import { Copy } from "lucide-react";
import { useId, useState } from "react";
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
	const [inviteLink, setInviteLink] = useState<string | null>(null);
	
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
			const response = await inviteChild({
				variables: {
					childId,
					email: data.email,
				},
			});

			const token = (response.data as { inviteChildToAuth?: string })?.inviteChildToAuth;
			if (token) {
				const origin = typeof window !== "undefined" ? window.location.origin : "";
				const link = `${origin}/child-signup?token=${token}`;
				setInviteLink(link);

				toast.success("招待リンクを作成しました", {
					description: "リンクをコピーして子どもに送信してください",
				});
			}
		} catch (error) {
			console.error("招待リンク作成エラー:", error);
			toast.error("招待リンクの作成に失敗しました", {
				description: "もう一度お試しください",
			});
		}
	};

	const handleCopyLink = async () => {
		if (!inviteLink) return;

		try {
			await navigator.clipboard.writeText(inviteLink);
			toast.success("リンクをコピーしました", {
				description: "子どもに送信してください",
			});
		} catch {
			toast.error("コピーに失敗しました");
		}
	};

	const handleClose = () => {
		reset();
		setInviteLink(null);
		onOpenChange(false);
	};

	return (
		<Dialog open={open} onOpenChange={handleClose}>
			<DialogContent className="sm:max-w-md">
				<DialogHeader>
					<DialogTitle>認証アカウント招待リンク作成</DialogTitle>
					<DialogDescription>
						{childName}
						さんのメールアドレスを入力して招待リンクを作成してください。
						<br />
						作成されたリンクを子どもに送信すると、パスワードを設定してログインできます。
					</DialogDescription>
				</DialogHeader>

				{!inviteLink ? (
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
								招待リンクからパスワードを設定すると、自動的にアカウントが紐付けられます
							</p>
						</div>

						{/* ボタン */}
						<div className="flex justify-end gap-3">
							<Button
								type="button"
								variant="outline"
								onClick={handleClose}
								disabled={loading}
							>
								キャンセル
							</Button>
							<Button type="submit" disabled={loading}>
								{loading ? "作成中..." : "招待リンクを作成"}
							</Button>
						</div>
					</form>
				) : (
					<div className="space-y-4">
						{/* 招待リンク表示 */}
						<div className="space-y-2">
							<Label>招待リンク</Label>
							<div className="flex gap-2">
								<Input
									value={inviteLink}
									readOnly
									className="text-sm font-mono"
								/>
								<Button
									onClick={handleCopyLink}
									variant="outline"
									size="icon"
									className="flex-shrink-0"
								>
									<Copy className="w-4 h-4" />
								</Button>
							</div>
							<p className="text-xs text-green-700 dark:text-green-300">
								✓ リンクをコピーして、{childName}さんに送信してください
							</p>
						</div>

						{/* 完了ボタン */}
						<div className="flex justify-end">
							<Button onClick={handleClose}>
								完了
							</Button>
						</div>
					</div>
				)}
			</DialogContent>
		</Dialog>
	);
}
