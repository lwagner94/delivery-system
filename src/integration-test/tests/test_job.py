import requests
from copy import copy

from requests.api import head

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

def test_claim(service, created_job, agent_token, provider_token):
    res = requests.get(service + "/auth/user/self", headers=agent_token)
    agent_id = res.json()["id"]
    res = requests.get(service + "/auth/user/self", headers=provider_token)
    provider_id = res.json()["id"]

    res = requests.get(service + "/job/" + created_job, headers=provider_token)
    assert res.status_code == 200
    assert res.json()["job_id"] == created_job
    assert res.json()["agent_user_id"] == None

    body = res.json()
    body["agent_user_id"] = agent_id
    body["status"] = "claimed"

    res = requests.put(service + "/job/" + created_job, headers=agent_token, json=body)
    assert res.status_code == 200

    res = requests.get(service + "/job/" + created_job, headers=provider_token)
    assert res.status_code == 200
    assert res.json()["agent_user_id"] == agent_id
    assert res.json()["status"] == "claimed"

def test_unauthorized_update(service, created_job, provider_token):
    res = requests.put(service + f"/job/{created_job}")
    assert res.status_code == 401

    res = requests.put(service + f"/job/{created_job}", headers=provider_token)
    assert res.status_code == 403

def test_invalid_job_update(service, agent_token):
    res = requests.put(service + "/job/unknown", headers=agent_token)
    assert res.status_code == 404

def test_invalid_parameters_update(service, created_job, agent_token):
    request = copy(standard_job_info)
    request["pickup_at"] = "NotARealAddress"
    res = requests.put(service + f"/job/{created_job}", headers=agent_token)
    assert res.status_code == 400

    request["pickup_at"] = "Herrengasse 10, 8010 Graz"
    request["deliver_at"] = "NotARealAddress"
    res = requests.put(service + f"/job/{created_job}", headers=agent_token)
    assert res.status_code == 400

def test_unauthorized_get(service, created_job):
    res = requests.get(service + f"/job/{created_job}")
    assert res.status_code == 401

def test_get_unknown_job(service, agent_token):
    res = requests.get(service + f"/job/unknown", headers=agent_token)
    assert res.status_code == 404

def test_job_tracking(service, created_job):
    res = requests.get(service + f"/job/tracking/unknown")
    assert res.status_code == 404

    res = requests.get(service + f"/job/tracking/{created_job}")
    assert res.status_code == 200

#TODO test get jobs