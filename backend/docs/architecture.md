# アーキテクチャ: Repository Pattern + Service Layer + DI

## 概要

GraphQL リクエストの処理を、責務ごとに以下の層に分離しています：

```
GraphQL Schema (API Layer)
       ↓ 依存
Service Layer (Business Logic)
       ↓ 依存
Repository Layer (Data Access)
       ↓ 実装
Firestore (Infrastructure)
```

## ディレクトリ構造

```
app/
├── api/graphql/
│   ├── schema.py       # GraphQL スキーマ・ミューテーション定義
│   ├── resolvers.py    # リゾルバー（Service 層を呼び出す）
│   └── types.py        # Strawberry 型定義
├── services/
│   ├── account_service.py          # 口座ビジネスロジック
│   ├── family_service.py           # 家族・招待ビジネスロジック
│   └── transaction_service.py      # 取引ビジネスロジック
├── repositories/
│   ├── interfaces.py               # Repository 抽象クラス (ABC)
│   ├── mock_repositories.py        # テスト用 Mock 実装
│   └── sqlalchemy/                 # Firestore 実装（ディレクトリ名は歴史的理由）
├── domain/
│   └── entities.py     # ドメインエンティティ（dataclass）
├── core/
│   ├── config.py       # 設定値管理（Firebase 等）
│   ├── container.py    # DI コンテナ（injector パッケージ）
│   ├── context.py      # GraphQL コンテキスト（Firebase Auth + サービスの初期化）
│   └── exceptions.py   # ドメイン例外階層
└── batch/
    └── process_recurring_deposits.py   # バッチ処理（将来拡張用）
```

## データストア / 認証

| 用途 | 技術 |
|------|------|
| 認証 | Firebase Authentication（Google OAuth） |
| データ | Cloud Firestore（ネイティブモード） |
| ストレージ | Firebase Storage（プロフィール画像） |

## ドメインモデル（家族中心モデル）

すべてのデータは家族（`Family`）に紐付きます。

```
Family
 └── FamilyMember (role: parent / child)
 └── Account (savings account per child)
      └── Transaction (deposit / withdraw)
```

各コレクションパスの例：
- `families/{familyId}`
- `family_members/{familyId}/members/{uid}`
- `accounts/{familyId}/accounts/{accountId}`
- `transactions/{familyId}/transactions/{transactionId}`

## 各層の責務

### 1. Repository Layer (`repositories/`)

**責務**: Firestore との CRUD 操作のみ

- Firestore ドキュメントの読み書き
- ビジネスロジックの排除
- ABC で契約を定義、Mock/Firestore の 2 実装

```python
# interfaces.py
class AccountRepository(ABC):
    @abstractmethod
    def get_by_id(self, family_id: str, account_id: str) -> Account | None: ...
    @abstractmethod
    def create(self, family_id: str, name: str, ...) -> Account: ...

# mock_repositories.py（テスト用）
class MockAccountRepository(AccountRepository):
    def __init__(self):
        self._accounts: dict[str, Account] = {}
    def get_by_id(self, family_id: str, account_id: str) -> Account | None:
        return self._accounts.get(account_id)
```

### 2. Service Layer (`services/`)

**責務**: ビジネスロジックの実装

- ドメインルール（権限チェック、バリデーション等）の集約
- 複数リポジトリの協調
- `@inject` デコレータで依存性注入

```python
class AccountService:
    @inject
    def __init__(self, account_repo: AccountRepository, member_repo: FamilyMemberRepository):
        self.account_repo = account_repo
        self.member_repo = member_repo

    def create_account(self, family_id: str, name: str, current_uid: str) -> Account:
        member = self.member_repo.get_by_uid(family_id, current_uid)
        if not member or member.role != "parent":
            raise BusinessRuleViolationException("parent_only", "Only parents can create accounts")
        return self.account_repo.create(family_id=family_id, name=name, balance=0)
```

### 3. Dependency Injection (`core/container.py`)

**責務**: 依存性の解決

- `injector` パッケージによる自動依存解決
- 本番: Firestore Repository をバインド
- テスト: `Injector` に Mock Repository を手動バインド

```python
# container.py
def create_injector() -> Injector:
    return Injector([FirestoreModule()])

# テスト時
injector = Injector([MockModule()])
service = injector.get(AccountService)  # Mock が自動注入される
```

### 4. GraphQL Schema / Resolvers (`api/graphql/`)

**責務**: HTTP → ビジネスロジックの橋渡し

- `schema.py`: Strawberry 型・ミューテーション定義、エラーハンドリング
- `resolvers.py`: Service を呼び出してドメインオブジェクト → GraphQL 型変換

エラーハンドリングは `_handle_domain_exceptions()` コンテキストマネージャーで統一管理：

```python
@contextmanager
def _handle_domain_exceptions():
    try:
        yield
    except ResourceNotFoundException as e:
        raise Exception(f"Resource not found: {e.message}") from e
    except BusinessRuleViolationException as e:
        raise Exception(f"Permission denied: {e.message}") from e
    except InsufficientBalanceException as e:
        raise Exception(f"Insufficient balance: {e.message}") from e
    except InvalidAmountException as e:
        raise Exception(f"Invalid amount: {e.message}") from e
    except DomainException as e:
        raise Exception(f"Domain error: {e.message}") from e

@strawberry.mutation
def deposit(self, info: Info, family_id: str, account_id: str, amount: int) -> TransactionType:
    current_uid = _require_auth(info)
    transaction_service = info.context["transaction_service"]
    with _handle_domain_exceptions():
        return resolvers.deposit(family_id, account_id, current_uid, amount, transaction_service)
```

### 5. 例外階層 (`core/exceptions.py`)

```
DomainException
├── ResourceNotFoundException     # リソースが見つからない
├── BusinessRuleViolationException # ビジネスルール違反（権限チェック等）
├── InsufficientBalanceException   # 残高不足
├── InvalidAmountException         # 金額バリデーション失敗
└── ValidationException            # 入力値バリデーション失敗
```

## テスト戦略

全テストは `tests/` 以下。Mock リポジトリを使って Firestore なしで実行可能。

```
tests/
├── graphql/    # GraphQL Schema の結合テスト（Strawberry の execute_sync 使用）
├── services/   # Service 層の単体テスト
└── repositories/ # Repository 層の単体テスト
```

```python
# Service テスト例
class TestAccountService:
    def test_create_account_as_child_fails(self, injector_with_mocks):
        service = injector_with_mocks.get(AccountService)
        with pytest.raises(BusinessRuleViolationException):
            service.create_account(family_id=FAMILY_ID, name="口座", current_uid=CHILD_UID)
```

## デプロイ構成

| コンポーネント | 環境 | 技術 |
|---|---|---|
| Backend | Cloud Run (asia-northeast1) | Python / FastAPI + Strawberry |
| Frontend | Cloud Run (asia-northeast1) | Next.js |
| DB / Auth / Storage | Firebase / GCP | Firestore, Firebase Auth, Firebase Storage |
| CI/CD | GitHub Actions | Cloud Build + Artifact Registry |
| シークレット管理 | GCP Secret Manager | — |


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

   - Firebase Auth との統合

3. **キャッシュ層の追加** (オプション)

   - CachedRepository の実装
   - Redis との統合

4. **エラーハンドリングの強化**
   - カスタム例外クラスの定義
   - GraphQL エラーレスポンスの統一
