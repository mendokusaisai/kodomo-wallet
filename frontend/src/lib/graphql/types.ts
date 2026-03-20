// GraphQL の型定義（家族中心モデル）

export interface FamilyMember {
	uid: string;
	familyId: string;
	name: string;
	role: "parent" | "child";
	email: string | null;
	joinedAt: string;
}

export interface Family {
	id: string;
	name: string | null;
	createdAt: string;
	members: FamilyMember[];
}

export interface Account {
	id: string;
	familyId: string;
	name: string;
	balance: number;
	currency: string;
	goalName?: string | null;
	goalAmount?: number | null;
	createdAt: string;
	updatedAt: string;
}

export interface Transaction {
	id: string;
	accountId: string;
	familyId: string;
	type: "deposit" | "withdraw" | "reward";
	amount: number;
	note?: string | null;
	createdAt: string;
	createdByUid: string;
}

// Query のレスポンス型
export interface MyFamilyResponse {
	myFamily: Family | null;
}

export interface FamilyAccountsResponse {
	familyAccounts: Account[];
}

export interface AccountTransactionsResponse {
	accountTransactions: Transaction[];
}

// Mutation のレスポンス型
export interface CreateFamilyResponse {
	createFamily: Family;
}

export interface CreateAccountResponse {
	createAccount: Account;
}

export interface DepositResponse {
	deposit: Transaction;
}

export interface WithdrawResponse {
	withdraw: Transaction;
}

export interface UpdateGoalResponse {
	updateGoal: Account;
}

export interface InviteChildResponse {
	inviteChild: string; // token
}

export interface InviteParentResponse {
	inviteParent: string; // token
}

export interface JoinAsChildResponse {
	joinAsChild: FamilyMember;
}

export interface JoinAsParentResponse {
	joinAsParent: FamilyMember;
}
