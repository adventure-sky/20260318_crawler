import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import time

BASE_URL = "https://www.shufa.org.tw"
NEWS_URL = f"{BASE_URL}/news"
TOTAL_PAGES = 12

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}


def get_news_list(page: int) -> list[dict]:
    params = {"page": page} if page > 1 else {}
    resp = requests.get(NEWS_URL, headers=HEADERS, params=params, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    news_items = []

    rows = soup.select("table tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 2:
            continue
        date_col = cols[0].get_text(strip=True)
        link_tag = cols[1].find("a")
        if not link_tag:
            continue
        title = link_tag.get_text(strip=True)
        href = link_tag.get("href", "")
        url = BASE_URL + href if href.startswith("/") else href
        news_items.append({"日期": date_col, "標題": title, "連結": url})

    return news_items


# --- Streamlit UI ---
st.set_page_config(page_title="中華民國書學會 新聞爬蟲", page_icon="🖌️", layout="wide")

st.title("🖌️ 中華民國書學會 最新消息爬蟲")
st.markdown("資料來源：[shufa.org.tw](https://www.shufa.org.tw/news)")
st.divider()

pages = st.slider("爬取頁數", min_value=1, max_value=TOTAL_PAGES, value=3)

if st.button("開始爬取", type="primary"):
    all_news = []
    progress = st.progress(0, text="準備中...")

    for i, page in enumerate(range(1, pages + 1), 1):
        progress.progress(i / pages, text=f"正在爬取第 {page}/{pages} 頁...")
        try:
            items = get_news_list(page)
            all_news.extend(items)
        except Exception as e:
            st.warning(f"第 {page} 頁發生錯誤：{e}")
        time.sleep(0.8)

    progress.empty()

    if all_news:
        df = pd.DataFrame(all_news)
        st.success(f"共取得 **{len(df)}** 筆資料")

        # 讓標題欄位顯示為可點擊連結
        df_display = df.copy()
        df_display["標題"] = df_display.apply(
            lambda r: f'<a href="{r["連結"]}" target="_blank">{r["標題"]}</a>', axis=1
        )
        st.write(df_display[["日期", "標題"]].to_html(escape=False, index=False), unsafe_allow_html=True)

        # 下載 CSV
        csv_data = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="下載 CSV",
            data=csv_data,
            file_name="shufa_news.csv",
            mime="text/csv",
        )
    else:
        st.error("未取得任何資料，請稍後再試。")
