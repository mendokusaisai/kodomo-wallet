"use client";
/* eslint-disable react-hooks/exhaustive-deps */

import { useMutation } from "@apollo/client/react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { ACCEPT_PARENT_INVITE } from "@/lib/graphql/queries";
import { getUser } from "@/lib/supabase/auth";

type AcceptParentInviteResponse = { acceptParentInvite: boolean };

function AcceptInviteInner() {
	const router = useRouter();
	const searchParams = useSearchParams();
	const [status, setStatus] = useState<
		"idle" | "processing" | "success" | "error"
	>("idle");
	const [message, setMessage] = useState<string>("");
	const [acceptInvite] =
		useMutation<AcceptParentInviteResponse>(ACCEPT_PARENT_INVITE);

	// eslint-disable-next-line react-hooks/exhaustive-deps
	useEffect(() => {
		const run = async () => {
			const token = searchParams.get("token");
			if (!token) {
				setStatus("error");
				setMessage("無効な招待リンクです（token がありません）");
				return;
			}
			const user = await getUser();
			if (!user) {
				// ログインしていない場合はログインへ
				const current =
					typeof window !== "undefined"
						? window.location.pathname + window.location.search
						: "/accept-invite";
				router.push(`/login?redirect=${encodeURIComponent(current)}`);
				return;
			}

			try {
				setStatus("processing");
				const res = await acceptInvite({
					variables: { token, currentParentId: user.id },
				});
				const ok = res.data?.acceptParentInvite === true;
				if (ok) {
					setStatus("success");
					setMessage("招待を受け入れました。家族関係が追加されました。");
					// ダッシュボードへ遷移
					setTimeout(() => router.push("/dashboard"), 1200);
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
		run();
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	return (
		<div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
			<div className="bg-white rounded-lg shadow p-6 max-w-md w-full text-center">
				<h1 className="text-xl font-bold mb-3">親招待の受け入れ</h1>
				{status === "idle" || status === "processing" ? (
					<p className="text-gray-600">処理中です…</p>
				) : status === "success" ? (
					<p className="text-green-700">{message}</p>
				) : (
					<>
						<p className="text-red-600">{message}</p>
						<Button className="mt-4" onClick={() => router.push("/dashboard")}>
							ダッシュボードへ
						</Button>
					</>
				)}
			</div>
		</div>
	);
}

export default function AcceptInvitePage() {
	return (
		<Suspense
			fallback={
				<div className="min-h-screen flex items-center justify-center">
					読み込み中…
				</div>
			}
		>
			<AcceptInviteInner />
		</Suspense>
	);
}
