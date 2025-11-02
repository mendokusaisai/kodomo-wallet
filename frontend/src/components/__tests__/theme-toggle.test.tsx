import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { ThemeToggle } from '../theme-toggle'
import { ThemeProvider } from '../theme-provider'

// next-themes のモック
jest.mock('next-themes', () => ({
  useTheme: () => ({
    theme: 'light',
    setTheme: jest.fn(),
  }),
  ThemeProvider: ({ children }: { children: React.ReactNode }) => children,
}))

describe('ThemeToggle', () => {
  it('正しくレンダリングされる', () => {
    render(
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        <ThemeToggle />
      </ThemeProvider>
    )

    // ボタンが存在することを確認
    const button = screen.getByRole('button')
    expect(button).toBeInTheDocument()
  })

  it('アクセシビリティラベルがある', () => {
    render(
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        <ThemeToggle />
      </ThemeProvider>
    )

    // aria-label または title があることを確認
    const button = screen.getByRole('button')
    expect(
      button.getAttribute('aria-label') || button.getAttribute('title')
    ).toBeTruthy()
  })
})
