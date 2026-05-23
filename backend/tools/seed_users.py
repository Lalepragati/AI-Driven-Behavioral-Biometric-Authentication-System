"""Seed users into the local backend by POSTing to the register endpoint.

Usage:
  python backend/tools/seed_users.py --url http://127.0.0.1:8001

The script reads `backend/data/sample_users.json` and posts each entry to
`/api/v1/auth/register`.
"""
import json
import argparse
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


def seed(url: str, users_path: Path):
    users = load_users(users_path)
    register_url = url.rstrip("/") + "/api/v1/auth/register"
    for u in users:
        print(f"Registering {u.get('user_id')} -> {register_url}")
        try:
            r = requests.post(register_url, json=u, timeout=10)
        except Exception as ex:
            print(f"ERROR posting {u.get('user_id')}: {ex}")
            continue
        if r.status_code in (200, 201):
            print(f"OK: {u.get('user_id')}")
        else:
            print(f"FAILED ({r.status_code}): {r.text}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8001", help="Backend base URL")
    parser.add_argument("--file", default="backend/data/sample_users.json", help="Path to sample users file")
    args = parser.parse_args()
    path = Path(args.file)
    if not path.exists():
        print(f"Users file not found: {path}", file=sys.stderr)
        raise SystemExit(1)
    seed(args.url, path)


if __name__ == "__main__":
    main()
