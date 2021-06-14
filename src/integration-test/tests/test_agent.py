import requests
from copy import copy

from requests.api import head


DEFAULT_BODY = {
    "status": "idle",
    "longitude": 47.05812932556646,
    "latitude": 15.459891192023168,
    "current_job": ""
}

def test_unauthorized_update(service, agent_token, provider_token, admin_token):
    res = requests.put(service + "/agent/self", json=DEFAULT_BODY)
    assert res.status_code == 401

    res = requests.get(service + "/auth/user/self", headers=agent_token)
    agent_id = res.json().get("id")
    res = requests.put(service + f"/agent/{agent_id}", json=DEFAULT_BODY, headers=provider_token)
    assert res.status_code == 403

    res = requests.put(service + f"/agent/{agent_id}", json=DEFAULT_BODY, headers=admin_token)
    assert res.status_code == 403

    res = requests.get(service + "/agent/self")
    assert res.status_code == 401

def test_unauthorized_get(service):
    res = requests.get(service + "/agent/self")
    assert res.status_code == 401

def test_authorized(service, agent_token, admin_token, provider_token):
    res = requests.put(service + "/agent/self", json=DEFAULT_BODY, headers=agent_token)
    assert res.status_code == 200

    res = requests.get(service + "/auth/user/self", headers=agent_token)
    agent_id = res.json().get("id")

    res = requests.get(service + f"/agent/{agent_id}", headers=admin_token)
    assert res.status_code == 200

    res = requests.get(service + f"/agent/{agent_id}", headers=provider_token)
    assert res.status_code == 200

def test_claim_job(service, agent_token, created_job):
    new_status = copy(DEFAULT_BODY)
    new_status["current_job"] = created_job
    new_status["status"] = "picking_up"
    res = requests.put(service + "/agent/self", json=new_status, headers=agent_token)
    assert res.status_code == 200

    new_status["status"] = "delivering"
    res = requests.put(service + "/agent/self", json=new_status, headers=agent_token)
    assert res.status_code == 200

    new_status["current_job"] = ""
    new_status["status"] = "idle"
    res = requests.put(service + "/agent/self", json=new_status, headers=agent_token)
    assert res.status_code == 200

    new_status["status"] = "off_duty"
    new_status["longitude"] = 0
    new_status["latitude"] = 0
    res = requests.put(service + "/agent/self", json=new_status, headers=agent_token)
    assert res.status_code == 200

    res = requests.get(service + "/agent/self", headers=agent_token)
    assert res.status_code == 200
    assert res.json().get("status") == "off_duty"
    assert res.json().get("longitude") == 0
    assert res.json().get("latitude") == 0

def test_invalid_states(service, agent_token, created_job):
    new_status = copy(DEFAULT_BODY)
    new_status["current_job"] = created_job
    new_status["status"] = "invalid"
    res = requests.put(service + "/agent/self", json=new_status, headers=agent_token)
    assert res.status_code == 400

def test_invalid_coordinates(service, agent_token):
    new_status = copy(DEFAULT_BODY)
    new_status["status"] = "invalid"
    new_status["longitude"] = -181
    res = requests.put(service + "/agent/self", json=new_status, headers=agent_token)
    assert res.status_code == 400

    new_status["longitude"] = 181
    res = requests.put(service + "/agent/self", json=new_status, headers=agent_token)
    assert res.status_code == 400

    new_status["longitude"] = 0
    new_status["latitude"] = -91
    res = requests.put(service + "/agent/self", json=new_status, headers=agent_token)
    assert res.status_code == 400

    new_status["latitude"] = 91
    res = requests.put(service + "/agent/self", json=new_status, headers=agent_token)
    assert res.status_code == 400

def test_invalid_job(service, agent_token):
    new_status = copy(DEFAULT_BODY)
    new_status["current_job"] = "unknown_job"
    res = requests.put(service + "/agent/self", json=new_status, headers=agent_token)
    assert res.status_code == 400

def test_invalid_agent(service, agent_token):
    res = requests.put(service + "/agent/unknown", json=DEFAULT_BODY, headers=agent_token)
    assert res.status_code == 403
