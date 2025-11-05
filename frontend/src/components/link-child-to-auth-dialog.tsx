"use client";

import { useMutation } from "@apollo/client/react";
import { zodResolver } from "@hookform/resolvers/zod";
import { Copy } from "lucide-react";
import { useEffect, useId, useState } from "react";
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

	const [inviteChild, { loading }] = useMutation(INVITE_CHILD_TO_AUTH);

	// デバッグ: inviteLinkの変更を監視
	useEffect(() => {
		console.log("🔄 inviteLink状態が変更されました:", inviteLink);
	}, [inviteLink]);

	const onSubmit = async (data: LinkAuthFormData) => {
		try {
			const response = await inviteChild({
				variables: {
					childId,
					email: data.email,
				},
			});

			console.log("🔍 招待リンク作成レスポンス:", response);
			console.log("🔍 response.data:", response.data);

			const token = (response.data as { inviteChildToAuth?: string })
				?.inviteChildToAuth;
			console.log("🔍 取得されたトークン:", token);

			if (token) {
				const origin =
					typeof window !== "undefined" ? window.location.origin : "";
				const link = `${origin}/child-signup?token=${token}`;
				console.log("✅ 生成された招待リンク:", link);
				setInviteLink(link);
				console.log("✅ setInviteLink実行後の状態確認");

				// 状態更新を待つため、少し遅延させる
				setTimeout(() => {
					console.log("🔍 setInviteLink後のinviteLink値:", link);
				}, 100);

				toast.success("招待リンクを作成しました", {
					description: "リンクをコピーして子どもに送信してください",
				});
			} else {
				console.error("❌ トークンが取得できませんでした");
				toast.error("招待リンクの作成に失敗しました", {
					description: "トークンが取得できませんでした",
				});
			}
		} catch (error) {
			console.error("❌ 招待リンク作成エラー:", error);
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

	// ダイアログの開閉を制御（意図しない閉じを防ぐ）
	const handleDialogOpenChange = (isOpen: boolean) => {
		if (!isOpen) {
			handleClose();
		}
	};

	return (
		<Dialog open={open} onOpenChange={handleDialogOpenChange}>
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

				{/* デバッグ用 */}
				<div className="text-xs text-gray-500 bg-yellow-50 p-2 rounded">
					🔍 inviteLink: {inviteLink || "(null)"}
					<br />🔍 条件: !inviteLink = {String(!inviteLink)}
					<br />🔍 inviteLink === null = {String(inviteLink === null)}
					<br />🔍 typeof inviteLink = {typeof inviteLink}
				</div>

				{inviteLink === null || inviteLink === "" ? (
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
							<Button onClick={handleClose}>完了</Button>
						</div>
					</div>
				)}
			</DialogContent>
		</Dialog>
	);
}
