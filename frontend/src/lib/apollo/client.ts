import {
	ApolloClient,
	from,
	HttpLink,
	InMemoryCache,
} from "@apollo/client/core";
import { setContext } from "@apollo/client/link/context";
import { RetryLink } from "@apollo/client/link/retry";
import { createClient } from "@/lib/supabase/client";

const httpLink = new HttpLink({
	uri: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/graphql",
});

// リトライ設定（Renderの起動待ち対応）
const retryLink = new RetryLink({
	delay: {
		initial: 1000, // 初回リトライまで1秒
		max: 5000, // 最大5秒待つ
		jitter: true, // ランダムな遅延を追加
	},
	attempts: {
		max: 5, // 最大5回リトライ
		retryIf: (error) => {
			// 503エラー（サーバー起動中）の場合のみリトライ
			return (
				error?.message?.includes("503") ||
				error?.message?.includes("Service Unavailable") ||
				error?.message?.includes("Failed to fetch")
			);
		},
	},
});

// Supabase のセッショントークンを GraphQL リクエストのヘッダーに追加
const authLink = setContext(async (_, { headers }) => {
	const supabase = createClient();
	const {
		data: { session },
	} = await supabase.auth.getSession();

	return {
		headers: {
			...headers,
			authorization: session?.access_token
				? `Bearer ${session.access_token}`
				: "",
		},
	};
});

// Apollo Client の作成
export const apolloClient = new ApolloClient({
	link: from([retryLink, authLink, httpLink]),
	cache: new InMemoryCache(),
	defaultOptions: {
		watchQuery: {
			fetchPolicy: "cache-and-network",
		},
	},
});
