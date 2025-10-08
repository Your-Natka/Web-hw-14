"""
Модуль `mailer.py`

Відповідає за надсилання службових електронних листів:
- підтвердження електронної пошти користувача після реєстрації;
- посилання для скидання пароля.

Використовується SMTP-сервер (наприклад, MailHog у середовищі розробки).
"""

import os
from email.message import EmailMessage
import smtplib
from urllib.parse import quote

# ---------- Конфігурація SMTP ----------
SMTP_HOST = os.getenv("SMTP_HOST", "mailhog")
"""str: Хост SMTP-сервера (за замовчуванням — mailhog)."""

SMTP_PORT = int(os.getenv("SMTP_PORT", 1025))
"""int: Порт SMTP-сервера (MailHog працює на 1025)."""

FROM_EMAIL = os.getenv("FROM_EMAIL", "no-reply@example.com")
"""str: Адреса відправника для службових листів."""

APP_HOST = os.getenv("APP_HOST", "http://localhost:8000")
"""str: Базова URL-адреса бекенду для побудови посилань (verify/reset)."""

# ---------- Функції для відправлення листів ----------

def send_verification_email(to_email: str, token: str):
    """
    Надсилає лист із посиланням для підтвердження електронної пошти.

    Args:
        to_email (str): Адреса одержувача.
        token (str): Токен підтвердження (JWT), який додається в URL.

    Формує посилання виду:
        ``http://localhost:8000/auth/verify?token=...``

    Після переходу користувач підтверджує свою електронну адресу.
    """
    verify_link = f"{APP_HOST}/auth/verify?token={quote(token)}"
    msg = EmailMessage()
    msg["Subject"] = "Verify your email"
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(f"Click to verify: {verify_link}")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.send_message(msg)

def send_reset_email(to_email: str, token: str):
    """
    Надсилає лист із посиланням для скидання пароля користувача.

    Args:
        to_email (str): Електронна адреса користувача.
        token (str): JWT-токен для підтвердження операції скидання пароля.

    Формує посилання виду:
        ``http://localhost:8000/auth/reset-password?token=...``

    Після переходу користувач може задати новий пароль.
    """
    reset_link = f"{APP_HOST}/auth/reset-password?token={token}"
    msg = EmailMessage()
    msg["Subject"] = "Reset your password"
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(f"Click to reset your password: {reset_link}")
    
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.send_message(msg)