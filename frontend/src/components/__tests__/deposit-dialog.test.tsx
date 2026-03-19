import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { DepositDialog } from '../deposit-dialog'

// Apollo Client のモック
jest.mock('@apollo/client/react', () => ({
  ...jest.requireActual('@apollo/client/react'),
  useMutation: () => [
    jest.fn().mockResolvedValue({ data: { deposit: { id: '1' } } }),
    { loading: false, error: null },
  ],
}))

// Toast のモック
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}))

const mockOnOpenChange = jest.fn()

describe('DepositDialog', () => {
  const defaultProps = {
    open: true,
    onOpenChange: mockOnOpenChange,
    accountId: 'test-account-id',
    accountName: 'テスト太郎',
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('正しくレンダリングされる', () => {
    render(<DepositDialog {...defaultProps} />)

    expect(screen.getByText('入金')).toBeInTheDocument()
    expect(screen.getByLabelText(/金額/)).toBeInTheDocument()
    expect(screen.getByLabelText(/説明/)).toBeInTheDocument()
  })

  it('バリデーション: 金額が空の場合エラー表示', async () => {
    const user = userEvent.setup()
    
    render(<DepositDialog {...defaultProps} />)

    const submitButton = screen.getByRole('button', { name: /入金する/ })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('金額を入力してください')).toBeInTheDocument()
    })
  })

  it('キャンセルボタンでダイアログを閉じる', async () => {
    const user = userEvent.setup()
    
    render(<DepositDialog {...defaultProps} />)

    const cancelButton = screen.getByRole('button', { name: /キャンセル/ })
    await user.click(cancelButton)

    expect(mockOnOpenChange).toHaveBeenCalledWith(false)
  })

  it('説明欄が空のまま送信できる', async () => {
    const user = userEvent.setup()

    render(<DepositDialog {...defaultProps} />)

    await user.type(screen.getByLabelText(/金額/), '1000')
    // 説明欄は入力しない

    const submitButton = screen.getByRole('button', { name: /入金する/ })
    await user.click(submitButton)

    // 説明に関するバリデーションエラーが表示されないこと
    await waitFor(() => {
      expect(screen.queryByText('説明を入力してください')).not.toBeInTheDocument()
    })

    // ダイアログが閉じること（送信成功）
    await waitFor(() => {
      expect(mockOnOpenChange).toHaveBeenCalledWith(false)
    })
  })

  it('説明欄のラベルが「説明（任意）」と表示される', () => {
    render(<DepositDialog {...defaultProps} />)

    expect(screen.getByText('説明（任意）')).toBeInTheDocument()
  })
})
