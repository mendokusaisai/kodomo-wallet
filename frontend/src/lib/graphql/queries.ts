import { gql } from "@apollo/client";

// ==================== Query ====================

export const GET_ME = gql`
  query GetMe {
    me {
      id
      name
      role
      avatarUrl
      createdAt
    }
  }
`;

export const GET_ACCOUNTS = gql`
  query GetAccounts {
    accounts {
      id
      userId
      balance
      currency
      goalName
      goalAmount
      createdAt
      updatedAt
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
  query GetWithdrawalRequests($accountId: String) {
    withdrawalRequests(accountId: $accountId) {
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
  mutation ApproveWithdrawal($requestId: String!) {
    approveWithdrawal(requestId: $requestId) {
      id
      status
      updatedAt
    }
  }
`;

export const REJECT_WITHDRAWAL = gql`
  mutation RejectWithdrawal($requestId: String!) {
    rejectWithdrawal(requestId: $requestId) {
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
