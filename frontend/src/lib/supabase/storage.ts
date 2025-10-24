import { createClient } from "./client";

const AVATAR_BUCKET = "avatars";

/**
 * アバター画像をSupabase Storageにアップロードする
 * @param file アップロードする画像ファイル
 * @param userId ユーザーID（ファイル名の一部として使用）
 * @returns アップロードされた画像の公開URL
 */
export async function uploadAvatar(
	file: File,
	userId: string,
): Promise<string> {
	const supabase = createClient();

	// ファイル拡張子を取得
	const fileExt = file.name.split(".").pop();
	// ユニークなファイル名を生成（ユーザーIDとタイムスタンプ）
	const fileName = `${userId}-${Date.now()}.${fileExt}`;
	const filePath = `${userId}/${fileName}`;

	// ファイルをアップロード
	const { error: uploadError } = await supabase.storage
		.from(AVATAR_BUCKET)
		.upload(filePath, file, {
			cacheControl: "3600",
			upsert: false,
		});

	if (uploadError) {
		throw new Error(`アップロードエラー: ${uploadError.message}`);
	}

	// 公開URLを取得
	const {
		data: { publicUrl },
	} = supabase.storage.from(AVATAR_BUCKET).getPublicUrl(filePath);

	return publicUrl;
}

/**
 * 古いアバター画像を削除する（オプション）
 * @param avatarUrl 削除する画像のURL
 */
export async function deleteAvatar(avatarUrl: string): Promise<void> {
	if (!avatarUrl) return;

	const supabase = createClient();

	try {
		// URLからファイルパスを抽出
		const url = new URL(avatarUrl);
		const pathParts = url.pathname.split("/");
		const bucketIndex = pathParts.indexOf(AVATAR_BUCKET);
		if (bucketIndex === -1) return;

		const filePath = pathParts.slice(bucketIndex + 1).join("/");

		// ファイルを削除
		const { error } = await supabase.storage
			.from(AVATAR_BUCKET)
			.remove([filePath]);

		if (error) {
			console.error("画像削除エラー:", error);
		}
	} catch (error) {
		console.error("画像削除処理エラー:", error);
	}
}
