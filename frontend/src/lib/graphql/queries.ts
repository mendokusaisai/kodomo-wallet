import { gql } from "@apollo/client";

// ==================== Query ====================

export const GET_ME = gql`
  query GetMe($userId: String!) {
    me(userId: $userId) {
      id
      name
      role
      avatarUrl
      createdAt
    }
  }
`;

export const GET_ACCOUNTS = gql`
	query GetAccounts($userId: String!) {
		accounts(userId: $userId) {
			id
			userId
			balance
			currency
			goalName
			goalAmount
			createdAt
			updatedAt
			user {
				id
				name
				role
				authUserId
			}
		}
	}
`;
export const GET_TRANSACTIONS = gql`
  query GetTransactions($accountId: String!) {
    transactions(accountId: $accountId) {
      id
      accountId
      type
      amount
      description
      createdAt
    }
  }
`;

export const GET_WITHDRAWAL_REQUESTS = gql`
  query GetWithdrawalRequests($parentId: String!) {
    withdrawalRequests(parentId: $parentId) {
      id
      accountId
      amount
      description
      status
      createdAt
      updatedAt
    }
  }
`;

// ==================== Mutation ====================

// ==================== Mutation ====================

export const DEPOSIT = gql`
	mutation Deposit($accountId: String!, $amount: Int!, $description: String!) {
		deposit(accountId: $accountId, amount: $amount, description: $description) {
			id
			accountId
			type
			amount
			description
			createdAt
		}
	}
`;

export const WITHDRAW = gql`
	mutation Withdraw($accountId: String!, $amount: Int!, $description: String!) {
		withdraw(accountId: $accountId, amount: $amount, description: $description) {
			id
			accountId
			type
			amount
			description
			createdAt
		}
	}
`;

export const CREATE_CHILD = gql`
	mutation CreateChild(
		$parentId: String!
		$childName: String!
		$initialBalance: Int
	) {
		createChild(
			parentId: $parentId
			childName: $childName
			initialBalance: $initialBalance
		) {
			id
			name
			role
			createdAt
		}
	}
`;

export const LINK_CHILD_TO_AUTH = gql`
	mutation LinkChildToAuth($childId: String!, $authUserId: String!) {
		linkChildToAuth(childId: $childId, authUserId: $authUserId) {
			id
			name
			role
			createdAt
		}
	}
`;

export const LINK_CHILD_TO_AUTH_BY_EMAIL = gql`
	mutation LinkChildToAuthByEmail($childId: String!, $email: String!) {
		linkChildToAuthByEmail(childId: $childId, email: $email) {
			id
			name
			role
			createdAt
		}
	}
`;

export const INVITE_CHILD_TO_AUTH = gql`
	mutation InviteChildToAuth($childId: String!, $email: String!) {
		inviteChildToAuth(childId: $childId, email: $email) {
			id
			name
			email
			role
			createdAt
		}
	}
`;

export const CREATE_WITHDRAWAL_REQUEST = gql`
  mutation CreateWithdrawalRequest(
    $accountId: String!
    $amount: Int!
    $description: String!
  ) {
    createWithdrawalRequest(
      accountId: $accountId
      amount: $amount
      description: $description
    ) {
      id
      accountId
      amount
      description
      status
      createdAt
    }
  }
`;

export const APPROVE_WITHDRAWAL = gql`
  mutation ApproveWithdrawalRequest($requestId: String!) {
    approveWithdrawalRequest(requestId: $requestId) {
      id
      status
      updatedAt
    }
  }
`;

export const REJECT_WITHDRAWAL = gql`
  mutation RejectWithdrawalRequest($requestId: String!) {
    rejectWithdrawalRequest(requestId: $requestId) {
      id
      status
      updatedAt
    }
  }
`;

export const UPDATE_GOAL = gql`
  mutation UpdateGoal(
    $accountId: String!
    $goalName: String
    $goalAmount: Int
  ) {
    updateGoal(
      accountId: $accountId
      goalName: $goalName
      goalAmount: $goalAmount
    ) {
      id
      goalName
      goalAmount
      updatedAt
    }
  }
`;
