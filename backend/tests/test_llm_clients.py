"""Unit tests for LLM HTTP dispatch (mocked, no network)."""

from unittest.mock import MagicMock, patch

import pytest

from app.config import settings
from app.services import llm_clients


@pytest.fixture
def openai_response_json():
    return {
        "choices": [{"message": {"content": "  Hello from OpenAI  "}}],
    }


@pytest.fixture
def anthropic_response_json():
    return {
        "content": [{"type": "text", "text": "Hello from Claude"}],
    }


@pytest.fixture
def gemini_response_json():
    return {
        "candidates": [
            {"content": {"parts": [{"text": "Hello from Gemini"}]}},
        ],
    }


def test_dispatch_openai_parses_text(openai_response_json, monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "openai")
    monkeypatch.setattr(settings, "LLM_API_KEY", "sk-test")

    mock_resp = MagicMock()
    mock_resp.json.return_value = openai_response_json
    mock_resp.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.post.return_value = mock_resp

    with patch("app.services.llm_clients.httpx.Client", return_value=mock_client):
        out = llm_clients.dispatch_llm("sys", "user")
    assert out == "Hello from OpenAI"
    mock_client.post.assert_called_once()


def test_dispatch_anthropic_parses_text(anthropic_response_json, monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "anthropic")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "sk-ant-test")

    mock_resp = MagicMock()
    mock_resp.json.return_value = anthropic_response_json
    mock_resp.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.post.return_value = mock_resp

    with patch("app.services.llm_clients.httpx.Client", return_value=mock_client):
        out = llm_clients.dispatch_llm("sys", "user")
    assert out == "Hello from Claude"


def test_dispatch_gemini_parses_text(gemini_response_json, monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "g-key")

    mock_resp = MagicMock()
    mock_resp.json.return_value = gemini_response_json
    mock_resp.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.post.return_value = mock_resp

    with patch("app.services.llm_clients.httpx.Client", return_value=mock_client):
        out = llm_clients.dispatch_llm("sys", "user")
    assert out == "Hello from Gemini"


def test_dispatch_unknown_provider(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "openai")
    monkeypatch.setattr(settings, "LLM_API_KEY", "x")
    object.__setattr__(settings, "LLM_PROVIDER", "bogus")
    with pytest.raises(RuntimeError, match="Unknown LLM_PROVIDER"):
        llm_clients.dispatch_llm("a", "b")
    object.__setattr__(settings, "LLM_PROVIDER", "openai")
