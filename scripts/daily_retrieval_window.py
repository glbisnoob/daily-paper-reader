"""Prepare a fixed 06:00 UTC+8 window and checkpoint successful retrievals."""

import argparse
import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from retrieval_window import LOCAL_TIMEZONE, explicit_window, parse_timestamp

STATE_PATH = ROOT / "archive" / "daily_retrieval_state.json"


def plan_window(now: datetime, days: int, previous_end: str = "", scheduled: bool = False):
    local = now.astimezone(LOCAL_TIMEZONE)
    end = local.replace(hour=6, minute=0, second=0, microsecond=0)
    if local < end:
        end -= timedelta(days=1)
    start = end - timedelta(days=days)
    if scheduled and previous_end:
        # A failed run never advances the checkpoint. Catch up all missing time.
        start = parse_timestamp(previous_end)
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def read_checkpoint(path: Path | None = None) -> dict:
    path = path or STATE_PATH
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_checkpoint(path: Path | None = None) -> None:
    path = path or STATE_PATH
    if os.environ.get("DPR_CHECKPOINT_ENABLED") != "true":
        return
    window = explicit_window()
    if window is None:
        return
    start, end = window
    previous = read_checkpoint(path).get("completed_through", "")
    # Manual backfills must never move a newer daily checkpoint backwards.
    if previous and parse_timestamp(previous) >= end:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "completed_through": end.isoformat(),
        "last_window_start": start.isoformat(),
        "timezone": "Asia/Hong_Kong",
        "cutoff_hour": 6,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def prepare(now: datetime | None = None) -> None:
    scheduled = os.environ.get("GITHUB_EVENT_NAME") == "schedule"
    days = 1 if scheduled else int(os.environ.get("REQUESTED_DAYS") or "10")
    if not 1 <= days <= 365:
        raise ValueError("fetch_days must be between 1 and 365")
    values = {"DPR_EFFECTIVE_FETCH_DAYS": str(days), "DPR_SKIP_RETRIEVAL": "false"}
    enabled = (scheduled or days == 30) and os.environ.get("PUBLISH_ONLY") != "true"
    values["DPR_CHECKPOINT_ENABLED"] = str(enabled and not os.environ.get("REQUESTED_PROFILE", "").strip()).lower()
    if enabled:
        previous = read_checkpoint().get("completed_through", "") if scheduled else ""
        start, end = plan_window(now or datetime.now(timezone.utc), days, previous, scheduled)
        if start >= end:
            values["DPR_SKIP_RETRIEVAL"] = "true"
            print("The fixed window is already covered by a successful retrieval.")
        else:
            values["DPR_FETCH_START"] = start.isoformat()
            values["DPR_FETCH_END"] = end.isoformat()
            # Catch-up remains in the author's daily pipeline even after a long gap.
            days = min(30, math.ceil((end - start).total_seconds() / 86400))
            values["DPR_EFFECTIVE_FETCH_DAYS"] = str(days)
            print(f"Fixed retrieval window (UTC+8): {start.astimezone(LOCAL_TIMEZONE).isoformat()} to {end.astimezone(LOCAL_TIMEZONE).isoformat()} (end exclusive)")
    with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as target:
        for key, value in values.items():
            target.write(f"{key}={value}\n")
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as target:
        target.write(f"days={days}\n")
        target.write(f"long_range={str(days > 30).lower()}\n")
        target.write(f"skip_retrieval={values['DPR_SKIP_RETRIEVAL']}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "complete"))
    args = parser.parse_args()
    if args.action == "complete":
        write_checkpoint()
    else:
        prepare()
