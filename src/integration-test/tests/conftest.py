import pytest
import requests

URL = "http://localhost:8000"


@pytest.fixture
def service():
    assert requests.post(URL + "/auth/test_reset").status_code == 200

    assert requests.post(URL + "/job/test_reset").status_code == 200
    yield URL


def log_in(service, role):
    email = f"{role}@example.com"
    res = requests.post(service + "/auth/login", json={"email": email, "password": "secret"})
    assert res.status_code == 200
    assert res.json().get("token") is not None
    return {"Authorization": f"Bearer {res.json()['token']}"}


@pytest.fixture
def admin_token(service):
    yield log_in(service, "admin")


@pytest.fixture
def provider_token(service):
    yield log_in(service, "provider")


@pytest.fixture
def agent_token(service):
    yield log_in(service, "agent")
