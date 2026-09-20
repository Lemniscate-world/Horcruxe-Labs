"""Notifie Discord à la fin de chaque tour agent (opt-in).

Lit DISCORD_WEBHOOK_URL dans .env (sans dépendance).
Si absent : silencieux, rien ne casse.
Usage : python scripts/notify_discord.py --text "..."
"""

import json
import os
import sys
import urllib.request
from pathlib import Path


def load_env():
    p = Path(__file__).parent.parent / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def main():
    load_env()
    url = os.environ.get("DISCORD_WEBHOOK_URL", "")
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "tour agent fini"
    if not url:
        print("pas de webhook, skip")
        return
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps({"content": text[:1900]}).encode(),
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=10)
        print("discord notifié")
    except Exception as e:
        print(f"discord échec : {e}")


if __name__ == "__main__":
    main()
