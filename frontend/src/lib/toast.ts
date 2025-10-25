import { toast } from "sonner";

/**
 * エラーメッセージを表示
 */
export function showError(message: string, description?: string) {
	toast.error(message, {
		description,
		duration: 5000,
	});
}

/**
 * 成功メッセージを表示
 */
export function showSuccess(message: string, description?: string) {
	toast.success(message, {
		description,
		duration: 3000,
	});
}

/**
 * 情報メッセージを表示
 */
export function showInfo(message: string, description?: string) {
	toast.info(message, {
		description,
		duration: 3000,
	});
}

/**
 * 警告メッセージを表示
 */
export function showWarning(message: string, description?: string) {
	toast.warning(message, {
		description,
		duration: 4000,
	});
}

/**
 * GraphQLエラーをユーザーフレンドリーなメッセージに変換
 */
export function handleGraphQLError(error: unknown): void {
	console.error("GraphQL Error:", error);

	if (error instanceof Error) {
		if (error.message.includes("unauthorized")) {
			showError("認証エラー", "ログインし直してください");
		} else if (error.message.includes("not found")) {
			showError("データが見つかりません", "ページを再読み込みしてください");
		} else if (error.message.includes("network")) {
			showError("ネットワークエラー", "インターネット接続を確認してください");
		} else {
			showError("エラーが発生しました", error.message);
		}
	} else {
		showError("予期しないエラーが発生しました");
	}
}
