from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_run_endpoint_minimal(monkeypatch):
    # monkeypatch requests.get to return a simple pdf-like text bytes
    class DummyResp:
        status_code = 200
        content = b"Sample policy text about knee surgery. This policy covers knee surgery after 24 months waiting."
        def raise_for_status(self): pass
    import app.api.routes as routes
    def fake_get(url, timeout=20):
        return DummyResp()
    monkeypatch.setattr("requests.get", fake_get)
    payload = {
        "documents": "http://example.com/sample.pdf",
        "questions": ["Does this policy cover knee surgery, and what are the conditions?"]
    }
    r = client.post("/api/v1/hackrx/run", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "answers" in data
    assert len(data["answers"]) == 1
