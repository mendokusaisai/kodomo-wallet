"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useId, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { signInWithGoogle, signUp } from "@/lib/supabase/auth";

export default function SignUpPage() {
	const router = useRouter();
	const [name, setName] = useState("");
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [confirmPassword, setConfirmPassword] = useState("");
	const [isLoading, setIsLoading] = useState(false);
	const [isSocialLoading, setIsSocialLoading] = useState(false);
	const nameId = useId();
	const emailId = useId();
	const passwordId = useId();
	const confirmPasswordId = useId();

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();

		// パスワード確認チェック
		if (password !== confirmPassword) {
			toast.error("パスワードが一致しません");
			return;
		}

		// パスワードの長さチェック
		if (password.length < 6) {
			toast.error("パスワードは6文字以上にしてください");
			return;
		}

		setIsLoading(true);

		try {
			await signUp(email, password, name);
			toast.success("アカウントを作成しました", {
				description: "確認メールをご確認ください",
			});
			router.push("/login");
		} catch (error) {
			console.error("サインアップエラー:", error);
			const errorMessage =
				error instanceof Error ? error.message : "もう一度お試しください";
			toast.error("アカウント作成に失敗しました", {
				description: errorMessage,
			});
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
							新規登録
						</h1>
						<p className="text-sm md:text-base text-gray-600 dark:text-gray-400">
							Kodomo Walletへようこそ
						</p>
					</div>

					{/* サインアップフォーム */}
					<form onSubmit={handleSubmit} className="space-y-4">
						{/* ソーシャルログイン */}
						<div className="space-y-3">
							<Button
								type="button"
								onClick={async () => {
									setIsSocialLoading(true);
									try {
										await signInWithGoogle();
									} catch (error) {
										console.error("Google login error:", error);
										toast.error("Googleログインに失敗しました");
										setIsSocialLoading(false);
									}
								}}
								disabled={isLoading || isSocialLoading}
								variant="outline"
								className="w-full"
							>
								<svg
									className="w-5 h-5 mr-2"
									viewBox="0 0 24 24"
									aria-label="Google"
								>
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
								Googleで登録
							</Button>
						</div>

						{/* 区切り線 */}
						<div className="relative">
							<div className="absolute inset-0 flex items-center">
								<div className="w-full border-t border-gray-300 dark:border-gray-600" />
							</div>
							<div className="relative flex justify-center text-sm">
								<span className="px-2 bg-white dark:bg-gray-900 text-gray-500 dark:text-gray-400">
									または
								</span>
							</div>
						</div>

						<div>
							<Label htmlFor={nameId}>お名前</Label>
							<Input
								id={nameId}
								type="text"
								value={name}
								onChange={(e) => setName(e.target.value)}
								placeholder="山田太郎"
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
								minLength={6}
								className="mt-1"
							/>
							<p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
								6文字以上で入力してください
							</p>
						</div>

						<div>
							<Label htmlFor={confirmPasswordId}>パスワード(確認)</Label>
							<Input
								id={confirmPasswordId}
								type="password"
								value={confirmPassword}
								onChange={(e) => setConfirmPassword(e.target.value)}
								placeholder="••••••••"
								required
								minLength={6}
								className="mt-1"
							/>
						</div>

						<Button type="submit" disabled={isLoading} className="w-full">
							{isLoading ? "作成中..." : "アカウントを作成"}
						</Button>
					</form>

					{/* ログインリンク */}
					<div className="mt-6 text-center text-sm">
						<span className="text-gray-600 dark:text-gray-400">
							既にアカウントをお持ちの方は{" "}
						</span>
						<Link
							href="/login"
							className="text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300"
						>
							ログイン
						</Link>
					</div>
				</div>

				{/* フッター */}
				<p className="text-center text-xs md:text-sm text-gray-600 dark:text-gray-400 mt-4">
					登録すると、利用規約とプライバシーポリシーに同意したものとみなされます
				</p>
			</div>
		</div>
	);
}
