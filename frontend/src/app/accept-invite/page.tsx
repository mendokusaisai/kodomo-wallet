"use client";

import { useLazyQuery, useMutation } from "@apollo/client/react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
	ACCEPT_PARENT_INVITE,
	GET_PARENT_INVITE_EMAIL,
} from "@/lib/graphql/queries";
import { getUser } from "@/lib/supabase/auth";
import { createClient } from "@/lib/supabase/client";
import { showError, showSuccess } from "@/lib/toast";

type AcceptParentInviteResponse = { acceptParentInvite: boolean };
type GetParentInviteEmailResponse = { parentInviteByToken: string | null };

function AcceptInviteInner() {
	const router = useRouter();
	const searchParams = useSearchParams();
	const supabase = createClient();

	const [status, setStatus] = useState<
		| "checking"
		| "user_exists"
		| "user_not_exists"
		| "signup"
		| "processing"
		| "success"
		| "error"
	>("checking");
	const [message, setMessage] = useState<string>("");
	const [inviteEmail, setInviteEmail] = useState<string>("");
	const [token, setToken] = useState<string>("");

	// サインアップフォーム用
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [confirmPassword, setConfirmPassword] = useState("");
	const [name, setName] = useState("");

	const [getInviteEmail] = useLazyQuery<GetParentInviteEmailResponse>(
		GET_PARENT_INVITE_EMAIL,
	);
	const [acceptInvite] =
		useMutation<AcceptParentInviteResponse>(ACCEPT_PARENT_INVITE);

	// 初期チェック: トークンからメールアドレスを取得し、アカウント存在確認
	useEffect(() => {
		const checkInvite = async () => {
			const tokenParam = searchParams.get("token");
			if (!tokenParam) {
				setStatus("error");
				setMessage("無効な招待リンクです（token がありません）");
				return;
			}
			setToken(tokenParam);

			try {
				// トークンからメールアドレスを取得
				const { data, error: gqlError } = await getInviteEmail({
					variables: { token: tokenParam },
				});

				if (gqlError || !data?.parentInviteByToken) {
					setStatus("error");
					setMessage("招待が見つからないか、有効期限切れです");
					return;
				}

				const email = data.parentInviteByToken;
				setInviteEmail(email);
				setEmail(email); // サインアップフォーム用にセット

				// ログイン状態を確認
				const user = await getUser();

				if (user) {
					// 既にログイン済み → 招待受け入れ処理へ
					await processAcceptInvite(tokenParam, user.id);
				} else {
					// 未ログイン → サインアップフォームを表示
					setStatus("user_not_exists");
				}
			} catch (e) {
				setStatus("error");
				setMessage(
					e instanceof Error ? e.message : "招待情報の取得に失敗しました",
				);
			}
		};
		checkInvite();
	}, [searchParams, getInviteEmail]);

	const processAcceptInvite = async (
		inviteToken: string,
		userId: string,
	) => {
		try {
			setStatus("processing");
			setMessage("招待を受け入れています...");

			const res = await acceptInvite({
				variables: { token: inviteToken, currentParentId: userId },
			});

			const ok = res.data?.acceptParentInvite === true;
			if (ok) {
				setStatus("success");
				setMessage("招待を受け入れました。家族関係が追加されました。");
				showSuccess("招待を受け入れました");
				setTimeout(() => router.push("/dashboard"), 1500);
			} else {
				setStatus("error");
				setMessage("招待の受け入れに失敗しました。");
			}
		} catch (e) {
			setStatus("error");
			setMessage(
				e instanceof Error ? e.message : "不明なエラーが発生しました",
			);
		}
	};

	const handleSignup = async (e: React.FormEvent) => {
		e.preventDefault();

		if (password !== confirmPassword) {
			showError("パスワードが一致しません");
			return;
		}

		if (password.length < 8) {
			showError("パスワードは8文字以上で入力してください");
			return;
		}

		try {
			setStatus("processing");
			setMessage("アカウントを作成しています...");

			// アカウント作成
			const { data: signUpData, error: signUpError } =
				await supabase.auth.signUp({
					email,
					password,
					options: {
						data: {
							name,
							role: "parent",
						},
					},
				});

			if (signUpError) throw signUpError;
			if (!signUpData.user) {
				throw new Error("アカウント作成に失敗しました");
			}

			showSuccess("アカウントを作成しました");

			// 自動ログイン
			const { error: signInError } = await supabase.auth.signInWithPassword({
				email,
				password,
			});

			if (signInError) {
				// ログイン失敗の場合、手動でログインしてもらう
				setStatus("error");
				setMessage(
					"アカウントは作成されましたが、ログインに失敗しました。ログインページから手動でログインしてください。",
				);
				setTimeout(() => {
					router.push(
						`/login?redirect=${encodeURIComponent(`/accept-invite?token=${token}`)}`,
					);
				}, 2000);
				return;
			}

			// ログイン成功 → 招待受け入れ
			await processAcceptInvite(token, signUpData.user.id);
		} catch (error) {
			setStatus("error");
			setMessage(
				error instanceof Error ? error.message : "不明なエラーが発生しました",
			);
			showError(
				"エラーが発生しました",
				error instanceof Error ? error.message : "不明なエラー",
			);
		}
	};

	const handleGoToLogin = () => {
		router.push(
			`/login?redirect=${encodeURIComponent(`/accept-invite?token=${token}`)}`,
		);
	};

	return (
		<div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 p-6">
			<div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg p-6 max-w-md w-full">
				<h1 className="text-2xl font-bold mb-4 text-center text-gray-900 dark:text-gray-100">
					👨‍👩‍👧 親アカウント招待
				</h1>

				{status === "checking" && (
					<div className="text-center">
						<p className="text-gray-600 dark:text-gray-400">確認中...</p>
					</div>
				)}

				{status === "processing" && (
					<div className="text-center">
						<p className="text-gray-600 dark:text-gray-400">{message}</p>
					</div>
				)}

				{status === "success" && (
					<div className="text-center">
						<p className="text-green-700 dark:text-green-400">{message}</p>
					</div>
				)}

				{status === "error" && (
					<div className="text-center space-y-4">
						<p className="text-red-600 dark:text-red-400">{message}</p>
						<Button onClick={() => router.push("/dashboard")}>
							ダッシュボードへ
						</Button>
					</div>
				)}

				{status === "user_not_exists" && (
					<div className="space-y-6">
						<div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-900 rounded-lg p-4">
							<p className="text-sm text-blue-800 dark:text-blue-300">
								招待メールアドレス: <strong>{inviteEmail}</strong>
							</p>
						</div>

						<div className="space-y-4">
							<p className="text-gray-700 dark:text-gray-300 text-sm">
								このメールアドレスでアカウントを作成するか、既にアカウントをお持ちの場合はログインしてください。
							</p>

							<Button
								onClick={handleGoToLogin}
								variant="outline"
								className="w-full"
							>
								既にアカウントをお持ちの方はログイン
							</Button>

							<div className="relative">
								<div className="absolute inset-0 flex items-center">
									<span className="w-full border-t border-gray-300 dark:border-gray-700" />
								</div>
								<div className="relative flex justify-center text-xs uppercase">
									<span className="bg-white dark:bg-gray-900 px-2 text-gray-500">
										または
									</span>
								</div>
							</div>

							<form onSubmit={handleSignup} className="space-y-4">
								<div>
									<Label htmlFor="name">お名前</Label>
									<Input
										id="name"
										type="text"
										placeholder="山田 太郎"
										value={name}
										onChange={(e) => setName(e.target.value)}
										required
									/>
								</div>

								<div>
									<Label htmlFor="email">メールアドレス</Label>
									<Input
										id="email"
										type="email"
										value={email}
										readOnly
										className="bg-gray-100 dark:bg-gray-800"
									/>
									<p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
										招待されたメールアドレスが自動入力されています
									</p>
								</div>

								<div>
									<Label htmlFor="password">パスワード（8文字以上）</Label>
									<Input
										id="password"
										type="password"
										placeholder="••••••••"
										value={password}
										onChange={(e) => setPassword(e.target.value)}
										required
										minLength={8}
									/>
								</div>

								<div>
									<Label htmlFor="confirmPassword">
										パスワード（確認）
									</Label>
									<Input
										id="confirmPassword"
										type="password"
										placeholder="••••••••"
										value={confirmPassword}
										onChange={(e) => setConfirmPassword(e.target.value)}
										required
										minLength={8}
									/>
								</div>

								<Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700">
									新規アカウント作成して招待を受け入れる
								</Button>
							</form>
						</div>
					</div>
				)}
			</div>
		</div>
	);
}

export default function AcceptInvitePage() {
	return (
		<Suspense
			fallback={
				<div className="min-h-screen flex items-center justify-center">
					読み込み中…
				</div>
			}
		>
			<AcceptInviteInner />
		</Suspense>
	);
}
