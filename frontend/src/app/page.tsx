import Link from "next/link";

export default function Home() {
	return (
		<div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
			<main className="text-center space-y-8 p-8">
				<div className="space-y-4">
					<h1 className="text-6xl font-bold text-blue-600">🏦 Kodomo Wallet</h1>
					<p className="text-2xl text-gray-600">
						親子で楽しく学べるおこづかい管理アプリ
					</p>
				</div>

				<div className="bg-white rounded-2xl shadow-xl p-8 max-w-2xl mx-auto">
					<h2 className="text-2xl font-semibold mb-6 text-gray-800">
						Phase 3: フロントエンド実装中 🚀
					</h2>
					<ul className="text-left space-y-3 text-gray-700 mb-8">
						<li>✅ Apollo Client セットアップ完了</li>
						<li>✅ GraphQL クエリ・ミューテーション定義</li>
						<li>✅ ダッシュボード画面作成</li>
						<li>✅ ログインページ作成</li>
						<li>⏳ 入金機能実装中</li>
						<li>⏳ トランザクション履歴表示</li>
					</ul>

					<Link
						href="/login"
						className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition-colors"
					>
						ログインページへ →
					</Link>
				</div>

				<div className="space-y-2">
					<p className="text-gray-600">
						<strong>バックエンド:</strong> http://localhost:8000 ✓
					</p>
					<p className="text-gray-600">
						<strong>フロントエンド:</strong> http://localhost:3000 ✓
					</p>
				</div>
			</main>
		</div>
	);
}
