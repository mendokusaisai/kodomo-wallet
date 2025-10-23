"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { createClient } from "@/lib/supabase/client";

export default function LoginPage() {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const router = useRouter();
	const supabase = createClient();

	const handleLogin = async (e: React.FormEvent) => {
		e.preventDefault();
		setLoading(true);
		setError(null);

		const { error } = await supabase.auth.signInWithPassword({
			email,
			password,
		});

		if (error) {
			setError(error.message);
		} else {
			router.push("/dashboard");
			router.refresh();
		}
		setLoading(false);
	};

	// テストユーザーで自動ログイン
	const handleQuickLogin = async (testEmail: string) => {
		setEmail(testEmail);
		setPassword("password123");
		setLoading(true);
		setError(null);

		const { error } = await supabase.auth.signInWithPassword({
			email: testEmail,
			password: "password123",
		});

		if (error) {
			setError(error.message);
		} else {
			router.push("/dashboard");
			router.refresh();
		}
		setLoading(false);
	};

	return (
		<div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
			<div className="w-full max-w-md">
				<div className="bg-white rounded-2xl shadow-xl p-8">
					{/* ヘッダー */}
					<div className="text-center mb-8">
						<h1 className="text-3xl font-bold text-gray-900 mb-2">
							Kodomo Wallet
						</h1>
						<p className="text-gray-600">親子で楽しく学べるおこづかい管理</p>
					</div>

					{/* エラーメッセージ */}
					{error && (
						<div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
							<p className="text-sm text-red-600">{error}</p>
						</div>
					)}

					{/* ログインフォーム */}
					<form onSubmit={handleLogin} className="space-y-4">
						<div>
							<label
								htmlFor="email"
								className="block text-sm font-medium text-gray-700 mb-1"
							>
								メールアドレス
							</label>
							<input
								id="email"
								type="email"
								value={email}
								onChange={(e) => setEmail(e.target.value)}
								className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								placeholder="your@email.com"
								required
							/>
						</div>

						<div>
							<label
								htmlFor="password"
								className="block text-sm font-medium text-gray-700 mb-1"
							>
								パスワード
							</label>
							<input
								id="password"
								type="password"
								value={password}
								onChange={(e) => setPassword(e.target.value)}
								className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								placeholder="••••••••"
								required
							/>
						</div>

						<button
							type="submit"
							disabled={loading}
							className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
						>
							{loading ? "処理中..." : "ログイン"}
						</button>
					</form>

					{/* テストユーザークイックログイン */}
					<div className="mt-8 pt-6 border-t border-gray-200">
						<p className="text-xs text-gray-500 text-center mb-3">
							テストアカウントでログイン
						</p>
						<div className="space-y-2">
							<button
								type="button"
								onClick={() => handleQuickLogin("parent@test.com")}
								disabled={loading}
								className="w-full bg-green-100 hover:bg-green-200 text-green-800 font-medium py-2 px-4 rounded-lg transition-colors text-sm disabled:opacity-50"
							>
								👨‍👩‍👧 親アカウント
							</button>
							<button
								type="button"
								onClick={() => handleQuickLogin("child1@test.com")}
								disabled={loading}
								className="w-full bg-purple-100 hover:bg-purple-200 text-purple-800 font-medium py-2 px-4 rounded-lg transition-colors text-sm disabled:opacity-50"
							>
								👦 子供アカウント1
							</button>
							<button
								type="button"
								onClick={() => handleQuickLogin("child2@test.com")}
								disabled={loading}
								className="w-full bg-pink-100 hover:bg-pink-200 text-pink-800 font-medium py-2 px-4 rounded-lg transition-colors text-sm disabled:opacity-50"
							>
								👧 子供アカウント2
							</button>
						</div>
					</div>
				</div>

				{/* フッター */}
				<p className="text-center text-sm text-gray-600 mt-4">
					開発中のため、テストアカウントのみ利用可能です
				</p>
			</div>
		</div>
	);
}
