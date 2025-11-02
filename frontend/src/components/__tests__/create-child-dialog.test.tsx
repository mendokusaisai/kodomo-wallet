import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CreateChildDialog } from "../create-child-dialog";

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

describe("CreateChildDialog", () => {
  const mockProps = {
    open: true,
    onOpenChange: jest.fn(),
    parentId: "test-parent-id",
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("ダイアログが開いている時にコンテンツが表示される", () => {
    render(<CreateChildDialog {...mockProps} />);

    expect(screen.getByText("子どもアカウント追加")).toBeInTheDocument();
    expect(screen.getByText(/お子さんの名前と初期残高を入力してください/)).toBeInTheDocument();
  });

  it("名前入力フィールドが正しく表示される", () => {
    render(<CreateChildDialog {...mockProps} />);

    const nameInput = screen.getByLabelText(/子どもの名前/i);
    expect(nameInput).toBeInTheDocument();
    expect(nameInput).toHaveAttribute("placeholder", "例: 太郎");
  });

  it("初期残高入力フィールドが正しく表示される", () => {
    render(<CreateChildDialog {...mockProps} />);

    const balanceInput = screen.getByLabelText(/初期残高/i);
    expect(balanceInput).toBeInTheDocument();
    expect(balanceInput).toHaveAttribute("type", "number");
    expect(balanceInput).toHaveAttribute("placeholder", "0");
  });

  it("作成ボタンとキャンセルボタンが表示される", () => {
    render(<CreateChildDialog {...mockProps} />);

    expect(screen.getByRole("button", { name: /作成/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /キャンセル/i })).toBeInTheDocument();
  });

  it("名前と初期残高を入力できる", async () => {
    const user = userEvent.setup();
    render(<CreateChildDialog {...mockProps} />);

    const nameInput = screen.getByLabelText(/子どもの名前/i) as HTMLInputElement;
    const balanceInput = screen.getByLabelText(/初期残高/i) as HTMLInputElement;

    await user.type(nameInput, "太郎");
    await user.clear(balanceInput);
    await user.type(balanceInput, "5000");

    expect(nameInput.value).toBe("太郎");
    expect(balanceInput.value).toBe("5000");
  });

  it("キャンセルボタンをクリックするとダイアログが閉じる", async () => {
    const user = userEvent.setup();
    render(<CreateChildDialog {...mockProps} />);

    const cancelButton = screen.getByRole("button", { name: /キャンセル/i });
    await user.click(cancelButton);

    expect(mockProps.onOpenChange).toHaveBeenCalledWith(false);
  });

  it("ダイアログが閉じている時はコンテンツが表示されない", () => {
    render(<CreateChildDialog {...mockProps} open={false} />);

    expect(screen.queryByText("子どもアカウント追加")).not.toBeInTheDocument();
  });
});
