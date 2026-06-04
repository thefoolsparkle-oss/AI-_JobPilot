import os
import pytest

os.environ["DATABASE_URL"] = "sqlite:///./test_jobpilot.db"
os.environ["JOBPILOT_SETTINGS_FILE"] = os.path.join(os.path.dirname(__file__), "..", "test_settings.json")
os.environ["JOBPILOT_SECRET_KEY_FILE"] = os.path.join(os.path.dirname(__file__), "..", "test_secret_key")

from fastapi.testclient import TestClient
from app.main import app
from app.db.session import engine, Base

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "test_jobpilot.db")
SETTINGS_FILE = os.environ["JOBPILOT_SETTINGS_FILE"]
SECRET_FILE = os.environ["JOBPILOT_SECRET_KEY_FILE"]
REAL_SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "settings.json")
REAL_SECRET_FILE = os.path.join(os.path.dirname(__file__), "..", ".secret_key")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")


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


client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_frontend_root():
    r = client.get("/")
    assert r.status_code == 200
    assert b"JobPilot" in r.content


def test_frontend_pages():
    pages = ["/profile/", "/templates/", "/jobs/parse/", "/jobs/match/",
             "/resumes/", "/applications/", "/assistant/", "/tracker/", "/settings/"]
    for p in pages:
        r = client.get(p)
        assert r.status_code == 200, f"Page {p} returned {r.status_code}"


def test_templates_api():
    r = client.get("/api/templates")
    assert r.status_code == 200
    assert len(r.json()) == 3


def test_profile_lifecycle():
    r = client.get("/api/profiles")
    assert r.status_code == 200

    r = client.put("/api/profiles", json={"name": "测试用户"})
    assert r.status_code == 200
    assert r.json()["name"] == "测试用户"

    r = client.post("/api/profiles/education", json={
        "school": "测试大学", "degree": "本科", "major": "计算机",
        "start_date": "2022-09", "end_date": "2026-06"
    })
    assert r.status_code == 200
    edu_id = r.json()["id"]

    r = client.get("/api/profiles")
    assert len(r.json()["education"]) == 1

    client.delete(f"/api/profiles/education/{edu_id}")

    r = client.post("/api/profiles/experiences", json={
        "experience_type": "project", "name": "Test Project", "organization": "个人",
        "facts": [{"content": "做了测试", "sort_order": 0}]
    })
    assert r.status_code == 200
    exp_id = r.json()["id"]

    r = client.put(f"/api/profiles/experiences/{exp_id}", json={
        "experience_type": "project", "name": "Updated Project", "organization": "个人",
        "facts": []
    })
    assert r.status_code == 200

    r = client.post("/api/profiles/skills", json={
        "name": "Python", "level": "advanced", "category": "programming"
    })
    assert r.status_code == 200

    r = client.put("/api/profiles/preferences", json={
        "target_roles": ["AI实习生"], "preferred_locations": ["远程"], "remote_preference": "remote"
    })
    assert r.status_code == 200


def test_jd_parse_no_key():
    r = client.post("/api/jobs/parse", json={"jd_text": "AI产品实习生 要求熟悉AI工具 每周4天"})
    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert "parsed_jd" in data

    r = client.get(f"/api/jobs/{data['id']}")
    assert r.status_code == 200


def test_job_list():
    r = client.get("/api/jobs")
    assert r.status_code == 200


def test_job_delete_404():
    r = client.delete("/api/jobs/99999")
    assert r.status_code == 404


def test_resume_generate_no_key():
    r = client.post("/api/resumes/generate", json={"job_id": 1, "template_id": 1})
    assert r.status_code in [200, 404]


def test_application_package_no_key():
    r = client.post("/api/applications/generate", json={"job_id": 1})
    assert r.status_code in [200, 404]


def test_search_strategy():
    r = client.post("/api/discover/search-strategy")
    assert r.status_code == 200


def test_form_assistant():
    r = client.post("/api/assistant/form", json={"form_text": "请描述你的项目经历"})
    assert r.status_code == 200
    data = r.json()
    assert "meaning" in data
    assert "suggestion" in data
    assert "needs_user_check" in data


def test_tracker():
    r = client.get("/api/tracker/records")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_settings_flow():
    r = client.get("/api/settings")
    assert r.status_code == 200
    assert r.json()["has_key"] is False

    r = client.put("/api/settings/key", json={"api_key": "sk-test12345678"})
    assert r.status_code == 200

    r = client.get("/api/settings")
    assert r.status_code == 200
    assert r.json()["has_key"] is True
    masked = r.json()["masked_key"]
    assert masked.startswith("sk-t")
    assert "test" not in masked.lower()


def test_settings_fernet_encryption():
    client.put("/api/settings/key", json={"api_key": "sk-my-real-key-123"})
    import json
    settings_path = SETTINGS_FILE
    if os.path.exists(settings_path):
        raw = json.loads(open(settings_path, encoding="utf-8").read())
        encrypted = raw.get("DEEPSEEK_API_KEY", "")
        assert "sk-my-real-key" not in encrypted

    r = client.get("/api/settings")
    assert r.json()["masked_key"].startswith("sk-")


def test_settings_base64_migration():
    import base64
    import json

    legacy_key = "sk-legacy-key-123"
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({"DEEPSEEK_API_KEY": base64.b64encode(legacy_key.encode()).decode()}, f)

    r = client.get("/api/settings")
    assert r.status_code == 200
    assert r.json()["has_key"] is True
    assert r.json()["masked_key"].startswith("sk-l")

    raw = json.loads(open(SETTINGS_FILE, encoding="utf-8").read())
    assert raw["DEEPSEEK_API_KEY"] != base64.b64encode(legacy_key.encode()).decode()


def test_search_execute():
    r = client.post("/api/discover/search", json={"query": "AI产品实习生", "max_results": 3})
    assert r.status_code == 200
    data = r.json()
    assert "query" in data
    assert "results" in data
    assert isinstance(data["results"], list)


def test_full_search_strategy():
    r = client.post("/api/discover/search-all")
    assert r.status_code == 200
    data = r.json()
    assert "queries" in data
    assert "results" in data


def test_ocr_upload_rejects_non_image():
    r = client.post(
        "/api/assistant/ocr-upload",
        files={"file": ("not-image.txt", b"hello", "text/plain")},
    )
    assert r.status_code == 400


def test_ocr_upload_uses_safe_filename(monkeypatch):
    from app.services.ocr_service import OCRService

    seen_paths = []

    def fake_extract(self, image_path: str) -> str:
        seen_paths.append(image_path)
        return "识别文本"

    monkeypatch.setattr(OCRService, "extract_text", fake_extract)
    r = client.post(
        "/api/assistant/ocr-upload",
        files={"file": ("../evil.png", b"fake image bytes", "image/png")},
    )
    assert r.status_code == 200
    assert r.json()["text"] == "识别文本"
    assert r.json()["filename"] == "evil.png"
    assert seen_paths
    assert ".." not in seen_paths[0]
    assert seen_paths[0].endswith(".png")
