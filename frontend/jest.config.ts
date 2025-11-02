import type { Config } from 'jest'
import nextJest from 'next/jest.js'

const createJestConfig = nextJest({
  // next.config.js と .env ファイルを読み込むための Next.js アプリのパス
  dir: './',
})

// Jest の設定
const config: Config = {
  coverageProvider: 'v8',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  moduleNameMapper: {
    // path alias の設定（tsconfig.json と同じ）
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testMatch: [
    '**/__tests__/**/*.{ts,tsx}',
    '**/*.{spec,test}.{ts,tsx}',
  ],
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{ts,tsx}',
    '!src/**/_*.{ts,tsx}',
  ],
  modulePathIgnorePatterns: ['<rootDir>/.next/'],
}

// createJestConfig は next/jest が非同期で Next.js の設定を読み込めるようにするためエクスポート
export default createJestConfig(config)
