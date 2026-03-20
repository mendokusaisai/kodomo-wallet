import { NextResponse } from "next/server";

// Firebase は OAuth を popup で処理するため、このルートは使用しない
// 念のため /dashboard へリダイレクト
export async function GET(request: Request) {
	const { origin } = new URL(request.url);
	return NextResponse.redirect(`${origin}/dashboard`);
}
