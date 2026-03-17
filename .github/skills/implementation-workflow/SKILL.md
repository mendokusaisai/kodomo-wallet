---
name: implementation-workflow
description: TDD ベースのフェーズ単位実装ワークフロー。docs/tasks.md の計画に基づき、各フェーズでテスト駆動開発を実施。テスト通過時に semantic commit でコミット。エラー発生時は示唆する。進捗を progress.md に記録。実装フェーズで使用。
---

# Implementation Workflow Skill

実装作業を体系的に進めるための TDD ベースのワークフローを自動化します。

## 概要

docs/tasks.md に記載された計画（Phase 単位）に基づき、以下のサイクルを反復実行：

```
1. Phase を読み込み、スコープを確認
2. テスト/テストケースを設計・実装（TDD）
3. 本実装をテスト駆動で進める
4. テスト全て通過を確認
5. semantic commit でコミット
6. progress.md に進捗を記録
```

## 使用場面

- ユーザーが「実装」と指示した場合
- docs/tasks.md に詳細なタスク計画がある場合
- テスト駆動開発で安定実装を重視する場合

## ワークフロー詳細

### Step 1: docs/tasks.md を読み込み、フェーズリストを抽出

ファイルを読み、以下を確認：
- フェーズ数とスコープ
- 各フェーズの「要件に関連するファイルパス」
- 各フェーズの「受け入れ条件」（テスト対象）

### Step 2: progress.md を初期化

プロジェクトのルートに progress.md を作成（既存時は追記）。以下の形式で記録開始：

```markdown
# Implementation Progress

## Overview
- Total Phases: [N]
- Start Date: [YYYY-MM-DD]
- Status: In Progress

## Phase Summary
| Phase | Name | Status | Progress | Commit |
|-------|------|--------|----------|--------|
| 1 | [Phase Name] | ⏳ Pending | - | - |
| 2 | [Phase Name] | ⏳ Pending | - | - |

## Detailed Logs

### Phase 1: [Phase Name]
- [ ] Test Design
- [ ] Test Implementation
- [ ] Main Implementation
- [ ] All Tests Pass
- [ ] Commit

Details:
- Files modified: (will be filled)
- Tests created: (will be filled)
- Commit hash: (will be filled)
```

### Step 3: 現在の Phase を開始

各フェーズで以下を実行：

#### 3.1 テスト設計（Design Phase）

「受け入れ条件」から検証項目を抽出し、テストケースを設計：
- 各 acceptance criteria に対し、1つ以上のテストケースをマップ
- テストの種類（ユニット / 統合 / E2E）を決定
- 入力・期待出力を明確化

#### 3.2 テスト実装（Test-First）

実装テストを先に書く：
- pytest（Python）/ Jest（TypeScript）等、プロジェクトに合わせて使用
- テストは FAIL 状態で一度確認
- テストファイルは `tests/` 配下に保存

#### 3.3 本実装（TDD Loop）

テストが通るまで実装：
- 最小限の実装で RED → GREEN に
- リファクタリングは GREEN 確認後
- 進捗は逐次 progress.md に記録（3.5 参照）

#### 3.4 テスト全体確認

Phase に関連する全テストを実行：
```bash
# Python
pytest tests/ -v

# TypeScript/JavaScript  
npm test
```

すべてで PASS を確認。FAIL 時は原因を示唆（デバッグは別フェーズで）。

#### 3.5 進捗記録（毎ステップ）

progress.md の該当 Phase セクションを更新：

```markdown
### Phase N: [Name]
- [x] Test Design
- [x] Test Implementation  
- [ ] Main Implementation
- [ ] All Tests Pass
- [ ] Commit

Details:
- Files modified: src/module.py, tests/test_module.py
- Tests created: test_function_X, test_edge_case_Y
- Implementation status: 30% complete (reason: awaiting API design clarification)
```

### Step 4: コミット（Phase Complete）

全テストが通ったら、semantic commit を実行：

```
<type>(<scope>): <subject>

<body>

Closes: <issue-ref>
```

**Commit 例：**
```
feat(gcp-backend): implement Cloud Run deployment for backend service

- Add Dockerfile for backend containerization
- Configure Cloud Run service parameters
- Implement health check endpoint
- Add environment variable injection from Secret Manager

Tests:
- ✅ test_cloud_run_deployment_creates_service
- ✅ test_health_check_responds_correctly
- ✅ test_env_vars_injected_from_secrets

Closes: Phase 3
```

