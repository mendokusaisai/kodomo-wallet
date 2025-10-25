import { Skeleton } from "@/components/ui/skeleton";

export function DashboardSkeleton() {
	return (
		<div className="min-h-screen bg-gray-50 p-4 md:p-6 lg:p-8">
			<div className="max-w-7xl mx-auto">
				{/* ヘッダースケルトン */}
				<div className="mb-6 md:mb-8 flex flex-col sm:flex-row justify-between items-start gap-4">
					<div className="flex items-center gap-3 md:gap-4">
						<Skeleton className="w-12 h-12 md:w-16 md:h-16 rounded-full" />
						<div className="space-y-2">
							<Skeleton className="h-6 md:h-8 w-48 md:w-64" />
							<Skeleton className="h-4 md:h-5 w-32 md:w-40" />
						</div>
					</div>
					<div className="flex gap-2 md:gap-3">
						<Skeleton className="h-9 md:h-10 w-24 md:w-32" />
						<Skeleton className="h-9 md:h-10 w-16 md:w-20" />
						<Skeleton className="h-9 md:h-10 w-20 md:w-24" />
					</div>
				</div>

				{/* アカウントカードスケルトン */}
				<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
					{[1, 2, 3].map((i) => (
						<div
							key={i}
							className="bg-white rounded-lg shadow-md p-4 md:p-6 space-y-4"
						>
							{/* ユーザー情報 */}
							<div className="flex items-center gap-3 pb-3 border-b">
								<Skeleton className="w-10 h-10 md:w-12 md:h-12 rounded-full" />
								<Skeleton className="h-5 w-24" />
							</div>

							{/* 残高 */}
							<div className="space-y-2">
								<Skeleton className="h-4 w-12" />
								<Skeleton className="h-8 md:h-10 w-32" />
							</div>

							{/* 目標 */}
							<div className="space-y-2">
								<Skeleton className="h-4 w-20" />
								<Skeleton className="h-2 w-full" />
								<Skeleton className="h-4 w-28" />
							</div>

							{/* ボタン */}
							<div className="flex gap-2 pt-2">
								<Skeleton className="h-9 flex-1" />
								<Skeleton className="h-9 flex-1" />
							</div>
						</div>
					))}
				</div>
			</div>
		</div>
	);
}
