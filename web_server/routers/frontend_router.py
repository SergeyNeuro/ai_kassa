# web_server/routers/frontend_router.py
import os
import datetime
import logging

from fastapi import APIRouter, Request, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from servises.auth_service import AuthObj
from utils import generate_jwt_token
from config import COOKIE_NAME, JWT_EXPIRES_MIN

logger = logging.getLogger(f"app.{__name__}")

router = APIRouter()

# Пути к шаблонам (внутри контейнера)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # web_server/
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def _set_auth_cookie(
        response: RedirectResponse,
        menu_id: int,
        kassa_id: int
) -> None:
    expire = datetime.datetime.now() + datetime.timedelta(minutes=JWT_EXPIRES_MIN)
    token = generate_jwt_token(menu_id=menu_id, kassa_id=kassa_id, expire=expire)

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=False,          # поставь True при HTTPS
        samesite="lax",
        expires=expire.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        max_age=JWT_EXPIRES_MIN * 60,
        path="/",
    )

def _is_authenticated(request: Request) -> bool:
    return bool(request.cookies.get(COOKIE_NAME))

@router.api_route("/logout", methods=["GET", "POST"], include_in_schema=False)
async def logout():
    resp = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    resp.delete_cookie(COOKIE_NAME, path="/")
    return resp

@router.get("/", response_class=HTMLResponse)
async def root_redirect():
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
async def login_submit(
        request: Request,
        auth_obj: AuthObj = Depends(AuthObj)
):
    try:
        form = await request.form()

        username = (form.get("username") or "").strip()
        password = (form.get("password") or "").strip()
        menu_id = int((form.get("menu_id") or "").strip())
        kassa_id = int((form.get("kassa_id") or "").strip())

        logger.info(f"Пришел запрос на аутентификации username: {username}, password: {password}, "
                    f"menu_id: {menu_id}, kassa_id: {kassa_id}")

        # проверяем аутентификацию
        check_auth = await auth_obj.for_test_auth(
            login=username, password=password, menu_id=int(menu_id), kassa_id=int(kassa_id)
        )
        logger.info(f"Результат аутентификации: {check_auth}")
        if not check_auth:
            raise

        resp = RedirectResponse(url="/predict/upload", status_code=status.HTTP_302_FOUND)
        _set_auth_cookie(resp, menu_id, kassa_id)
        return resp

    except Exception as _ex:
        logger.error(f"Ошибка при аутентификации: {_ex}")
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неверный логин или пароль"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

# ====== СТРАНИЦЫ ПРОДУКТА (фронт) ======
@router.get("/predict/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    if not _is_authenticated(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("upload.html", {"request": request})

@router.get("/predict/result", response_class=HTMLResponse)
async def result_page(request: Request):
    if not _is_authenticated(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("result.html", {"request": request})



