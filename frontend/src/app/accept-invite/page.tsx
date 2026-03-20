"use client";

import { useMutation } from "@apollo/client/react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useId, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { auth } from "@/lib/firebase/client";
import { signInWithGoogle, signUp } from "@/lib/firebase/auth";
import { JOIN_AS_PARENT } from "@/lib/graphql/queries";
import type { JoinAsParentResponse } from "@/lib/graphql/types";

function AcceptInviteInner() {
	const router = useRouter();
	const searchParams = useSearchParams();

	const [status, setStatus] = useState<
		"checking" | "form" | "processing" | "success" | "error"
	>("checking");
	const [message, setMessage] = useState("");
	const [name, setName] = useState("");
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [token, setToken] = useState("");

	const nameId = useId();
	const emailId = useId();
	const passwordId = useId();

	const [joinAsParent] = useMutation<JoinAsParentResponse>(JOIN_AS_PARENT);

	const processJoin = async (
		joinToken: string,
		joinName: string,
		joinEmail: string,
	) => {
		try {
			setStatus("processing");
			const res = await joinAsParent({
				variables: { token: joinToken, name: joinName, email: joinEmail },
			});
			if (res.data?.joinAsParent) {
				setStatus("success");
				setMessage("招待を受け入れました！");
				setTimeout(() => router.push("/dashboard"), 1500);
			} else {
				setStatus("error");
				setMessage("招待の受け入れに失敗しました。");
			}
		} catch (e) {
			setStatus("error");
			setMessage(e instanceof Error ? e.message : "エラーが発生しました");
		}
	};

	useEffect(() => {
		const tokenParam = searchParams.get("token");
		if (!tokenParam) {
			setStatus("error");
			setMessage("無効な招待リンクです（token がありません）");
			return;
		}
		setToken(tokenParam);

		const currentUser = auth.currentUser;
		if (currentUser) {
			const displayName = currentUser.displayName || "";
			const userEmail = currentUser.email || "";
			void processJoin(tokenParam, displayName, userEmail);
		} else {
			setStatus("form");
		}
	}, [searchParams]);

	const handleSignupAndJoin = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!token || !name || !email || !password) return;
		try {
			setStatus("processing");
			await signUp(email, password);
			await processJoin(token, name, email);
		} catch (e) {
			setStatus("form");
			setMessage(e instanceof Error ? e.message : "サインアップに失敗しました");
		}
	};

	const handleGoogleSignupAndJoin = async () => {
		if (!token) return;
		try {
			setStatus("processing");
			await signInWithGoogle();
			const currentUser = auth.currentUser;
			if (!currentUser) throw new Error("ログインに失敗しました");
			const displayName = currentUser.displayName || "";
			const userEmail = currentUser.email || "";
			await processJoin(token, displayName, userEmail);
		} catch (e) {
			setStatus("form");
			setMessage(e instanceof Error ? e.message : "ログインに失敗しました");
		}
	};

	if (status === "checking" || status === "processing") {
		return (
			<div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950">
				<div className="text-center">
					<div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
					<p className="text-gray-600 dark:text-gray-400">
						{status === "processing" ? "処理中..." : "確認中..."}
					</p>
				</div>
			</div>
		);
	}

	if (status === "success") {
		return (
			<div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950">
				<div className="text-center">
					<div className="text-4xl mb-4">🎉</div>
					<h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
						招待を受け入れました！
					</h1>
					<p className="text-gray-600 dark:text-gray-400">
						ダッシュボードへ移動しています...
					</p>
				</div>
			</div>
		);
	}

	if (status === "error") {
		return (
			<div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950">
				<div className="text-center max-w-md mx-auto p-6">
					<div className="text-4xl mb-4">❌</div>
					<h1 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
						エラーが発生しました
					</h1>
					<p className="text-gray-600 dark:text-gray-400">{message}</p>
				</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 p-4">
			<div className="w-full max-w-md">
				<div className="bg-white dark:bg-gray-900 rounded-xl shadow-md p-6 md:p-8">
					<h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2 text-center">
						👨‍👩‍👧 家族に参加する
					</h1>
					<p className="text-sm text-gray-600 dark:text-gray-400 text-center mb-6">
						招待を受け入れるためにアカウントを作成してください
					</p>

					{message && (
						<div className="mb-4 p-3 bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-300 rounded-lg text-sm">
							{message}
						</div>
					)}

					<Button
						type="button"
						variant="outline"
						className="w-full mb-4 flex items-center justify-center gap-2"
						onClick={handleGoogleSignupAndJoin}
					>
						<svg className="w-5 h-5" viewBox="0 0 24 24">
							<path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
							<path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
							<path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
							<path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
						</svg>
						Google で参加
					</Button>

					<div className="relative mb-4">
						<div className="absolute inset-0 flex items-center">
							<span className="w-full border-t" />
						</div>
						<div className="relative flex justify-center text-xs uppercase">
							<span className="bg-white dark:bg-gray-900 px-2 text-gray-500">
								または
							</span>
						</div>
					</div>

					<form onSubmit={handleSignupAndJoin} className="space-y-4">
						<div>
							<Label htmlFor={nameId}>名前</Label>
							<Input
								id={nameId}
								value={name}
								onChange={(e) => setName(e.target.value)}
								placeholder="山田 花子"
								required
								className="mt-1"
							/>
						</div>
						<div>
							<Label htmlFor={emailId}>メールアドレス</Label>
							<Input
								id={emailId}
								type="email"
								value={email}
								onChange={(e) => setEmail(e.target.value)}
								placeholder="hanako@example.com"
								required
								className="mt-1"
							/>
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
								className="mt-1"
							/>
						</div>
						<Button type="submit" className="w-full">
							アカウントを作成して参加
						</Button>
					</form>
				</div>
			</div>
		</div>
	);
}

export default function AcceptInvitePage() {
	return (
		<Suspense>
			<AcceptInviteInner />
		</Suspense>
	);
}
