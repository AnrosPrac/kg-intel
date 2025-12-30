import json
import os
from datetime import date

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def today_file():
    return f"{DATA_DIR}/kg_{date.today()}.json"

def yesterday_file():
    from datetime import timedelta
    y = date.today() - timedelta(days=1)
    return f"{DATA_DIR}/kg_{y}.json"

def save(data):
    with open(today_file(), "w") as f:
        json.dump(data, f, indent=2)

def load_yesterday():
    try:
        with open(yesterday_file()) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
