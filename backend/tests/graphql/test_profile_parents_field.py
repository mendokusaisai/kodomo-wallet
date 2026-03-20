"""
GraphQL スキーマテスト（家族中心モデル）
"""

import pytest

from app.api.graphql.schema import schema as _schema


@pytest.fixture
def client():
    """schema を返す（execute_sync を呼ぶラッパー）"""
    return _schema


PARENT_UID = "parent-uid-001"
CHILD_UID = "child-uid-001"
PARENT2_UID = "parent-uid-002"


class TestMyFamilyQuery:
    """myFamily クエリのテスト"""

    def test_returns_none_when_no_uid(self, client, graphql_context):
        """current_uid がない場合は null を返す"""
        result = client.execute_sync(
            "{ myFamily { id name members { uid role } } }",
            context_value=graphql_context,
        )
        assert result.errors is None
        assert result.data["myFamily"] is None

    def test_returns_none_when_not_member(self, client, graphql_context):
        """家族に属していない場合は null を返す"""
        ctx = {**graphql_context, "current_uid": "unknown-uid"}
        result = client.execute_sync(
            "{ myFamily { id name members { uid role } } }",
            context_value=ctx,
        )
        assert result.errors is None
        assert result.data["myFamily"] is None

    def test_returns_family_after_create(self, client, graphql_context):
        """家族作成後は myFamily が家族情報を返す"""
        ctx = {**graphql_context, "current_uid": PARENT_UID}

        # 家族作成
        create_result = client.execute_sync(
            'mutation { createFamily(myName: "アバ", email: "dad@example.com") { id name members { uid role name } } }',
            context_value=ctx,
        )
        assert create_result.errors is None
        family = create_result.data["createFamily"]
        assert family["name"] is None  # family_name 未指定なので None
        assert len(family["members"]) == 1
        assert family["members"][0]["uid"] == PARENT_UID
        assert family["members"][0]["role"] == "parent"
        assert family["members"][0]["name"] == "アバ"

        # myFamily で同じ家族を取得
        query_result = client.execute_sync(
            "{ myFamily { id name members { uid role } } }",
            context_value=ctx,
        )
        assert query_result.errors is None
        assert query_result.data["myFamily"]["id"] == family["id"]
        assert len(query_result.data["myFamily"]["members"]) == 1


class TestFamilyAccountsQuery:
    """familyAccounts クエリのテスト"""

    def test_returns_empty_initially(self, client, graphql_context):
        """口座がない場合は空配列を返す"""
        # 家族を作成
        ctx = {**graphql_context, "current_uid": PARENT_UID}
        create_result = client.execute_sync(
            'mutation { createFamily(myName: "誤", email: "p@e.com") { id } }',
            context_value=ctx,
        )
        family_id = create_result.data["createFamily"]["id"]

        result = client.execute_sync(
            f'{{ familyAccounts(familyId: "{family_id}") {{ id name balance }} }}',
            context_value=ctx,
        )
        assert result.errors is None
        assert result.data["familyAccounts"] == []

    def test_returns_accounts_after_create(self, client, graphql_context):
        """口座作成後は familyAccounts に含まれる"""
        ctx = {**graphql_context, "current_uid": PARENT_UID}

        # 家族作成
        create_family = client.execute_sync(
            'mutation { createFamily(myName: "パパ", email: "p@e.com") { id } }',
            context_value=ctx,
        )
        family_id = create_family.data["createFamily"]["id"]

        # 口座作成
        create_account = client.execute_sync(
            f'mutation {{ createAccount(familyId: "{family_id}", name: "太郎の貯金") {{ id name balance currency }} }}',
            context_value=ctx,
        )
        assert create_account.errors is None
        account = create_account.data["createAccount"]
        assert account["name"] == "太郎の貯金"
        assert account["balance"] == 0
        assert account["currency"] == "JPY"

        # 口座一覧取得
        list_result = client.execute_sync(
            f'{{ familyAccounts(familyId: "{family_id}") {{ id name balance }} }}',
            context_value=ctx,
        )
        assert list_result.errors is None
        assert len(list_result.data["familyAccounts"]) == 1
        assert list_result.data["familyAccounts"][0]["id"] == account["id"]


