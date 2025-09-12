from fastapi import FastAPI
from app.api.routers import api_router
from app.middleware.auto_refresh import auto_refresh_token_middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.middleware.logging import LoggingMiddleware
import app.logging_config  # to initialize logging config

app = FastAPI(title="PhilateList")

app.add_middleware(LoggingMiddleware)

app.middleware("http")(auto_refresh_token_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],  # Разрешить все домены (настройте правильно для продакшена!)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы
    allow_headers=["*"],  # Разрешить все заголовки
)

static_path = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

app.include_router(api_router, prefix="/api")
