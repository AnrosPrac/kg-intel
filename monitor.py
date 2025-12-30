import requests
import os
from config import ENTITY_GRAPH
from storage import save, load_yesterday
from reporter import generate

API_KEY = os.environ["KG_API_KEY"]
KG_URL = "https://kgsearch.googleapis.com/v1/entities:search"


# -------------------------------------------------
# Knowledge Graph Fetcher (TYPE-AWARE)
# -------------------------------------------------
def fetch_entity(query, types=None):
    params = {
        "query": query,
        "limit": 5,
        "indent": True,
        "key": API_KEY
    }

    if types:
        params["types"] = types

    resp = requests.get(KG_URL, params=params, timeout=10)
    data = resp.json()
    items = data.get("itemListElement", [])

    return pick_best(items, query)


# -------------------------------------------------
# Best Entity Picker (ANTI-CITY / ANTI-NOISE)
# -------------------------------------------------
def pick_best(items, query):
    if not items:
        return None

    q = query.lower()

    # First pass: strong name match
    for item in items:
        r = item.get("result", {})
        name = r.get("name", "").lower()
        if q in name:
            return r

    # Second pass: has KG ID (canonical)
    for item in items:
        r = item.get("result", {})
        if r.get("@id"):
            return r

    # Fallback
    return items[0].get("result")


# -------------------------------------------------
# Scan Logical Entity Group
# -------------------------------------------------
def scan_group(group):
    results = {}
    types = group.get("types")

    # primary name
    results[group["name"]] = fetch_entity(group["name"], types)

    # aliases
    for alias in group.get("aliases", []):
        results[alias] = fetch_entity(alias, types)

    return results


# -------------------------------------------------
# Orchestrator (PARENT AWARE, SAFE)
# -------------------------------------------------
def orchestrate():
    today = {
        "PARENT_ORG": scan_group(ENTITY_GRAPH["parent"]),
        "FOUNDER": scan_group(ENTITY_GRAPH["founder"]),
        "CHILD_ORGS": {
            child["id"]: scan_group(child)
            for child in ENTITY_GRAPH.get("children", [])
        }
    }

    yesterday = load_yesterday() or {}

    y_parent = yesterday.get("PARENT_ORG") or {}
    y_founder = yesterday.get("FOUNDER") or {}
    y_children = yesterday.get("CHILD_ORGS") or {}

    save(today)

    blocks = []

    # ---------------- Parent ----------------
    blocks.append("PARENT ORGANIZATION")
    blocks.append("=" * 40)
    for name, entity in today["PARENT_ORG"].items():
        blocks.append(generate(name, entity, y_parent.get(name)))
        blocks.append("-" * 40)

    # ---------------- Founder ----------------
    blocks.append("FOUNDER")
    blocks.append("=" * 40)
    for name, entity in today["FOUNDER"].items():
        blocks.append(generate(name, entity, y_founder.get(name)))
        blocks.append("-" * 40)

    # ---------------- Products ----------------
    blocks.append("PRODUCTS / PLATFORMS")
    blocks.append("=" * 40)
    for child_id, child_block in today["CHILD_ORGS"].items():
        blocks.append(f"PRODUCT: {child_id.upper()}")
        blocks.append("-" * 40)
        for name, entity in child_block.items():
            blocks.append(
                generate(
                    name,
                    entity,
                    y_children.get(child_id, {}).get(name)
                )
            )
            blocks.append("-" * 40)

    return "\n".join(blocks)


# -------------------------------------------------
# Telegram Sender (SAFE, CHUNKED)
# -------------------------------------------------
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
        print("Telegram:", resp.status_code)


# -------------------------------------------------
# Entry Point
# -------------------------------------------------
if __name__ == "__main__":
    send_telegram("KG Intelligence Reporter ONLINE — Sidhi Labs entity monitoring active.")
    report = orchestrate()
    send_telegram(report)
