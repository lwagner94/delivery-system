import requests

standard_job_info = {
        "pickup_at": "Herrengasse 10, 8010 Graz",
        "deliver_at": "Inffeldgasse 16a, 8010 Graz",
        "description": "1x Pizza Hawaii"
    }


def test_create_job(service, provider_token):
    res = requests.post(service + "/job", json=standard_job_info, headers=provider_token)
    assert res.status_code == 201
    location = res.headers.get("Location")

    res = requests.get(location, headers=provider_token)
    assert res.status_code == 200


def test_create_job_wrong_role(service, agent_token):
    res = requests.post(service + "/job", json=standard_job_info, headers=agent_token)
    assert res.status_code == 403


def test_create_job_not_logged_in(service, agent_token):
    res = requests.post(service + "/job", json=standard_job_info)
    assert res.status_code == 401