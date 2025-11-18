from __future__ import annotations

from app.core import config


def build_invite_link(topic_id: str) -> str:
    """Returns absolute invite link for sharing topic page."""
    base = config.SITE_BASE_URL.rstrip("/")
    return f"{base}/topic/{topic_id}"
