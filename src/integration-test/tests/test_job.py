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
    res = requests.put(service + f"/job/{created_job}", json=request, headers=agent_token)
    assert res.status_code == 400

    request["pickup_at"] = "Herrengasse 10, 8010 Graz"
    request["deliver_at"] = "NotARealAddress"
    res = requests.put(service + f"/job/{created_job}", json=request, headers=agent_token)
    assert res.status_code == 400

def test_update_job_without_body(service, created_job, agent_token):
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

def test_get_job_in_radius(service, created_job, agent_token, admin_token):
    # setup job
    job_params_update = { "pickup_at": "Herrengasse 10, 8010 Graz", "deliver_at": "Inffeldgasse 16a, 8010 Graz", "status": "test-job" }
    job = requests.put(service + f"/job/{created_job}", params=job_params_update, headers=admin_token)

    # setup agent
    geo_params = { "address": "Europaplatz 12 8020 Graz" }
    geo = requests.get(service + "/geo/coordinates", params=geo_params, headers=agent_token)
    agent_location_lat = geo.json()["latitude"]
    agent_location_lon = geo.json()["longitude"]

    # agent is currently at Graz HBF and searches for jobs in a radius of 2300m
    job_params_search = { "radius": 1000, "latitude": agent_location_lat, "longitude": agent_location_lon, "status": 'test-job' }
    job = requests.get(service + "/job", params=job_params_search, headers=agent_token)
    assert len(job.json()) == 0

    # unfortunately agent didn't find any jobs -> increase radius
    job_params_search["radius"] = 2500
    job = requests.get(service + "/job", params=job_params_search, headers=agent_token)
    assert len(job.json()) == 1
    assert len(job.json()[0]["id"]) == created_job
    
def test_update_job_empty_body(service, created_job, agent_token):
    res = requests.put(service + f"/job/{created_job}", headers=agent_token)
    assert res.status_code == 400

def test_create_job_empty_body(service, created_job, provider_token):
    res = requests.post(service + "/job", headers=provider_token)
    assert res.status_code == 400
