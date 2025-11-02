"use client";

import { useMutation, useQuery } from "@apollo/client/react";
import { ArrowLeft, Save, User } from "lucide-react";
import Image from "next/image";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";
import DeleteAccountDialog from "@/components/delete-account-dialog";
import RecurringDepositSettings from "@/components/recurring-deposit-settings";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
	DELETE_CHILD,
	GET_ME,
	UPDATE_PROFILE,
} from "@/lib/graphql/queries";
import type { GetMeResponse } from "@/lib/graphql/types";
import { getUser } from "@/lib/supabase/auth";
import { deleteAvatar, uploadAvatar } from "@/lib/supabase/storage";

export default function ChildSettingsPage() {
	const params = useParams();
	const childUserId = params.userId as string;
	const router = useRouter();
	const [currentUserId, setCurrentUserId] = useState<string | null>(null);
	const [name, setName] = useState("");
	const [avatarUrl, setAvatarUrl] = useState("");
	const [avatarFile, setAvatarFile] = useState<File | null>(null);
	const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
	const fileInputRef = useRef<HTMLInputElement>(null);
	const nameInputId = useId();
	const avatarInputId = useId();

	// 現在のログインユーザー情報を取得
	useEffect(() => {
		const fetchUser = async () => {
			try {
				const user = await getUser();
				if (!user) {
					router.push("/login");
					return;
				}
				setCurrentUserId(user.id);
			} catch (error) {
				console.error("ユーザー取得エラー:", error);
				router.push("/login");
			}
		};
		fetchUser();
	}, [router]);

	// 現在のログインユーザー情報を取得（権限チェック用）
	const { data: meData, loading: meLoading } = useQuery<GetMeResponse>(GET_ME, {
		variables: { userId: currentUserId || "" },
		skip: !currentUserId,
	});

	// 子どものプロフィール情報を取得
	const {
		data: childProfileData,
		loading: childProfileLoading,
		refetch,
	} = useQuery<GetMeResponse>(GET_ME, {
		variables: { userId: childUserId },
		skip: !childUserId,
	});

	// 子どもプロフィールデータの初期化
	useEffect(() => {
		if (childProfileData?.me) {
			setName(childProfileData.me.name || "");
			setAvatarUrl(childProfileData.me.avatarUrl || "");
		}
	}, [childProfileData]);

	// 親権限チェック
	const isParent = meData?.me?.role === "parent";
	const isOwnProfile = currentUserId === childUserId;
	const isParentOfChild =
		isParent &&
		childProfileData?.me?.role === "child" &&
		childProfileData?.me?.parents?.some(
			(parent) => parent.id === currentUserId,
		);

	// デバッグ用
	useEffect(() => {
		if (!meLoading && !childProfileLoading) {
			console.log("権限チェック情報:", {
				currentUserId,
				childUserId,
				isParent,
				isOwnProfile,
				isParentOfChild,
				meRole: meData?.me?.role,
				childRole: childProfileData?.me?.role,
				childParents: childProfileData?.me?.parents?.map((p) => p.id),
			});
		}
	}, [
		meLoading,
		childProfileLoading,
		currentUserId,
		childUserId,
		isParent,
		isOwnProfile,
		isParentOfChild,
		meData,
		childProfileData,
	]);

	// 更新用mutation
	const [updateProfile, { loading: updating }] = useMutation(UPDATE_PROFILE, {
		onCompleted: () => {
			alert("プロフィールを更新しました");
			refetch();
		},
		onError: (error: { message: string }) => {
			alert(`更新に失敗しました: ${error.message}`);
		},
	});

	// 削除用mutation
	const [deleteChild] = useMutation(DELETE_CHILD, {
		onCompleted: () => {
			alert("子どもアカウントを削除しました");
			router.push("/dashboard");
		},
		onError: (error: { message: string }) => {
			alert(`削除に失敗しました: ${error.message}`);
		},
	});

	const handleDeleteChild = async (childId: string) => {
		if (!currentUserId) return;

		await deleteChild({
			variables: {
				parentId: currentUserId,
				childId: childId,
			},
		});
	};

	const handleUpdateProfile = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!childUserId) return;

		try {
			let finalAvatarUrl = avatarUrl;

			// 新しい画像ファイルが選択されている場合、アップロード
			if (avatarFile) {
				// 古い画像を削除（オプション）
				if (avatarUrl) {
					await deleteAvatar(avatarUrl);
				}

				// 新しい画像をアップロード
				finalAvatarUrl = await uploadAvatar(avatarFile, childUserId);
			}

			await updateProfile({
				variables: {
					userId: childUserId,
					currentUserId: currentUserId || "",
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

	// 権限チェック：親でない場合はアクセス拒否
	// データ読み込み中は権限チェックをスキップ
	if (!meLoading && !childProfileLoading && meData && childProfileData) {
		// 自分自身のプロフィール、または親が自分の子どものプロフィールの場合のみアクセス可能
		const hasAccess = isOwnProfile || isParentOfChild;

		if (!hasAccess) {
			return (
				<div className="min-h-screen bg-gray-100 p-6 flex items-center justify-center">
					<div className="bg-white rounded-lg shadow-md p-8 text-center">
						<p className="text-red-600 font-bold">アクセスが拒否されました</p>
						<p className="text-gray-600 mt-2">
							このページにアクセスする権限がありません
						</p>
						<p className="text-xs text-gray-500 mt-2">
							デバッグ: isParent={String(isParent)}, isOwnProfile=
							{String(isOwnProfile)}, isParentOfChild={String(isParentOfChild)}
						</p>
						<Button onClick={() => router.push("/dashboard")} className="mt-4">
							ダッシュボードに戻る
						</Button>
					</div>
				</div>
			);
		}
	}

	if (childProfileLoading || meLoading) {
		return (
			<div className="min-h-screen bg-gray-100 p-6 flex items-center justify-center">
				<div className="text-gray-600">読み込み中...</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen bg-gray-100 p-6">
			<div className="max-w-2xl mx-auto">
				{/* ヘッダー */}
				<div className="mb-6 flex items-center gap-4">
					<Button
						onClick={() => router.push("/dashboard")}
						variant="ghost"
						size="sm"
					>
						<ArrowLeft className="w-4 h-4 mr-2" />
						戻る
					</Button>
					<h1 className="text-2xl font-bold text-gray-900">
						{childProfileData?.me?.name || "子ども"}の設定
					</h1>
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
				<div className="bg-white rounded-lg shadow-md p-6">
					<h2 className="text-xl font-bold text-gray-900 mb-4">
						アカウント情報
					</h2>
					<div className="space-y-3">
						<div>
							<p className="text-sm text-gray-600">ロール</p>
							<p className="text-lg font-semibold">
								{childProfileData?.me?.role === "parent" ? "親" : "子ども"}
							</p>
						</div>
						<div>
							<p className="text-sm text-gray-600">ユーザーID</p>
							<p className="text-sm font-mono text-gray-800 break-all">
								{childUserId}
							</p>
						</div>
					</div>
				</div>

				{/* アカウント削除セクション（親が子どもを削除する場合のみ表示） */}
				{isParent && isParentOfChild && (
					<div className="bg-white rounded-lg shadow-md p-6 border border-red-200">
						<h2 className="text-xl font-bold text-red-600 mb-4">
							アカウントの削除
						</h2>
						<p className="text-sm text-gray-700 mb-4">
							この操作は取り消せません。子どもアカウントに関連する
							<strong>すべてのデータ</strong>
							（残高、トランザクション履歴、目標など）が完全に削除されます。
						</p>
						<DeleteAccountDialog
							accountId={childUserId}
							accountName={childProfileData?.me?.name || ""}
							onDelete={handleDeleteChild}
							buttonText="アカウントを削除"
							title={`${childProfileData?.me?.name || "子ども"}のアカウントを削除`}
							description={
								<span>
									<span className="font-semibold text-gray-900">
										{childProfileData?.me?.name}
									</span>{" "}
									のアカウントを完全に削除します。すべてのお小遣いデータ、トランザクション履歴、目標などが削除されます。
								</span>
							}
						/>
					</div>
				)}

				{/* 定期お小遣い設定セクション（親が子どもに対してのみ表示） */}
				{isParent && isParentOfChild && (
					<RecurringDepositSettings
						childUserId={childUserId}
						currentUserId={currentUserId ?? ""}
						childName={childProfileData?.me?.name || ""}
					/>
				)}
			</div>
		</div>
	);
}
