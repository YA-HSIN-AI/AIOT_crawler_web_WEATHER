
import requests
import json
import os
import time


URL = (
    "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/"
    "F-A0010-001?Authorization=CWA-777A875C-4258-446E-AD60-3B06160B5F80"
    "&downloadType=WEB&format=JSON"
)

DATA_DIR = "weather_data"
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_data(url: str):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Error fetching data:", e)
        return None

def save_json(data):
    ts = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(DATA_DIR, f"weather_{ts}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved: {filename}")

if __name__ == "__main__":
    print("🌐 Crawling CWA Open Data...")
    data = fetch_data(URL)
    if data:
        save_json(data)


URL = (
    "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/"
    "F-A0010-001?Authorization=CWA-777A875C-4258-446E-AD60-3B06160B5F80"
    "&downloadType=WEB&format=JSON"
)

DATA_DIR = "weather_data"
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_data(url: str):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Error fetching data:", e)
        return None

def save_json(data):
    ts = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(DATA_DIR, f"weather_{ts}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved: {filename}")

if __name__ == "__main__":
    print("🌐 Crawling CWA Open Data...")
    data = fetch_data(URL)
    if data:
        save_json(data)

