import {
	ApolloClient,
	from,
	HttpLink,
	InMemoryCache,
} from "@apollo/client/core";
import { setContext } from "@apollo/client/link/context";
import { RetryLink } from "@apollo/client/link/retry";
import { auth } from "@/lib/firebase/client";

const httpLink = new HttpLink({
	uri: process.env.NEXT_PUBLIC_GRAPHQL_ENDPOINT || "http://localhost:8000/graphql",
});

// リトライ設定（Cloud Run の起動待ち対応）
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

// Firebase ID トークンを GraphQL リクエストのヘッダーに追加
const authLink = setContext(async (_, { headers }) => {
	let token: string | null = null;
	try {
		const user = auth.currentUser;
		if (user) {
			token = await user.getIdToken();
		}
	} catch (e) {
		console.error("Firebase ID トークンの取得に失敗しました:", e);
	}

	return {
		headers: {
			...headers,
			authorization: token ? `Bearer ${token}` : "",
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

