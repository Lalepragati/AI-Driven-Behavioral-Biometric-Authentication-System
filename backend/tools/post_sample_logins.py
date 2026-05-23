"""Post synthetic keystroke login samples for each user in the sample_users.json.

Usage:
  python backend/tools/post_sample_logins.py --url http://127.0.0.1:8001

This will POST to `/api/v1/auth/login` for each user and print the JSON response.
"""
import json
import argparse
import random
import sys
from pathlib import Path

try:
    import requests
except Exception:
    print("Please install requests: pip install requests", file=sys.stderr)
    raise


def load_users(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def make_keystroke_sample(user_id: str, session_id: str, text: str = "password"):
    events = []
    t = 0.0
    for ch in text:
        d = random.uniform(0.04, 0.12)
        events.append({"key": ch, "event_type": "keydown", "timestamp": round(t, 4)})
        t += d
        events.append({"key": ch, "event_type": "keyup", "timestamp": round(t, 4)})
        t += random.uniform(0.02, 0.08)
    return {
        "user_id": user_id,
        "session_id": session_id,
        "text": text,
        "events": events,
        "context": {"device": "desktop", "ip_address": "127.0.0.1"},
    }


def post_login(register_url: str, user: dict):
    sample = make_keystroke_sample(user.get("user_id"), session_id=f"AUTO-{user.get('user_id')}")
    payload = {
        "user_id": user.get("user_id"),
        "password": user.get("password"),
        "sample": sample,
        "failed_attempts": 0,
        "device": "desktop",
        "ip_address": "127.0.0.1",
    }
    try:
        r = requests.post(register_url, json=payload, timeout=10)
    except Exception as ex:
        return {"status": "error", "error": str(ex)}
    try:
        return {"status_code": r.status_code, "json": r.json()}
    except Exception:
        return {"status_code": r.status_code, "text": r.text}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8001", help="Backend base URL")
    parser.add_argument("--file", default="backend/data/sample_users.json", help="Path to sample users file")
    args = parser.parse_args()
    path = Path(args.file)
    if not path.exists():
        print(f"Users file not found: {path}", file=sys.stderr)
        raise SystemExit(1)
    users = load_users(path)
    login_url = args.url.rstrip("/") + "/api/v1/auth/login"
    for u in users:
        print(f"Posting login for {u.get('user_id')} -> {login_url}")
        res = post_login(login_url, u)
        print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
