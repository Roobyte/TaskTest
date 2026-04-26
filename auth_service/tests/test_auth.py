import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.routers.auth import get_http_client


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class _FakeHTTPClient:
    async def post(self, *_args, **_kwargs):
        return _FakeResponse(200, {"id": "user-1"})


@pytest.mark.anyio
async def test_verify_no_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/token/verify")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_verify_with_cookie_session(monkeypatch):
    monkeypatch.setattr(
        "app.dependencies.decode_token",
        lambda _token: {"sub": "user-1", "jti": "jti-1", "exp": 9999999999},
    )

    async def fake_get(key: str):
        if key == "blacklist:jti-1":
            return None
        if key == "session:jti-1":
            return "user-1"
        return None

    monkeypatch.setattr("app.dependencies.redis_client.get", fake_get)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        ac.cookies.set("auth_session", "session-token")
        response = await ac.get("/token/verify")

    assert response.status_code == 200
    assert response.json() == {"user_id": "user-1"}


@pytest.mark.anyio
async def test_login_sets_cookie_and_persists_session(monkeypatch):
    async def override_http_client():
        yield _FakeHTTPClient()

    app.dependency_overrides[get_http_client] = override_http_client

    monkeypatch.setattr("app.routers.auth.create_access_token", lambda _user_id: "token-1")
    monkeypatch.setattr(
        "app.routers.auth.decode_token",
        lambda _token: {"sub": "user-1", "jti": "jti-1", "exp": 9999999999},
    )

    calls = []

    async def fake_setex(key: str, ttl: int, value: str):
        calls.append((key, ttl, value))
        return True

    monkeypatch.setattr("app.routers.auth.redis_client.setex", fake_setex)

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/login", json={"login": "john", "password": "secret"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"access_token": "token-1", "token_type": "bearer"}
    assert calls and calls[0][0] == "session:jti-1"
    assert calls[0][2] == "user-1"
    assert "auth_session=token-1" in response.headers.get("set-cookie", "")
