import { render, screen } from "@testing-library/react";
import { TransactionHistory } from "../transaction-history";

// Apollo Client のモック
const mockUseQuery = jest.fn();
jest.mock("@apollo/client/react", () => ({
  useQuery: (...args: unknown[]) => mockUseQuery(...args),
}));

// date-fns のモック
jest.mock("date-fns", () => ({
  format: jest.fn((date: Date) => "2025/11/01 10:00"),
}));

jest.mock("date-fns/locale", () => ({
  ja: {},
}));

describe("TransactionHistory", () => {
  const mockAccountId = "test-account-id";

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("ローディング中はSkeletonを表示する", () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: true,
      error: null,
    });

    render(<TransactionHistory accountId={mockAccountId} />);
    // Skeleton要素が表示されることを確認
    const container = document.querySelector('.animate-pulse');
    expect(container).not.toBeNull();
  });

  it("エラー時はエラーメッセージを表示する", () => {
    mockUseQuery.mockReturnValue({
      data: null,
      loading: false,
      error: new Error("Network error"),
    });

    render(<TransactionHistory accountId={mockAccountId} />);

    expect(screen.getByText("取引履歴の読み込みに失敗しました")).toBeInTheDocument();
  });

  it("取引が0件の場合は空メッセージを表示する", () => {
    mockUseQuery.mockReturnValue({
      data: { transactions: [] },
      loading: false,
      error: null,
    });

    render(<TransactionHistory accountId={mockAccountId} />);

    expect(screen.getByText("まだ取引履歴がありません")).toBeInTheDocument();
  });

  it("取引データがnullの場合は空メッセージを表示する", () => {
    mockUseQuery.mockReturnValue({
      data: { transactions: null },
      loading: false,
      error: null,
    });

    render(<TransactionHistory accountId={mockAccountId} />);

    expect(screen.getByText("まだ取引履歴がありません")).toBeInTheDocument();
  });

  it("取引履歴が正しく表示される", () => {
    const mockTransactions = [
      {
        id: "1",
        type: "deposit",
        amount: 1000,
        description: "お小遣い",
        createdAt: "2025-11-01T10:00:00Z",
      },
      {
        id: "2",
        type: "withdraw",
        amount: 500,
        description: "ゲーム購入",
        createdAt: "2025-11-02T15:30:00Z",
      },
    ];

    mockUseQuery.mockReturnValue({
      data: { transactions: mockTransactions },
      loading: false,
      error: null,
    });

    render(<TransactionHistory accountId={mockAccountId} />);
    // 取引内容が表示されることを確認
    expect(screen.getByText("お小遣い")).toBeInTheDocument();
    expect(screen.getByText("ゲーム購入")).toBeInTheDocument();
  // 金額は部分一致で検索
  expect(screen.getByText(/1,000/)).toBeInTheDocument();
  expect(screen.getByText(/500/)).toBeInTheDocument();
  });

  it("入金タイプの取引が正しいスタイルで表示される", () => {
    const mockTransactions = [
      {
        id: "1",
        type: "deposit",
        amount: 1000,
        description: "",
        createdAt: "2025-11-01T10:00:00Z",
      },
    ];

    mockUseQuery.mockReturnValue({
      data: { transactions: mockTransactions },
      loading: false,
      error: null,
    });

    render(<TransactionHistory accountId={mockAccountId} />);
    expect(screen.getByText("入金")).toBeInTheDocument();
  expect(screen.getByText(/1,000/)).toBeInTheDocument();
  });

  it("出金タイプの取引が正しいスタイルで表示される", () => {
    const mockTransactions = [
      {
        id: "1",
        type: "withdraw",
        amount: 500,
        description: "",
        createdAt: "2025-11-01T10:00:00Z",
      },
    ];

    mockUseQuery.mockReturnValue({
      data: { transactions: mockTransactions },
      loading: false,
      error: null,
    });

    render(<TransactionHistory accountId={mockAccountId} />);
    expect(screen.getByText("出金")).toBeInTheDocument();
  expect(screen.getByText(/500/)).toBeInTheDocument();
  });

  it("報酬タイプの取引が正しいスタイルで表示される", () => {
    const mockTransactions = [
      {
        id: "1",
        type: "reward",
        amount: 300,
        description: "",
        createdAt: "2025-11-01T10:00:00Z",
      },
    ];

    mockUseQuery.mockReturnValue({
      data: { transactions: mockTransactions },
      loading: false,
      error: null,
    });

    render(<TransactionHistory accountId={mockAccountId} />);
    expect(screen.getByText("報酬")).toBeInTheDocument();
  expect(screen.getByText(/300/)).toBeInTheDocument();
  });
});
