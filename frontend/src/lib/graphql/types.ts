// GraphQL の型定義

export interface Profile {
	id: string;
	name: string;
	role: "parent" | "child";
	avatarUrl?: string;
	createdAt: string;
}

export interface Account {
	id: string;
	userId: string;
	balance: number;
	currency: string;
	goalName?: string;
	goalAmount?: number;
	createdAt: string;
	updatedAt: string;
	user?: Profile; // アカウント所有者の情報
}

export interface Transaction {
	id: string;
	accountId: string;
	type: "deposit" | "withdraw" | "reward";
	amount: number;
	description?: string;
	createdAt: string;
}

export interface WithdrawalRequest {
	id: string;
	accountId: string;
	amount: number;
	description?: string;
	status: "pending" | "approved" | "rejected";
	createdAt: string;
	updatedAt: string;
}

// Query のレスポンス型
export interface GetMeResponse {
	me: Profile | null;
}

export interface GetAccountsResponse {
	accounts: Account[];
}

export interface GetTransactionsResponse {
	transactions: Transaction[];
}

export interface GetWithdrawalRequestsResponse {
	withdrawalRequests: WithdrawalRequest[];
}

// Mutation のレスポンス型
export interface DepositResponse {
	deposit: Transaction;
}

export interface CreateWithdrawalRequestResponse {
	createWithdrawalRequest: WithdrawalRequest;
}

export interface ApproveWithdrawalResponse {
	approveWithdrawal: WithdrawalRequest;
}

export interface RejectWithdrawalResponse {
	rejectWithdrawal: WithdrawalRequest;
}

export interface UpdateGoalResponse {
	updateGoal: Account;
}
