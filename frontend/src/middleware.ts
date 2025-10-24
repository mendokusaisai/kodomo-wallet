import { createServerClient } from "@supabase/ssr";
import { type NextRequest, NextResponse } from "next/server";

export async function middleware(request: NextRequest) {
	const response = NextResponse.next({
		request: {
			headers: request.headers,
		},
	});

	const supabase = createServerClient(
		process.env.NEXT_PUBLIC_SUPABASE_URL || "",
		process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "",
		{
			cookies: {
				getAll() {
					return request.cookies.getAll();
				},
				setAll(cookiesToSet) {
					cookiesToSet.forEach(({ name, value }) => {
						request.cookies.set(name, value);
					});
					cookiesToSet.forEach(({ name, value, options }) => {
						response.cookies.set(name, value, options);
					});
				},
			},
		},
	);

	// セッション確認
	const {
		data: { session },
	} = await supabase.auth.getSession();

	const isAuthPage =
		request.nextUrl.pathname.startsWith("/login") ||
		request.nextUrl.pathname.startsWith("/signup");
	const isProtectedPage = request.nextUrl.pathname.startsWith("/dashboard");

	// 未ログイン状態で保護されたページにアクセスしようとした場合
	if (!session && isProtectedPage) {
		const redirectUrl = new URL("/login", request.url);
		redirectUrl.searchParams.set("redirect", request.nextUrl.pathname);
		return NextResponse.redirect(redirectUrl);
	}

	// ログイン済み状態でログイン/サインアップページにアクセスした場合
	if (session && isAuthPage) {
		const redirect = request.nextUrl.searchParams.get("redirect");
		const redirectUrl = new URL(redirect || "/dashboard", request.url);
		return NextResponse.redirect(redirectUrl);
	}

	return response;
}

export const config = {
	matcher: [
		/*
		 * 以下のパスを除くすべてのリクエストパスにマッチ:
		 * - _next/static (静的ファイル)
		 * - _next/image (画像最適化ファイル)
		 * - favicon.ico (ファビコン)
		 * - public フォルダ内のファイル
		 */
		"/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
	],
};
