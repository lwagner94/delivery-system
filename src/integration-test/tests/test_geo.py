
import requests

def test_geolocate_basic(service, admin_token, provider_token, agent_token):
    params = {"address": "Inffeldgasse 16a, 8010 Graz"}

    for token in (admin_token, provider_token, agent_token):
        res = requests.get(service + "/geo/coordinates", params=params, headers=token)
        assert res.status_code == 200
        assert res.json().get("longitude") is not None
        assert res.json().get("latitude") is not None

def test_geolocate_unauthorized(service):
    params = {"address": "Inffeldgasse 16a, 8010 Graz"}
    res = requests.get(service + "/geo/coordinates", params=params)
    assert res.status_code == 401

def test_geolocate_invalid(service, admin_token):
    params = {"addresss": "NotARealAddress"}
    res = requests.get(service + "/geo/coordinates", params=params, headers=admin_token)
    assert res.status_code == 400