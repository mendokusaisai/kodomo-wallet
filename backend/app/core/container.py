"""
'injector'パッケージを使用した依存性注入コンテナ

Firestore リポジトリを使用するクリーンな DI 実装。
"""

from injector import Binder, Injector, Module, singleton

from app.repositories.firestore import (
    FirestoreAccountRepository,
    FirestoreChildInviteRepository,
    FirestoreFamilyMemberRepository,
    FirestoreFamilyRepository,
    FirestoreParentInviteRepository,
    FirestoreTransactionRepository,
)
from app.repositories.interfaces import (
    AccountRepository,
    ChildInviteRepository,
    FamilyMemberRepository,
    FamilyRepository,
    ParentInviteRepository,
    TransactionRepository,
)
from app.services.mailer import ConsoleMailer, Mailer


class RepositoryModule(Module):
    """Firestore リポジトリのバインディングを設定するモジュール"""

    def configure(self, binder: Binder) -> None:
        """Repository インターフェースを Firestore 実装にバインド"""
        binder.bind(FamilyRepository, to=FirestoreFamilyRepository, scope=singleton)
        binder.bind(FamilyMemberRepository, to=FirestoreFamilyMemberRepository, scope=singleton)
        binder.bind(AccountRepository, to=FirestoreAccountRepository, scope=singleton)
        binder.bind(TransactionRepository, to=FirestoreTransactionRepository, scope=singleton)
        binder.bind(ParentInviteRepository, to=FirestoreParentInviteRepository, scope=singleton)
        binder.bind(ChildInviteRepository, to=FirestoreChildInviteRepository, scope=singleton)
        binder.bind(Mailer, to=ConsoleMailer(), scope=singleton)


def create_injector() -> Injector:
    """設定済みの Injector インスタンスを作成します。"""
    return Injector([RepositoryModule()])

