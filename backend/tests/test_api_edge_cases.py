import os
import json
import pytest

os.environ["DATABASE_URL"] = "sqlite:///./test_jobpilot.db"
os.environ["JOBPILOT_SETTINGS_FILE"] = os.path.join(os.path.dirname(__file__), "..", "test_settings.json")
os.environ["JOBPILOT_SECRET_KEY_FILE"] = os.path.join(os.path.dirname(__file__), "..", "test_secret_key")
os.environ["RATE_LIMIT_ENABLED"] = "false"

from app.db.session import engine, Base
from app.db.models import Job
from app.db.session import SessionLocal


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture(scope="session")
def auth():
    r = client.post("/api/auth/register", json={"email": "edge@test.com", "password": "testpass"})
    if r.status_code == 409:
        r = client.post("/api/auth/login", json={"email": "edge@test.com", "password": "testpass"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


class TestHealthEndpoint:
    def test_health_ok(self):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestCORSMiddleware:
    def test_cors_headers_present(self):
        r = client.options("/api/health", headers={
            "Origin": "http://localhost:8000",
            "Access-Control-Request-Method": "GET",
        })
        assert r.status_code in [200, 405]

    def test_cors_origin_allowed(self):
        r = client.get("/api/health", headers={"Origin": "http://127.0.0.1:8001"})
        assert r.status_code == 200


class TestRateLimitingDisabled:
    def test_many_requests_pass(self):
        for _ in range(50):
            r = client.get("/api/health")
            assert r.status_code == 200


class TestFrontendServing:
    def test_root_serves_index(self):
        r = client.get("/")
        assert r.status_code == 200

    def test_spa_fallback(self):
        r = client.get("/nonexistent-page")
        assert r.status_code == 200

    def test_path_traversal_blocked(self):
        r = client.get("/../.env")
        assert r.status_code == 200
        assert b"DEEPSEEK" not in r.content


class TestAPIErrorHandling:
    def test_404_on_nonexistent_job(self, auth):
        r = client.get("/api/jobs/99999", headers=auth)
        assert r.status_code == 404

    def test_400_on_empty_jd_parse(self, auth):
        r = client.post("/api/jobs/parse", json={"jd_text": ""}, headers=auth)
        assert r.status_code == 400

    def test_validation_error(self, auth):
        r = client.post("/api/jobs/parse", json={}, headers=auth)
        assert r.status_code == 422

    def test_auth_required(self):
        r = client.get("/api/profiles")
        assert r.status_code == 401

    def test_invalid_token(self):
        r = client.get("/api/profiles", headers={"Authorization": "Bearer invalid"})
        assert r.status_code == 401


class TestTemplatesAPI:
    def test_list_templates(self, auth):
        r = client.get("/api/templates", headers=auth)
        assert r.status_code == 200
        templates = r.json()
        assert len(templates) == 3
        styles = [t["style"] for t in templates]
        assert "cn_tech" in styles


class TestSettingsEncrypted:
    def test_key_encrypted_in_storage(self):
        client.put("/api/settings/key", json={"api_key": "sk-test-unique-key-abc"})
        settings_path = os.path.join(os.path.dirname(__file__), "..", "test_settings.json")
        with open(settings_path, encoding="utf-8") as f:
            raw = json.load(f)
        assert "sk-test-unique-key" not in raw.get("DEEPSEEK_API_KEY", "")

    def test_masked_key_format(self):
        client.put("/api/settings/key", json={"api_key": "sk-abcdefghijklmnop"})
        r = client.get("/api/settings")
        masked = r.json()["masked_key"]
        assert masked.startswith("sk-")
        assert "*" in masked


class TestProfileEdgeCases:
    def test_update_nonexistent_education(self, auth):
        r = client.put("/api/profiles/education/99999", json={
            "school": "X", "degree": "Y", "major": "Z"
        }, headers=auth)
        assert r.status_code == 404

    def test_delete_nonexistent_experience(self, auth):
        r = client.delete("/api/profiles/experiences/99999", headers=auth)
        assert r.status_code == 404

    def test_parse_experience_empty_text(self, auth):
        r = client.post("/api/profiles/experiences/parse", json={
            "text": "", "experience_type": "project"
        }, headers=auth)
        assert r.status_code == 200

    def test_parse_experience_with_text(self, auth):
        r = client.post("/api/profiles/experiences/parse", json={
            "text": "在腾讯做了一个AI项目，使用Python和PyTorch", "experience_type": "internship"
        }, headers=auth)
        assert r.status_code == 200


class TestJobsEdgeCases:
    def test_batch_match_empty(self, auth):
        r = client.post("/api/jobs/batch-match", json={"job_ids": []}, headers=auth)
        assert r.status_code == 200
        assert r.json()["results"] == []

    def test_batch_match_nonexistent(self, auth):
        r = client.post("/api/jobs/batch-match", json={"job_ids": [99999]}, headers=auth)
        assert r.status_code == 200
        assert r.json()["results"] == []


class TestTracker:
    def test_empty_records(self, auth):
        r = client.get("/api/tracker/records", headers=auth)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_empty_analytics(self, auth):
        r = client.get("/api/tracker/analytics", headers=auth)
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 0

    def test_upsert_nonexistent_job(self, auth):
        r = client.post("/api/tracker/records/99999", json={"status": "applied"}, headers=auth)
        assert r.status_code == 404


class TestApplicationsEdgeCases:
    def test_generate_no_job(self, auth):
        r = client.post("/api/applications/generate", json={"job_id": 99999}, headers=auth)
        assert r.status_code == 404


class TestResumesEdgeCases:
    def test_generate_resume_nonexistent_job(self, auth):
        r = client.post("/api/resumes/generate", json={"job_id": 99999, "template_id": 1}, headers=auth)
        assert r.status_code == 404

    def test_list_resumes_empty(self, auth):
        r = client.get("/api/resumes", headers=auth)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_export_pdf_nonexistent(self, auth):
        r = client.post("/api/resumes/99999/export-pdf", headers=auth)
        assert r.status_code == 404


class TestOCRUpload:
    def test_non_image_extension(self, auth):
        r = client.post(
            "/api/assistant/ocr-upload",
            files={"file": ("document.pdf", b"pdf content", "application/pdf")},
            headers=auth,
        )
        assert r.status_code == 400

    def test_text_file(self, auth):
        r = client.post(
            "/api/assistant/ocr-upload",
            files={"file": ("readme.txt", b"hello", "text/plain")},
            headers=auth,
        )
        assert r.status_code == 400

    def test_oversized_file(self, auth):
        r = client.post(
            "/api/assistant/ocr-upload",
            files={"file": ("big.jpg", b"x" * (5 * 1024 * 1024 + 1), "image/jpeg")},
            headers=auth,
        )
        assert r.status_code == 413


class TestFormAssistEdgeCases:
    def test_empty_form_text(self, auth):
        r = client.post("/api/assistant/form", json={"form_text": ""}, headers=auth)
        assert r.status_code == 200
        data = r.json()
        assert "meaning" in data
        assert "needs_user_check" in data

    def test_form_with_job_context(self, auth):
        db = SessionLocal()
        job = Job(user_id=1, title="AI Intern", company="TestCo", raw_jd_text="test jd", parsed_jd={"title": "AI Intern"})
        db.add(job)
        db.commit()
        job_id = job.id
        db.close()

        r = client.post("/api/assistant/form", json={"form_text": "Why do you want this job?", "job_id": job_id}, headers=auth)
        assert r.status_code == 200

    def test_form_with_invalid_job_id(self, auth):
        r = client.post("/api/assistant/form", json={"form_text": "Test question", "job_id": 99999}, headers=auth)
        assert r.status_code == 200


class TestSearchDiscovery:
    def test_empty_search_strategy(self, auth):
        r = client.post("/api/discover/search-strategy", headers=auth)
        assert r.status_code == 200

    def test_search_empty_query(self, auth):
        r = client.post("/api/discover/search", json={"query": "", "max_results": 1}, headers=auth)
        assert r.status_code == 200
