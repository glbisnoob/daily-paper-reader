"""Explicit, half-open retrieval windows shared by the pipeline stages."""

import os
from datetime import datetime, timedelta, timezone

LOCAL_TIMEZONE = timezone(timedelta(hours=8))


def parse_timestamp(value: str) -> datetime:
    stamp = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("Retrieval timestamps must include a timezone")
    return stamp.astimezone(timezone.utc)


def explicit_window() -> tuple[datetime, datetime] | None:
    start = os.environ.get("DPR_FETCH_START", "").strip()
    end = os.environ.get("DPR_FETCH_END", "").strip()
    if not start and not end:
        return None
    if not start or not end:
        raise ValueError("DPR_FETCH_START and DPR_FETCH_END must be set together")
    window = parse_timestamp(start), parse_timestamp(end)
    if window[0] >= window[1]:
        raise ValueError("Retrieval start must be earlier than end")
    return window


def window_presentation(start: datetime, end: datetime) -> tuple[str, str]:
    first = start.astimezone(LOCAL_TIMEZONE)
    last = end.astimezone(LOCAL_TIMEZONE)
    label = f"{first:%Y-%m-%d %H:%M} ~ {last:%Y-%m-%d %H:%M} (UTC+8)"
    if end - start <= timedelta(days=1):
        token = f"{last:%Y%m%d}"
    else:
        token = f"{first:%Y%m%d}-{last:%Y%m%d}"
    return token, label