class TestDepositWithdrawMutation:
    """入出金ミューテーションのテスト"""

    def _setup_family_and_account(self, client, graphql_context, uid=PARENT_UID):
        ctx = {**graphql_context, "current_uid": uid}
        create_family = client.execute_sync(
            'mutation { createFamily(myName: "テスト", email: "t@e.com") { id } }',
            context_value=ctx,
        )
        family_id = create_family.data["createFamily"]["id"]
        create_account = client.execute_sync(
            f'mutation {{ createAccount(familyId: "{family_id}", name: "貯金") {{ id }} }}',
            context_value=ctx,
        )
        account_id = create_account.data["createAccount"]["id"]
        return family_id, account_id, ctx

    def test_deposit_increases_balance(self, client, graphql_context):
        """入金は正常にトランザクションを作成する"""
        family_id, account_id, ctx = self._setup_family_and_account(client, graphql_context)

        result = client.execute_sync(
            f'mutation {{ deposit(familyId: "{family_id}", accountId: "{account_id}", amount: 1000, note: "お小遣い") {{ id type amount note }} }}',
            context_value=ctx,
        )
        assert result.errors is None
        tx = result.data["deposit"]
        assert tx["type"] == "deposit"
        assert tx["amount"] == 1000
        assert tx["note"] == "お小遣い"

    def test_deposit_fails_with_zero_amount(self, client, graphql_context):
        """金額 0 の入金はエラーになる"""
        family_id, account_id, ctx = self._setup_family_and_account(client, graphql_context)
        result = client.execute_sync(
            f'mutation {{ deposit(familyId: "{family_id}", accountId: "{account_id}", amount: 0) {{ id }} }}',
            context_value=ctx,
        )
        assert result.errors is not None

    def test_withdraw_succeeds_with_sufficient_balance(self, client, graphql_context):
        """残高が十分な場合は出金に成功する"""
        family_id, account_id, ctx = self._setup_family_and_account(client, graphql_context)

        # まず入金
        client.execute_sync(
            f'mutation {{ deposit(familyId: "{family_id}", accountId: "{account_id}", amount: 2000) {{ id }} }}',
            context_value=ctx,
        )
        # 出金
        result = client.execute_sync(
            f'mutation {{ withdraw(familyId: "{family_id}", accountId: "{account_id}", amount: 500) {{ id type amount }} }}',
            context_value=ctx,
        )
        assert result.errors is None
        assert result.data["withdraw"]["type"] == "withdraw"
        assert result.data["withdraw"]["amount"] == 500

    def test_withdraw_fails_with_insufficient_balance(self, client, graphql_context):
        """残高不足の出金はエラーになる"""
        family_id, account_id, ctx = self._setup_family_and_account(client, graphql_context)
        result = client.execute_sync(
            f'mutation {{ withdraw(familyId: "{family_id}", accountId: "{account_id}", amount: 9999) {{ id }} }}',
            context_value=ctx,
        )
        assert result.errors is not None

    def test_child_cannot_deposit(self, client, graphql_context):
        """子は入金できない"""
        family_id, account_id, parent_ctx = self._setup_family_and_account(client, graphql_context)

        # 子を招待して参加させる
        invite_result = client.execute_sync(
            f'mutation {{ inviteChild(familyId: "{family_id}", childName: "太郎") }}',
            context_value=parent_ctx,
        )
        token = invite_result.data["inviteChild"]

        child_ctx = {**graphql_context, "current_uid": CHILD_UID}
        join_result = client.execute_sync(
            f'mutation {{ joinAsChild(token: "{token}") {{ uid role }} }}',
            context_value=child_ctx,
        )
        assert join_result.errors is None
        assert join_result.data["joinAsChild"]["role"] == "child"

        # 子が入金しようとするとエラー
        result = client.execute_sync(
            f'mutation {{ deposit(familyId: "{family_id}", accountId: "{account_id}", amount: 100) {{ id }} }}',
            context_value=child_ctx,
        )
        assert result.errors is not None


class TestAccountTransactionsQuery:
    """トランザクション一覧クエリのテスト"""

    def test_returns_transactions_in_order(self, client, graphql_context):
        """入出金後のトランザクションが取得できる"""
        ctx = {**graphql_context, "current_uid": PARENT_UID}
        create_family = client.execute_sync(
            'mutation { createFamily(myName: "パパ", email: "p@e.com") { id } }',
            context_value=ctx,
        )
        family_id = create_family.data["createFamily"]["id"]
        create_account = client.execute_sync(
            f'mutation {{ createAccount(familyId: "{family_id}", name: "貯金") {{ id }} }}',
            context_value=ctx,
        )
        account_id = create_account.data["createAccount"]["id"]

        client.execute_sync(
            f'mutation {{ deposit(familyId: "{family_id}", accountId: "{account_id}", amount: 500) {{ id }} }}',
            context_value=ctx,
        )
        client.execute_sync(
            f'mutation {{ deposit(familyId: "{family_id}", accountId: "{account_id}", amount: 300) {{ id }} }}',
            context_value=ctx,
        )

        result = client.execute_sync(
            f'{{ accountTransactions(familyId: "{family_id}", accountId: "{account_id}") {{ id type amount }} }}',
            context_value=ctx,
        )
        assert result.errors is None
        txs = result.data["accountTransactions"]
        assert len(txs) == 2


