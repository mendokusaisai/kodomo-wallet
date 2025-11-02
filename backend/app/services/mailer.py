"""
メール送信のスタブ実装。

本番のメールプロバイダ（SendGrid/Resend等）に置き換え可能な薄い抽象。
現在はコンソールに送信内容をログ出力するだけです。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class Mailer:
    """メール送信のインターフェース（抽象）"""

    def send_parent_invite(
        self, to_email: str, invite_link: str, *, inviter_name: str, child_name: str
    ) -> None:  # noqa: D401 - simple stub
        """親招待メールを送信する（スタブ）"""
        raise NotImplementedError


@dataclass
class ConsoleMailer(Mailer):
    """コンソールにログ出力するだけのスタブ実装"""

    def send_parent_invite(
        self, to_email: str, invite_link: str, *, inviter_name: str, child_name: str
    ) -> None:
        subject = "【こどもウォレット】親アカウント招待"
        body = (
            f"{inviter_name} さんが {child_name} さんの保護者としてあなたを招待しました。\n"
            f"以下のリンクから受け付けてください（7日間有効）：\n{invite_link}"
        )
        logger.info("[MAIL:stub] to=%s subject=%s\n%s", to_email, subject, body)
