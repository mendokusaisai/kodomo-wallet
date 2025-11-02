import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import GoalDialog from "../goal-dialog";

// Apollo Client のモック
jest.mock("@apollo/client/react", () => ({
  useMutation: jest.fn(() => [
    jest.fn(),
    { loading: false, error: null, data: null },
  ]),
}));

// toast ヘルパーのモック
jest.mock("@/lib/toast", () => ({
  showSuccess: jest.fn(),
  showError: jest.fn(),
}));

// ConfirmDialog のモック
jest.mock("@/components/confirm-dialog", () => ({
  ConfirmDialog: ({ onConfirm, children }: { onConfirm: () => void; children: React.ReactNode }) => (
    <div data-testid="confirm-dialog">
      <button onClick={onConfirm}>確認</button>
      {children}
    </div>
  ),
}));

describe("GoalDialog", () => {
  const mockProps = {
    accountId: "test-account-id",
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("目標未設定時は「目標を設定」ボタンが表示される", () => {
    render(<GoalDialog {...mockProps} />);

    expect(screen.getByRole("button", { name: /目標を設定/i })).toBeInTheDocument();
  });

  it("目標設定済み時は「目標を編集」ボタンが表示される", () => {
    render(
      <GoalDialog
        {...mockProps}
        currentGoalName="MacBook Pro"
        currentGoalAmount={300000}
      />
    );

    expect(screen.getByRole("button", { name: /目標を編集/i })).toBeInTheDocument();
  });

  it("ボタンをクリックするとダイアログが開く", async () => {
    const user = userEvent.setup();
    render(<GoalDialog {...mockProps} />);

    const button = screen.getByRole("button", { name: /目標を設定/i });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText("貯金目標の設定")).toBeInTheDocument();
    });
  });

  it("目標名と目標金額の入力フィールドが表示される", async () => {
    const user = userEvent.setup();
    render(<GoalDialog {...mockProps} />);

    const button = screen.getByRole("button", { name: /目標を設定/i });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByLabelText(/目標名/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/目標金額/i)).toBeInTheDocument();
    });
  });

  it("目標名と目標金額を入力できる", async () => {
    const user = userEvent.setup();
    render(<GoalDialog {...mockProps} />);

    const button = screen.getByRole("button", { name: /目標を設定/i });
    await user.click(button);

    await waitFor(async () => {
      const nameInput = screen.getByLabelText(/目標名/i) as HTMLInputElement;
      const amountInput = screen.getByLabelText(/目標金額/i) as HTMLInputElement;

      await user.type(nameInput, "MacBook Pro");
      await user.clear(amountInput);
      await user.type(amountInput, "300000");

      expect(nameInput.value).toBe("MacBook Pro");
      expect(amountInput.value).toBe("300000");
    });
  });

  it("既存の目標が入力フィールドに表示される", async () => {
    const user = userEvent.setup();
    render(
      <GoalDialog
        {...mockProps}
        currentGoalName="ゲーム機"
        currentGoalAmount={50000}
      />
    );

    const button = screen.getByRole("button", { name: /目標を編集/i });
    await user.click(button);

    await waitFor(() => {
      const nameInput = screen.getByLabelText(/目標名/i) as HTMLInputElement;
      const amountInput = screen.getByLabelText(/目標金額/i) as HTMLInputElement;

      expect(nameInput.value).toBe("ゲーム機");
      expect(amountInput.value).toBe("50000");
    });
  });

  it("設定ボタンが表示される", async () => {
    const user = userEvent.setup();
    render(<GoalDialog {...mockProps} />);

    const openButton = screen.getByRole("button", { name: /目標を設定/i });
    await user.click(openButton);

    await waitFor(() => {
      const submitButton = screen.getByRole("button", { name: /保存/i });
      expect(submitButton).toBeInTheDocument();
      expect(submitButton).toHaveAttribute("type", "submit");
    });
  });

  it("目標未設定時は目標クリアボタンが表示されない", async () => {
    const user = userEvent.setup();
    render(<GoalDialog {...mockProps} />);

    const button = screen.getByRole("button", { name: /目標を設定/i });
    await user.click(button);

    await waitFor(() => {
      expect(screen.queryByRole("button", { name: /クリア/i })).not.toBeInTheDocument();
    });
  });

});
