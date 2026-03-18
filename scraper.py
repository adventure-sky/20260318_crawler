import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://www.shufa.org.tw"
NEWS_URL = f"{BASE_URL}/news"
TOTAL_PAGES = 12
OUTPUT_FILE = "shufa_news.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}


def get_news_list(page: int) -> list[dict]:
    """擷取指定頁碼的新聞列表"""
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

        news_items.append({
            "date": date_col,
            "title": title,
            "url": url,
        })

    return news_items


def scrape_all() -> list[dict]:
    """爬取所有頁面的新聞"""
    all_news = []

    for page in range(1, TOTAL_PAGES + 1):
        print(f"正在爬取第 {page}/{TOTAL_PAGES} 頁...")
        try:
            items = get_news_list(page)
            all_news.extend(items)
            print(f"  → 取得 {len(items)} 筆")
        except Exception as e:
            print(f"  → 第 {page} 頁發生錯誤：{e}")

        time.sleep(1)

    return all_news


def save_to_csv(data: list[dict], filename: str):
    """將資料儲存為 CSV"""
    if not data:
        print("無資料可儲存")
        return

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "title", "url"])
        writer.writeheader()
        writer.writerows(data)

    print(f"\n已儲存 {len(data)} 筆資料至 {filename}")


if __name__ == "__main__":
    news = scrape_all()
    save_to_csv(news, OUTPUT_FILE)
