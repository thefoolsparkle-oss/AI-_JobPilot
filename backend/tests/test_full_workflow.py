import os
import json
import pytest

os.environ["DATABASE_URL"] = "sqlite:///./test_jobpilot.db"
os.environ["JOBPILOT_SETTINGS_FILE"] = os.path.join(os.path.dirname(__file__), "..", "test_settings.json")
os.environ["JOBPILOT_SECRET_KEY_FILE"] = os.path.join(os.path.dirname(__file__), "..", "test_secret_key")
os.environ["RATE_LIMIT_ENABLED"] = "false"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_auth_register():
    r = client.post("/api/auth/register", json={"email": "flowtest@jobpilot.com", "password": "testtest"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_auth_login():
    r = client.post("/api/auth/login", json={"email": "flowtest@jobpilot.com", "password": "testtest"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_auth_register_duplicate():
    r = client.post("/api/auth/register", json={"email": "flowtest@jobpilot.com", "password": "testtest"})
    assert r.status_code == 409


def test_auth_login_wrong_password():
    r = client.post("/api/auth/login", json={"email": "flowtest@jobpilot.com", "password": "wrong"})
    assert r.status_code == 401


def test_auth_register_short_password():
    r = client.post("/api/auth/register", json={"email": "short@test.com", "password": "12345"})
    assert r.status_code == 400


def test_auth_me():
    r = client.post("/api/auth/login", json={"email": "flowtest@jobpilot.com", "password": "testtest"})
    token = r.json()["access_token"]
    r2 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert r2.json()["email"] == "flowtest@jobpilot.com"


def test_protected_route_no_auth():
    r = client.get("/api/profiles")
    assert r.status_code == 401


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
    auth = _login()
    r = client.get("/api/templates", headers=auth)
    assert r.status_code == 200
    assert len(r.json()) == 3


def test_profile_lifecycle():
    auth = _login()

    r = client.get("/api/profiles", headers=auth)
    assert r.status_code == 200

    r = client.put("/api/profiles", json={"name": "测试用户"}, headers=auth)
    assert r.status_code == 200
    assert r.json()["name"] == "测试用户"

    r = client.post("/api/profiles/education", json={
        "school": "测试大学", "degree": "本科", "major": "计算机",
        "start_date": "2022-09", "end_date": "2026-06"
    }, headers=auth)
    assert r.status_code == 200
    edu_id = r.json()["id"]

    r = client.get("/api/profiles", headers=auth)
    assert len(r.json()["education"]) == 1

    client.delete(f"/api/profiles/education/{edu_id}", headers=auth)

    r = client.post("/api/profiles/experiences", json={
        "experience_type": "project", "name": "Test Project", "organization": "个人",
        "facts": [{"content": "做了测试", "sort_order": 0}]
    }, headers=auth)
    assert r.status_code == 200
    exp_id = r.json()["id"]

    r = client.put(f"/api/profiles/experiences/{exp_id}", json={
        "experience_type": "project", "name": "Updated Project", "organization": "个人",
        "facts": []
    }, headers=auth)
    assert r.status_code == 200

    r = client.post("/api/profiles/skills", json={
        "name": "Python", "level": "advanced", "category": "programming"
    }, headers=auth)
    assert r.status_code == 200

    r = client.put("/api/profiles/preferences", json={
        "target_roles": ["AI实习生"], "preferred_locations": ["远程"], "remote_preference": "remote"
    }, headers=auth)
    assert r.status_code == 200


def test_jd_parse():
    auth = _login()
    r = client.post("/api/jobs/parse", json={"jd_text": "AI产品实习生 要求熟悉AI工具 每周4天"}, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert "parsed_jd" in data

    r = client.get(f"/api/jobs/{data['id']}", headers=auth)
    assert r.status_code == 200


def test_job_list():
    auth = _login()
    r = client.get("/api/jobs", headers=auth)
    assert r.status_code == 200


def test_job_delete_404():
    auth = _login()
    r = client.delete("/api/jobs/99999", headers=auth)
    assert r.status_code == 404


def test_resume_generate():
    auth = _login()
    r = client.post("/api/resumes/generate", json={"job_id": 1, "template_id": 1}, headers=auth)
    assert r.status_code in [200, 404]


def test_application_package():
    auth = _login()
    r = client.post("/api/applications/generate", json={"job_id": 1}, headers=auth)
    assert r.status_code in [200, 404]


def test_search_strategy():
    auth = _login()
    r = client.post("/api/discover/search-strategy", headers=auth)
    assert r.status_code == 200


def test_form_assistant():
    auth = _login()
    r = client.post("/api/assistant/form", json={"form_text": "请描述你的项目经历"}, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert "meaning" in data
    assert "suggestion" in data
    assert "needs_user_check" in data


def test_tracker():
    auth = _login()
    r = client.get("/api/tracker/records", headers=auth)
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
    settings_path = os.path.join(os.path.dirname(__file__), "..", "test_settings.json")
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
    settings_path = os.path.join(os.path.dirname(__file__), "..", "test_settings.json")
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump({"DEEPSEEK_API_KEY": base64.b64encode(legacy_key.encode()).decode()}, f)

    r = client.get("/api/settings")
    assert r.status_code == 200
    assert r.json()["has_key"] is True
    assert r.json()["masked_key"].startswith("sk-l")

    raw = json.loads(open(settings_path, encoding="utf-8").read())
    assert raw["DEEPSEEK_API_KEY"] != base64.b64encode(legacy_key.encode()).decode()


def test_search_execute():
    auth = _login()
    r = client.post("/api/discover/search", json={"query": "AI产品实习生", "max_results": 3}, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert "query" in data
    assert "results" in data
    assert isinstance(data["results"], list)


def test_full_search_strategy():
    auth = _login()
    r = client.post("/api/discover/search-all", headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert "queries" in data
    assert "results" in data


def test_ocr_upload_rejects_non_image():
    auth = _login()
    r = client.post(
        "/api/assistant/ocr-upload",
        files={"file": ("not-image.txt", b"hello", "text/plain")},
        headers=auth,
    )
    assert r.status_code == 400


def test_ocr_upload_uses_safe_filename(monkeypatch):
    auth = _login()
    from app.services.ocr_service import OCRService

    seen_paths = []

    def fake_extract(self, image_path: str) -> str:
        seen_paths.append(image_path)
        return "识别文本"

    monkeypatch.setattr(OCRService, "extract_text", fake_extract)
    r = client.post(
        "/api/assistant/ocr-upload",
        files={"file": ("../evil.png", b"fake image bytes", "image/png")},
        headers=auth,
    )
    assert r.status_code == 200
    assert r.json()["text"] == "识别文本"
    assert r.json()["filename"] == "evil.png"
    assert seen_paths
    assert ".." not in seen_paths[0]
    assert seen_paths[0].endswith(".png")


def test_user_isolation():
    r1 = client.post("/api/auth/register", json={"email": "user_a@test.com", "password": "testpass1"})
    t1 = r1.json()["access_token"]
    r2 = client.post("/api/auth/register", json={"email": "user_b@test.com", "password": "testpass2"})
    t2 = r2.json()["access_token"]

    h1 = {"Authorization": f"Bearer {t1}"}
    h2 = {"Authorization": f"Bearer {t2}"}

    client.put("/api/profiles", json={"name": "User A"}, headers=h1)
    client.put("/api/profiles", json={"name": "User B"}, headers=h2)

    p1 = client.get("/api/profiles", headers=h1).json()
    p2 = client.get("/api/profiles", headers=h2).json()
    assert p1["name"] == "User A"
    assert p2["name"] == "User B"

    client.post("/api/jobs/parse", json={"jd_text": "Job for A"}, headers=h1)
    client.post("/api/jobs/parse", json={"jd_text": "Job for B"}, headers=h2)

    jobs_a = client.get("/api/jobs", headers=h1).json()
    jobs_b = client.get("/api/jobs", headers=h2).json()
    assert len(jobs_a) == 1
    assert len(jobs_b) == 1


def _login(email="flowtest@jobpilot.com", password="testtest"):
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    if r.status_code != 200:
        client.post("/api/auth/register", json={"email": email, "password": password})
        r = client.post("/api/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