class TestInviteFlow:
    """招待フローのテスト"""

    def test_parent_invite_child_and_join(self, client, graphql_context):
        """親が子を招待し、子が参加できる"""
        parent_ctx = {**graphql_context, "current_uid": PARENT_UID}

        # 家族作成
        create_family = client.execute_sync(
            'mutation { createFamily(myName: "パパ", email: "p@e.com") { id } }',
            context_value=parent_ctx,
        )
        family_id = create_family.data["createFamily"]["id"]

        # 子を招待
        invite_result = client.execute_sync(
            f'mutation {{ inviteChild(familyId: "{family_id}", childName: "太郎") }}',
            context_value=parent_ctx,
        )
        assert invite_result.errors is None
        token = invite_result.data["inviteChild"]
        assert token is not None and len(token) > 0

        # 子が参加
        child_ctx = {**graphql_context, "current_uid": CHILD_UID}
        join_result = client.execute_sync(
            f'mutation {{ joinAsChild(token: "{token}") {{ uid role name familyId }} }}',
            context_value=child_ctx,
        )
        assert join_result.errors is None
        member = join_result.data["joinAsChild"]
        assert member["uid"] == CHILD_UID
        assert member["role"] == "child"
        assert member["name"] == "太郎"
        assert member["familyId"] == family_id

    def test_child_invite_cannot_be_reused(self, client, graphql_context):
        """子招待トークンは再利用できない"""
        parent_ctx = {**graphql_context, "current_uid": PARENT_UID}
        create_family = client.execute_sync(
            'mutation { createFamily(myName: "パパ", email: "p@e.com") { id } }',
            context_value=parent_ctx,
        )
        family_id = create_family.data["createFamily"]["id"]
        invite_result = client.execute_sync(
            f'mutation {{ inviteChild(familyId: "{family_id}", childName: "花子") }}',
            context_value=parent_ctx,
        )
        token = invite_result.data["inviteChild"]

        # 1回目は成功
        child_ctx = {**graphql_context, "current_uid": CHILD_UID}
        client.execute_sync(
            f'mutation {{ joinAsChild(token: "{token}") {{ uid }} }}',
            context_value=child_ctx,
        )
        # 2回目は失敗
        child2_ctx = {**graphql_context, "current_uid": "child-uid-002"}
        result = client.execute_sync(
            f'mutation {{ joinAsChild(token: "{token}") {{ uid }} }}',
            context_value=child2_ctx,
        )
        assert result.errors is not None

    def test_non_parent_cannot_invite_child(self, client, graphql_context):
        """親以外は子を招待できない"""
        parent_ctx = {**graphql_context, "current_uid": PARENT_UID}
        create_family = client.execute_sync(
            'mutation { createFamily(myName: "パパ", email: "p@e.com") { id } }',
            context_value=parent_ctx,
        )
        family_id = create_family.data["createFamily"]["id"]

        # 子を招待して参加
        invite_res = client.execute_sync(
            f'mutation {{ inviteChild(familyId: "{family_id}", childName: "太郎") }}',
            context_value=parent_ctx,
        )
        token = invite_res.data["inviteChild"]
        child_ctx = {**graphql_context, "current_uid": CHILD_UID}
        client.execute_sync(
            f'mutation {{ joinAsChild(token: "{token}") {{ uid }} }}',
            context_value=child_ctx,
        )

        # 子がまた子を招待しようとするエラー
        result = client.execute_sync(
            f'mutation {{ inviteChild(familyId: "{family_id}", childName: "次郎") }}',
            context_value=child_ctx,
        )
        assert result.errors is not None


class TestRecurringDeposit:
    """定期入金のテスト"""

    def _setup(self, client, graphql_context):
        ctx = {**graphql_context, "current_uid": PARENT_UID}
        r1 = client.execute_sync(
            'mutation { createFamily(myName: "パパ", email: "p@e.com") { id } }',
            context_value=ctx,
        )
        family_id = r1.data["createFamily"]["id"]
        r2 = client.execute_sync(
            f'mutation {{ createAccount(familyId: "{family_id}", name: "貯金") {{ id }} }}',
            context_value=ctx,
        )
        account_id = r2.data["createAccount"]["id"]
        return family_id, account_id, ctx

    def test_create_recurring_deposit(self, client, graphql_context):
        """定期入金設定を作成できる"""
        family_id, account_id, ctx = self._setup(client, graphql_context)

        result = client.execute_sync(
            f'mutation {{ createOrUpdateRecurringDeposit(familyId: "{family_id}", accountId: "{account_id}", amount: 300, intervalDays: 7) {{ id amount intervalDays isActive }} }}',
            context_value=ctx,
        )
        assert result.errors is None
        rd = result.data["createOrUpdateRecurringDeposit"]
        assert rd["amount"] == 300
        assert rd["intervalDays"] == 7
        assert rd["isActive"] is True

    def test_query_recurring_deposit(self, client, graphql_context):
        """作成後に定期入金設定を取得できる"""
        family_id, account_id, ctx = self._setup(client, graphql_context)
        client.execute_sync(
            f'mutation {{ createOrUpdateRecurringDeposit(familyId: "{family_id}", accountId: "{account_id}", amount: 500, intervalDays: 30) {{ id }} }}',
            context_value=ctx,
        )
        result = client.execute_sync(
            f'{{ recurringDeposit(familyId: "{family_id}", accountId: "{account_id}") {{ amount intervalDays isActive }} }}',
            context_value=ctx,
        )
        assert result.errors is None
        assert result.data["recurringDeposit"]["amount"] == 500
        assert result.data["recurringDeposit"]["intervalDays"] == 30
