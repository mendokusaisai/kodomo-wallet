"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { createClient } from "@/lib/supabase/client";

function ChildSignupInner() {
	const router = useRouter();
	const searchParams = useSearchParams();
	const supabase = createClient();

	const [status, setStatus] = useState<"idle" | "error">("idle");
	const [message, setMessage] = useState<string>("");

	const handleGoogleSignUp = async () => {
		const token = searchParams.get("token");
		if (!token) {
			setStatus("error");
			setMessage("無効な招待リンクです");
			return;
		}

		const { error } = await supabase.auth.signInWithOAuth({
			provider: "google",
			options: {
				redirectTo: `${window.location.origin}/auth/callback?invite_token=${token}`,
			},
		});

		if (error) {
			setStatus("error");
			setMessage(error.message);
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

	// エラー画面
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

	// Google サインアップ画面
	return (
		<div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 p-6">
			<div className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-6 max-w-md w-full">
				<h1 className="text-2xl font-bold mb-2 text-center">
					🎉 こどもウォレットへようこそ
				</h1>
				<p className="text-gray-600 dark:text-gray-400 text-sm mb-6 text-center">
					親から招待されたGoogleアカウントでログインしてください
				</p>

				{status === "error" && (
					<div className="mb-4 p-3 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-900 rounded">
						<p className="text-sm text-red-600 dark:text-red-400">{message}</p>
					</div>
				)}

				<Button
					onClick={handleGoogleSignUp}
					className="w-full bg-blue-600 hover:bg-blue-700 flex items-center justify-center gap-2"
				>
					<svg className="w-5 h-5" viewBox="0 0 24 24" aria-label="Google logo">
						<title>Google</title>
						<path
							fill="currentColor"
							d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
						/>
						<path
							fill="currentColor"
							d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
						/>
						<path
							fill="currentColor"
							d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
						/>
						<path
							fill="currentColor"
							d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
						/>
					</svg>
					Google でサインアップ
				</Button>

				<div className="mt-4 p-3 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-900 rounded">
					<p className="text-xs text-blue-700 dark:text-blue-300">
						💡 親が招待したメールアドレスのGoogleアカウントを使用してください
					</p>
				</div>

				<div className="mt-6 text-center">
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
