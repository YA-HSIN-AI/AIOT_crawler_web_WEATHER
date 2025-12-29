import os
import json
import sys
import subprocess
from datetime import datetime

import pandas as pd
import streamlit as st


# -------------------------------
# MUST be first Streamlit command
# -------------------------------
st.set_page_config(
    page_title="一週農業氣象預報 + 農業積溫分析（預報解讀）",
    layout="wide",
)


# ===============================
# Settings
# ===============================
DATA_DIR = "weather_data"


# ===============================
# Helpers
# ===============================
def ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def list_json_files():
    if not os.path.exists(DATA_DIR):
        return []
    files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".json")]
    files.sort()
    return files


def load_latest_json():
    files = list_json_files()
    if not files:
        return None, None

    latest_file = files[-1]
    path = os.path.join(DATA_DIR, latest_file)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), latest_file
    except Exception as e:
        return {"_error": f"Failed to read {latest_file}: {e}"}, latest_file


def run_crawler():
    """
    Try to run crawler.py using current python.
    Works on Streamlit Cloud if crawler.py exists in repo and dependencies are installed.
    """
    if not os.path.exists("crawler.py"):
        return False, "找不到 crawler.py（請確認 repo 內有 crawler.py）"

    ensure_data_dir()

    try:
        p = subprocess.run(
            [sys.executable, "crawler.py"],
            capture_output=True,
            text=True,
            check=False,
        )
        # crawler may print logs
        if p.returncode != 0:
            return False, f"crawler.py 執行失敗（exit={p.returncode}）\n\nSTDERR:\n{p.stderr}\n\nSTDOUT:\n{p.stdout}"
        return True, f"crawler.py 執行成功\n\nSTDOUT:\n{p.stdout}"
    except Exception as e:
        return False, f"無法執行 crawler.py：{e}"


def extract_temps_from_json(data: dict):
    """
    Best-effort parser.
    Your CWA JSON schema may vary. If parsing fails, we fallback to a demo temps list.
    """
    # Fallback demo temps
    fallback = [18, 20, 22, 23, 21, 19, 18]

    if not isinstance(data, dict):
        return fallback

    # Common places we might find temps (schema-dependent)
    # If you later confirm your JSON structure, we can make this exact.
    # For now: try to locate any list of 7 numbers inside.
    def find_numbers(obj):
        nums = []
        if isinstance(obj, dict):
            for v in obj.values():
                nums.extend(find_numbers(v))
        elif isinstance(obj, list):
            for v in obj:
                nums.extend(find_numbers(v))
        else:
            # try parse numeric strings
            if isinstance(obj, (int, float)):
                nums.append(float(obj))
            elif isinstance(obj, str):
                try:
                    nums.append(float(obj))
                except Exception:
                    pass
        return nums

    nums = find_numbers(data)
    # heuristic: if we have >=7 numbers, take last 7 as "temps"
    if len(nums) >= 7:
        temps = [round(x, 1) for x in nums[-7:]]
        # sanity: avoid nonsense like huge ids, timestamps etc.
        # keep values within plausible temperature range
        temps2 = [t for t in temps if -10 <= t <= 45]
        if len(temps2) >= 7:
            return temps2[-7:]
    return fallback


def crop_range(crop: str):
    table = {
        "水稻": (20, 30),
        "玉米": (18, 30),
        "高麗菜": (15, 25),
        "番茄": (18, 28),
    }
    return table.get(crop, (18, 28))


def impact_judgement(avg_temp: float, opt_min: float, opt_max: float):
    if avg_temp < opt_min:
        return "偏低", "⚠️", "氣溫偏低，作物生長速率可能放緩，需留意低溫影響。"
    if avg_temp > opt_max:
        return "偏高", "⚠️", "氣溫偏高，可能增加熱逆境風險，需注意水分管理。"
    return "適宜", "✅", "氣溫條件適中，有利作物正常生長。"


# ===============================
# Sidebar
# ===============================
st.sidebar.header("🔧 情境設定")

region = st.sidebar.selectbox(
    "📍 分析地區（示範）",
    ["全台"],
    key="region_select",
)

crop = st.sidebar.selectbox(
    "🌾 作物類型",
    ["水稻", "玉米", "高麗菜", "番茄"],
    key="crop_select",
)

st.sidebar.markdown("### 📅 預報期間")
st.sidebar.info("以 **今日起算之未來 7 天氣象預報** 進行解讀")

st.sidebar.markdown("---")
st.sidebar.info(
    "📌 本系統為「預報解讀型 Demo」\n\n"
    "- 使用 CWA 一週氣象預報資料\n"
    "- 提供作物生長條件與風險判斷\n"
    "- 非歷史回溯分析"
)

st.sidebar.markdown("---")
st.sidebar.subheader("☁️ Cloud 資料")
st.sidebar.caption("Cloud 不會有你本機的 weather_data，因此需在雲端執行 crawler.py 產生資料。")


# ===============================
# Main
# ===============================
st.title("🌤️ 一週農業氣象預報 + 農業積溫分析")

data, latest_fname = load_latest_json()

if data is None:
    st.warning("⚠️ 尚未載入氣象預報資料（Cloud 沒有本機檔案）")

    col1, col2 = st.columns([1, 3])
    with col1:
        run = st.button("🔄 立即抓取最新預報", key="run_crawler_btn")
    with col2:
        st.caption("按下後會在雲端執行 crawler.py，並產生 weather_data/*.json（若需要 API KEY，請在 Cloud Secrets 設定）。")

    with st.expander("🧩 如果抓不到資料我該怎麼做？"):
        st.markdown(
            """
1) 確認 repo 內有 `crawler.py`  
2) `requirements.txt` 至少包含：`streamlit`, `requests`, `pandas`  
3) 若 CWA API 需要金鑰，請到 Streamlit Cloud → **Manage app** → **Settings → Secrets** 加入：
```toml
CWA_API_KEY="你的key"
