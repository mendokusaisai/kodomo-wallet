import {
	ApolloClient,
	ApolloLink,
	HttpLink,
	InMemoryCache,
} from "@apollo/client/core";
import { setContext } from "@apollo/client/link/context";
import { createClient } from "@/lib/supabase/client";

const httpLink = new HttpLink({
	uri: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/graphql",
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
	link: ApolloLink.from([authLink, httpLink]),
	cache: new InMemoryCache(),
	defaultOptions: {
		watchQuery: {
			fetchPolicy: "cache-and-network",
		},
	},
});
