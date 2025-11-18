from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class Interval(BaseModel):
    """Defines a single availability window stored in UTC+3."""

    start: datetime
    end: datetime
