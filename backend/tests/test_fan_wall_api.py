"""Fan Wall API regression tests for list/stats/submit/like core flows."""

import os
from pathlib import Path
import uuid

import pytest
import requests
from dotenv import load_dotenv


load_dotenv(Path("/app/frontend/.env"))
BASE_URL = os.environ.get("REACT_APP_BACKEND_URL")


@pytest.fixture(scope="session")
def api_base_url():
    if not BASE_URL:
        pytest.skip("REACT_APP_BACKEND_URL is missing")
    return BASE_URL.rstrip("/")


@pytest.fixture(scope="session")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def test_api_root(session, api_base_url):
    response = session.get(f"{api_base_url}/api/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Portal HARNAS UMKM 2026 API aktif"
    assert data["database"] == "Supabase PostgreSQL"


def test_fan_wall_stats_structure(session, api_base_url):
    response = session.get(f"{api_base_url}/api/fan-wall/stats")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["voices"], int)
    assert isinstance(data["provinces"], int)
    assert isinstance(data["organizations"], int)
    assert isinstance(data["supports"], int)
    assert data["voices"] >= 1


def test_fan_wall_list_default_only_approved(session, api_base_url):
    response = session.get(f"{api_base_url}/api/fan-wall")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    sample = data[0]
    assert "id" in sample
    assert sample["is_approved"] is True


def test_fan_wall_filter_by_role(session, api_base_url):
    response = session.get(f"{api_base_url}/api/fan-wall", params={"role": "Pelaku UMKM"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert all(item["role"] == "Pelaku UMKM" for item in data)


def test_fan_wall_filter_by_province(session, api_base_url):
    response = session.get(f"{api_base_url}/api/fan-wall", params={"province": "Kalimantan Barat"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert all(item["province"] == "Kalimantan Barat" for item in data)


def test_fan_wall_search_by_name(session, api_base_url):
    response = session.get(f"{api_base_url}/api/fan-wall", params={"search": "Bahrul"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any("bahrul" in item["full_name"].lower() for item in data)


def test_fan_wall_sort_popular_descending(session, api_base_url):
    response = session.get(f"{api_base_url}/api/fan-wall", params={"sort": "popular"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    likes = [item["likes_count"] for item in data]
    assert likes == sorted(likes, reverse=True)


def test_submit_message_hidden_until_approved_and_like_404_when_unapproved(session, api_base_url):
    unique = f"TEST_AUTOMATION_{uuid.uuid4().hex[:8]}"
    payload = {
        "full_name": unique,
        "business_name": "TEST Biz",
        "role": "Lainnya",
        "province": "DKI Jakarta",
        "city_regency": "Jakarta Selatan",
        "message": "Ini adalah pesan pengujian otomatis untuk validasi moderasi konten.",
        "avatar_url": "",
    }

    submit = session.post(f"{api_base_url}/api/fan-wall", json=payload)
    assert submit.status_code == 201
    created = submit.json()
    assert created["full_name"] == payload["full_name"]
    assert created["is_approved"] is False
    assert created["role"] == "Lainnya"

    list_response = session.get(f"{api_base_url}/api/fan-wall", params={"search": unique})
    assert list_response.status_code == 200
    listed = list_response.json()
    assert listed == []

    like_response = session.post(f"{api_base_url}/api/fan-wall/{created['id']}/like")
    assert like_response.status_code == 404
    like_data = like_response.json()
    assert like_data["detail"] == "Aspirasi tidak ditemukan"


def test_like_endpoint_increments_approved_message(session, api_base_url):
    before_resp = session.get(f"{api_base_url}/api/fan-wall", params={"search": "Bahrul"})
    assert before_resp.status_code == 200
    before_data = before_resp.json()
    assert len(before_data) >= 1
    target = before_data[0]
    before_likes = target["likes_count"]

    like_resp = session.post(f"{api_base_url}/api/fan-wall/{target['id']}/like")
    assert like_resp.status_code == 200
    liked = like_resp.json()
    assert liked["id"] == target["id"]
    assert liked["likes_count"] >= before_likes
    if liked.get("already_liked") is False:
        assert liked["likes_count"] == before_likes + 1
    else:
        assert liked["likes_count"] == before_likes

    after_resp = session.get(f"{api_base_url}/api/fan-wall", params={"search": "Bahrul"})
    assert after_resp.status_code == 200
    after_data = after_resp.json()
    assert len(after_data) >= 1
    after_target = next(item for item in after_data if item["id"] == target["id"])
    if liked.get("already_liked") is False:
        assert after_target["likes_count"] >= before_likes + 1
    else:
        assert after_target["likes_count"] >= before_likes


def test_like_endpoint_idempotent_for_identical_client_fingerprint(session, api_base_url):
    list_resp = session.get(f"{api_base_url}/api/fan-wall", params={"search": "Ratna"})
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) >= 1
    target = items[0]

    headers = {
        "x-forwarded-for": "203.0.113.10",
        "user-agent": "pytest-dedupe-check/1.0",
    }
    first = session.post(f"{api_base_url}/api/fan-wall/{target['id']}/like", headers=headers)
    assert first.status_code == 200
    first_data = first.json()

    second = session.post(f"{api_base_url}/api/fan-wall/{target['id']}/like", headers=headers)
    assert second.status_code == 200
    second_data = second.json()

    assert second_data["id"] == first_data["id"]
    assert second_data["already_liked"] is True
    assert second_data["likes_count"] == first_data["likes_count"]


def test_like_nonexistent_message_returns_404(session, api_base_url):
    missing_id = str(uuid.uuid4())
    response = session.post(f"{api_base_url}/api/fan-wall/{missing_id}/like")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Aspirasi tidak ditemukan"
