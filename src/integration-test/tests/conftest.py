import pytest
import requests

URL = "http://localhost:8000"

JOB_INFO = {
        "pickup_at": "Herrengasse 10, 8010 Graz",
        "deliver_at": "Inffeldgasse 16a, 8010 Graz",
        "description": "1x Pizza Hawaii"
    }



@pytest.fixture
def service():
    assert requests.post(URL + "/auth/test_reset").status_code == 200

    assert requests.post(URL + "/job/test_reset").status_code == 200
    assert requests.post(URL + "/geo/test_reset").status_code == 200
    assert requests.post(URL + "/agent/test_reset").status_code == 200
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

@pytest.fixture
def created_job(service, provider_token):
    res = requests.post(service + "/job", json=JOB_INFO, headers=provider_token)
    assert res.status_code == 201
    location = res.headers.get("Location")

    res = requests.get(location, headers=provider_token)
    assert res.status_code == 200
    assert res.json().get("job_id") is not None
    yield res.json()["job_id"]
