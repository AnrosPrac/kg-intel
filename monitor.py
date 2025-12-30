import requests
import os
from config import QUERIES
from storage import save, load_yesterday
from reporter import generate

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

def orchestrate():
    today = {q: fetch_entity(q) for q in QUERIES}
    yesterday = load_yesterday()
    save(today)

    blocks = []
    for name, entity in today.items():
        blocks.append(generate(name, entity, yesterday.get(name)))
        blocks.append("-" * 40)

    return "\n".join(blocks)

def send_telegram(text):
    import requests, os

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    MAX = 3500
    for i in range(0, len(text), MAX):
        resp = requests.post(url, json={
            "chat_id": chat,
            "text": text[i:i+MAX]
        })
        print("Telegram response:", resp.status_code, resp.text)

if __name__ == "__main__":
    send_telegram("KG Intelligence Reporter is ONLINE and executed successfully.")
    report = orchestrate()
    send_telegram(report)

