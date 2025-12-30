import requests
import os
from config import QUERIES

API_KEY = os.environ["KG_API_KEY"]

def fetch_entity(query):
    url = "https://kgsearch.googleapis.com/v1/entities:search"
    params = {
        "query": query,
        "limit": 1,
        "indent": True,
        "key": API_KEY
    }
    r = requests.get(url, params=params).json()
    items = r.get("itemListElement", [])
    return items[0]["result"] if items else None

def run():
    snapshot = {}
    for q in QUERIES:
        snapshot[q] = fetch_entity(q)
    return snapshot


from storage import save, load_yesterday
from reporter import generate

def orchestrate():
    today = run()
    yesterday = load_yesterday()

    save(today)

    full_report = []
    for name, entity in today.items():
        full_report.append(
            generate(name, entity, yesterday.get(name))
        )
        full_report.append("-" * 40)

    return "\n".join(full_report)

def send_telegram(text):
    import requests, os
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat, "text": text})

if __name__ == "__main__":
    report = orchestrate()
    send_telegram("🗞️ DAILY KG INTELLIGENCE REPORT\n\n" + report)

