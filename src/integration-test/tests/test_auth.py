

import pytest
import requests

def test_login_missing_parameters(service):
    res = requests.post(service + "/auth/login", json={"email": "admin@example.com"})
    assert res.status_code == 400

    res = requests.post(service + "/auth/login", json={"password": "invalid"})
    assert res.status_code == 400

    res = requests.post(service + "/auth/login")
    assert res.status_code == 400


def test_logout(service, admin_token):
    res = requests.post(service + "/auth/logout", headers=admin_token)
    assert res.status_code == 200


def test_logout_missing_header(service):
    res = requests.post(service + "/auth/logout")
    assert res.status_code == 401


def test_get_own_user(service, admin_token):
    res = requests.get(service + "/auth/user/self", headers=admin_token)
    assert res.status_code == 200
    assert res.json().get("email") == "admin@example.com"
    assert res.json().get("role") == "admin"
    assert res.json().get("id") is not None


def test_get_user_if_not_logged_in(service):
    res = requests.get(service + "/auth/user/self")
    assert res.status_code == 401


def test_get_foreign_user_as_non_admin(service, admin_token, provider_token, agent_token):
    res = requests.get(service + "/auth/user/self", headers=admin_token)
    admin_id = res.json().get("id")

    res = requests.get(service + f"/auth/user/{admin_id}", )
    assert res.status_code == 401

    res = requests.get(service + f"/auth/user/{admin_id}", headers=provider_token)
    assert res.status_code == 403
    res = requests.get(service + f"/auth/user/{admin_id}", headers=provider_token)
    assert res.status_code == 403


def test_create_user_as_admin(service, admin_token):
    res = requests.post(service + "/auth/user", json={"email": "admin2@example.com", "password": "secret", "role": "admin"}, headers=admin_token)
    assert res.status_code == 201


def test_create_user_where_it_should_be_forbidden(service, provider_token, agent_token):

    res = requests.post(service + "/auth/user",
                        json={"email": "admin2@example.com", "password": "secret", "role": "admin"},
                        headers=provider_token)
    assert res.status_code == 403
    assert res.status_code == 403
    res = requests.post(service + "/auth/user",
                        json={"email": "admin2@example.com", "password": "secret", "role": "admin"},
                        headers=agent_token)
    assert res.status_code == 403

    res = requests.post(service + "/auth/user",
                        json={"email": "admin2@example.com", "password": "secret", "role": "admin"})
    assert res.status_code == 401


def test_delete_other_user(service, admin_token, provider_token, agent_token):
    res = requests.get(service + "/auth/user/self", headers=agent_token)
    agent_id = res.json().get("id")

    res = requests.delete(service + f"/auth/user/{agent_id}", headers=provider_token)
    assert res.status_code == 403
    res = requests.get(service + f"/auth/user/{agent_id}", headers=admin_token)
    assert res.status_code == 200


def test_delete_own_user(service, admin_token, provider_token, agent_token):
    res = requests.delete(service + f"/auth/user/self", headers=provider_token)
    assert res.status_code == 200
    res = requests.delete(service + f"/auth/user/self", headers=agent_token)
    assert res.status_code == 200
    res = requests.delete(service + f"/auth/user/self", headers=admin_token)
    assert res.status_code == 200