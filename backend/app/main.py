import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from app.api.applications import router as applications_router
from app.api.auth import router as auth_router
from app.api.jobs import router as jobs_router
from app.api.profiles import router as profiles_router
from app.api.resumes import router as resumes_router
from app.api.settings import router as settings_router
from app.api.tracker import router as tracker_router
from app.core.config import settings
from app.db.session import Base, engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting JobPilot...")
    Base.metadata.create_all(bind=engine)
    from app.db.session import SessionLocal
    from app.services.resume_service import TemplateService
    db = SessionLocal()
    try:
        TemplateService().seed_templates(db)
        logger.info("Database initialized and templates seeded.")
    finally:
        db.close()
    yield
    logger.info("Shutting down JobPilot.")


app = FastAPI(
    title="JobPilot - AI Job Search Copilot",
    description="An open-source AI-powered job search assistant built on DeepSeek",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:8001", "http://127.0.0.1:8000", "http://127.0.0.1:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RATE_LIMIT_WINDOW = settings.RATE_LIMIT_WINDOW
RATE_LIMIT_MAX_REQUESTS = settings.RATE_LIMIT_MAX_REQUESTS
rate_limit_store: dict[str, list[float]] = {}


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if not settings.RATE_LIMIT_ENABLED or request.url.path.startswith("/_next"):
        return await call_next(request)
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW

    timestamps = rate_limit_store.get(client_ip, [])
    timestamps = [t for t in timestamps if t > window_start]

    if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={"detail": f"Rate limit exceeded. Max {RATE_LIMIT_MAX_REQUESTS} requests per {RATE_LIMIT_WINDOW}s."},
        )

    timestamps.append(now)
    rate_limit_store[client_ip] = timestamps

    response = await call_next(request)
    return response


@app.middleware("http")
async def log_request_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    if request.url.path.startswith("/api"):
        logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration:.0f}ms)")
    return response


app.include_router(profiles_router)
app.include_router(resumes_router)
app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(settings_router)
app.include_router(tracker_router)
app.include_router(auth_router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}


FRONTEND_DIR = (Path(__file__).resolve().parent.parent.parent / "frontend" / "out").resolve()


def _resolve_frontend_path(full_path: str) -> Path | None:
    """Safely resolve a URL path to a file within FRONTEND_DIR. Returns None if path escapes."""
    if not full_path:
        return None
    sanitized = full_path.lstrip("/")
    if ".." in sanitized.split("/"):
        return None
    resolved = (FRONTEND_DIR / sanitized).resolve()
    if not str(resolved).startswith(str(FRONTEND_DIR)):
        return None
    if resolved.is_file():
        return resolved
    if resolved.is_dir() and (resolved / "index.html").exists():
        return resolved / "index.html"
    return None


if FRONTEND_DIR.exists():
    app.mount("/_next", StaticFiles(directory=FRONTEND_DIR / "_next"), name="next")

    @app.api_route("/{full_path:path}", methods=["GET", "HEAD"])
    async def serve_frontend(full_path: str, request: Request):
        file = _resolve_frontend_path(full_path)
        if file:
            resp = FileResponse(file)
            if request.method == "HEAD":
                return Response(headers=dict(resp.headers))
            return resp
        resp = FileResponse(FRONTEND_DIR / "index.html")
        if request.method == "HEAD":
            return Response(headers=dict(resp.headers))
        return resp

    @app.api_route("/", methods=["GET", "HEAD"])
    async def serve_root(request: Request):
        resp = FileResponse(FRONTEND_DIR / "index.html")
        if request.method == "HEAD":
            return Response(headers=dict(resp.headers))
        return resp


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
