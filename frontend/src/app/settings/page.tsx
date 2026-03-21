"use client";

import { useMutation, useQuery } from "@apollo/client/react";
import { ArrowLeft, Copy, UserPlus, Users } from "lucide-react";
import { useRouter } from "next/navigation";
import { useId, useState } from "react";
import { LogoutButton } from "@/components/logout-button";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { auth } from "@/lib/firebase/client";
import {
	CREATE_ACCOUNT,
	INVITE_CHILD,
	INVITE_PARENT,
	MY_FAMILY,
} from "@/lib/graphql/queries";
import type {
	CreateAccountResponse,
	InviteChildResponse,
	InviteParentResponse,
	MyFamilyResponse,
} from "@/lib/graphql/types";

export default function SettingsPage() {
	const router = useRouter();
	const currentUid = auth.currentUser?.uid;

	const [inviteParentEmail, setInviteParentEmail] = useState("");
	const [parentInviteLink, setParentInviteLink] = useState<string | null>(null);
	const inviteParentEmailId = useId();

	const [childName, setChildName] = useState("");
	const [childInviteLink, setChildInviteLink] = useState<string | null>(null);
	const childNameId = useId();

	const [accountName, setAccountName] = useState("");
	const [isCreatingAccount, setIsCreatingAccount] = useState(false);
	const accountNameId = useId();

	const {
		data: familyData,
		loading: familyLoading,
		refetch,
	} = useQuery<MyFamilyResponse>(MY_FAMILY);

	const family = familyData?.myFamily;
	const currentMember = family?.members.find((m) => m.uid === currentUid);
	const isParent = currentMember?.role === "parent";

	const [inviteParent, { loading: invitingParent }] =
		useMutation<InviteParentResponse>(INVITE_PARENT);
	const [inviteChild, { loading: invitingChild }] =
		useMutation<InviteChildResponse>(INVITE_CHILD);
	const [createAccount] = useMutation<CreateAccountResponse>(CREATE_ACCOUNT, {
		refetchQueries: [{ query: MY_FAMILY }],
	});

	const handleInviteParent = async () => {
		if (!family?.id || !inviteParentEmail) return;
		try {
			const res = await inviteParent({
				variables: { familyId: family.id, email: inviteParentEmail },
			});
			const token = res.data?.inviteParent;
			if (token) {
				const link = `${window.location.origin}/accept-invite?token=${token}`;
				setParentInviteLink(link);
				setInviteParentEmail("");
			}
		} catch (error) {
			console.error("親招待エラー:", error);
		}
	};

	const handleInviteChild = async () => {
		if (!family?.id || !childName.trim()) return;
		try {
			const res = await inviteChild({
				variables: { familyId: family.id, childName: childName.trim() },
			});
			const token = res.data?.inviteChild;
			if (token) {
				const link = `${window.location.origin}/child-signup?token=${token}`;
				setChildInviteLink(link);
				setChildName("");
			}
		} catch (error) {
			console.error("子招待エラー:", error);
		}
	};

	const handleCreateAccount = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!family?.id || !accountName.trim()) return;
		setIsCreatingAccount(true);
		try {
			await createAccount({
				variables: { familyId: family.id, name: accountName.trim() },
			});
			setAccountName("");
			await refetch();
		} catch (error) {
			console.error("アカウント作成エラー:", error);
		} finally {
			setIsCreatingAccount(false);
		}
	};

	const copyToClipboard = async (text: string) => {
		try {
			await navigator.clipboard.writeText(text);
		} catch {
			// fallback
		}
	};

	if (familyLoading) {
		return (
			<div className="min-h-screen bg-gray-50 dark:bg-gray-950 p-4 md:p-6 lg:p-8">
				<div className="max-w-2xl mx-auto space-y-6">
					<div className="flex items-center gap-4">
						<Skeleton className="h-10 w-20" />
						<Skeleton className="h-8 w-32" />
					</div>
					<Skeleton className="h-48 w-full rounded-lg" />
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

				{/* 現在のユーザー情報 */}
				{currentMember && (
					<div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-4 md:p-6 mb-6">
						<h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
							アカウント情報
						</h2>
						<div className="space-y-2">
							<div>
								<p className="text-xs text-gray-500">名前</p>
								<p className="font-semibold">{currentMember.name}</p>
							</div>
							<div>
								<p className="text-xs text-gray-500">ロール</p>
								<p className="font-semibold">
									{currentMember.role === "parent" ? "👨‍👩‍👧 親" : "👦 子ども"}
								</p>
							</div>
							{currentMember.email && (
								<div>
									<p className="text-xs text-gray-500">メール</p>
									<p className="font-mono text-sm">{currentMember.email}</p>
								</div>
							)}
						</div>
					</div>
				)}

				{/* 家族メンバー一覧 */}
				{family && (
					<div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-4 md:p-6 mb-6">
						<div className="flex items-center gap-3 mb-4">
							<Users className="w-5 h-5 text-blue-600" />
							<h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
								家族メンバー{family.name ? ` (${family.name})` : ""}
							</h2>
						</div>
						<div className="space-y-2">
							{family.members.map((member) => (
								<div
									key={member.uid}
									className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
								>
									<div>
										<p className="font-medium">{member.name}</p>
										<p className="text-xs text-gray-500">
											{member.role === "parent" ? "親" : "子ども"}
											{member.uid === currentUid && " (あなた)"}
										</p>
									</div>
								</div>
							))}
						</div>
					</div>
				)}

				{/* 親のみ表示セクション */}
				{isParent && family && (
					<>
						{/* 口座作成 */}
						<div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-4 md:p-6 mb-6">
							<h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
								💰 口座を作成
							</h2>
							<form onSubmit={handleCreateAccount} className="space-y-4">
								<div>
									<Label htmlFor={accountNameId}>口座名</Label>
									<Input
										id={accountNameId}
										value={accountName}
										onChange={(e) => setAccountName(e.target.value)}
										placeholder="太郎のおこづかい"
										required
										className="mt-1"
									/>
								</div>
								<Button
									type="submit"
									disabled={isCreatingAccount}
									className="w-full"
								>
									{isCreatingAccount ? "作成中..." : "口座を作成"}
								</Button>
							</form>
						</div>

						{/* 子ども招待 */}
						<div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-4 md:p-6 mb-6">
							<div className="flex items-center gap-3 mb-4">
								<UserPlus className="w-5 h-5 text-green-600" />
								<h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
									👦 子どもを招待
								</h2>
							</div>
							<div className="space-y-4">
								<div>
									<Label htmlFor={childNameId}>子どもの名前</Label>
									<Input
										id={childNameId}
										value={childName}
										onChange={(e) => setChildName(e.target.value)}
										placeholder="太郎"
										className="mt-1"
									/>
								</div>
								<Button
									onClick={handleInviteChild}
									disabled={invitingChild || !childName.trim()}
									className="w-full bg-green-600 hover:bg-green-700"
								>
									{invitingChild ? "作成中..." : "招待リンクを作成"}
								</Button>
								{childInviteLink && (
									<div className="p-4 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-900 rounded-lg">
										<Label className="text-green-800 dark:text-green-400 font-semibold">
											子ども招待リンク
										</Label>
										<div className="mt-2 flex gap-2">
											<Input
												value={childInviteLink}
												readOnly
												className="text-xs font-mono"
											/>
											<Button
												onClick={() => copyToClipboard(childInviteLink)}
												variant="outline"
												size="sm"
											>
												<Copy className="w-4 h-4" />
											</Button>
										</div>
										<p className="text-xs text-green-700 dark:text-green-300 mt-2">
											このリンクを子どもに送ってください。
										</p>
									</div>
								)}
							</div>
						</div>

						{/* 親招待 */}
						<div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-4 md:p-6 mb-6">
							<div className="flex items-center gap-3 mb-4">
								<UserPlus className="w-5 h-5 text-blue-600" />
								<h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
									👨 もう一人の親を招待
								</h2>
							</div>
							<p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
								配偶者やパートナーを招待して、お小遣いを一緒に管理できます。
							</p>
							<div className="space-y-4">
								<div>
									<Label htmlFor={inviteParentEmailId}>メールアドレス</Label>
									<Input
										id={inviteParentEmailId}
										type="email"
										value={inviteParentEmail}
										onChange={(e) => setInviteParentEmail(e.target.value)}
										placeholder="partner@example.com"
										className="mt-1"
									/>
								</div>
								<Button
									onClick={handleInviteParent}
									disabled={invitingParent || !inviteParentEmail}
									className="w-full bg-blue-600 hover:bg-blue-700"
								>
									{invitingParent ? "作成中..." : "招待リンクを作成"}
								</Button>
								{parentInviteLink && (
									<div className="p-4 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-900 rounded-lg">
										<Label className="text-blue-800 dark:text-blue-400 font-semibold">
											親招待リンク
										</Label>
										<div className="mt-2 flex gap-2">
											<Input
												value={parentInviteLink}
												readOnly
												className="text-xs font-mono"
											/>
											<Button
												onClick={() => copyToClipboard(parentInviteLink)}
												variant="outline"
												size="sm"
											>
												<Copy className="w-4 h-4" />
											</Button>
										</div>
										<p className="text-xs text-blue-700 dark:text-blue-300 mt-2">
											このリンクを相手に送信してください。リンクは7日間有効です。
										</p>
									</div>
								)}
							</div>
						</div>
					</>
				)}
			</div>
		</div>
	);
}
