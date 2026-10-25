import time
import urllib.parse
from bs4 import BeautifulSoup
import requests

# -------------------------------------------------------------------
# 設定エリア
# -------------------------------------------------------------------
TIMETABLE_URL = (
    "http://sairiku.net/result/2026/ageo_1025/shtml/TimeTable.html"
)

# 検索したい学校・所属名 (速報サイト上の表記と一致させてください)
TARGET_KEYWORD = "電気通信大"  # ← ご自身の学校名・所属名

OUTPUT_FILE = "target2026.txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
    )
}
# -------------------------------------------------------------------


def make_target_list():
    print(f"[{TIMETABLE_URL}] を読み込んでいます...")

    try:
        res = requests.get(TIMETABLE_URL, headers=HEADERS, timeout=5)
        res.encoding = "cp932"
        soup = BeautifulSoup(res.text, "html.parser")

        links = soup.find_all("a", href=True)
        print(f"タイムテーブル上の全リンク数: {len(links)}")

        matched_items = []
        visited_urls = set()

        for a in links:
            href = a["href"]

            # .html 以外のリンクや、TimeTable自身・トップページなどは除外
            if not href.endswith(".html") or "TimeTable" in href:
                continue

            abs_url = urllib.parse.urljoin(TIMETABLE_URL, href)
            if abs_url in visited_urls:
                continue

            visited_urls.add(abs_url)

            try:
                sub_res = requests.get(abs_url, headers=HEADERS, timeout=3)
                sub_res.encoding = "cp932"

                # 指定した学校名が含まれているか判定
                if TARGET_KEYWORD in sub_res.text:
                    sub_soup = BeautifulSoup(sub_res.text, "html.parser")
                    race_title = (
                        sub_soup.title.text.strip()
                        if sub_soup.title
                        else a.get_text(strip=True)
                    )
                    matched_items.append((abs_url, race_title))
                    print(f"  ✅ ヒット: {race_title} ({abs_url})")

            except Exception as e:
                print(f"  ⚠️ 読み込みエラー ({abs_url}): {e}")

            time.sleep(0.1)

        # target2026.txt に保存
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(
                f"# '{TARGET_KEYWORD}' 出場種目リスト"
                f" (全{len(matched_items)}件)\n\n"
            )
            for url, title in matched_items:
                f.write(f"# {title}\n")
                f.write(f"{url}\n\n")

        print(
            f"\n🎉 完了！ {len(matched_items)} 件の対象URLを"
            f" '{OUTPUT_FILE}' に保存しました。"
        )

    except Exception as e:
        print(f"❌ TimeTableの取得失敗: {e}")


if __name__ == "__main__":
    make_target_list()
