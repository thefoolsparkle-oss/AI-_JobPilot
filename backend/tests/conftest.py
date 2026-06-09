import os
import pytest

os.environ["DATABASE_URL"] = "sqlite:///./test_jobpilot.db"
os.environ["JOBPILOT_SETTINGS_FILE"] = os.path.join(os.path.dirname(__file__), "..", "test_settings.json")
os.environ["JOBPILOT_SECRET_KEY_FILE"] = os.path.join(os.path.dirname(__file__), "..", "test_secret_key")
os.environ["RATE_LIMIT_ENABLED"] = "false"

from fastapi.testclient import TestClient
from app.main import app
from app.db.session import engine, Base, SessionLocal
from app.db.models import User, Profile
from app.auth import get_password_hash

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "test_jobpilot.db")
SETTINGS_FILE = os.environ["JOBPILOT_SETTINGS_FILE"]
SECRET_FILE = os.environ["JOBPILOT_SECRET_KEY_FILE"]
REAL_SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "settings.json")
REAL_SECRET_FILE = os.path.join(os.path.dirname(__file__), "..", ".secret_key")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")

TEST_EMAIL = "test@jobpilot.com"
TEST_PASSWORD = "testpass123"


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    real_settings_exists = os.path.exists(REAL_SETTINGS_FILE)
    real_secret_exists = os.path.exists(REAL_SECRET_FILE)
    Base.metadata.create_all(bind=engine)
    for f in [SETTINGS_FILE, SECRET_FILE]:
        if os.path.exists(f):
            os.remove(f)
    if os.path.isdir(UPLOAD_DIR):
        for name in os.listdir(UPLOAD_DIR):
            try:
                os.remove(os.path.join(UPLOAD_DIR, name))
            except OSError:
                pass
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    import time
    time.sleep(0.5)
    for f in [TEST_DB_PATH, SETTINGS_FILE, SECRET_FILE]:
        try:
            if os.path.exists(f):
                os.remove(f)
        except PermissionError:
            pass
    assert os.path.exists(REAL_SETTINGS_FILE) == real_settings_exists
    assert os.path.exists(REAL_SECRET_FILE) == real_secret_exists
    if os.path.isdir(UPLOAD_DIR):
        for name in os.listdir(UPLOAD_DIR):
            try:
                os.remove(os.path.join(UPLOAD_DIR, name))
            except OSError:
                pass


@pytest.fixture(scope="session")
def auth_headers():
    """Register test user and return auth headers."""
    client = TestClient(app)
    resp = client.post("/api/auth/register", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def authed_client(auth_headers):
    """Return a helper that makes requests with auth."""
    client = TestClient(app)

    class AuthedClient:
        def get(self, path, **kwargs):
            h = kwargs.pop("headers", {})
            h.update(auth_headers)
            return client.get(path, headers=h, **kwargs)

        def post(self, path, **kwargs):
            h = kwargs.pop("headers", {})
            h.update(auth_headers)
            return client.post(path, headers=h, **kwargs)

        def put(self, path, **kwargs):
            h = kwargs.pop("headers", {})
            h.update(auth_headers)
            return client.put(path, headers=h, **kwargs)

        def delete(self, path, **kwargs):
            h = kwargs.pop("headers", {})
            h.update(auth_headers)
            return client.delete(path, headers=h, **kwargs)

        def options(self, path, **kwargs):
            h = kwargs.pop("headers", {})
            h.update(auth_headers)
            return client.options(path, headers=h, **kwargs)

    return AuthedClient()
