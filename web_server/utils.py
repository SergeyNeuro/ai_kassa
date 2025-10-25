import datetime
import logging
from typing import Optional

import jwt

from config import JWT_SECRET

logger = logging.getLogger(f"app.{__name__}")


def generate_jwt_token(
    menu_id: int, kassa_id: int, expire: datetime.datetime
):
    """генерируем JWT токен для аутентификации"""

    return jwt.encode(
        {
            "menu_id": menu_id,
            "kassa_id": kassa_id,
            "exp": expire
        },
        JWT_SECRET,
        algorithm="HS256"
    )

def decode_token(string: str, algorithm="HS256") -> Optional[dict]:
    """Зашифровываем данные"""
    try:
        return jwt.decode(string, JWT_SECRET, algorithms=[algorithm])
    except jwt.exceptions.InvalidSignatureError:
        logger.error(f"Неверная сигнатура токена доступа")
        return None
    except jwt.exceptions.DecodeError:
        logger.error(f"Неверная расшифровка токена доступа")
        return None
    except jwt.ExpiredSignatureError:
        # потом поменять, что токен протух
        logger.warning(f"Токен протух: {string}")
        return None