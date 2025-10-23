# アーキテクチャ: Repository Pattern + Service Layer + DI

## 概要

Resolvers のデータベース依存を解決するため、以下のアーキテクチャパターンを導入しました:

```
GraphQL Resolvers (API Layer)
       ↓ 依存
Service Layer (Business Logic)
       ↓ 依存
Repository Layer (Data Access)
       ↓ 実装
SQLAlchemy / Mock (Infrastructure)
```

## ディレクトリ構造

```
app/
├── api/graphql/
│   ├── resolvers.py        # GraphQL resolvers (Service層を使用)
│   └── types.py            # GraphQL type definitions
├── services/
│   └── business_services.py # ビジネスロジック層 (@inject使用)
├── repositories/
│   ├── interfaces.py       # Repository抽象クラス (ABC)
│   ├── sqlalchemy_repositories.py  # SQLAlchemy実装
│   └── mock_repositories.py        # テスト用Mock実装
├── core/
│   └── container.py        # DI container (injectorパッケージ使用)
└── models/
    └── models.py           # SQLAlchemy models
```

## 各層の責務

### 1. Repository Layer (`repositories/`)

**責務**: データアクセスのみ

- データベースとの直接的なやり取り
- CRUD 操作の実装
- SQLAlchemy の詳細を隠蔽

```python
# interfaces.py - 抽象クラスで契約を定義
class ProfileRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: str) -> Profile | None:
        pass

# sqlalchemy_repositories.py - SQLAlchemy実装
class SQLAlchemyProfileRepository(ProfileRepository):
    def get_by_id(self, user_id: str) -> Profile | None:
        return self.db.query(Profile).filter(Profile.id == user_id).first()

# mock_repositories.py - テスト用Mock実装
class MockProfileRepository(ProfileRepository):
    def get_by_id(self, user_id: str) -> Profile | None:
        return self.profiles.get(user_id)
```

### 2. Service Layer (`services/`)

**責務**: ビジネスロジック

- ドメインルールの実装
- 複数の Repository の調整
- `@inject` デコレータによる依存性注入
- トランザクション境界の管理（リポジトリ呼び出しまで）

```python
class ProfileService:
    """Service for profile-related business logic"""

    @inject
    def __init__(self, profile_repo: ProfileRepository):
        self.profile_repo = profile_repo

    def get_profile(self, user_id: str) -> Profile | None:
        """Get user profile by ID"""
        return self.profile_repo.get_by_id(user_id)

class TransactionService:
    """Service for transaction-related business logic"""

    @inject
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        account_repo: AccountRepository,
    ):
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo

    def create_deposit(
        self, account_id: str, amount: int, description: str | None = None
    ) -> Transaction:
        # ビジネスロジック: 入金処理
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")

        new_balance = int(account.balance) + amount
        self.account_repo.update_balance(account, new_balance)

        return self.transaction_repo.create(
            account_id=account_id,
            transaction_type="deposit",
            amount=amount,
            description=description,
            created_at=datetime.now(UTC),
        )
```

### 3. Dependency Injection (`core/container.py` と `@inject`)

**責務**: 依存性の注入

- `injector`パッケージの`@inject`デコレータを使用
- Service クラスのコンストラクタで自動依存解決
- Resolver は直接 Service インスタンスを引数で受け取る
- テスト時は手動で Mock を注入

```python
from injector import inject

# Service層で@injectを使用
class ProfileService:
    @inject
    def __init__(self, profile_repo: ProfileRepository):
        self.profile_repo = profile_repo

class TransactionService:
    @inject
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        account_repo: AccountRepository,
    ):
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo

# Resolverはサービスを直接受け取る（DIコンテナ不要）
def get_profile_by_id(
    user_id: str,
    profile_service: ProfileService,  # ← 直接受け取る
) -> Profile | None:
    return profile_service.get_profile(user_id)

# テスト時はMockを手動注入
def test_get_profile():
    mock_repo = MockProfileRepository()
    service = ProfileService(mock_repo)  # 手動注入
    # テスト...
```

**注意**: 現在の実装では、`core/container.py`は使用していません。Resolver が直接 Service インスタンスを受け取る設計になっています。

### 4. GraphQL Resolvers (`api/graphql/resolvers.py`)

**責務**: HTTP リクエストとビジネスロジックの橋渡し

- GraphQL クエリ/ミューテーションの処理
- Service インスタンスを直接受け取る（依存性注入）
- トランザクションのコミット（ミューテーション時のみ）

```python
def get_profile_by_id(
    user_id: str,
    profile_service: ProfileService,
) -> Profile | None:
    """Get user profile by ID"""
    return profile_service.get_profile(user_id)

def create_deposit(
    account_id: str,
    amount: int,
    db: Session,
    transaction_service: TransactionService,
    description: str | None = None,
) -> Transaction:
    """Create a deposit transaction and commit"""
    transaction = transaction_service.create_deposit(account_id, amount, description)
    # Commit at resolver level
    db.commit()
    return transaction
```

## メリット

### 1. **テストしやすさ**

- MockRepository を使って Service を DB なしでテスト可能
- MockService を使って Resolver を Service なしでテスト可能
- 各層を完全に独立してテスト可能（全 70 テスト実装済み）

