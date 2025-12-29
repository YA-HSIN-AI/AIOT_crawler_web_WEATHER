# crawler.py
import os
import json
import time
import requests
from typing import Optional, Tuple

# CWA OpenData endpoint (不要把 Authorization 寫死在 URL)
CWA_ENDPOINT = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001"
DATA_DIR = "weather_data"


def _get_api_key() -> Optional[str]:
    """
    依序嘗試：
    1) Streamlit secrets: st.secrets["CWA_API_KEY"]
    2) Environment variable: CWA_API_KEY
    """
    # 先嘗試 Streamlit secrets（即使不是用 streamlit run，也可能讀得到）
    try:
        import streamlit as st  # noqa: F401
        key = st.secrets.get("CWA_API_KEY", None)
        if key:
            return str(key).strip()
    except Exception:
        pass

    # 再嘗試環境變數
    key = os.getenv("CWA_API_KEY", "").strip()
    return key or None


def fetch_cwa_json(api_key: str, timeout: int = 20, retries: int = 3) -> dict:
    """
    向 CWA 抓 JSON，內建簡單重試。
    """
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
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            # 簡單退避
            time.sleep(1 + i)

    raise RuntimeError(f"Error fetching CWA data after {retries} retries: {last_err}")


def save_json(data: dict, data_dir: str = DATA_DIR) -> str:
    os.makedirs(data_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")  # ✅ Windows 檔名安全
    filename = os.path.join(data_dir, f"weather_{ts}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filename


def crawl_and_save(api_key: Optional[str] = None, data_dir: str = DATA_DIR) -> Tuple[str, dict]:
    """
    回傳 (檔案路徑, json)
    """
    api_key = (api_key or _get_api_key() or "").strip()
    if not api_key:
        raise RuntimeError("Missing API key. Please set Streamlit Secrets: CWA_API_KEY")

    data = fetch_cwa_json(api_key=api_key)
    path = save_json(data, data_dir=data_dir)
    return path, data


if __name__ == "__main__":
    print("🌐 Crawling CWA Open Data...")
    try:
        path, _ = crawl_and_save()
        print(f"✅ Saved: {path}")
    except Exception as e:
        print("❌ Error:", e)
        raise
