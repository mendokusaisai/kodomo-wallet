"use client";

import { useMutation, useQuery } from "@apollo/client/react";
import { ArrowLeft, Save, Trash2, User } from "lucide-react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";
import DeleteAccountDialog from "@/components/delete-account-dialog";
import { LogoutButton } from "@/components/logout-button";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
	GET_CHILDREN_COUNT,
	GET_ME,
	UPDATE_PROFILE,
} from "@/lib/graphql/queries";
import type { GetMeResponse } from "@/lib/graphql/types";
import { getUser } from "@/lib/supabase/auth";
import { createClient } from "@/lib/supabase/client";
import { deleteAvatar, uploadAvatar } from "@/lib/supabase/storage";

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

	// プロフィールデータが読み込まれたら初期値を設定
	useEffect(() => {
		if (meData?.me) {
			setName(meData.me.name);
			setAvatarUrl(meData.me.avatarUrl || "");
		}
	}, [meData]);

	const [updateProfile, { loading: updating }] = useMutation(UPDATE_PROFILE, {
		onCompleted: () => {
			alert("プロフィールを更新しました");
			refetch();
		},
		onError: (error: { message: string }) => {
			alert(`更新に失敗しました: ${error.message}`);
		},
	});

	const handleUpdateProfile = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!userId) return;

		try {
			let finalAvatarUrl = avatarUrl;

			// 新しい画像ファイルが選択されている場合、アップロード
			if (avatarFile) {
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
			alert(
				`更新に失敗しました: ${error instanceof Error ? error.message : "不明なエラー"}`,
			);
		}
	};

	const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		const file = e.target.files?.[0];
		if (!file) return;

		// ファイルサイズチェック（5MB以下）
		if (file.size > 5 * 1024 * 1024) {
			alert("ファイルサイズは5MB以下にしてください");
			return;
		}

		// ファイルタイプチェック
		if (!file.type.startsWith("image/")) {
			alert("画像ファイルを選択してください");
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

	const handleDeleteAccount = async (accountId: string) => {
		// 親の場合、子どもがいないかチェック
		if (meData?.me?.role === "parent") {
			const childrenCount = childrenCountData?.childrenCount || 0;
			if (childrenCount > 0) {
				alert(
					`アカウントを削除できません。\n\nこのアカウントには${childrenCount}人の子どもアカウントが紐づいています。\n先にすべての子どもアカウントを削除してから、再度お試しください。`,
				);
				return;
			}
		}

		try {
			// Supabase認証アカウントを削除（これによりプロフィールもカスケード削除される）
			const { error } = await supabase.auth.admin.deleteUser(accountId);

			if (error) throw error;

			alert("アカウントを削除しました");
			router.push("/login");
		} catch (error) {
			console.error("削除エラー:", error);
			alert("アカウントの削除に失敗しました。サポートにお問い合わせください。");
		}
	};

	if (meLoading) {
		return (
			<div className="min-h-screen flex items-center justify-center">
				<div className="text-lg">読み込み中...</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen bg-gray-50 p-8">
			<div className="max-w-2xl mx-auto">
				{/* ヘッダー */}
				<div className="mb-8 flex items-center justify-between">
					<div className="flex items-center gap-4">
						<Button
							variant="outline"
							size="sm"
							onClick={() => router.push("/dashboard")}
						>
							<ArrowLeft className="w-4 h-4 mr-2" />
							戻る
						</Button>
						<h1 className="text-3xl font-bold text-gray-900">設定</h1>
					</div>
					<LogoutButton />
				</div>

				{/* プロフィール編集セクション */}
				<div className="bg-white rounded-lg shadow-md p-6 mb-6">
					<div className="flex items-center gap-3 mb-6">
						<User className="w-6 h-6 text-blue-600" />
						<h2 className="text-xl font-bold text-gray-900">プロフィール</h2>
					</div>

					<form onSubmit={handleUpdateProfile} className="space-y-4">
						<div>
							<Label htmlFor={nameInputId}>名前</Label>
							<Input
								id={nameInputId}
								type="text"
								value={name}
								onChange={(e) => setName(e.target.value)}
								placeholder="山田 太郎"
								required
							/>
						</div>

						<div>
							<Label htmlFor={avatarInputId}>アバター画像（任意）</Label>
							<div className="space-y-3">
								<Input
									ref={fileInputRef}
									id={avatarInputId}
									type="file"
									accept="image/*"
									onChange={handleFileChange}
									className="cursor-pointer"
								/>
								<p className="text-xs text-gray-500">
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
										onError={(e) => {
											e.currentTarget.style.display = "none";
										}}
									/>
									{avatarPreview && (
										<p className="text-sm text-blue-600">
											新しい画像（保存後に反映されます）
										</p>
									)}
								</div>
							</div>
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
				<div className="bg-white rounded-lg shadow-md p-6 mb-6">
					<h2 className="text-xl font-bold text-gray-900 mb-4">
						アカウント情報
					</h2>
					<div className="space-y-3">
						<div>
							<p className="text-sm text-gray-600">ロール</p>
							<p className="text-lg font-semibold">
								{meData?.me?.role === "parent" ? "親" : "子ども"}
							</p>
						</div>
						<div>
							<p className="text-sm text-gray-600">ユーザーID</p>
							<p className="text-xs font-mono text-gray-700">{userId}</p>
						</div>
						<div>
							<p className="text-sm text-gray-600">作成日</p>
							<p className="text-sm">
								{meData?.me?.createdAt
									? new Date(meData.me.createdAt).toLocaleDateString("ja-JP")
									: "-"}
							</p>
						</div>
					</div>
				</div>

				{/* 危険な操作セクション */}
				<div className="bg-white rounded-lg shadow-md p-6 border-2 border-red-200">
					<div className="flex items-center gap-3 mb-4">
						<Trash2 className="w-6 h-6 text-red-600" />
						<h2 className="text-xl font-bold text-red-900">危険な操作</h2>
					</div>

					<div className="space-y-4">
						<div className="bg-red-50 border border-red-200 rounded-lg p-4">
							<h3 className="font-semibold text-red-900 mb-2">
								アカウントの削除
							</h3>
							<p className="text-sm text-red-700 mb-4">
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
