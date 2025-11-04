import { ArrowRight, PiggyBank, Shield, Sparkles } from "lucide-react";
import Link from "next/link";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";

export default function Home() {
	return (
		<div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4 md:p-8">
			{/* テーマ切り替えボタン */}
			<div className="absolute top-4 right-4">
				<ThemeToggle />
			</div>

			<main className="text-center space-y-8 md:space-y-12 max-w-5xl mx-auto">
				{/* ヒーローセクション */}
				<div className="space-y-4 md:space-y-6">
					<div className="flex items-center justify-center gap-3">
						<div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl p-2 md:p-3 shadow-lg">
							<svg
								className="w-8 h-8 md:w-12 md:h-12 text-white"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									strokeLinecap="round"
									strokeLinejoin="round"
									strokeWidth={2}
									d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
								/>
							</svg>
						</div>
						<h1 className="text-4xl md:text-6xl lg:text-7xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
							Kodomo Wallet
						</h1>
					</div>
					<p className="text-lg md:text-2xl text-gray-700 dark:text-gray-300">
						おこづかい管理アプリ
					</p>
				</div>

				{/* サービス特徴カード */}
				<div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
					<div className="bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow">
						<PiggyBank className="w-12 h-12 text-blue-600 dark:text-blue-400 mx-auto mb-4" />
						<h3 className="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-2">
							残高・履歴を家族で管理
						</h3>
						<p className="text-gray-600 dark:text-gray-400 text-sm">
							お子様のお小遣いをデジタルで管理。入金・出金・履歴を家族で共有できます。
						</p>
					</div>

					<div className="bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow">
						<Sparkles className="w-12 h-12 text-purple-600 dark:text-purple-400 mx-auto mb-4" />
						<h3 className="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-2">
							目標設定 & 達成率表示
						</h3>
						<p className="text-gray-600 dark:text-gray-400 text-sm">
							欲しいものに向けて貯金目標を設定。達成率をグラフで可視化して楽しく貯められます。
						</p>
					</div>

					<div className="bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow">
						<Shield className="w-12 h-12 text-green-600 dark:text-green-400 mx-auto mb-4" />
						<h3 className="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-2">
							安心・安全なシステム
						</h3>
						<p className="text-gray-600 dark:text-gray-400 text-sm">
							Supabase認証とRow Level
							Securityで、家族のデータをしっかり保護します。
						</p>
					</div>
				</div>

				{/* 本番向け CTA & サポート */}
				<div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-6 md:p-8">
					<h2 className="text-xl md:text-2xl font-semibold mb-6 text-gray-800 dark:text-gray-100">
						🎉 Kodomo Wallet で家族のお金をもっとスマートに！
					</h2>
					<div className="flex flex-col sm:flex-row gap-4 justify-center">
						<Button asChild size="lg" className="text-base md:text-lg">
							<Link href="/login" className="flex items-center gap-2">
								ログイン
								<ArrowRight className="w-5 h-5" />
							</Link>
						</Button>
						<Button
							asChild
							variant="outline"
							size="lg"
							className="text-base md:text-lg"
						>
							<Link href="/signup">新規登録</Link>
						</Button>
					</div>
				</div>

				{/* フッター情報 */}
				<div className="space-y-2 text-sm md:text-base mt-8">
					<div className="flex flex-col sm:flex-row gap-4 justify-center items-center text-gray-600 dark:text-gray-400">
						<p className="flex items-center gap-2">
							<span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
							<strong>Backend:</strong> FastAPI + GraphQL
						</p>
						<p className="flex items-center gap-2">
							<span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
							<strong>Frontend:</strong> Next.js 15 + TypeScript
						</p>
						<p className="flex items-center gap-2">
							<span className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
							<strong>認証:</strong> Supabase Auth
						</p>
					</div>
					<div className="text-center text-xs text-gray-400 mt-2">
						&copy; 2025 Kodomo Wallet. All rights reserved.
					</div>
				</div>
			</main>
		</div>
	);
}
