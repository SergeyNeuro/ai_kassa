import os
import logging
from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, HTTPException, Request, Response, Form, status

router = APIRouter(prefix="/api/auth", tags=["auth"])

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", 120))
COOKIE_NAME = os.getenv("COOKIE_NAME", "ai_kassa_auth")
DEMO_LOGIN = os.getenv("DEMO_LOGIN", "demo")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "demo123")


logger = logging.getLogger(f"app.{__name__}")


def create_jwt_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRES_MIN)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


@router.post("/login")
async def login(
        response: Response,
        username: str = Form(...),
        password: str = Form(...),
        menu_id: int = Form(...),
        kassa_id: int = Form(...)
):
    """Обработка формы входа"""
    logger.info(f"Пришел запрос на аутентификации username: {username}, password: {password}, "
                f"menu_id: {menu_id}, kassa_id: {kassa_id}")

    if username != DEMO_LOGIN or password != DEMO_PASSWORD:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    token = create_jwt_token(username)
    response = Response(status_code=status.HTTP_302_FOUND)
    response.headers["Location"] = "/dashboard"
    response.set_cookie(COOKIE_NAME, token, httponly=True, max_age=JWT_EXPIRES_MIN * 60)
    return response


@router.post("/logout")
async def logout(response: Response):
    """Выход из системы"""
    response = Response(status_code=status.HTTP_302_FOUND)
    response.headers["Location"] = "/login"
    response.delete_cookie(COOKIE_NAME)
    return response
