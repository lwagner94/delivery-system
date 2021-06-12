import requests
from copy import copy


DEFAULT_BODY = {
    "status": "idle",
    "longitude": 47.05812932556646,
    "latitude": 15.459891192023168,
    "current_job": ""
}

def test_unauthorized(service):
    res = requests.put(service + "/agent/self", json=DEFAULT_BODY)
    assert res.status_code == 401

def test_authorized(service, agent_token):
    res = requests.put(service + "/agent/self", json=DEFAULT_BODY, headers=agent_token)
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
    res = requests.put(service + "/agent/self", json=new_status, headers=agent_token)
    assert res.status_code == 200

def test_invalid_states(service, agent_token, created_job):
    new_status = copy(DEFAULT_BODY)
    new_status["current_job"] = created_job
    new_status["status"] = "invalid"
    res = requests.put(service + "/agent/self", json=new_status, headers=agent_token)
    assert res.status_code == 400

