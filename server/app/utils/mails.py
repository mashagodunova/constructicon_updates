from typing import Any

import emails  # type: ignore
from app.core import settings

from .templates import render


def send_email(
        email_to: str, subject: str = "", html: str = "",
        environment: dict[str, Any] | None = None
    ) -> None:
    environment = environment or {}

    message = emails.Message(
        subject=subject,
        html=html,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    # if settings.SMTP_TLS:
    #     smtp_options["tls"] = True
    # if settings.SMTP_USER:
    #     smtp_options["user"] = settings.SMTP_USER
    # if settings.SMTP_PASSWORD:
    #     smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    response.raise_if_needed()


def send_new_account_email(link: str, email: str, username: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    send_email(
        email_to=email,
        subject=subject,
        html=render('emails/new_account.html', link=link),
        environment={
            "project_name": settings.PROJECT_NAME,
            "email": email,
        },
    )
