import requests
import os
from config import ENTITY_GRAPH
from storage import save, load_yesterday
from reporter import generate

API_KEY = os.environ["KG_API_KEY"]

KG_URL = "https://kgsearch.googleapis.com/v1/entities:search"


# -----------------------------
# Knowledge Graph Fetcher
# -----------------------------
def fetch_entity(query):
    params = {
        "query": query,
        "limit": 1,
        "indent": True,
        "key": API_KEY
    }
    resp = requests.get(KG_URL, params=params, timeout=10)
    data = resp.json()
    items = data.get("itemListElement", [])
    return items[0]["result"] if items else None


# -----------------------------
# Scan a logical entity group
# -----------------------------
def scan_group(group):
    results = {}

    # primary name
    results[group["name"]] = fetch_entity(group["name"])

    # aliases
    for alias in group.get("aliases", []):
        results[alias] = fetch_entity(alias)

    return results


# -----------------------------
# Orchestrator (PARENT AWARE)
# -----------------------------
def orchestrate():
    today = {
        "PARENT_ORG": scan_group(ENTITY_GRAPH["parent"]),
        "FOUNDER": scan_group(ENTITY_GRAPH["founder"]),
        "CHILD_ORGS": {
            child["name"]: scan_group(child)
            for child in ENTITY_GRAPH.get("children", [])
        }
    }

    yesterday = load_yesterday()
    save(today)

    blocks = []

    # Parent
    blocks.append("PARENT ORGANIZATION")
    blocks.append("=" * 40)
    for name, entity in today["PARENT_ORG"].items():
        blocks.append(generate(name, entity, yesterday.get("PARENT_ORG", {}).get(name)))
        blocks.append("-" * 40)

    # Founder
    blocks.append("FOUNDER")
    blocks.append("=" * 40)
    for name, entity in today["FOUNDER"].items():
        blocks.append(generate(name, entity, yesterday.get("FOUNDER", {}).get(name)))
        blocks.append("-" * 40)

    # Children
    blocks.append("SUBSIDIARIES / PRODUCTS")
    blocks.append("=" * 40)
    for child_name, child_block in today["CHILD_ORGS"].items():
        blocks.append(f"CHILD ENTITY: {child_name}")
        blocks.append("-" * 40)
        for name, entity in child_block.items():
            blocks.append(
                generate(
                    name,
                    entity,
                    yesterday.get("CHILD_ORGS", {})
                             .get(child_name, {})
                             .get(name)
                )
            )
            blocks.append("-" * 40)

    return "\n".join(blocks)


# -----------------------------
# Telegram Sender (SAFE)
# -----------------------------
def send_telegram(text):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    MAX = 3500
    for i in range(0, len(text), MAX):
        resp = requests.post(
            url,
            json={
                "chat_id": chat,
                "text": text[i:i + MAX]
            },
            timeout=10
        )
        print("Telegram response:", resp.status_code, resp.text)


# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    send_telegram("KG Intelligence Reporter ONLINE. Parent-organization mode enabled.")
    report = orchestrate()
    send_telegram(report)
