import { gql } from "@apollo/client";

// ==================== Query ====================

export const MY_FAMILY = gql`
  query MyFamily {
    myFamily {
      id
      name
      createdAt
      members {
        uid
        familyId
        name
        role
        email
        joinedAt
      }
    }
  }
`;

export const FAMILY_ACCOUNTS = gql`
  query FamilyAccounts($familyId: String!) {
    familyAccounts(familyId: $familyId) {
      id
      familyId
      name
      balance
      currency
      goalName
      goalAmount
      createdAt
      updatedAt
    }
  }
`;

export const ACCOUNT_TRANSACTIONS = gql`
  query AccountTransactions($familyId: String!, $accountId: String!, $limit: Int) {
    accountTransactions(familyId: $familyId, accountId: $accountId, limit: $limit) {
      id
      accountId
      familyId
      type
      amount
      note
      createdAt
      createdByUid
    }
  }
`;

// ==================== Mutation ====================

export const CREATE_FAMILY = gql`
  mutation CreateFamily($myName: String!, $email: String!, $familyName: String) {
    createFamily(myName: $myName, email: $email, familyName: $familyName) {
      id
      name
      createdAt
      members {
        uid
        name
        role
      }
    }
  }
`;

export const CREATE_ACCOUNT = gql`
  mutation CreateAccount($familyId: String!, $name: String!, $currency: String) {
    createAccount(familyId: $familyId, name: $name, currency: $currency) {
      id
      familyId
      name
      balance
      currency
    }
  }
`;

export const DEPOSIT = gql`
  mutation Deposit($familyId: String!, $accountId: String!, $amount: Int!, $note: String) {
    deposit(familyId: $familyId, accountId: $accountId, amount: $amount, note: $note) {
      id
      type
      amount
      note
      createdAt
    }
  }
`;

export const WITHDRAW = gql`
  mutation Withdraw($familyId: String!, $accountId: String!, $amount: Int!, $note: String) {
    withdraw(familyId: $familyId, accountId: $accountId, amount: $amount, note: $note) {
      id
      type
      amount
      note
      createdAt
    }
  }
`;

export const UPDATE_GOAL = gql`
  mutation UpdateGoal($familyId: String!, $accountId: String!, $goalName: String, $goalAmount: Int) {
    updateGoal(familyId: $familyId, accountId: $accountId, goalName: $goalName, goalAmount: $goalAmount) {
      id
      goalName
      goalAmount
      updatedAt
    }
  }
`;

export const INVITE_CHILD = gql`
  mutation InviteChild($familyId: String!, $childName: String!) {
    inviteChild(familyId: $familyId, childName: $childName)
  }
`;

export const INVITE_PARENT = gql`
  mutation InviteParent($familyId: String!, $email: String!) {
    inviteParent(familyId: $familyId, email: $email)
  }
`;

export const JOIN_AS_CHILD = gql`
  mutation JoinAsChild($token: String!) {
    joinAsChild(token: $token) {
      uid
      familyId
      name
      role
    }
  }
`;

export const JOIN_AS_PARENT = gql`
  mutation JoinAsParent($token: String!, $name: String!, $email: String!) {
    joinAsParent(token: $token, name: $name, email: $email) {
      uid
      familyId
      name
      role
    }
  }
`;
