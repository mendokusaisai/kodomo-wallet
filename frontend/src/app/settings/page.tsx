"use client";

import { useMutation, useQuery } from "@apollo/client/react";
import { ArrowLeft, Copy, Save, Trash2, User, UserPlus } from "lucide-react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";
import DeleteAccountDialog from "@/components/delete-account-dialog";
import { LogoutButton } from "@/components/logout-button";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
	CREATE_PARENT_INVITE,
	GET_CHILDREN_COUNT,
	GET_ME,
	UPDATE_PROFILE,
} from "@/lib/graphql/queries";
import type { GetMeResponse } from "@/lib/graphql/types";
import { getUser } from "@/lib/supabase/auth";
import { createClient } from "@/lib/supabase/client";
import { deleteAvatar, uploadAvatar } from "@/lib/supabase/storage";
import { showError, showSuccess, showWarning } from "@/lib/toast";

export default function SettingsPage() {
	const router = useRouter();
	const supabase = createClient();
	const [userId, setUserId] = useState<string | null>(null);
	const [name, setName] = useState("");
	const [avatarUrl, setAvatarUrl] = useState("");
	const [avatarFile, setAvatarFile] = useState<File | null>(null);
	const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
	const fileInputRef = useRef<HTMLInputElement>(null);
	const nameInputId = useId();
	const avatarInputId = useId();

	// 親招待用のstate
	const [inviteEmail, setInviteEmail] = useState("");
	const [inviteLink, setInviteLink] = useState<string | null>(null);
	const inviteEmailId = useId();

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
		refetch,
	} = useQuery<GetMeResponse>(GET_ME, {
		variables: { userId },
		skip: !userId,
	});

	// 子どもの数を取得（親の場合のみ）
	const { data: childrenCountData } = useQuery<{ childrenCount: number }>(
		GET_CHILDREN_COUNT,
		{
			variables: { parentId: userId },
			skip: !userId || meData?.me?.role !== "parent",
		},
	);

	// 親招待mutation
	const [createParentInvite, { loading: inviting }] = useMutation<{
		createParentInvite: string;
	}>(CREATE_PARENT_INVITE, {
		onError: (error: { message: string }) => {
			showError("招待リンクの作成に失敗しました", error.message);
		},
	});

	// プロフィールデータが読み込まれたら初期値を設定
	useEffect(() => {
		if (meData?.me) {
			setName(meData.me.name);
			setAvatarUrl(meData.me.avatarUrl || "");
		}
	}, [meData]);

	const [updateProfile, { loading: updating }] = useMutation(UPDATE_PROFILE, {
		onCompleted: () => {
			showSuccess("プロフィールを更新しました");
			refetch();
		},
		onError: (error: { message: string }) => {
			showError("更新に失敗しました", error.message);
		},
	});

	const handleUpdateProfile = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!userId) return;

		try {
			let finalAvatarUrl = avatarUrl;

			// 子どもロールの場合のみアバターアップロード処理
			if (meData?.me?.role === "child" && avatarFile) {
				// 古い画像を削除（オプション）
				if (avatarUrl) {
					await deleteAvatar(avatarUrl);
				}

				// 新しい画像をアップロード
				finalAvatarUrl = await uploadAvatar(avatarFile, userId);
			}

			await updateProfile({
				variables: {
					userId,
					currentUserId: userId,
					name: name || null,
					avatarUrl: finalAvatarUrl || null,
				},
			});

			// アップロード後、ファイル選択とプレビューをクリア
			setAvatarFile(null);
			setAvatarPreview(null);
			if (fileInputRef.current) {
				fileInputRef.current.value = "";
			}
		} catch (error) {
			showError(
				"更新に失敗しました",
				error instanceof Error ? error.message : "不明なエラー",
			);
		}
	};

	const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		const file = e.target.files?.[0];
		if (!file) return;

		// ファイルサイズチェック（5MB以下）
		if (file.size > 5 * 1024 * 1024) {
			showError("ファイルサイズは5MB以下にしてください");
			return;
		}

		// ファイルタイプチェック
		if (!file.type.startsWith("image/")) {
			showError("画像ファイルを選択してください");
			return;
		}

		setAvatarFile(file);

		// プレビュー用のURLを生成
		const reader = new FileReader();
		reader.onloadend = () => {
			setAvatarPreview(reader.result as string);
		};
		reader.readAsDataURL(file);
	};

	const handleCreateInvite = async () => {
		if (!userId) return;
		if (!inviteEmail) {
			showWarning("メールアドレスを入力してください");
			return;
		}

		try {
			const res = await createParentInvite({
				variables: {
					inviterId: userId,
					email: inviteEmail,
				},
			});

			const token: string | undefined = res.data?.createParentInvite;
			if (token) {
				const origin =
					typeof window !== "undefined" ? window.location.origin : "";
				const link = `${origin}/accept-invite?token=${token}`;
				setInviteLink(link);
				showSuccess("招待リンクを作成しました");
				setInviteEmail("");
			}
		} catch {
			/* すでに onError で通知 */
		}
	};

	const handleCopyInviteLink = async () => {
		if (!inviteLink) return;

		try {
			await navigator.clipboard.writeText(inviteLink);
			showSuccess("招待リンクをコピーしました");
		} catch (error) {
			showError(
				"コピーに失敗しました",
				error instanceof Error ? error.message : "不明なエラー",
			);
		}
	};

	const handleDeleteAccount = async (accountId: string) => {
		// 親の場合、子どもがいないかチェック
		if (meData?.me?.role === "parent") {
			const childrenCount = childrenCountData?.childrenCount || 0;
			if (childrenCount > 0) {
				showWarning(
					"アカウントを削除できません",
					`このアカウントには${childrenCount}人の子どもアカウントが紐づいています。先にすべての子どもアカウントを削除してから、再度お試しください。`,
				);
				return;
			}
		}

		try {
			// Supabase認証アカウントを削除（これによりプロフィールもカスケード削除される）
			const { error } = await supabase.auth.admin.deleteUser(accountId);

			if (error) throw error;

			showSuccess("アカウントを削除しました");
			router.push("/login");
		} catch (error) {
			console.error("削除エラー:", error);
			showError(
				"アカウントの削除に失敗しました",
				"サポートにお問い合わせください",
			);
		}
	};

	if (meLoading) {
		return (
			<div className="min-h-screen bg-gray-50 dark:bg-gray-950 p-4 md:p-6 lg:p-8">
				<div className="max-w-2xl mx-auto space-y-6">
					<div className="flex items-center gap-4">
						<Skeleton className="h-10 w-20" />
						<Skeleton className="h-8 w-32" />
					</div>
					<Skeleton className="h-64 w-full rounded-lg" />
					<Skeleton className="h-48 w-full rounded-lg" />
				</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen bg-gray-50 dark:bg-gray-950 p-4 md:p-6 lg:p-8">
			<div className="max-w-2xl mx-auto">
				{/* ヘッダー */}
				<div className="mb-6 md:mb-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
					<div className="flex items-center gap-4">
						<Button
							variant="outline"
							size="sm"
							onClick={() => router.push("/dashboard")}
						>
							<ArrowLeft className="w-4 h-4 mr-2" />
							戻る
						</Button>
						<h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-gray-100">
							設定
						</h1>
					</div>
					<LogoutButton />
				</div>

				{/* プロフィール編集セクション */}
				<div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-4 md:p-6 mb-6">
					<div className="flex items-center gap-3 mb-6">
						<User className="w-6 h-6 text-blue-600 dark:text-blue-400" />
						<h2 className="text-lg md:text-xl font-bold text-gray-900 dark:text-gray-100">
							プロフィール
						</h2>
					</div>

					<form onSubmit={handleUpdateProfile} className="space-y-4">
						<div>
							<Label htmlFor={nameInputId} className="mb-2 block">名前</Label>
							<Input
								id={nameInputId}
								type="text"
								value={name}
								onChange={(e) => setName(e.target.value)}
								placeholder="山田 太郎"
								required
							/>
						</div>

						{/* 子どもロールの場合のみアバター設定を表示 */}
						{meData?.me?.role === "child" && (
							<>
								<div>
									<Label htmlFor={avatarInputId} className="mb-2 block">アバター画像（任意）</Label>
									<div className="space-y-3">
										<Input
											ref={fileInputRef}
											id={avatarInputId}
											type="file"
											accept="image/*"
											onChange={handleFileChange}
											className="cursor-pointer"
										/>
										<p className="text-xs text-gray-500 dark:text-gray-400">
											JPG、PNG、GIF形式の画像ファイル（最大5MB）
										</p>
									</div>
								</div>

								{/* プレビュー表示 */}
								{(avatarPreview || avatarUrl) && (
									<div>
										<Label>プレビュー</Label>
										<div className="mt-2 flex items-center gap-4">
											<Image
												src={avatarPreview || avatarUrl}
												alt="Avatar preview"
												width={64}
												height={64}
												className="rounded-full object-cover"
												unoptimized
												onError={(e) => {
													e.currentTarget.style.display = "none";
												}}
											/>
											{avatarPreview && (
												<p className="text-sm text-blue-600 dark:text-blue-400">
													新しい画像（保存後に反映されます）
												</p>
											)}
										</div>
									</div>
								)}
							</>
						)}

						<Button
							type="submit"
							className="w-full bg-blue-600 hover:bg-blue-700"
							disabled={updating}
						>
							<Save className="w-4 h-4 mr-2" />
							{updating ? "保存中..." : "保存"}
						</Button>
					</form>
				</div>

				{/* アカウント情報セクション */}
				<div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-4 md:p-6 mb-6">
					<h2 className="text-lg md:text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
						アカウント情報
					</h2>
					<div className="space-y-3">
						<div>
							<p className="text-sm text-gray-600 dark:text-gray-400">ロール</p>
							<p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
								{meData?.me?.role === "parent" ? "親" : "子ども"}
							</p>
						</div>
						<div>
							<p className="text-sm text-gray-600 dark:text-gray-400">
								ユーザーID
							</p>
							<p className="text-xs font-mono text-gray-700 dark:text-gray-300 break-all">
								{userId}
							</p>
						</div>
						<div>
							<p className="text-sm text-gray-600 dark:text-gray-400">作成日</p>
							<p className="text-sm text-gray-900 dark:text-gray-100">
								{meData?.me?.createdAt
									? new Date(meData.me.createdAt).toLocaleDateString("ja-JP")
									: "-"}
							</p>
						</div>
					</div>
				</div>

				{/* 親招待セクション（親の場合のみ表示） */}
				{meData?.me?.role === "parent" && (
					<div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-4 md:p-6 mb-6">
						<div className="flex items-center gap-3 mb-4">
							<UserPlus className="w-6 h-6 text-blue-600 dark:text-blue-400" />
							<h2 className="text-lg md:text-xl font-bold text-gray-900 dark:text-gray-100">
								もう一人の親を招待
							</h2>
						</div>
						<p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
							配偶者やパートナーを招待して、子どものお小遣いを一緒に管理できます。
						</p>

						<div className="space-y-4">
							{/* メールアドレス入力 */}
							<div>
								<Label htmlFor={inviteEmailId} className="mb-2 block">招待するメールアドレス</Label>
								<Input
									id={inviteEmailId}
									type="email"
									placeholder="partner@example.com"
									value={inviteEmail}
									onChange={(e) => setInviteEmail(e.target.value)}
								/>
							</div>

							{/* 招待ボタン */}
							<Button
								onClick={handleCreateInvite}
								disabled={inviting || !inviteEmail}
								className="w-full bg-blue-600 hover:bg-blue-700"
							>
								<UserPlus className="w-4 h-4 mr-2" />
								{inviting ? "作成中..." : "招待リンクを作成"}
							</Button>

							{/* 招待リンク表示 */}
							{inviteLink && (
								<div className="mt-4 p-4 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-900 rounded-lg">
									<Label className="text-green-800 dark:text-green-400 font-semibold">
										招待リンク
									</Label>
									<div className="mt-2 flex gap-2">
										<Input
											value={inviteLink}
											readOnly
											className="text-sm font-mono"
										/>
										<Button
											onClick={handleCopyInviteLink}
											variant="outline"
											size="sm"
										>
											<Copy className="w-4 h-4" />
										</Button>
									</div>
									<p className="text-xs text-green-700 dark:text-green-300 mt-2">
										このリンクを相手に送信してください。リンクは7日間有効です。
									</p>
								</div>
							)}
						</div>
					</div>
				)}

				{/* 危険な操作セクション */}
				<div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-4 md:p-6 border-2 border-red-200 dark:border-red-900">
					<div className="flex items-center gap-3 mb-4">
						<Trash2 className="w-6 h-6 text-red-600 dark:text-red-400" />
						<h2 className="text-lg md:text-xl font-bold text-red-900 dark:text-red-400">
							危険な操作
						</h2>
					</div>

					<div className="space-y-4">
						<div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-900 rounded-lg p-4">
							<h3 className="font-semibold text-red-900 dark:text-red-400 mb-2">
								アカウントの削除
							</h3>
							<p className="text-sm text-red-700 dark:text-red-300 mb-4">
								アカウントを削除すると、すべてのデータが完全に削除されます。この操作は取り消せません。
							</p>
							{meData?.me && userId && (
								<DeleteAccountDialog
									accountId={userId}
									accountName={meData.me.name}
									onDelete={handleDeleteAccount}
									buttonText="アカウントを削除"
									title="アカウントの削除"
									description={
										<span>
											<span className="font-semibold text-gray-900">
												{meData.me.name}
											</span>{" "}
											のアカウントを完全に削除します。すべてのお小遣いデータ、トランザクション履歴、目標などが削除されます。
										</span>
									}
								/>
							)}
						</div>
					</div>
				</div>
			</div>
		</div>
	);
}
