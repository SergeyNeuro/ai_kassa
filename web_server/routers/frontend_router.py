# web_server/routers/frontend_router.py
import os
from datetime import timedelta, datetime, timezone

from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

# Пути к шаблонам (внутри контейнера)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # web_server/
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Настройки из .env
DEMO_LOGIN = os.getenv("DEMO_LOGIN", "demo")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "demo123")
COOKIE_NAME = os.getenv("COOKIE_NAME", "ai_kassa_auth")
JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", "120"))  # срок жизни куки

def _set_auth_cookie(response: RedirectResponse, value: str) -> None:
    expires = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRES_MIN)
    response.set_cookie(
        key=COOKIE_NAME,
        value=value,
        httponly=True,
        secure=False,          # поставь True при HTTPS
        samesite="lax",
        expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
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
async def login_submit(request: Request):
    form = await request.form()
    username = (form.get("username") or "").strip()
    password = (form.get("password") or "").strip()

    if username == DEMO_LOGIN and password == DEMO_PASSWORD:
        resp = RedirectResponse(url="/predict/upload", status_code=status.HTTP_302_FOUND)
        _set_auth_cookie(resp, value="demo-session")
        return resp

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



