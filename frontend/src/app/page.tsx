export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-blue-50 to-blue-100 dark:from-gray-900 dark:to-gray-800">
      <main className="text-center space-y-8 p-8">
        <div className="space-y-4">
          <h1 className="text-6xl font-bold text-blue-600 dark:text-blue-400">
            🏦 Kodomo Wallet
          </h1>
          <p className="text-2xl text-gray-600 dark:text-gray-300">
            親子で使えるお小遣い管理アプリ
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 max-w-md mx-auto">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">
            Phase 1: プロジェクト基盤構築 完了！ ✅
          </h2>
          <ul className="text-left space-y-2 text-gray-700 dark:text-gray-300">
            <li>✅ Next.js セットアップ完了</li>
            <li>✅ FastAPI セットアップ完了</li>
            <li>✅ 必要なパッケージインストール完了</li>
            <li>✅ 環境変数ファイル作成完了</li>
          </ul>
        </div>

        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-400">
            次のステップ: Phase 2 で Supabase を設定します
          </p>
        </div>
      </main>
    </div>
  );
}
