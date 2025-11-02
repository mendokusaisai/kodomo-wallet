import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import WithdrawalRequestDialog from "../withdrawal-request-dialog";

// Apollo Client のモック
jest.mock("@apollo/client/react", () => ({
  useMutation: jest.fn(() => [
    jest.fn(),
    { loading: false, error: null, data: null },
  ]),
}));

// sonner のモック
jest.mock("sonner", () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

// toast ヘルパーのモック
jest.mock("@/lib/toast", () => ({
  showSuccess: jest.fn(),
  showError: jest.fn(),
}));

describe("WithdrawalRequestDialog", () => {
  const mockProps = {
    accountId: "test-account-id",
    currentBalance: 10000,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("出金申請ボタンが表示される", () => {
    render(<WithdrawalRequestDialog {...mockProps} />);

    const button = screen.getByRole("button", { name: /出金申請/i });
    expect(button).toBeInTheDocument();
  });

  it("ボタンをクリックするとダイアログが開く", async () => {
    const user = userEvent.setup();
    render(<WithdrawalRequestDialog {...mockProps} />);

    const button = screen.getByRole("button", { name: /出金申請/i });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText("現在の残高")).toBeInTheDocument();
      expect(screen.getByText("¥10,000")).toBeInTheDocument();
    });
  });

  it("金額入力フィールドが正しく表示される", async () => {
    const user = userEvent.setup();
    render(<WithdrawalRequestDialog {...mockProps} />);

    const button = screen.getByRole("button", { name: /出金申請/i });
    await user.click(button);

    await waitFor(() => {
      const amountInput = screen.getByLabelText(/金額/i);
      expect(amountInput).toBeInTheDocument();
      expect(amountInput).toHaveAttribute("type", "number");
      expect(amountInput).toHaveAttribute("min", "1");
      expect(amountInput).toHaveAttribute("max", "10000");
    });
  });

  it("メモ入力フィールドが正しく表示される", async () => {
    const user = userEvent.setup();
    render(<WithdrawalRequestDialog {...mockProps} />);

    const button = screen.getByRole("button", { name: /出金申請/i });
    await user.click(button);

    await waitFor(() => {
      const descriptionInput = screen.getByLabelText(/メモ/i);
      expect(descriptionInput).toBeInTheDocument();
      expect(descriptionInput).toHaveAttribute("type", "text");
    });
  });

  it("申請ボタンが表示される", async () => {
    const user = userEvent.setup();
    render(<WithdrawalRequestDialog {...mockProps} />);

    const openButton = screen.getByRole("button", { name: /出金申請/i });
    await user.click(openButton);

    await waitFor(() => {
      const submitButton = screen.getByRole("button", { name: /申請する/i });
      expect(submitButton).toBeInTheDocument();
      expect(submitButton).toHaveAttribute("type", "submit");
    });
  });

  it("金額とメモを入力できる", async () => {
    const user = userEvent.setup();
    render(<WithdrawalRequestDialog {...mockProps} />);

    const openButton = screen.getByRole("button", { name: /出金申請/i });
    await user.click(openButton);

    await waitFor(async () => {
      const amountInput = screen.getByLabelText(/金額/i) as HTMLInputElement;
      const descriptionInput = screen.getByLabelText(/メモ/i) as HTMLInputElement;

      await user.clear(amountInput);
      await user.type(amountInput, "5000");
      await user.type(descriptionInput, "お小遣い");

      expect(amountInput.value).toBe("5000");
      expect(descriptionInput.value).toBe("お小遣い");
    });
  });
});
