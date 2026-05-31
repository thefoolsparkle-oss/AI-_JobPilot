from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.session import engine, Base
from app.api.profiles import router as profiles_router
from app.api.resumes import router as resumes_router
from app.api.jobs import router as jobs_router
from app.api.applications import router as applications_router
from app.api.settings import router as settings_router
from app.api.tracker import router as tracker_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="JobPilot - AI Job Search Copilot",
    description="An open-source AI-powered job search assistant built on DeepSeek",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(profiles_router)
app.include_router(resumes_router)
app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(settings_router)
app.include_router(tracker_router)


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
