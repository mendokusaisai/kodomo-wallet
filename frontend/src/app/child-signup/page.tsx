"use client";

import { useMutation } from "@apollo/client/react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useId, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ACCEPT_CHILD_INVITE } from "@/lib/graphql/queries";
import { createClient } from "@/lib/supabase/client";

type AcceptChildInviteResponse = { acceptChildInvite: boolean };

function ChildSignupInner() {
	const router = useRouter();
	const searchParams = useSearchParams();
	const supabase = createClient();

	const [status, setStatus] = useState<
		"idle" | "processing" | "success" | "error"
	>("idle");
	const [message, setMessage] = useState<string>("");

	// 新規登録用のstate
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [isSigningUp, setIsSigningUp] = useState(false);

	const passwordId = useId();

	const [acceptInvite] = useMutation<AcceptChildInviteResponse>(
		ACCEPT_CHILD_INVITE,
	);

	const processInvite = useCallback(
		async (token: string, authUserId: string) => {
			try {
				setStatus("processing");
				const res = await acceptInvite({
					variables: { token, authUserId },
				});
				const ok = res.data?.acceptChildInvite === true;
				if (ok) {
					setStatus("success");
					setMessage(
						"アカウントが正常に作成されました！ダッシュボードに移動します...",
					);
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
		},
		[acceptInvite, router],
	);

	const handleSignUp = async (e: React.FormEvent) => {
		e.preventDefault();
		const token = searchParams.get("token");
		if (!token) {
			setStatus("error");
			setMessage("無効な招待リンクです");
			return;
		}

		if (!email) {
			setStatus("error");
			setMessage("メールアドレスを入力してください");
			return;
		}

		setIsSigningUp(true);
		try {
			// 1. アカウント作成
			const { data, error } = await supabase.auth.signUp({
				email,
				password,
			});

			if (error) throw error;
			if (!data.user) throw new Error("ユーザー作成に失敗しました");

			// 2. ログイン
			const { error: loginError } = await supabase.auth.signInWithPassword({
				email,
				password,
			});

			if (loginError) throw loginError;

			// 3. 招待を受け入れる
			await processInvite(token, data.user.id);
		} catch (error) {
			setStatus("error");
			setMessage(
				error instanceof Error
					? error.message
					: "アカウント作成に失敗しました",
			);
		} finally {
			setIsSigningUp(false);
		}
	};

	// トークンの検証
	useEffect(() => {
		const token = searchParams.get("token");
		if (!token) {
			setStatus("error");
			setMessage("無効な招待リンクです（token がありません）");
		}
	}, [searchParams]);

	// エラー・成功画面
	if (status === "processing" || status === "success") {
		return (
			<div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 p-6">
				<div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 max-w-md w-full text-center">
					<h1 className="text-xl font-bold mb-3">
						{status === "processing" ? "処理中..." : "完了！"}
					</h1>
					<p className="text-gray-600 dark:text-gray-400">{message}</p>
				</div>
			</div>
		);
	}

	if (status === "error" && !searchParams.get("token")) {
		return (
			<div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 p-6">
				<div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 max-w-md w-full text-center">
					<h1 className="text-xl font-bold mb-3 text-red-600">エラー</h1>
					<p className="text-red-600">{message}</p>
					<Button className="mt-4" onClick={() => router.push("/login")}>
						ログインページへ
					</Button>
				</div>
			</div>
		);
	}

	// サインアップフォーム
	return (
		<div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 p-6">
			<div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-6 max-w-md w-full">
				<h1 className="text-2xl font-bold mb-2 text-center">
					🎉 こどもウォレットへようこそ
				</h1>
				<p className="text-gray-600 dark:text-gray-400 text-sm mb-6 text-center">
					パスワードを設定してアカウントを作成しましょう
				</p>

				<form onSubmit={handleSignUp} className="space-y-4">
					<div>
						<Label htmlFor="email">メールアドレス</Label>
						<Input
							id="email"
							type="email"
							value={email}
							onChange={(e) => setEmail(e.target.value)}
							placeholder="your@email.com"
							required
						/>
						<p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
							親から招待されたメールアドレスを入力してください
						</p>
					</div>

					<div>
						<Label htmlFor={passwordId}>パスワード</Label>
						<Input
							id={passwordId}
							type="password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							placeholder="8文字以上"
							required
							minLength={8}
						/>
						<p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
							8文字以上で設定してください
						</p>
					</div>

					{status === "error" && (
						<div className="p-3 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-900 rounded">
							<p className="text-sm text-red-600 dark:text-red-400">
								{message}
							</p>
						</div>
					)}

					<Button
						type="submit"
						className="w-full bg-blue-600 hover:bg-blue-700"
						disabled={isSigningUp}
					>
						{isSigningUp ? "作成中..." : "アカウントを作成"}
					</Button>
				</form>

				<div className="mt-4 text-center">
					<p className="text-sm text-gray-600 dark:text-gray-400">
						すでにアカウントをお持ちの場合は
						<Button
							variant="link"
							className="p-0 h-auto ml-1"
							onClick={() => router.push("/login")}
						>
							ログイン
						</Button>
					</p>
				</div>
			</div>
		</div>
	);
}

export default function ChildSignupPage() {
	return (
		<Suspense
			fallback={
				<div className="min-h-screen flex items-center justify-center">
					読み込み中…
				</div>
			}
		>
			<ChildSignupInner />
		</Suspense>
	);
}
