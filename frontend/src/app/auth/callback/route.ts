import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET(request: Request) {
	const { searchParams, origin } = new URL(request.url);
	const code = searchParams.get("code");
	const inviteToken = searchParams.get("invite_token");
	const next = searchParams.get("next") ?? "/dashboard";

	if (code) {
		const supabase = await createClient();
		const { error } = await supabase.auth.exchangeCodeForSession(code);

		if (!error) {
			// 招待トークンがある場合、child-invite-callback にリダイレクト
			if (inviteToken) {
				const forwardedHost = request.headers.get("x-forwarded-host");
				const isLocalEnv = process.env.NODE_ENV === "development";

				const callbackUrl = `/child-invite-callback?token=${inviteToken}`;

				if (isLocalEnv) {
					return NextResponse.redirect(`${origin}${callbackUrl}`);
				}
				if (forwardedHost) {
					return NextResponse.redirect(
						`https://${forwardedHost}${callbackUrl}`,
					);
				}
				return NextResponse.redirect(`${origin}${callbackUrl}`);
			}

			// 通常のログインの場合
			const forwardedHost = request.headers.get("x-forwarded-host");
			const isLocalEnv = process.env.NODE_ENV === "development";

			if (isLocalEnv) {
				return NextResponse.redirect(`${origin}${next}`);
			}
			if (forwardedHost) {
				return NextResponse.redirect(`https://${forwardedHost}${next}`);
			}
			return NextResponse.redirect(`${origin}${next}`);
		}
	}

	// エラーの場合はログインページにリダイレクト
	return NextResponse.redirect(`${origin}/login?error=auth_failed`);
}
