# crawler.py
import os
import json
import time
import requests
import urllib3
from typing import Optional, Tuple

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CWA_ENDPOINT = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001"
DATA_DIR = "weather_data"


def _get_api_key() -> Optional[str]:
    try:
        import streamlit as st
        key = st.secrets.get("CWA_API_KEY", None)
        if key:
            return str(key).strip()
    except Exception:
        pass

    key = os.getenv("CWA_API_KEY", "").strip()
    return key or None


def fetch_cwa_json(api_key: str, timeout: int = 30, retries: int = 3) -> dict:
    session = requests.Session()
    last_err = None

    for i in range(retries):
        try:
            r = session.get(
                CWA_ENDPOINT,
                params={
                    "Authorization": api_key,
                    "downloadType": "WEB",
                    "format": "JSON",
                },
                timeout=timeout,
                headers={"User-Agent": "Mozilla/5.0"},
                verify=False,  # ✅ Streamlit Cloud SSL workaround
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            time.sleep(1 + i)

    raise RuntimeError(f"Error fetching CWA data after {retries} retries: {last_err}")


def save_json(data: dict, data_dir: str = DATA_DIR) -> str:
    os.makedirs(data_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(data_dir, f"weather_{ts}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filename


def crawl_and_save(api_key: Optional[str] = None, data_dir: str = DATA_DIR) -> Tuple[str, dict]:
    api_key = (api_key or _get_api_key() or "").strip()
    if not api_key:
        raise RuntimeError("Missing API key. Please set Streamlit Secrets: CWA_API_KEY")

    data = fetch_cwa_json(api_key=api_key)
    path = save_json(data, data_dir=data_dir)
    return path, data


if __name__ == "__main__":
    print("🌐 Crawling CWA Open Data...")
    path, _ = crawl_and_save()
    print(f"✅ Saved: {path}")
