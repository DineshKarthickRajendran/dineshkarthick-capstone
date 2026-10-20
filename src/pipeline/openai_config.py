"""OpenAI-compatible client configuration helpers."""

from __future__ import annotations

import os


def configure_openai_base_url() -> str | None:
    """Map the legacy OPENAI_API_BASE variable to the SDK's OPENAI_BASE_URL."""
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE")
    if base_url:
        os.environ.setdefault("OPENAI_BASE_URL", base_url)
    return base_url
