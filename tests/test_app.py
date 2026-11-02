import hashlib
import hmac
import json
from unittest import mock

import pytest
import requests

import app as bot


PUSH = {
    "repository": {"name": "repo_name"},
    "pusher": {"name": "yahya"},
    "commits": [{"message": "fix <b> & snake_case\n\nbody", "url": "https://example.test/c/1"}],
}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(bot, "WEBHOOK_SECRET", None)
    return bot.app.test_client()


@pytest.fixture
def post():
    with mock.patch.object(bot.requests, "post") as sender:
        yield sender


def sign(body, secret):
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def test_home(client):
    assert client.get("/").status_code == 200


def test_push_sends_escaped_first_line(client, post):
    assert client.post("/webhook", json=PUSH).status_code == 200
    payload = post.call_args.kwargs["json"]
    assert payload["parse_mode"] == "HTML"
    assert "fix &lt;b&gt; &amp; snake_case" in payload["text"]
    assert "body" not in payload["text"]
    assert post.call_args.kwargs["timeout"] == bot.TELEGRAM_TIMEOUT


def test_each_commit_gets_a_message(client, post):
    data = {**PUSH, "commits": PUSH["commits"] * 3}
    client.post("/webhook", json=data)
    assert post.call_count == 3


def test_ping_event_sends_nothing(client, post):
    assert client.post("/webhook", json={"zen": "Keep it simple."}).status_code == 200
    post.assert_not_called()


def test_non_json_body_is_ignored(client, post):
    assert client.post("/webhook", data="not json").status_code == 200
    post.assert_not_called()


def test_telegram_failure_does_not_fail_the_webhook(client, post):
    post.side_effect = requests.ConnectionError("https://api.telegram.org/botSECRET")
    assert client.post("/webhook", json=PUSH).status_code == 200


def test_telegram_failure_does_not_log_the_token(client, post, caplog):
    post.side_effect = requests.ConnectionError("https://api.telegram.org/botSECRET")
    client.post("/webhook", json=PUSH)
    assert "SECRET" not in caplog.text


def test_valid_signature_is_accepted(client, post, monkeypatch):
    monkeypatch.setattr(bot, "WEBHOOK_SECRET", "s3cret")
    body = json.dumps(PUSH).encode()
    response = client.post("/webhook", data=body, content_type="application/json",
                           headers={"X-Hub-Signature-256": sign(body, "s3cret")})
    assert response.status_code == 200
    post.assert_called_once()


@pytest.mark.parametrize("header", [None, "sha256=wrong", "sha1=abc"])
def test_bad_signature_is_rejected(client, post, monkeypatch, header):
    monkeypatch.setattr(bot, "WEBHOOK_SECRET", "s3cret")
    headers = {"X-Hub-Signature-256": header} if header else {}
    response = client.post("/webhook", json=PUSH, headers=headers)
    assert response.status_code == 401
    post.assert_not_called()