```python
# Resolver層の単体テスト例
def test_get_profile_by_id_success():
    mock_profile_service = Mock()
    mock_profile_service.get_profile.return_value = sample_profile

    result = resolvers.get_profile_by_id(user_id, mock_profile_service)

    assert result == sample_profile
    mock_profile_service.get_profile.assert_called_once_with(user_id)

# Service層のユニットテスト例
def test_create_deposit():
    # Mock repositories
    account_repo = MockAccountRepository()
    transaction_repo = MockTransactionRepository()

    # Service under test
    service = TransactionService(transaction_repo, account_repo)

    # Test
    result = service.create_deposit("account-1", 1000, "Test deposit")
    assert result.amount == 1000
```

### 2. **疎結合**

- Resolvers は SQLAlchemy の詳細を知らない
- Services は Repository インターフェースに依存
- データベース実装の変更が容易

### 3. **保守性**

- 責務が明確に分離
- ビジネスロジックが集約
- 変更の影響範囲が限定的

### 4. **拡張性**

- 新しい Repository の追加が容易
- 異なるデータソース(Redis, API 等)への対応が可能
- キャッシュ層の追加が容易

## Before / After

### Before (直接 DB 依存)

```python
def create_deposit(db: Session, account_id: str, amount: int) -> Transaction:
    # Resolverがデータベース操作の詳細を知っている
    account = db.query(AccountModel).filter(AccountModel.id == account_id).first()
    if not account:
        raise ValueError("Account not found")

    account.balance += amount

    transaction = TransactionModel(
        account_id=account_id,
        type="deposit",
        amount=amount,
        created_at=datetime.now(UTC),
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction
```

**問題点**:

- Resolver が SQLAlchemy に強く依存
- テスト時に実際の DB が必要
- ビジネスロジックが散在

### After (Repository + Service)

```python
# Resolver (API層) - Serviceを直接受け取る
def get_profile_by_id(
    user_id: str,
    profile_service: ProfileService,
) -> Profile | None:
    """Get user profile by ID"""
    return profile_service.get_profile(user_id)

def create_deposit(
    account_id: str,
    amount: int,
    db: Session,
    transaction_service: TransactionService,
    description: str | None = None,
) -> Transaction:
    """Create a deposit transaction and commit"""
    transaction = transaction_service.create_deposit(account_id, amount, description)
    db.commit()
    return transaction

# Service (ビジネスロジック層) - @injectで依存性注入
class TransactionService:
    @inject
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        account_repo: AccountRepository,
    ):
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo

    def create_deposit(self, account_id: str, amount: int, description: str | None = None) -> Transaction:
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")

        new_balance = int(account.balance) + amount
        self.account_repo.update_balance(account, new_balance)

        return self.transaction_repo.create(
            account_id=account_id,
            transaction_type="deposit",
            amount=amount,
            description=description,
            created_at=datetime.now(UTC),
        )

# Repository (データアクセス層)
class SQLAlchemyTransactionRepository(TransactionRepository):
    def create(self, account_id: str, transaction_type: str, amount: int, ...) -> Transaction:
        transaction = Transaction(...)
        self.db.add(transaction)
        self.db.flush()
        return transaction
```

**改善点**:

- 各層の責務が明確
- Resolver は直接 Service インスタンスを受け取る（DI コンテナ不要）
- MockRepository でテスト可能
- ビジネスロジックが Service に集約
- `@inject`デコレータによる自動依存解決

## テスト戦略

### 1. Repository 層のテスト (`test_repositories.py`)

- SQLAlchemyRepository と MockRepository の両方をテスト
- データアクセス層の正確性を保証

### 2. Service 層のテスト (`test_services.py`)

- MockRepository を使用
- ビジネスロジックに集中
- データベース不要で高速

```python
def test_create_deposit_insufficient_balance():
    account_repo = MockAccountRepository()
    transaction_repo = MockTransactionRepository()
    service = TransactionService(transaction_repo, account_repo)

    # ビジネスルールのテスト
    with pytest.raises(ValueError, match="Account not found"):
        service.create_deposit("non-existent-account", 1000)
```

### 3. Resolver 層のテスト (`test_resolvers.py`)

- Mock Service を使用した単体テスト
- Resolver のロジックのみをテスト
- データベース不要で高速

```python
def test_get_profile_by_id_success():
    mock_profile_service = Mock()
    mock_profile_service.get_profile.return_value = sample_profile

    result = resolvers.get_profile_by_id(user_id, mock_profile_service)

    assert result == sample_profile
    mock_profile_service.get_profile.assert_called_once_with(user_id)
```

### 4. 統合テスト (`test_graphql_integration.py`)

- 実際の Repository、Service、Resolver を組み合わせてテスト
- エンドツーエンドの動作確認
- SQLite インメモリ DB を使用

## テスト構成の概要

| テストファイル                | 対象層     | 依存関係          | テスト数 |
| ----------------------------- | ---------- | ----------------- | -------- |
| `test_models.py`              | Model      | SQLAlchemy        | 11       |
| `test_repositories.py`        | Repository | Mock + SQLAlchemy | 21       |
| `test_services.py`            | Service    | Mock Repository   | 13       |
| `test_resolvers.py`           | Resolver   | Mock Service      | 15       |
| `test_graphql_integration.py` | 統合       | 全層 + SQLite     | 10       |
| **合計**                      | -          | -                 | **70**   |

## 次のステップ

1. **GraphQL Schema の実装**

   - Strawberry を使用したスキーマ定義
   - Resolver との統合

2. **認証・認可の実装**

   - Supabase 認証との統合
   - Row Level Security (RLS) の活用

3. **キャッシュ層の追加** (オプション)

   - CachedRepository の実装
   - Redis との統合

4. **エラーハンドリングの強化**
   - カスタム例外クラスの定義
   - GraphQL エラーレスポンスの統一
