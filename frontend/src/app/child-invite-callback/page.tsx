"use client";

import { useMutation } from "@apollo/client/react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { ACCEPT_CHILD_INVITE } from "@/lib/graphql/queries";
import { getUser } from "@/lib/supabase/auth";

type AcceptChildInviteResponse = { acceptChildInvite: boolean };

function ChildInviteCallbackInner() {
	const router = useRouter();
	const searchParams = useSearchParams();
	const [status, setStatus] = useState<"processing" | "success" | "error">(
		"processing",
	);
	const [message, setMessage] = useState<string>("招待を受け入れています...");

	const [acceptInvite] =
		useMutation<AcceptChildInviteResponse>(ACCEPT_CHILD_INVITE);

	useEffect(() => {
		const processInvite = async () => {
			try {
				const token = searchParams.get("token");
				if (!token) {
					setStatus("error");
					setMessage("無効な招待トークンです");
					return;
				}

				// 現在のログインユーザーを取得
				const user = await getUser();
				if (!user) {
					setStatus("error");
					setMessage("ログインユーザーが見つかりません");
					return;
				}

				// 招待を受け入れる
				const res = await acceptInvite({
					variables: { token, authUserId: user.id },
				});

				const ok = res.data?.acceptChildInvite === true;
				if (ok) {
					setStatus("success");
					setMessage(
						"アカウントが正常に作成されました！ダッシュボードに移動します...",
					);
					setTimeout(() => router.push("/dashboard"), 1500);
				} else {
					setStatus("error");
					setMessage("招待の受け入れに失敗しました。");
				}
			} catch (e) {
				setStatus("error");
				setMessage(
					e instanceof Error ? e.message : "不明なエラーが発生しました",
				);
			}
		};

		processInvite();
	}, [searchParams, acceptInvite, router]);

	return (
		<div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 p-6">
			<div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 max-w-md w-full text-center">
				{status === "processing" && (
					<>
						<div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
						<h1 className="text-xl font-bold mb-3">処理中...</h1>
						<p className="text-gray-600 dark:text-gray-400">{message}</p>
					</>
				)}

				{status === "success" && (
					<>
						<div className="text-green-600 text-5xl mb-4">✓</div>
						<h1 className="text-xl font-bold mb-3 text-green-600">完了！</h1>
						<p className="text-gray-600 dark:text-gray-400">{message}</p>
					</>
				)}

				{status === "error" && (
					<>
						<div className="text-red-600 text-5xl mb-4">✕</div>
						<h1 className="text-xl font-bold mb-3 text-red-600">エラー</h1>
						<p className="text-red-600 dark:text-red-400 mb-4">{message}</p>
						<Button onClick={() => router.push("/login")}>
							ログインページへ
						</Button>
					</>
				)}
			</div>
		</div>
	);
}

export default function ChildInviteCallbackPage() {
	return (
		<Suspense
			fallback={
				<div className="min-h-screen flex items-center justify-center">
					<div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
				</div>
			}
		>
			<ChildInviteCallbackInner />
		</Suspense>
	);
}
