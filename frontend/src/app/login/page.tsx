"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useId, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { signIn } from "@/lib/supabase/auth";

function LoginForm() {
	const router = useRouter();
	const searchParams = useSearchParams();
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [isLoading, setIsLoading] = useState(false);
	const emailId = useId();
	const passwordId = useId();

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setIsLoading(true);

		try {
			await signIn(email, password);
			toast.success("ログインしました");
			// リダイレクトパラメータがある場合はそのページへ、なければダッシュボードへ
			const redirect = searchParams.get("redirect") || "/dashboard";
			router.push(redirect);
			router.refresh();
		} catch (error) {
			console.error("ログインエラー:", error);
			toast.error("ログインに失敗しました", {
				description: "メールアドレスとパスワードを確認してください",
			});
		} finally {
			setIsLoading(false);
		}
	};

	// テストユーザーでログイン
	const handleTestLogin = async () => {
		setIsLoading(true);
		try {
			await signIn("kodomo-test@outlook.com", "password123");
			toast.success("ログインしました");
			const redirect = searchParams.get("redirect") || "/dashboard";
			router.push(redirect);
			router.refresh();
		} catch (error) {
			console.error("ログインエラー:", error);
			toast.error("ログインに失敗しました");
		} finally {
			setIsLoading(false);
		}
	};

	// 子どもアカウントでログイン
	const handleChildLogin = async () => {
		setIsLoading(true);
		try {
			await signIn("child@test.com", "password123");
			toast.success("ログインしました");
			const redirect = searchParams.get("redirect") || "/dashboard";
			router.push(redirect);
			router.refresh();
		} catch (error) {
			console.error("ログインエラー:", error);
			toast.error("ログインに失敗しました");
		} finally {
			setIsLoading(false);
		}
	};

	return (
		<div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4">
			<div className="w-full max-w-md">
				<div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-6 md:p-8">
					{/* ヘッダー */}
					<div className="text-center mb-6 md:mb-8">
						<h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
							Kodomo Wallet
						</h1>
						<p className="text-sm md:text-base text-gray-600 dark:text-gray-400">
							親子で楽しく学べるおこづかい管理
						</p>
					</div>

					{/* ログインフォーム */}
					<form onSubmit={handleSubmit} className="space-y-4">
						<div>
							<Label htmlFor={emailId}>メールアドレス</Label>
							<Input
								id={emailId}
								type="email"
								value={email}
								onChange={(e) => setEmail(e.target.value)}
								placeholder="your@email.com"
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
								placeholder="••••••••"
								required
								className="mt-1"
							/>
						</div>

						<Button type="submit" disabled={isLoading} className="w-full">
							{isLoading ? "処理中..." : "ログイン"}
						</Button>
					</form>

					{/* テストユーザーログイン */}
					<div className="mt-6">
						<div className="space-y-2">
							<Button
								type="button"
								onClick={handleTestLogin}
								disabled={isLoading}
								variant="outline"
								className="w-full border-dashed bg-green-50 hover:bg-green-100 text-green-800 border-green-200"
							>
								👨 親アカウントでログイン
							</Button>
							<Button
								type="button"
								onClick={handleChildLogin}
								disabled={isLoading}
								variant="outline"
								className="w-full border-dashed bg-purple-50 hover:bg-purple-100 text-purple-800 border-purple-200"
							>
								👦 子どもアカウントでログイン
							</Button>
						</div>
					</div>

					{/* サインアップリンク */}
					<div className="mt-6 text-center">
						<p className="text-sm text-gray-600">
							アカウントをお持ちでない方は{" "}
							<Link
								href="/signup"
								className="text-blue-600 hover:text-blue-500 font-medium"
							>
								新規登録
							</Link>
						</p>
					</div>
				</div>
			</div>
		</div>
	);
}

export default function LoginPage() {
	return (
		<Suspense fallback={<LoginPageSkeleton />}>
			<LoginForm />
		</Suspense>
	);
}

function LoginPageSkeleton() {
	return (
		<div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4">
			<div className="w-full max-w-md">
				<div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-6 md:p-8">
					<div className="text-center mb-6 md:mb-8">
						<h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
							Kodomo Wallet
						</h1>
						<p className="text-sm md:text-base text-gray-600 dark:text-gray-400">
							読み込み中...
						</p>
					</div>
				</div>
			</div>
		</div>
	);
}
