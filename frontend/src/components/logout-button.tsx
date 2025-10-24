"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { signOut } from "@/lib/supabase/auth";

export function LogoutButton() {
	const router = useRouter();
	const [loading, setLoading] = useState(false);

	const handleLogout = async () => {
		setLoading(true);
		try {
			await signOut();
			toast.success("ログアウトしました");
			router.push("/login");
		} catch {
			toast.error("ログアウト中にエラーが発生しました");
			setLoading(false);
		}
	};

	return (
		<Button
			onClick={handleLogout}
			disabled={loading}
			variant="outline"
			className="border-red-500 text-red-500 hover:bg-red-50"
		>
			{loading ? "ログアウト中..." : "ログアウト"}
		</Button>
	);
}
