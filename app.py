import streamlit as st
import os
import json
import pandas as pd
import subprocess
import sys
import time

# ===============================
# Page config (一定要放最上面，不能在其他 st.* 後面)
# ===============================
st.set_page_config(
    page_title="一週農業氣象預報 + 農業積溫分析（預報解讀）",
    layout="wide"
)

# ===============================
# Data loader（最新預報 JSON）
# ===============================
DATA_DIR = "weather_data"

def load_latest_json():
    if not os.path.exists(DATA_DIR):
        return None, None

    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    if not files:
        return None, None

    latest_file = sorted(files)[-1]
    path = os.path.join(DATA_DIR, latest_file)

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), latest_file
    except Exception as e:
        return {"_error": str(e), "_file": latest_file}, latest_file

def run_crawler():
    """
    在 Streamlit Cloud 內執行 crawler.py
    - 把 stdout/stderr 回傳顯示，方便 debug
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    p = subprocess.run(
        [sys.executable, "crawler.py"],
        capture_output=True,
        text=True
    )

    return p.returncode, p.stdout, p.stderr

# ===============================
# Sidebar – 情境設定（預報解讀）
# ===============================
st.sidebar.header("🔧 情境設定")

region = st.sidebar.selectbox(
    "📍 分析地區（示範）",
    ["全台"],
    key="region_select"
)

crop = st.sidebar.selectbox(
    "🌾 作物類型",
    ["水稻", "玉米", "高麗菜", "番茄"],
    key="crop_select"
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

# ===============================
# Main UI – Title
# ===============================
st.title("🌤️ 一週農業氣象預報 + 農業積溫分析")

# 先讀本地資料（雲端第一次通常沒有）
data, latest_file = load_latest_json()

# ===============================
# 沒資料時：顯示「抓最新資料」按鈕（雲端必備）
# ===============================
if data is None:
    st.warning("⚠️ 尚未載入氣象預報資料（weather_data 目前沒有 JSON）")

    # 按鈕：抓最新資料
    if st.button("🔄 抓最新資料", use_container_width=True):
        with st.spinner("正在執行 crawler.py 抓取最新資料..."):
            code, out, err = run_crawler()

        st.write("returncode =", code)
        if out:
            st.code(out)
        if err:
            st.code(err)

        # 檢查是否真的產生 json
        files = []
        if os.path.exists(DATA_DIR):
            files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]

        if code != 0 or len(files) == 0:
            st.error("❌ 抓取失敗：沒有產生任何 JSON（請看上方 stdout/stderr）")
            st.stop()

        st.success(f"✅ 抓取完成：{len(files)} 個 JSON，準備重新載入")
        time.sleep(0.5)
        st.rerun()

    # Debug：看看資料夾到底有沒有東西
    with st.expander("🔎 Debug：目前 weather_data 內容"):
        st.write("DATA_DIR =", DATA_DIR)
        st.write("exists?", os.path.exists(DATA_DIR))
        if os.path.exists(DATA_DIR):
            st.write(os.listdir(DATA_DIR))

    st.stop()

# 如果 data 有讀到但內容是 error
if isinstance(data, dict) and "_error" in data:
    st.error(f"❌ JSON 讀取失敗：{data['_file']} / {data['_error']}")
    st.stop()

st.success(f"✅ 已成功載入最新一週氣象預報資料：{latest_file}")

# ===============================
# 🧭 分析情境 – 視覺卡片
# ===============================
st.subheader("🧭 分析情境（預報解讀）")

c1, c2 = st.columns(2)

with c1:
    st.markdown(
        f"""
        <div style="
            padding:24px;
            border-radius:16px;
            background:linear-gradient(135deg,#e0e7ff,#eef2ff);
            box-shadow:0 6px 14px rgba(0,0,0,0.08);
        ">
            <h4>📍 分析地區</h4>
            <h2 style="margin:0;">{region}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""
        <div style="
            padding:24px;
            border-radius:16px;
            background:linear-gradient(135deg,#ecfeff,#cffafe);
            box-shadow:0 6px 14px rgba(0,0,0,0.08);
        ">
            <h4>🌾 作物類型</h4>
            <h2 style="margin:0;">{crop}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

# ===============================
# 🌱 溫度對作物影響（預報解讀）- 先用示意溫度
# ===============================
st.subheader("🌱 一週溫度條件對作物影響（預估）")

temps = [18, 20, 22, 23, 21, 19, 18]

avg_temp = sum(temps) / len(temps)
min_temp = min(temps)
max_temp = max(temps)

crop_temp_range = {
    "水稻": (20, 30),
    "玉米": (18, 30),
    "高麗菜": (15, 25),
    "番茄": (18, 28)
}

opt_min, opt_max = crop_temp_range[crop]

if avg_temp < opt_min:
    impact_level = "偏低"
    impact_icon = "⚠️"
    impact_desc = "氣溫偏低，作物生長速率可能放緩，需留意低溫影響。"
elif avg_temp > opt_max:
    impact_level = "偏高"
    impact_icon = "⚠️"
    impact_desc = "氣溫偏高，可能增加熱逆境風險，需注意水分管理。"
else:
    impact_level = "適宜"
    impact_icon = "✅"
    impact_desc = "氣溫條件適中，有利作物正常生長。"

colA, colB, colC = st.columns(3)
colA.metric("🌡️ 一週平均溫度", f"{avg_temp:.1f} °C")
colB.metric("🌾 作物適宜溫度", f"{opt_min}–{opt_max} °C")
colC.metric("📊 綜合解讀", f"{impact_icon} {impact_level}")

st.info(
    f"""
📌 **作物氣象解讀（{crop}）**

- 預報期間最低溫：約 **{min_temp} °C**
- 預報期間最高溫：約 **{max_temp} °C**
- 綜合判斷：{impact_desc}
"""
)

# ===============================
# 📊 一週氣象預報趨勢（示意）
# ===============================
st.subheader("📊 一週農業氣象預報解讀（溫度趨勢）")

temp_df = pd.DataFrame({
    "預報日": [f"Day {i}" for i in range(1, 8)],
    "平均溫度 (°C)": temps
})

st.line_chart(temp_df.set_index("預報日"))

st.markdown(f"""
### 📌 一週預報解讀摘要（{crop}）

- 本週平均溫度約 **{avg_temp:.1f} °C**，屬於 **{impact_level}** 區間  
- 溫度趨勢呈現「先升後降」，中段需留意溫度變化  
- 整體氣象條件 **{impact_desc}**
""")

# ===============================
# 📦 原始資料（技術佐證）
# ===============================
with st.expander("📦 原始氣象預報 JSON（技術佐證）"):
    st.json(data)
