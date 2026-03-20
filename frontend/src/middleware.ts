import { type NextRequest, NextResponse } from "next/server";

export async function middleware(request: NextRequest) {
	// Firebase Auth は Edge runtime で直接検証できないため、
	// サインイン時にセットされた __session クッキーの存在で認証状態を確認する。
	// 実際の認証検証はバックエンド(Firebase Admin SDK)が行う。
	const session = request.cookies.get("__session");
	const isLoggedIn = !!session;

	const isAuthPage =
		request.nextUrl.pathname.startsWith("/login") ||
		request.nextUrl.pathname.startsWith("/signup");
	const isProtectedPage =
		request.nextUrl.pathname.startsWith("/dashboard") ||
		request.nextUrl.pathname.startsWith("/settings");

	// 未ログイン状態で保護されたページにアクセスしようとした場合
	if (!isLoggedIn && isProtectedPage) {
		const redirectUrl = new URL("/login", request.url);
		redirectUrl.searchParams.set("redirect", request.nextUrl.pathname);
		return NextResponse.redirect(redirectUrl);
	}

	// ログイン済み状態でログイン/サインアップページにアクセスした場合
	if (isLoggedIn && isAuthPage) {
		const redirect = request.nextUrl.searchParams.get("redirect");
		const redirectUrl = new URL(redirect || "/dashboard", request.url);
		return NextResponse.redirect(redirectUrl);
	}

	return NextResponse.next();
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