### Step 5: 次 Phase へ

progress.md の Phase Status を更新：

```markdown
| N | [Phase Name] | ✅ Complete | 100% | abc123def |
```

次 Phase を Step 3 から反復。

## エラー時の動作

実装中にエラー（テスト FAIL / 実装時 exception など）が発生したら：

1. **示唆を提示** - エラーの原因と可能性のある修正方針を提案
2. **ユーザー判断** - ユーザーが「デバッグ」を指示するまで、スキルは進まない
3. **デバッグ後** - 修正されたら Step 3.3 から再開

## SOLID 原則に基づく実装

各フェーズの実装時に、SOLID 原則を厳密に守ることで、保守性・拡張性・テスト性の高いコードを実現します。

### S: Single Responsibility Principle（単一責任原則）

1つのクラス/関数は1つの責任のみを持つ。責任が複数ある場合は分割。

**例：** 
- ❌ データ取得 + バリデーション + DB保存を1つの関数で実施
- ✅ `fetch_data()`, `validate()`, `persist()` に分割

### O: Open/Closed Principle（開放閉鎖原則）

拡張に開き、修正に閉じたコード設計。

**実装時のチェック：**
- 新機能追加時に既存コードの修正が最小限か？
- 抽象クラス / インターフェースで拡張ポイントを作成したか？

### L: Liskov Substitution Principle（リスコフの置換原則）

サブクラスはスーパークラスの代わりに使用可能であるべき。

**テスト観点：**
- 親クラス型で受け取った変数が、どんなサブクラスでも同じ結果を出すか？

### I: Interface Segregation Principle（インターフェース分離原則）

大きなインターフェースを小さく分割。クライアントは必要なインターフェースのみ依存。

**例：**
- ❌ `RepositoryInterface` に全CRUD操作を定義
- ✅ `Readable`, `Writable`, `Deletable` に分割

### D: Dependency Inversion Principle（依存性逆転原則）

高レベルモジュールは低レベルモジュールに依存しない。両者とも抽象に依存。

**実装例：**
```python
# ❌ 悪い例
class UserService:
    def __init__(self):
        self.db = DatabaseConnection()  # 具体的な実装に依存

# ✅ 良い例
class UserService:
    def __init__(self, repository: UserRepositoryInterface):
        self.repository = repository  # 抽象に依存
```

### 実装フェーズでの SOLID チェックリスト

各フェーズのリファクタリング時に確認：

- [ ] 各クラス/関数は単一責任を持つか？
- [ ] 新機能追加時に既存コード修正が最小限か？
- [ ] サブクラスが親クラスの置換可能性を満たすか？
- [ ] 不要なインターフェースメソッドを実装していないか？
- [ ] 具体的な実装ではなく抽象に依存しているか？

---

## 重要な制約

- **docs/tasks.md 厳格準拠** - 記載されている以上の実装を絶対に行わない
- **テスト駆動** - 本実装はテストなしに進めない
- **commit は Phase 単位** - ステップ単位の細切れ commit は避ける
- **TDD の循環** - RED → GREEN → REFACTOR サイクルを守る
- **SOLID 原則** - リファクタリング時に SOLID 原則を厳密に適用

## ファイル構成

実装スキル関連のファイル：
- `docs/tasks.md` - 実装計画（Phase 単位）
- `progress.md` - 進捗記録（このスキルが更新）
- `tests/` - テストコード（このスキルが作成・実行）
- ソースコード - テスト駆動で実装

## 使用例

```
ユーザー: 実装

Skill:
1. ✅ docs/tasks.md を読み込み
2. ✅ progress.md を初期化
3. 🔄 Phase 1 を開始
   - テスト設計を実施
   - テストコード作成
   - 実装を進行中...
   - テスト実行: 2/5 通過
   - progress.md を更新
```

---

## 参考: セマンティック Commit の型

- `feat`: 新機能
- `fix`: バグ修正
- `refactor`: コード改善（機能変わらず）
- `test`: テスト追加・修正
- `docs`: ドキュメント更新
- `chore`: ビルド、依存関係など
